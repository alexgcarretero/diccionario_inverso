# HTML parsers
from bs4 import BeautifulSoup


def parse_word(words_to_parse):
    """
    This function transforms the HTML response of the WordAPI into a word set.
    """
    words_set = set()

    soup = BeautifulSoup(words_to_parse, "lxml")
    soup = soup.find("div", attrs={"id": "columna_resultados_generales"})
    for word in soup.find_all("a"):
        words_set.add(str(word.text.strip()))
    return words_set


def parse_definitions(definitions_to_parse):
    """
    This function transforms the HTML response of the DictAPI into a definition list.
    """
    definitions = list()
    if definitions_to_parse is not None:
        soup = BeautifulSoup(definitions_to_parse, "lxml")

        for definition in soup.find_all("p", attrs={"class": "j"}):
            definitions.append(definition.text[3:])
    return definitions
