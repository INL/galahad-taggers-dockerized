"""Contains values used by both tagger worker and webservice."""

from pathlib import Path

UPLOAD_FOLDER = Path("input")
STATUS_FOLDER = Path("status")
PROCESS_FOLDER = Path("process")
OUTPUT_FOLDER = Path("output")
ERROR_FOLDER = Path("error")

for folder in [
    UPLOAD_FOLDER,
    STATUS_FOLDER,
    PROCESS_FOLDER,
    OUTPUT_FOLDER,
    ERROR_FOLDER,
]:
    folder.mkdir(exist_ok=True, parents=True)
