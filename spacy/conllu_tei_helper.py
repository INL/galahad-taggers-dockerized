# Only the following type of TEI-files are supported
# - Containing extensively <s> and <w> tags; will be processed as pretokenized on both levels

from os import link
import sys
import xml.etree.ElementTree as ET
from conllu import parse_incr


class TEIConversionException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


def _tag_without_namespace(element):
    _, _, tag = element.tag.rpartition("}")  # strip ns
    return tag


def has_sentences(element):
    return len(get_sentences(element)) > 0


def has_tokens(element):
    return len(get_tokens(element)) > 0


def get_sentences(element):
    # Xpath doesn't seem to handle the namespaces well, so we do it brute force
    ret = []
    for descendant in element.iter():
        if _tag_without_namespace(descendant) == "s":
            ret.append(descendant)
    return ret


def get_tokens(element):
    # it would be beautiful to use the Xpath element.findall(".//[w or pc]") here
    # but 'or' is not supported in elementTree
    # see https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support
    # therefore we just iterate the tree ourselves
    ret = []
    for descendant in element.iter():
        if (
            _tag_without_namespace(descendant) == "w"
            or _tag_without_namespace(descendant) == "pc"
        ):
            ret.append(descendant)
    return ret


def get_token_literals(element):
    words = get_tokens(element)
    tokens = list(map(lambda w: "".join(w.itertext()), words))
    # itertext() generates empty strings for self-closing-tags like <w pos="PUNT"/>
    return [t for t in tokens if t]  # '' is falsy


def get_tree(filename):
    parser = ET.XMLParser(encoding="utf-8")
    return ET.parse(filename, parser=parser)


def get_text_elements(tree):
    root = tree.getroot()
    ret = []
    for descendant in root.iter():
        if _tag_without_namespace(descendant) == "s":
            ret.append(descendant)
    return ret


def tei_to_spacy_docs(filename):
    """
    Convert a TEI file to a list of pretokenized strings, to be used by spacy or the like.
    Example:
    <tei><text>
        <s><w>Hello</w> <w>world</w> <pc>!</pc></s>
        <s><w>Goodbye</w> <w>world</w> <pc>!</pc></s>
    </text></tei>
    will be converted to:
    [
        ["Hello", "world", "!"],
        ["Goodbye", "world", "!"]
    ]
    """
    tree = get_tree(filename)
    if not has_tokens(tree):
        raise TEIConversionException("TEI document does not contain <w> nor <pc>-tags")
    if not has_sentences(tree):
        raise TEIConversionException("TEI document does not contain <s>-tags")

    texts = get_text_elements(tree)

    ret = []
    for text in texts:
        for sentence in get_sentences(text):
            literals = get_token_literals(sentence)
            ret.append(literals)

    if len(ret) == 0:
        raise TEIConversionException(
            "TEI document contains no sentences of processable size"
        )
    return ret


def conllu_to_tei(conllu_path, tei_path):
    """
    Generate a new TEI file with the conllu layer annotations.
    """
    root = ET.Element("TEI")
    text = ET.SubElement(root, "text")
    body = ET.SubElement(text, "body")
    word_id = 1

    for conllu_sentence in conllu_sentence_generator(conllu_path):

        paragraph = ET.SubElement(body, "p")
        tei_sentence = ET.SubElement(paragraph, "s")
        linkgroup = create_linkgroup(tei_sentence)

        for conllu_word in conllu_words_generator(conllu_sentence):
            # create
            element_type = "pc" if conllu_word["upos"] == "PUNCT" else "w"
            tei_word = ET.SubElement(tei_sentence, element_type)
            # add text
            tei_word.text = conllu_word["form"]
            # add id
            tei_word.set("id", f"w.{word_id}")
            # add lemma and pos
            merge_lemma_pos(tei_word, conllu_word)
            word_id += 1

        # now add the deprel and head
        tei_words = get_tokens(tei_sentence)
        for i, conllu_word in enumerate(conllu_words_generator(conllu_sentence)):
            tei_word = tei_words[i]
            merge_deprel_head(tei_sentence, tei_words, linkgroup, tei_word, conllu_word)

    # export the xml tree
    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write(tei_path, encoding="utf-8", xml_declaration=True)


