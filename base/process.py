"""
Initialize the tagger if needed and process input files by calling the specific tagger implementation 
and ensuring the output is written to the expected file.
"""

# The extension of output files produced by the tagger.
OUTPUT_EXTENSION = ".tsv"

# Expected throughput in chars per sec.
# The timeout and expected job duration are based on this,
# so set it to a lower value to increase the timeout.
PROCESSING_SPEED = 10000


def init() -> None:
    """
    Any initialization the tagger may need before processing.
    """
    pass


def process(in_file: str, out_file: str) -> None:
    """
    Process the file at path "in_file" and write the result to path "out_file".
    """
    f_out = open(out_file, "x")
    f_out.write("Did you forget to override process.py?")
    f_out.close()
