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
    if os.environ["USE_GPU"]:
        spacy.require_gpu()
    global nlp
    nlp = spacy.load(os.environ["SPACY_MODEL"])
    nlp.add_pipe("conll_formatter", last=True, config={"include_headers": True})
    print(f"Loaded pipeline: {nlp.pipe_names}")
    print(nlp.pipeline)

def process(in_file: str, out_file: str) -> None:
    """
    Process the file at path "in_file" and write the result to path "out_file".
    """
    process_by_line(in_file, out_file)

def process_all(in_file, out_file) -> None:
    with open(out_file, "x", encoding="utf-8") as f_out:
        with open(in_file, "r", encoding="utf-8") as f_in:
            pass

def process_by_line(in_file, out_file) -> None:
    with open(out_file, "x", encoding="utf-8") as f_out:
        with open(in_file, "r", encoding="utf-8") as f_in:

            is_xml = is_file_xml(in_file)
            # only non empty lines if not xml
            doc = tei2trankit(in_file) if is_xml else parse_txt(f_in)

            for line in tqdm(doc):
                if is_xml:
                    line = Doc(nlp.vocab, line)
                result = nlp(line)
                f_out.write(result._.conll_str)
                f_out.write("\n")  # sentence separator

def is_file_xml(in_file: str) -> bool:
    try:
        ET.parse(in_file)
        return True
    except:
        return False
    
def parse_txt(f_in) -> list[str]:
    return [line.strip() for line in f_in if not line.isspace() and line]
