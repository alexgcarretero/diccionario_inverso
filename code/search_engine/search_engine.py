from code.utils import HashableDict, Formatter


class SearchEngine:
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
        self.definitions = self._load_definitions(new_definitions)

    def set_with_definitions(self, new_with_definitions):
        self.with_definitions = new_with_definitions

    def search(self, query, sep=None, with_defs=None, raw=False):
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
        if sep is None:
            sep = " "
        query_split = query.split(sep=sep)
        try:
            if len(query_split) == 1:
                return self.formatter.format_word(self.definitions[query])
        except KeyError:
            return "No encuentro esa palabra."

    def _get_results(self, search_terms):
        current_results = set(self.definitions.values())

        for term in search_terms:
            local_results = set()
            flatted_term = Formatter.flatten_text(term)
            for word in current_results:
                for definition in word["definitions"]:
                    if flatted_term in Formatter.flatten_text(definition):
                        local_results.add(word)
            current_results.intersection_update(local_results)
        return current_results
