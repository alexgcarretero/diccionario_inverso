from utils import HashableDict, Formatter


# Where the searching stuff goes on
class SearchEngine:
    """
    With all the information loaded into the system, the SearchEngine is the responsible of
    the direct and inverse search into the dictionary.
    """
    @staticmethod
    def _load_definitions(data):
        definition_dict = dict()

        for letter, words in data.items():
            for word, definitions in words.items():
                word_object = HashableDict({
                    "word": word,
                    "definitions": definitions
                })
                definition_dict[word] = word_object
        return definition_dict

    def __init__(self, definitions, formatter=None):
        self.definitions = self._load_definitions(definitions)
        self.with_definitions = False
        self.formatter = formatter if formatter is not None else Formatter("console")

    def set_definitions(self, new_definitions):
        # If the system reloads the definitions in runtime.
        self.definitions = self._load_definitions(new_definitions)

    def set_with_definitions(self, new_with_definitions):
        self.with_definitions = new_with_definitions

    def search(self, query, sep=None, with_defs=None, raw=False):
        """
        The inverse search method.
        Here we retrieve all the information and return the formatted results
        Args:
            query (str): The search query.
            sep (str, optional): A separator for the query terms.
            with_defs (bool, optional): If true, it returns the results with the definitions, else only the words.
            raw (bool, optional): If true, the formatter will not take effect.

        Returns:
            list: The formatted word results.
        """
        if with_defs is None:
            with_defs = self.with_definitions

        if sep is None:
            sep = " "

        query = Formatter.flatten_text(query, sep=sep)
        return list(
            self.formatter.format_word(result, with_defs=with_defs, raw=raw)
            for result in self._get_results(query.split(sep))
        )

    def consult(self, query, sep=None):
        """
        The direct search method.
        It retrieves the definitions for a word.

        Args:
            query (str):  The word to be searched.
            sep (str): A separator for the query.

        Returns:
            list: The formatted word with it's definitions.

        """
        if sep is None:
            sep = " "
        query_split = query.split(sep=sep)
        try:
            if len(query_split) == 1:
                return self.formatter.format_word(self.definitions[query])
        except KeyError:
            return "No encuentro esa palabra."

    def _get_results(self, search_terms):
        """
        The REAL inverse search logic.

        Args:
            search_terms (list): The search terms.

        Returns:
            set: The results that matches with the search terms.
        """
        search_results = set()

        for word in self.definitions.values():
            for definition in word["definitions"]:
                flattened_definition = Formatter.flatten_text(definition)
                if all(Formatter.flatten_text(term) in flattened_definition for term in search_terms):
                    search_results.add(word)
                    break
        return search_results
