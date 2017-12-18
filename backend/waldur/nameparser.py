import nltk
import difflib
import re
from nltk.corpus import stopwords
from logging import getLogger

log = getLogger(__name__)

# Stopwords
nltk.download("punkt")
nltk.download('averaged_perceptron_tagger')
nltk.download("stopwords")
stop = stopwords.words('english')


def preprocess(sentences):
    """
    Method for preprocessing user input for later name extraction
    :param sentences: User input as string
    :return: preprocessed sentences - pos-tagged words
    """
    log.info("Preprocessing sentence(s): " + str(sentences))
    try:
        sentences = sentences[0].lower() + sentences[1:]
        sentences = " ".join([i for i in sentences.split() if i.lower() not in stop])
        tokenized_sentences = nltk.sent_tokenize(sentences)
        tokenized_words = [nltk.word_tokenize(sent) for sent in tokenized_sentences]
        tagged_sentences = [nltk.pos_tag(word) for word in tokenized_words]
        log.info("Sentences preprocessed.")
        return tagged_sentences
    except Exception as e:
        log.error("An exception occurred while preprocessing: " + str(e))


def extract_names(sentences):
    """
    Extracts names from user input
    :param sentences: User input as string
    :return: list of names, stopwords removed
    """
    # todo: check for a better way of chunking
    try:
        log.info("Extracting names from \"" + str(sentences) + "\".")
        names = []
        preprocessed_sentences = preprocess(sentences)
        for tagged_sentence in preprocessed_sentences:
            # NNP - proper noun, CC - coordinating conjunction
            chunkGram = r"""Chunk: {<NNP>+<CC>?<NNP>*}"""
            chunkParser = nltk.RegexpParser(chunkGram)
            chunked = chunkParser.parse(tagged_sentence)
            for chunk in chunked:
                if type(chunk) == nltk.tree.Tree:
                    names.append(' '.join([c[0] for c in chunk]))
        if len(names) == 0:
            log.info("No names found with NLTK. Falling back to regex.")
            return extract_names_regex(sentences)
        else:
            log.info("Following names extracted: " + str(names))
            return names
    except Exception as e:
        log.error("An exception occurred while extracting names: " + str(e))


def extract_names_regex(sentences):
    """
    Fallback name extractor. Looks for all strings that are in capital case or start with number.
    :param sentences: The user input
    :return: List of found names
    """
    sentences = sentences[0].lower() + sentences[1:]
    sentences = " ".join([i for i in sentences.split() if i.lower() not in stop])
    name_regex = "([A-Z\d]\S+(?=\s?[A-Z\d]?)(?:\s?[A-Z\d]\S+)*)"
    names = re.findall(name_regex, sentences)
    if len(names) == 0 or names == None:
        log.info("Did not find any names.")
        return []
    else:
        log.info("Following names extracted: " + str(names))
    return names


def getSimilarNames(extracted_names, list_of_names):
    """
    Compares names extracted from user input with names found from API
    :param extracted_names: Names extracted from user input
    :param list_of_names: Names from API
    :return: Most similar name, should later return all names with similar confidence as the best
    """
    # todo: Return all names with similar confidence
    # todo: Find a better algorithm for similarity determination
    try:
        log.info("Looking for similar names to " + str(extracted_names))
        best = ["", 0]
        results = []
        matcher = difflib.SequenceMatcher()
        for extraction in extracted_names:
            for name in list_of_names:
                matcher.set_seqs(extraction.lower(), name.lower())
                similarity = matcher.ratio()
                if 0.5 < similarity > best[1]:
                    best = [name, similarity]
        log.info("Found most similar name \"" + str(best[0]) + "\" with confidence " + str(best[1]))
        return best[0]
    except Exception as e:
        log.error("An exception occurred while finding similar names: " + str(e))
