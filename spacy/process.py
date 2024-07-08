import spacy
import os
from spacy_conll import init_parser
from tei2trankit import tei2trankit
from spacy.tokens import Doc
import xml.etree.ElementTree as ET
from tqdm import tqdm

"""
Initialize the tagger if needed and process input files by calling the specific tagger implementation 
and ensuring the output is written to the expected file.
"""

# The extension of output files produced by the tagger.
OUTPUT_EXTENSION = ".conllu"

# Expected throughput in chars per sec.
# The timeout and expected job duration are based on this,
# so set it to a lower value to increase the timeout.
PROCESSING_SPEED = 370  # todo: measure this!

nlp = None


def init() -> None:
    """
    Any initialization the tagger may need before processing.
    """
    global nlp
    nlp = spacy.load(os.environ["SPACY_MODEL"])
    nlp.add_pipe("conll_formatter", last=True, config={"include_headers": True})
    print(f"Loaded pipeline: {nlp.pipe_names}")
    print(nlp.pipeline)


nlp = None


def process(in_file: str, out_file: str) -> None:
    """
    Process the file at path "in_file" and write the result to path "out_file".
    """
    with open(out_file, "x") as f_out:
        with open(in_file, "r") as f_in:

            is_xml = False
            try:
                ET.parse(in_file)
                is_xml = True
            except:
                pass
            # only non empty lines if not xml
            doc = (
                tei2trankit(in_file)
                if is_xml
                else [line.strip() for line in f_in if not line.isspace() and line]
            )
            for line in tqdm(doc):
                if is_xml:
                    line = Doc(nlp.vocab, line)
                result = nlp(line)
                f_out.write(result._.conll_str)
                f_out.write("\n")  # sentence separator
