# standard
import os
import pathlib
import re
import time
import xml.etree.ElementTree as ET

# local
from conllu_tei_helper import parse_tei
from spacy.language import Language
from spacy.tokens import Doc

# third-party
import spacy

# The extension of output files produced by the tagger.
OUTPUT_EXTENSION = ".conllu"

# Expected throughput in chars per sec.
# The timeout and expected job duration are based on this,
# so set it to a lower value to increase the timeout.
PROCESSING_SPEED = 370  # TODO: measure this!

nlp = None


# https://github.com/explosion/spaCy/issues/3169#issuecomment-455183085
@Language.component("prevent-sbd")
def prevent_sentence_boundary_detection(doc):
    for token in doc:
        # This will entirely disable spaCy's sentence detection
        token.is_sent_start = False
    return doc


def init() -> None:
    """
    Any initialization the tagger may need before processing.
    """
    start_time = time.time()

    if os.getenv("CPU_GPU") == "gpu":
        spacy.require_gpu()

    global nlp
    nlp = spacy.load(os.environ["SPACY_MODEL"])
    nlp.add_pipe(factory_name="prevent-sbd", before="parser")
    nlp.add_pipe(
        "conll_formatter", last=True, config={"disable_pandas": True, "field_names": {}}
    )

    duration = time.time() - start_time
    print(f"Loaded pipeline in {duration:.2f}s: {nlp.pipe_names}")


def process(in_file: str, out_file: str) -> None:
    """
    Process the file at path "in_file" and write the result to path "out_file".
    """
    if nlp is None:
        init()
    with pathlib.Path(out_file).open("w+", encoding="utf-8") as f_out:
        with pathlib.Path(in_file).open(encoding="utf-8") as f_in:
            is_xml = is_file_xml(in_file)
            # only non empty lines if not xml
            doc = (
                [Doc(nlp.vocab, i) for i in parse_tei(in_file)]
                if is_xml
                else parse_txt(f_in)
            )  # need to be in a list

            results = nlp.pipe(doc)

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


def is_file_xml(in_file: str) -> bool:
    try:
        ET.parse(in_file)
        return True
    except:
        return False


def parse_txt(f_in) -> list[str]:
    # uniform whitespace
    # because spacy leaves for example tabs, resulting in a tsv with illegal extra tabs
    regex = re.compile(r"\s+")
    return [
        regex.sub(" ", line).strip() for line in f_in if not line.isspace() and line
    ]


# Based on:
# https://github.com/BramVanroy/spacy_conll/blob/b6225cfca7023ebf7a1488c48b1ded0bf3a07264/src/spacy_conll/formatter.py#L188
def to_conllu(token):
    sent_start = token.sent[0].i

    if token.dep_.lower().strip() == "root":
        head_idx = 0
    else:
        head_idx = token.head.i + 1 - sent_start

    miscs = {}
    if not token.whitespace_:
        miscs["SpaceAfter"] = "No"
    if token.ent_type_:
        miscs["NamedEntity"] = token.ent_iob_ + "-" + token.ent_type_

    token._.conll_misc_field = (
        "_" if not miscs else "|".join(f"{k}={v}" for k, v in miscs.items())
    )

    return (
        str(token.i - sent_start + 1),
        token.text,
        token.lemma_ or "_",
        token.pos_ or "_",
        token.tag_ or "_",
        str(token.morph) if token.has_morph and str(token.morph) else "_",
        str(head_idx),
        token.dep_ or "_",
        token._.conll_deps_graphs_field,
        token._.conll_misc_field,
    )
