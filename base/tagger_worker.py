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

import json
import multiprocessing as mp
import os
import time
import traceback
from multiprocessing.pool import Pool
from pathlib import Path
from urllib.request import Request, urlopen
from uuid import UUID, uuid4

import process
from process import OUTPUT_EXTENSION
from shared import OUTPUT_FOLDER, UPLOAD_FOLDER
from statuslogger import ProcessStatus, StatusLogger

CALLBACK_SERVER: str = os.getenv("CALLBACK_SERVER") or ""
NUM_WORKERS = int(os.getenv("NUM_WORKERS") or 1)
# Needs to be defined as a reference object, e.g. dict.
_global: dict[str, Pool] = {"pool": None}


def run_pending_tasks() -> None:
    """
    Send a new task to the pool if there is no busy task.
    If there is no pool running, start a new pool.
    """
    # One task at a time.
    tasks_in_queue: int = _global["pool"]._taskqueue.qsize()
    if tasks_in_queue > 0:
        return

    # Start new task when not busy
    pending_tasks = StatusLogger.get_all_pending_tasks()
    for sl in pending_tasks:
        # A task could have been cancelled in the meantime.
        # In which case the pending_tasks list is outdated. (It will refresh, though.)
        if sl.exists() and sl.get_status()["busy"] is False:
            sl.busy("Processing file")  # Sets busy true
            # Extra None check for typing
            if (not is_pool_running()) or _global["pool"] is None:
                # Spawn pool if not running
                _global["pool"] = mp.Pool(processes=NUM_WORKERS)
            # Perform task at running pool
            _global["pool"].apply_async(process_file, args=(sl.uuid,))


def process_file(uuid: UUID) -> None:
    """
    Process a file:
    Create a ProcessStatus, set the StatusLogger to busy, send the file to the tagger with a timeout,
    and set the status once finished, and send the result to the callback server.
    This function runs in a separate process.
    """
    # Register the process
    ps = ProcessStatus(uuid, os.getpid())
    sl = StatusLogger(uuid)

    # Set up paths
    in_path = UPLOAD_FOLDER / str(uuid)
    out_path = OUTPUT_FOLDER / (str(uuid) + OUTPUT_EXTENSION)

    try:
        tag(uuid, in_path, out_path, sl, ps)
    except Exception as e:
        # Process failed, free up the pid
        ps.delete_status()
        sl.error(f"An exception occurred: {e}")
        print(traceback.format_exc())
        # delete inputfile
        in_path.unlink(missing_ok=True)
        if CALLBACK_SERVER:
            send_error_to_callback_server(uuid, message=str(e))


def tag(
    uuid: UUID,
    in_path: Path,
    out_path: Path,
    sl: StatusLogger,
    ps: ProcessStatus,
) -> None:
    """
    Attempt to tag the file by the tagger with a timeout.
    Send the result to the server, whether successful or not.
    Also appropriately logs the status.
    """
    process.process(in_path, out_path)

    # Done processing
    ps.delete_status()  # Frees up the tagger
    in_path.unlink(missing_ok=True)

    sl.finished(f"result has size {out_path.stat().st_size}")
    if CALLBACK_SERVER:
        send_result_to_callback_server(uuid, out_path)
        sl.delete_status()


def send_result_to_callback_server(uuid: UUID, file: Path) -> None:
    """Send the result to the callback server."""
    url = CALLBACK_SERVER + "/result"
    boundary = uuid4().hex
    delimiter = ("--" + boundary).encode()
    file_data = file.read_bytes()
    # output has been read, can be deleted
    file.unlink(missing_ok=True)
    body = b"\r\n".join(
        [
            delimiter,
            b'Content-Disposition: form-data; name="file_id"',
            b"",
            str(uuid).encode(),
            delimiter,
            b'Content-Disposition: form-data; name="file"; uuid="'
            + file.name.encode()
            + b'"',
            b"Content-Type: application/octet-stream",
            b"",
            file_data,
            delimiter + b"--",
            b"",
        ],
    )
    request = Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    urlopen(request)


def send_error_to_callback_server(uuid: str, message: str) -> None:
    """Send the error to the callback server."""
    url = CALLBACK_SERVER + "/error"
    json_data = {"file_id": uuid, "message": message}
    body = json.dumps(json_data).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urlopen(request)


def is_pool_running() -> bool:
    """Check if the pool is running by trying to execute a dummy function."""
    if _global["pool"] is None:
        return False
    try:
        _global["pool"].apply_async(lambda: None)
    except ValueError as e:
        if str(e) == "Pool not running":
            return False
    return True


def terminate_pool() -> None:
    """Terminate the pool if it is running."""
    _global["pool"].terminate()


def run_background() -> None:
    """Background loop."""
    # Can't use fork with the gpu.
    mp.set_start_method("spawn", force=True)
    _global["pool"] = mp.Pool(processes=NUM_WORKERS)

    # It is ugly, but it is also used here:
    # https://pypi.org/project/schedule/
    while True:
        run_pending_tasks()
        time.sleep(0.05)
