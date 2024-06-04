"""
Web API for the server to talk to the tagger.

The server can upload files, delete files, and get the status of files.
File are processed automatically once uploaded, with the result being sent back to the callback server.
Input files are deleted automatically after being processed.

Deleting files also stops the tagger if that file was being processed. 
(Thus, deleting all input files is equivalent to stopping the tagger.)
"""

# Standard library
import os
import subprocess
import uuid

# Third-party
import bottle
from bottle import HTTPResponse, request, request, static_file, FileUpload
from bottle import post, get, delete

# Local
from shared import OUTPUT_FOLDER, UPLOAD_FOLDER, ERROR_FOLDER
from statuslogger import StatusLogger
from process import OUTPUT_EXTENSION, PROCESSING_SPEED

app = application = bottle.default_app()


@get("/")
def main():
    return """
    <p>Any file will be interpreted as plain text.</p>
    <p>[GET /health] health check endpoint</p>
    <p>[GET /input] get an upload form (for convenience)</p>
    <p>[POST /input] upload a file for processing. Returns an identifier for the uploaded file.</p>
    <p>[DELETE /input/FILE_IDENTIFIER] delete input file with FILE_IDENTIFIER from server.</p>
    <p>[GET /status] get a dict with the status of files</p>
    <p>[GET /status/FILE_IDENTIFIER] get status for file with FILE_IDENTIFIER</p>
    <p>[GET /error] get a list files with errors</p>
    <p>[GET /error/FILE_IDENTIFIER] download file with FILE_IDENTIFIER from server</p>
    <p>[GET /output] get a list of processed files</p>
    <p>[GET /output/FILE_IDENTIFIER] download processed file FILE_IDENTIFIER</p>
    <p>[DELETE /output/FILE_IDENTIFIER] delete file with FILE_IDENTIFIER from server</p>
    """


@get("/health")
def health():
    # du -sb includes the size of the dir, probably 4096. Which is fine, most files will be quite a bit larger.
    # And also, it sort of accounts for the delay of starting a thread
    queue_size = int(
        subprocess.check_output(["du", "-sb", "/input"]).split()[0].decode("utf-8")
    )
    return {
        "healthy": True,
        "queueSizeAtTagger": queue_size,  # bytes, but mostly ascii so 1 byte is 1 char.
        "processingSpeed": PROCESSING_SPEED,  # char/s
        "message": "I am healthy.",
    }


@get("/input")
# upload form for convenience
def handle_file():
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """


@post("/input")
def post_input():
    # check if the post request has the file part
    if "file" not in request.files:
        return HTTPResponse("No file part", 400)
    file: FileUpload = request.files["file"]
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == "":
        return HTTPResponse("No selected file", 400)
    if file:
        id = str(uuid.uuid4())
        file.save(os.path.join(UPLOAD_FOLDER, id))
        # register the file
        sl = StatusLogger(id)
        sl.init("File arrived")
        return id
    else:
        return HTTPResponse("File is not defined", 400)


@delete("/input/<id>")
def delete_input(id: str):
    path = os.path.join(UPLOAD_FOLDER, id)
    if os.path.isfile(path):
        sl = StatusLogger(id)
        sl.delete_status()
        os.remove(path)
        return HTTPResponse("File " + id + " deleted", 200)
    else:
        return HTTPResponse("File is not defined", 400)


@get("/status")
def get_status():
    return StatusLogger.get_all_statusses()


@get("/status/<id>")
def get_status_for(id: str):
    sl = StatusLogger(id)
    return sl.get_status()


@get("/error")
def get_error_files():
    return {"error_files": os.listdir(ERROR_FOLDER)}


@get("/error/<id>")
def get_error_file(id: str):
    filename = id
    return static_file(filename, ERROR_FOLDER)
    # what to do if the file doesn't exists?


@get("/output")
def get_processed_files():
    return {"processed_files": os.listdir(OUTPUT_FOLDER)}


@get("/output/<id>")
def get_processed_file(id: str):
    filename = id + OUTPUT_EXTENSION
    return static_file(filename, OUTPUT_FOLDER)
    # what to do if the file doesn't exists?


@delete("/output/<id>")
def delete_file(id: str):
    """
    Delete the file, its associated status, and stop the processing if it is running.
    """
    path = os.path.join(OUTPUT_FOLDER, id + OUTPUT_EXTENSION)

    # remove the status
    sl = StatusLogger(id)
    sl.delete_status()

    # remove the file
    if os.path.isfile(path):
        os.remove(path)
        print(path)
        return HTTPResponse("File " + id + " deleted", 200)


app.run(host="0.0.0.0", port=8080)
