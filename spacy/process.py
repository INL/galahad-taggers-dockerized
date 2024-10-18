import spacy
from spacy.language import Language
import os
from spacy_conll import init_parser
from conllu_tei_helper import tei_to_spacy_docs, conllu_to_tei
from spacy.tokens import Doc
import xml.etree.ElementTree as ET
from tqdm import tqdm
import time
import re
import tempfile

"""
Initialize the tagger if needed and process input files by calling the specific tagger implementation 
and ensuring the output is written to the expected file.
"""

# The extension of output files produced by the tagger.
OUTPUT_EXTENSION = ".xml"

# Expected throughput in chars per sec.
# The timeout and expected job duration are based on this,
# so set it to a lower value to increase the timeout.
PROCESSING_SPEED = 370  # todo: measure this!

nlp = None
docs_processed = 0
last_idle_time = None
total_idle_duration = 0
total_busy_duration = 0


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

    if os.getenv("USE_GPU"):
        spacy.require_gpu()

    global nlp
    nlp = spacy.load(os.environ["SPACY_MODEL"])
    nlp.add_pipe(factory_name="prevent-sbd", before="parser")
    nlp.add_pipe("conll_formatter", last=True, config={"disable_pandas": True})

    duration = time.time() - start_time
    print(f"Loaded pipeline in {duration:.2f}s: {nlp.pipe_names}")


def process(in_file: str, out_file: str) -> None:
    """
    Process the file at path "in_file" and write the result to path "out_file".
    """
    pid = os.getpid()

    # Idle time
    start_time = calculate_idle_duration(pid)

    # temporary file to store conllu
    with tempfile.NamedTemporaryFile() as temp_file:
        process_all(in_file, temp_file.name)
        conllu_to_tei(temp_file.name, out_file)

    calculate_statistics(in_file, pid, start_time)


def calculate_idle_duration(pid):
    global last_idle_time
    global total_idle_duration
    now = time.time()
    if last_idle_time is not None:
        idle_duration = now - last_idle_time
        total_idle_duration += idle_duration
        print(
            f"Thread {pid} was idle for {idle_duration:.3f}s (total: {total_idle_duration:.3f}s)"
        )
    last_idle_time = now
    return now


def calculate_statistics(in_file, pid, start_time):
    busy_duration = time.time() - start_time
    global total_busy_duration
    total_busy_duration += busy_duration
    print(
        f"Thread {pid} processed {in_file} in {busy_duration:.3f}s (total: {total_busy_duration:.3f}s)"
    )

    # Efficiency
    global total_idle_duration
    percentage_busy = total_busy_duration / (total_busy_duration + total_idle_duration)
    print(f"Thread {pid} was busy {percentage_busy:.2%} of the time")

    # Docs processed
    global docs_processed
    docs_processed += 1
    print(f"Thread {pid} has processed {docs_processed} document(s)")


def process_all(in_file, out_file) -> None:
    with open(out_file, "w+", encoding="utf-8") as f_out:
        with open(in_file, "r", encoding="utf-8") as f_in:
            is_xml = is_file_xml(in_file)
            # only non empty lines if not xml
            doc = (
                [Doc(nlp.vocab, i) for i in tei_to_spacy_docs(in_file)]
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
    regex = re.compile(r"\s+")
    return [
        regex.sub(" ", line).strip() for line in f_in if not line.isspace() and line
    ]


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
        token.lemma_ if token.lemma_ else "_",
        token.pos_ if token.pos_ else "_",
        token.tag_ if token.tag_ else "_",
        str(token.morph) if token.has_morph and str(token.morph) else "_",
        str(head_idx),
        token.dep_ if token.dep_ else "_",
        token._.conll_deps_graphs_field,
        token._.conll_misc_field,
    )
