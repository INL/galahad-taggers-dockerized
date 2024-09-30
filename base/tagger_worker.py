"""
Acts as a daemon that checks on an interval if there are any pending tasks (i.e. documents) to be processed.
It then processes them one by one (i.e. running the tagger process), keeps track of their statusses, 
and sends the results to the callback server. The server then responds with KEEP or DELETE,
which determines if the resulting tagged output file is kept or deleted.
Input files are deleted automatically after processing, or moved to the error folder if processing fails.

We use a multiprocessing pool to process files, because we want to kill the process if needed.
Additonally the taggers need to be initialized only once (and in the same thread), 
so that can be done at pool initialization.
"""

# Standard library
import errno
import os
import time
import multiprocessing as mp
from multiprocessing.pool import Pool
from typing import Optional
import subprocess
import requests
import traceback
import pathlib

# Local
import process
from timeout import timeout
from shared import OUTPUT_FOLDER, UPLOAD_FOLDER, ERROR_FOLDER
from statuslogger import StatusLogger, ProcessStatus
from process import PROCESSING_SPEED

CALLBACK_SERVER: str = os.getenv("CALLBACK_SERVER") or ""
NUM_WORKERS = int(os.getenv("NUM_WORKERS") or 1)


def run_pending_tasks() -> None:
    """
    Send a new task to the pool if there is no busy task.
    If there is no pool running, start a new pool.
    """
    global pool

    # One task at a time.
    tasks_in_queue = pool._taskqueue.qsize()
    if tasks_in_queue > 0:
        return

    # Start new task when not busy
    pending_tasks = StatusLogger.get_all_pending_tasks()
    for sl in pending_tasks:
        # A task could have been cancelled in the meantime.
        # In which case the pending_tasks list is outdated. (It will refresh, though.)
        if sl.exists():
            if sl.get_status()["busy"] is False:
                sl.busy("Parsing file")  # Sets busy true
                # Extra None check for typing
                if (not is_pool_running(pool)) or pool is None:
                    # Spawn pool if not running
                    pool = mp.Pool(processes=NUM_WORKERS, initializer=process.init)
                # Perform task at running pool
                pool.apply_async(process_file, args=(sl.filename,))


def process_file(filename: str):
    """
    Process a file:
    Create a ProcessStatus, set the StatusLogger to busy, send the file to the tagger with a timeout,
    and set the status once finished, and send the result to the callback server.
    This function runs in a separate process.
    """
    # Register the process
    ps = ProcessStatus(filename, os.getpid())
    sl = StatusLogger(filename)

    # Set up paths
    in_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, filename))
    out_path = os.path.abspath(
        os.path.join(OUTPUT_FOLDER, filename + process.OUTPUT_EXTENSION)
    )
    error_path = os.path.abspath(os.path.join(ERROR_FOLDER, filename))

    try:
        tag(filename, in_path, out_path, sl, ps)
    except Exception as e:
        # Process failed, free up the pid
        ps.delete_status()
        sl.error(f"An exception occurred: {e}")
        print(traceback.format_exc())
        # copy input file to error folder if it exists
        if os.path.isfile(in_path):
            os.rename(in_path, error_path)
        if CALLBACK_SERVER != "":
            sl.error("Sending error to callback server")
            send_error_to_callback_server(filename, out_path, message=str(e))


def tag(
    filename: str, in_path: str, out_path: str, sl: StatusLogger, ps: ProcessStatus
) -> None:
    """
    Attempt to tag the file by the tagger with a timeout.
    Send the result to the server, whether successful or not.
    Also appropriately logs the status.
    """
    # 300s = 5min fixed time
    # plus
    # bytes * speed variable time
    in_bytes_size = None
    while in_bytes_size is None:
        if os.path.isfile(in_path):
            try:
                in_bytes_size = int(
                    subprocess.check_output(["du", "-sb", in_path])
                    .split()[0]
                    .decode("utf-8")
                )
            except Exception as e:
                print(f"Error getting file size: {e}")
                time.sleep(1)
        else:
            raise FileNotFoundError(f"File {in_path} not found")

    time_out = 300 + in_bytes_size + PROCESSING_SPEED
    sl.busy("Will process with a timeout after " + str(time_out) + " seconds")

    # Runs the respective tagger software synchronously.
    @timeout(time_out, os.strerror(errno.ETIME))
    def doTagging():
        process.process(in_path, out_path)

    doTagging()

    # Done processing
    ps.delete_status()  # Frees up the tagger
    sl.finished("Removing input file")
    pathlib.Path(in_path).unlink(missing_ok=True)

    sl.finished(
        "Finished processing %s, result has size %d"
        % (filename, os.path.getsize(out_path))
    )
    if CALLBACK_SERVER != "":
        sl.finished("Sending output to callback server")
        send_result_to_callback_server(filename, out_path)
        sl.finished("Finished")
        sl.delete_status()


def keep_or_delete_file(response: requests.Response, out_path: str) -> None:
    """
    Keep or delete the file based on the server response.
    """
    if response.content.decode("utf-8") == "KEEP":
        print(f"I will keep the file: {out_path}")
    elif response.content.decode("utf-8") == "DELETE":
        print(f"I will delete the file: {out_path}")
        os.remove(out_path)
    else:
        print(f"Reply unintelligeble, will delete anyway {out_path}")
        os.remove(out_path)


def send_result_to_callback_server(filename: str, out_path: str) -> None:
    """
    Send the result to the callback server and keep or delete the file based on the server response.
    """
    file = open(out_path, "rb")
    url = CALLBACK_SERVER + "/result"
    payload = {"file_id": filename}
    files = {"file": file}
    r = requests.post(url, files=files, data=payload)
    keep_or_delete_file(r, out_path)


def send_error_to_callback_server(filename: str, out_path: str, message: str) -> None:
    """
    Send the error to the callback server and keep or delete the file based on the server response.
    """
    url = CALLBACK_SERVER + "/error"
    payload = {"file_id": filename}
    json_data = {"file_id": filename, "message": message}
    r = requests.post(url, json=json_data, params=payload)
    keep_or_delete_file(r, out_path)


def is_pool_running(pool: Optional[Pool]) -> bool:
    """
    Check if the pool is running by trying to execute a dummy function.
    """
    if pool is None:
        return False
    try:
        pool.apply_async(lambda: None)
    except ValueError as e:
        if str(e) == "Pool not running":
            return False
    return True


# Pool needs to be defined after the functions it will execute.
# https://stackoverflow.com/questions/41385708/multiprocessing-example-giving-attributeerror#comment101561695_42383397
pool = None

if __name__ == "__main__":
    # Can't use fork with the gpu.
    mp.set_start_method("spawn", force=True)
    pool = mp.Pool(processes=NUM_WORKERS, initializer=process.init)

    # It is ugly, but it is also used here:
    # https://pypi.org/project/schedule/
    while True:
        run_pending_tasks()
        time.sleep(0.05)
