# Only the following type of TEI-files are supported
# - Containing extensively <s> and <w> tags; will be processed as pretokenized on both levels

import sys
import xml.etree.ElementTree as ET

MAXIMUM_SENTENCE_SIZE = 100

class TEIConversionException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

def _tag_without_namespace(element):
    _, _, tag = element.tag.rpartition('}') # strip ns
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
        if _tag_without_namespace(descendant) == "w" or _tag_without_namespace(descendant) == "pc":
            ret.append(descendant)
    return ret

def get_token_literals(element):
    words = get_tokens(element)
    tokens = list(map( lambda w : "".join(w.itertext()), words))
    # itertext() generates empty strings for self-closing-tags like <w pos="PUNT"/>
    return [t for t in tokens if t] # '' is falsy

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
        raise TEIConversionException("TEI document contains no sentences of processable size")
    return ret

def trankit2tei(data, filename):
    tree = get_tree(filename)
    texts = get_text_elements(tree)
    def trankit_sentence_generator():
        for sentence in data['sentences']:
            yield sentence
    trankit_sentences = trankit_sentence_generator()

    def getTEIid(element):
        # TODO replace namespace with {*}?
        if element.get('{http://www.w3.org/XML/1998/namespace}id') is not None:
            return element.get('{http://www.w3.org/XML/1998/namespace}id')
        return element.get('id')

    for text in texts:
        for sentence in get_sentences(text):
            tokens = get_tokens(sentence)
            if len(tokens) > MAXIMUM_SENTENCE_SIZE:
                continue # sentence is too long, skip it

            linkgroup = ET.Element("linkGrp")
            linkgroup.set("type", "UD-SYN")
            linkgroup.set("targFunc", "head argument")
            sentence.append(linkgroup)

            trankit_sentence = trankit_sentences.__next__()

            def trankit_words_generator():
                for token in trankit_sentence['tokens']:
                    yield token
            trankit_words = trankit_words_generator()

            for token in tokens:
                trankit_word = trankit_words.__next__()

                link = ET.Element("link")
                # The deprel seems to be missing sometimes
                # Therefore we initialize it to a default value
                deprel = ""
                if 'deprel' in trankit_word:
                    deprel = trankit_word['deprel']
                # Prepend the deprel with "ud-syn:" to match the parlamint format
                deprel = "ud-syn:" + deprel
                link.set("ana", deprel)
                linkgroup.append(link)

                head = None
                if trankit_word['head'] == 0: # root
                    head = sentence
                else:
                    head = tokens[trankit_word['head'] - 1] # trankit starts at index 1
                link.set("target", "#" + str(getTEIid(head)) + " " + "#" + str(getTEIid(token)))

    # export the xml tree
    return ET.tostring(tree.getroot(), encoding='utf-8', method='xml')

if __name__ == "__main__":
    if(len(sys.argv)) != 2:
        print(f"Usage: {sys.argv[0]} FILENAME")
        sys.exit(0)
    print(tei2trankit(sys.argv[1]))
