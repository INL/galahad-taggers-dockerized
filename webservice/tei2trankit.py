# Only the following type of TEI-files are supported
# - Containing extensively <s> and <w> tags; will be processed as pretokenized on both levels

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


def tei2trankit(filename):
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


def trankit2tei(conllu_path, tei_path):
    tree = get_tree(tei_path)
    texts = get_text_elements(tree)

    def trankit_sentence_generator():
        data_file = open(conllu_path, "r", encoding="utf-8")
        for sentence in parse_incr(data_file):
            yield sentence

    trankit_sentences = trankit_sentence_generator()

    def getTEIid(element):
        # TODO replace namespace with {*}?
        if element.get("{http://www.w3.org/XML/1998/namespace}id") is not None:
            return element.get("{http://www.w3.org/XML/1998/namespace}id")
        return element.get("id")

    for text in texts:
        for sentence in get_sentences(text):
            tokens = get_tokens(sentence)

            linkgroup = ET.Element("linkGrp")
            linkgroup.set("type", "UD-SYN")
            linkgroup.set("targFunc", "head argument")
            sentence.append(linkgroup)

            trankit_sentence = trankit_sentences.__next__()

            def trankit_words_generator():
                for token in trankit_sentence:
                    yield token

            trankit_words = trankit_words_generator()

            for token in tokens:
                trankit_word = trankit_words.__next__()

                ###### lemma & pos ######
                if trankit_word["lemma"]:
                    token.set("lemma", trankit_word["lemma"])
                if trankit_word["xpos"]:
                    token.set("type", trankit_word["xpos"])
                if trankit_word["upos"]:
                    token.set("pos", trankit_word["upos"])
                if trankit_word["feats"]:
                    feats = "|".join(
                        [f"{k}={v}" for k, v in trankit_word["feats"].items()]
                    )
                    token.set("msd", feats)

                ###### deprel & head ######
                if trankit_word["deprel"] and trankit_word["head"]:
                    link = ET.Element("link")
                    deprel = trankit_word["deprel"]
                    # Prepend the deprel with "ud-syn:" to match the parlamint format
                    deprel = "ud-syn:" + deprel
                    link.set("ana", deprel)
                    linkgroup.append(link)

                    head = None
                    if trankit_word["head"] == 0:  # root
                        head = sentence
                    else:
                        head = tokens[
                            trankit_word["head"] - 1
                        ]  # trankit starts at index 1
                    link.set(
                        "target",
                        "#" + str(getTEIid(head)) + " " + "#" + str(getTEIid(token)),
                    )

    # export the xml tree
    return ET.tostring(tree.getroot(), encoding="utf-8", method="xml")


if __name__ == "__main__":
    if (len(sys.argv)) != 2:
        print(f"Usage: {sys.argv[0]} FILENAME")
        sys.exit(0)
    print(tei2trankit(sys.argv[1]))