def conllu_sentence_generator(conllu_path):
    data_file = open(conllu_path, "r", encoding="utf-8")
    for sentence in parse_incr(data_file):
        yield sentence


def conllu_words_generator(sentence):
    for token in sentence:
        yield token


def merge_tei_with_conllu_layer(conllu_path, tei_path):
    """
    Outputs the original TEI file with the conllu layer annotations added.
    """
    tree = get_tree(tei_path)
    texts = get_text_elements(tree)

    conllu_sentences = conllu_sentence_generator(conllu_path)

    for text in texts:
        for tei_sentence in get_sentences(text):
            tei_words: list[ET.Element] = get_tokens(tei_sentence)

            linkgroup = create_linkgroup(tei_sentence)

            conllu_sentence = conllu_sentences.__next__()

            conllu_words = conllu_words_generator(conllu_sentence)

            for tei_word in tei_words:
                # Handle empty tokens
                token_text: str = "".join(tei_word.itertext())
                if token_text == "":
                    print(f"Warning: Empty token in {tei_path}", file=sys.stderr)
                    if "lemma" in tei_word.attrib:
                        del tei_word.attrib["lemma"]
                    if "type" in tei_word.attrib:
                        del tei_word.attrib["type"]
                    continue

                # Handle mismatched sentence lengths
                try:
                    conllu_word = conllu_words.__next__()
                except StopIteration:
                    print(
                        f"Warning: CoNLL-U sentence is shorter than TEI sentence in {tei_path}",
                        file=sys.stderr,
                    )
                    continue  # keep the rest of the sentence as is

                ###### lemma & pos ######
                merge_lemma_pos(tei_word, conllu_word)

                ###### deprel & head ######
                merge_deprel_head(
                    tei_sentence, tei_words, linkgroup, tei_word, conllu_word
                )

    # export the xml tree
    return ET.tostring(tree.getroot(), encoding="utf-8", method="xml")


def create_linkgroup(tei_sentence):
    linkgroup = ET.Element("linkGrp")
    linkgroup.set("type", "UD-SYN")
    linkgroup.set("targFunc", "head argument")
    tei_sentence.append(linkgroup)
    return linkgroup


def getTEIid(element):
    if element.get("{http://www.w3.org/XML/1998/namespace}id") is not None:
        return element.get("{http://www.w3.org/XML/1998/namespace}id")
    return element.get("id")


def merge_lemma_pos(tei_word, conllu_word):
    if conllu_word["lemma"]:
        tei_word.set("lemma", conllu_word["lemma"])
    if conllu_word["xpos"]:
        tei_word.set("type", conllu_word["xpos"])
    if conllu_word["upos"]:
        tei_word.set("pos", conllu_word["upos"])
    if conllu_word["feats"]:
        feats = "|".join([f"{k}={v}" for k, v in conllu_word["feats"].items()])
        tei_word.set("msd", feats)


def merge_deprel_head(tei_sentence, tei_words, linkgroup, tei_word, conllu_word):
    if conllu_word["deprel"] and conllu_word["head"]:
        link = ET.Element("link")
        deprel = conllu_word["deprel"]
        # Prepend the deprel with "ud-syn:" to match the parlamint format
        deprel = "ud-syn:" + deprel
        link.set("ana", deprel)
        linkgroup.append(link)

        head = None
        if conllu_word["head"] == 0:  # root
            head = tei_sentence
        else:
            head = tei_words[conllu_word["head"] - 1]
        link.set(
            "target",
            "#" + str(getTEIid(head)) + " " + "#" + str(getTEIid(tei_word)),
        )
