"""
Initialize the tagger if needed and process input files by calling the tagger
and ensuring the output is written to the expected file.
"""

from pathlib import Path

# The extension of output files produced by the tagger.
OUTPUT_EXTENSION = ".tsv"


def init() -> None:
    """Any initialization the tagger may need before processing."""


def process(in_file: Path, out_file: Path) -> None:
    """Process the file at path "in_file" and write the result to path "out_file"."""
    with out_file.open("x", encoding="utf-8") as f_out:
        f_out.write("Did you forget to override process.py?")
