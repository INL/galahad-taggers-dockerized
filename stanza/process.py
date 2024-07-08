from io import TextIOWrapper
from unittest import result
from xmlrpc.client import Boolean
import stanza
from tei2trankit import tei2trankit
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

xml_nlp = None
txt_nlp = None


def init() -> None:
    """
    Any initialization the tagger may need before processing.
    """
    global xml_nlp
    xml_nlp = stanza.Pipeline(
        lang="nl", tokenize_pretokenized=True, processors="tokenize,lemma,pos,depparse"
    )

    global txt_nlp
    txt_nlp = stanza.Pipeline(lang="nl", processors="tokenize,lemma,pos,depparse")


def process(in_file: str, out_file: str) -> None:
    """
    Process the file at path "in_file" and write the result to path "out_file".
    """
    process_all(in_file, out_file)

def process_by_line(in_file, out_file) -> None:

    with open(out_file, "x") as f_out:
        with open(in_file, "r") as f_in:

            is_xml = is_file_xml(in_file)
            nlp = xml_nlp if is_xml else txt_nlp
            doc = tei2trankit(in_file) if is_xml else parse_txt(f_in)

            for line in tqdm(doc):
                if is_xml:
                    line = " ".join(line)
                result = nlp(line)
                f_out.write("{:C}".format(result))
                f_out.write("\n")

def process_all(in_file, out_file) -> None:
    
    with open(out_file, "x") as f_out:
        with open(in_file, "r") as f_in:

            is_xml = is_file_xml(in_file)
            nlp = xml_nlp if is_xml else txt_nlp
            doc = tei2trankit(in_file) if is_xml else f_in.read()

            result = nlp(doc)
            f_out.write("{:C}".format(result))
            f_out.write("\n")

def is_file_xml(in_file: str) -> bool:
    try:
        ET.parse(in_file)
        return True
    except:
        return False


def parse_txt(f_in: TextIOWrapper) -> list[str]:
    return [line.strip() for line in f_in if not line.isspace() and line]
