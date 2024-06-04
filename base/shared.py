# Contains values used by both tagger worker and webservice

import os

UPLOAD_FOLDER = "input"
OUTPUT_FOLDER = "output"
ERROR_FOLDER = "error"

TEXT_EXTENSIONS = {"txt"}
ALLOWED_EXTENSIONS = TEXT_EXTENSIONS


def file_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


# make sure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# make sure the output folder exists
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# make sure the error folder exists
if not os.path.exists(ERROR_FOLDER):
    os.makedirs(ERROR_FOLDER)
