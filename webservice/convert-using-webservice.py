# Standard
import os
import time
import sys
from concurrent import futures
import random

# Third-party
from tqdm import tqdm
import requests
import requests.exceptions

# Constants
WEBSERVICE_URL = "http://lancelot.ato.ivdnt.loc/termwerk"
NUM_WORKERS = 8 * 4 # 4 files per tagger is doable, especially with small files.
REQUEST_TIMEOUT = 5 # SECONDS
RETRY_TIMEOUT = 5 # SECONDS
SLEEP_BETWEEN_REQUESTS = 0.5 # SECONDS


def convert_file(in_file_path, out_file_path):
    """
    To be run in a thread. Infinitely retry on connection timeout.
    """
    try:
        convert_file_inner(in_file_path, out_file_path)
    except requests.exceptions.ConnectTimeout as e:
        print(f"Error connecting to webservice, will retry in {RETRY_TIMEOUT} seconds: {e}")
        time.sleep(RETRY_TIMEOUT)
        convert_file(in_file_path, out_file_path)


def convert_file_inner(in_file_path, out_file_path):
    file_name = os.path.basename(in_file_path)

    # Read the file content
    with open(in_file_path, "r", encoding="utf8") as file:
        content = file.read()

    # Send a POST request to the /input endpoint with multipart/form-data
    files = {"file": (file_name, content)}
    def post_file():
        return requests.post(f"{WEBSERVICE_URL}/input", files=files, timeout=REQUEST_TIMEOUT)
    response = post_file()

    # Keep retrying until the request is successful
    # Though connection timeout is not caught.
    while not response.ok:
        time.sleep(1)
        response = post_file()
    
    poll_status(in_file_path, out_file_path, job_uuid=response.text)


def poll_status(in_file_path, out_file_path, job_uuid):
    # Keep polling until finished
    while True:
        # status example: {pending: bool, busy: bool, finished: bool, error: bool, message: str}
        status = requests.get(f"{WEBSERVICE_URL}/status/{job_uuid}", timeout=REQUEST_TIMEOUT).json()

        if status["finished"]:
            # Retrieve output file if finished
            response = requests.get(f"{WEBSERVICE_URL}/output/{job_uuid}", timeout=REQUEST_TIMEOUT)
            if response.ok:
                # Write output file
                with open(out_file_path, "w") as output_file:
                    output_file.write(response.text)
                # Clean up on the server
                requests.delete(f"{WEBSERVICE_URL}/output/{job_uuid}", timeout=REQUEST_TIMEOUT)
            else:
                print(f"[Job {job_uuid}] Error downloading output file for: {in_file_path}")
            
            # Break regardless of success or failure
            # There is nothing we can do.
            break

        elif status["pending"] or status["busy"]:
            time.sleep(SLEEP_BETWEEN_REQUESTS)

        else:
            print(f"[Job {job_uuid}] Error converting file: {in_file_path} {status["message"]}")
            break


def convert_files_in_directory_tree(input_dir, output_dir):
    """
    Walks through the directory tree and converts each file found.
    """
    # used for progress bar
    total_files = directory_tree_file_count(input_dir)
    with tqdm(total=total_files) as progress_bar:

        # Parallel processing
        with futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        
            # Walk through the directory tree
            for root, _, files in os.walk(input_dir):

                # Create the output subdirectory for the current root
                output_subdir = os.path.join(output_dir, os.path.relpath(root, input_dir))
                os.makedirs(output_subdir, exist_ok=True)

                # Convert each file in the directory
                for file in files:

                    # Construct paths
                    in_file_path = os.path.join(root, file)
                    out_file_path = os.path.join(output_subdir, os.path.basename(in_file_path)) + ".conllu"

                    # Skip if the output file already exists
                    if os.path.exists(out_file_path):
                        progress_bar.update(1)
                        continue
                    
                    # Convert file
                    future = executor.submit(convert_file, in_file_path, out_file_path)
                    # Update progress bar once done
                    future.add_done_callback(lambda _ : progress_bar.update(1))


def directory_tree_file_count(dir: str):
    """
    The number of files in the entire directory tree.
    """
    total = 0
    for _, _, files in os.walk(dir):
        total += len(files)
    return total


if __name__ == "__main__":
    # Validate arguments
    if len(sys.argv) != 3:
        print(
            "Usage: python convert-using-webservice.py <input_directory> <output_directory>"
        )
        sys.exit(1)
    
    # CLI arguments
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # Check if the input directory exists
    if not os.path.isdir(input_dir):
        print(f"Input directory does not exist: {input_dir}")
        sys.exit(1)

    # Check if the output directory exists
    if not os.path.isdir(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    # Convert files in the directory tree
    convert_files_in_directory_tree(input_dir, output_dir)
