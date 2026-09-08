"""
Web API for the server to talk to the tagger.

The server can upload files, delete files, and get the status of files.
File are processed automatically once uploaded.
If defined, result are sent to the callback server.
Input files are deleted automatically after being processed.

Deleting files also stops the tagger if that file was being processed.
(Thus, deleting all input files is equivalent to stopping the tagger.)
"""

import threading
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import bottle
from bottle import FileUpload, HTTPResponse, delete, get, post, request, static_file
from process import OUTPUT_EXTENSION
from shared import ERROR_FOLDER, OUTPUT_FOLDER, UPLOAD_FOLDER
from statuslogger import StatusLogger
from tagger_worker import run_background, terminate_pool

app = application = bottle.default_app()


@get("/")
def main() -> str:
    """Simple API documentation."""
    return """
    <p>Any file will be interpreted as plain text.</p>
    <p>[GET /health] health check endpoint</p>
    <p>[GET /input] get an upload form (for convenience)</p>
    <p>[POST /input] upload a file for processing. Returns an identifier for the uploaded file.</p>
    <p>[DELETE /input/uuid] delete input file with uuid from server.</p>
    <p>[GET /status] get a dict with the status of files</p>
    <p>[GET /status/uuid] get status for file with uuid</p>
    <p>[GET /error] get a list files with errors</p>
    <p>[GET /error/uuid] download file with uuid from server</p>
    <p>[GET /output] get a list of processed files</p>
    <p>[GET /output/uuid] download processed file uuid</p>
    <p>[DELETE /output/uuid] delete file with uuid from server</p>
    """


@get("/health")
def health():
    return {"healthy": True, "message": "I am healthy."}


@get("/input")
def handle_file() -> str:
    """Render the file upload form."""
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
def post_input() -> HTTPResponse:
    """Upload file for processing."""
    # check if the post request has the file part
    if "file" not in request.files:
        return HTTPResponse("No file part", 400)
    file: FileUpload = request.files["file"]
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if not file.filename:
        return HTTPResponse("No selected file", 400)
    if file:
        uuid = str(uuid4())
        file_dest = UPLOAD_FOLDER / uuid
        file.save(str(file_dest))  # bottle needs a string
        if not file_dest.is_file():
            return HTTPResponse("File could not be saved. Please try again.", 500)
        # register the file
        sl = StatusLogger(uuid)
        sl.init("File arrived")
        return HTTPResponse(uuid, 202)
    return HTTPResponse("File is not defined", 400)


@delete("/input/<uuid>")
def delete_input(uuid: UUID) -> HTTPResponse:
    """Delete input file, its associated status, and stop processing if running."""
    file = UPLOAD_FOLDER / str(uuid)
    if file.is_file():
        sl = StatusLogger(uuid)
        sl.delete_status()
        file.unlink(missing_ok=True)
        return HTTPResponse(f"File {uuid} deleted", 200)
    return HTTPResponse("File not found", 400)


@get("/status")
def get_status() -> dict[str, Any]:
    """Get all statusses."""
    return StatusLogger.get_all_statusses()


@get("/status/<uuid>")
def get_status_for(uuid: UUID) -> dict[str, Any]:
    """Get status of uuid."""
    return StatusLogger(uuid).get_status()


@get("/error")
def get_error_files() -> dict[str, list[Path]]:
    """Get all errors."""
    return {"error_files": list(ERROR_FOLDER.iterdir())}


@get("/error/<uuid>")
def get_error_file(uuid: UUID) -> HTTPResponse:
    """Get error for uuid."""
    file = UPLOAD_FOLDER / str(uuid)
    if file.is_file():
        return static_file(str(uuid), ERROR_FOLDER)
    return HTTPResponse("File not found", 404)


@get("/output")
def get_processed_files() -> dict[str, list[str]]:
    """Return all finished uuids."""
    return {"processed_files": [file.stem for file in OUTPUT_FOLDER.iterdir()]}


@get("/output/<uuid>")
def get_processed_file(uuid: str) -> HTTPResponse:
    """Get output file."""
    file = Path(uuid + OUTPUT_EXTENSION)
    if (OUTPUT_FOLDER / file).is_file():
        return static_file(str(file), OUTPUT_FOLDER)
    return HTTPResponse("File not found", 404)


@delete("/output/<uuid>")
def delete_file(uuid: str) -> HTTPResponse:
    """Delete file, its status, and stop processing if running."""
    file = OUTPUT_FOLDER / (uuid + OUTPUT_EXTENSION)

    if file.is_file():
        # remove the file
        file.unlink()
        # remove status and stop processing
        sl = StatusLogger(uuid)
        sl.delete_status()
        return HTTPResponse("File " + uuid + " deleted", 200)
    return HTTPResponse("File not found", 404)


@post("/terminate")
def terminate() -> HTTPResponse:
    """Terminate the worker pool immediately, freeing RAM (& VRAM)."""
    terminate_pool()
    return HTTPResponse("Terminated the worker pool", 200)


if __name__ == "__main__":
    threading.Thread(target=run_background, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
