import os
import requests
import time
import sys
from tqdm import tqdm

# Define the webservice URL constant
WEBSERVICE_URL = "http://localhost:8120"


# Function to convert a file using the webservice
def convert_file(file_path, output_dir):
    file_name = os.path.basename(file_path)
    output_file_path = os.path.join(output_dir, file_name) + ".conllu"
    if os.path.exists(output_file_path):
        print(f"Output file already exists: {output_file_path}")
        return

    # Read the file content
    with open(file_path, "r", encoding="utf8") as file:
        content = file.read()

    # Send a POST request to the /input endpoint with multipart/form-data
    files = {"file": (file_name, content)}
    response = requests.post(f"{WEBSERVICE_URL}/input", files=files)

    # Check if the request was successful
    if response.ok:
        job_uuid = response.text
        # Send a GET request to the /status endpoint to check the job status
        while True:
            response = requests.get(f"{WEBSERVICE_URL}/status/{job_uuid}").json()
            todo = response["pending"] or response["busy"]

            # Check if the job is complete
            if response["finished"]:
                # Send a GET request to the /output/FILENAME endpoint to download the output file
                response = requests.get(f"{WEBSERVICE_URL}/output/{job_uuid}")
                if response.ok:
                    # Write the output file to the specified output directory
                    with open(output_file_path, "w") as output_file:
                        output_file.write(response.text)

                    # Send a DELETE request to the /output/FILENAME endpoint to clean up
                    requests.delete(f"{WEBSERVICE_URL}/output/{job_uuid}")

                else:
                    print(f"Error downloading output file for: {file_path}")
                break

            elif response["error"]:
                print(f"Error converting file: {file_path}")
                break

            elif not todo:
                print(
                    f"Job for is in invalid state (not pending, busy, finished or error): {file_path}"
                )
                break

            # Wait for some time before checking the job status again
            time.sleep(1)
    else:
        print(f"Error sending file content for: {file_path}")


# Function to convert files in a directory tree
def convert_files_in_directory(input_dir, output_dir):
    # Check if the input directory exists
    if not os.path.isdir(input_dir):
        print(f"Input directory does not exist: {input_dir}")
        return

    # Check if the output directory exists
    if not os.path.isdir(output_dir):
        print(f"Output directory does not exist: {output_dir}")
        return

    # Walk through the directory tree
    # Convert each file in the directory
    for root, dirs, files in os.walk(input_dir):
        # Create the output subdirectory for the current root
        output_subdir = os.path.join(output_dir, os.path.relpath(root, input_dir))
        os.makedirs(output_subdir, exist_ok=True)

        # Convert each file in the directory
        for file in tdqm(files):
            file_path = os.path.join(root, file)
            convert_file(file_path, output_subdir)


# Specify the input and output directories
# Validate and retrieve the input and output directories from program arguments
# if len(sys.argv) != 3:
#     print(
#         "Usage: python convert-using-webservice.py <input_directory> <output_directory>"
#     )
#     sys.exit(1)

input_dir = "input"  # sys.argv[1]
output_dir = "output"  # sys.argv[2]

# Check if the input directory exists
if not os.path.isdir(input_dir):
    print(f"Input directory does not exist: {input_dir}")
    sys.exit(1)

# Check if the output directory exists
if not os.path.isdir(output_dir):
    print(f"Output directory does not exist: {output_dir}")
    sys.exit(1)

# Convert files in the directory tree
convert_files_in_directory(input_dir, output_dir)
