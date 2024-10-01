"""
Initialize the tagger if needed and process input files by calling the specific tagger implementation 
and ensuring the output is written to the expected file.
"""

from flair.nn import Classifier
from flair.models import MultitaskModel
from flair.splitter import SegtokSentenceSplitter

# The extension of output files produced by the tagger.
OUTPUT_EXTENSION = ".tsv"

# Expected throughput in chars per sec.
# The timeout and expected job duration are based on this,
# so set it to a lower value to increase the timeout.
PROCESSING_SPEED = 10000

tagger = None
splitter = None


def init() -> None:
    """
    Any initialization the tagger may need before processing.
    """
    global tagger, splitter
    ner_tagger = Classifier.load("flair/ner-dutch-large")
    pos_tagger = Classifier.load("flair/upos-multi")
    tagger = MultitaskModel([ner_tagger, pos_tagger])
    splitter = SegtokSentenceSplitter()


def process(in_file: str, out_file: str) -> None:
    """
    Process the file at path "in_file" and write the result to path "out_file".
    """
    with open(out_file, "w+", encoding="utf-8") as f_out:
        with open(in_file, "r", encoding="utf-8") as f_in:
            doc = f_in.read()

            # Even when split, flair seems to quickly go out of memory.
            # So we feed it the sentences one by one.
            sentences = splitter.split(doc)
            all_tagged = []
            for sentence in sentences:
                tagger.predict(sentence, force_token_predictions=True, verbose=True)  # in-place tagging
                all_tagged.append(sentence)

            # Write to output
            f_out.write("token\tupos\tentity\n")
            for tagged_sentence in all_tagged:
                for tok in tagged_sentence:
                    f_out.write(f"{tok.form}\t{tok.get_label('upos').value}\t{tok.get_label('ner').value}\n")
                f_out.write("\n")
