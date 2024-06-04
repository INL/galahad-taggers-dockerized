"""
Initialize the pie tagger from the python class directly, and use that object to tag.
We use this method instead of calling 'pie tag' on the commandline, 
because we want to avoid the overhead of reinitializing the tagger.
"""

# Standard library
import os
import shutil
import tempfile
import sys

# Some path magic to import pie.
# Because pie mixes all kinds of absolute and relative imports.
script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "pie"))

from pie.tagger import Tagger

# The extension of output files produced by the tagger.
OUTPUT_EXTENSION = ".tsv"
# Expected throughput in chars per sec.
PROCESSING_SPEED = 370
# Global tagger for the sake of initialization.
tagger = None


def init() -> None:
    """
    We initialize the PIE tagger class directly.
    """
    global tagger
    tagger = Tagger(
        batch_size=50, lower=False, max_sent_len=35, vrt=False, tokenize=True
    )
    for model, tasks in [("model.tar", [])]:
        tagger.add_model(model, *tasks)
    print("Model initialized.")


def process(in_file: str, out_file: str) -> None:
    """
    Process the file with the global tagger instance.
    Pie outputs to the same directory as the input file.
    We process the file in a temporary directory so we don't polute /input.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # input
        temp_in_file = os.path.join(temp_dir, "file.txt")
        shutil.copy(in_file, temp_in_file)
        # tag
        tagger.tag_file(
            temp_in_file, use_beam=False, beam_width=10, keep_boundaries=False
        )
        # output
        temp_result_file = os.path.join(temp_dir, "file-pie.txt")
        shutil.move(temp_result_file, out_file)
