"""
Initialize the huggingface tagger from the python class directly, and use that object to tag.
"""

# Standard library
import sys

# Some path magic to import huggingface.
sys.path.append("./huggingface")
sys.path.append("./huggingface/tagging")

from huggingface.lemmatizer.TaggerLemmatizer import TaggerLemmatizer

# The extension of output files produced by the tagger.
OUTPUT_EXTENSION = ".tsv"
# Expected throughput in chars per sec.
PROCESSING_SPEED = 200
# Global tagger for the sake of initialization.
tagger = None


def init() -> None:
    global tagger
    tagger = TaggerLemmatizer("model.config")
    tagger.init()


def process(in_file: str, out_file: str) -> None:
    # Huggingface outputs to out_file itself, so no copying/moving needed.
    tagger.process(in_file, out_file)
