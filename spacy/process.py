import spacy
import os
from spacy_conll import init_parser
from tei2trankit import tei2trankit
from spacy.tokens import Doc
import xml.etree.ElementTree as ET
from tqdm import tqdm
import time

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
    start_time = time.time()

    if os.getenv("USE_GPU"):
        spacy.require_gpu()

    global nlp
    nlp = spacy.load(os.environ["SPACY_MODEL"])
    nlp.add_pipe("conll_formatter", last=True, config={"disable_pandas": True})

    duration = time.time() - start_time
    print(f"Loaded pipeline in {duration:.2f}s: {nlp.pipe_names}")


def process(in_file: str, out_file: str) -> None:
    """
    Process the file at path "in_file" and write the result to path "out_file".
    """
    process_all(in_file, out_file)


def process_all(in_file, out_file) -> None:
    with open(out_file, "w+", encoding="utf-8") as f_out:
        with open(in_file, "r", encoding="utf-8") as f_in:
            is_xml = is_file_xml(in_file)
            # only non empty lines if not xml
            doc = (
                [Doc(nlp.vocab, i) for i in tei2trankit(in_file)]
                if is_xml
                else parse_txt(f_in)
            )  # need to be in a list

            if os.getenv("USE_GPU"):
                results = nlp.pipe(doc)
            else:
                results = nlp.pipe(doc, n_process=2, batch_size=20)

            sent_id = 1
            for result in results:
                for sent in result.sents:
                    f_out.write(f"# sent_id = {sent_id}\n")
                    f_out.write(f"# text = {sent}\n")
                    for token in sent:
                        f_out.write("\t".join(to_conllu(token)))
                        f_out.write("\n")  # Tokens on newline
                    f_out.write("\n")  # sentence separator
                    sent_id += 1


def process_by_line(in_file, out_file) -> None:
    with open(out_file, "w+", encoding="utf-8") as f_out:
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


# https://github.com/BramVanroy/spacy_conll/blob/b6225cfca7023ebf7a1488c48b1ded0bf3a07264/src/spacy_conll/formatter.py#L188
def to_conllu(token):
    sent_start = token.sent[0].i

    if token.dep_.lower().strip() == "root":
        head_idx = 0
    else:
        head_idx = token.head.i + 1 - sent_start

    miscs = {}
    if token.whitespace_:
        miscs["SpaceAfter"] = "No"
    if token.ent_type_:
        miscs["NamedEntity"] = token.ent_iob_ + "-" + token.ent_type_

    token._.conll_misc_field = (
        "_" if not miscs else "|".join(f"{k}={v}" for k, v in miscs.items())
    )

    return (
        str(token.i - sent_start + 1),
        token.text,
        token.lemma_ if token.lemma_ else "_",
        token.pos_ if token.pos_ else "_",
        token.tag_ if token.tag_ else "_",
        str(token.morph) if token.has_morph and str(token.morph) else "_",
        str(head_idx),
        token.dep_ if token.dep_ else "_",
        token._.conll_deps_graphs_field,
        token._.conll_misc_field,
    )
