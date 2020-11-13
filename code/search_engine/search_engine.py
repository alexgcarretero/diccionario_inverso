from code.utils import HashableDict


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

    @staticmethod
    def format_word(word):
        last_length = len(word['word'])
        formatted_word = f"\n{word['word']}\n{'=' * last_length}\n"
        for i, definition in enumerate(word["definitions"], 1):
            formatted_definition = f"{i}\t{definition}\n"
            last_length = len(formatted_definition)
            formatted_word += formatted_definition
        return f"{formatted_word}\n{'=' * last_length}\n"

    def __init__(self, definitions):
        self.definitions = self._load_definitions(definitions)
        self.with_definitions = False

    def set_definitions(self, new_definitions):
        self.definitions = self._load_definitions(new_definitions)

    def set_with_definitions(self, new_with_definitions):
        self.with_definitions = new_with_definitions

    def search(self, query, sep=None, with_defs=None):
        if with_defs is None:
            with_defs = self.with_definitions

        if sep is None:
            sep = " "

        search_results = self._get_results(query.split(sep))

        if with_defs:
            return list(self.format_word(result) for result in search_results)
        return list(map(lambda x: x["word"], search_results))

    def consult(self, query, sep=None):
        if sep is None:
            sep = " "
        query_split = query.split(sep=sep)
        try:
            if len(query_split) == 1:
                return self.format_word(self.definitions[query])
        except KeyError:
            return "No encuentro esa palabra."

    def _get_results(self, search_terms):
        current_results = set(self.definitions.values())

        for term in search_terms:
            local_results = {
                word
                for word in current_results
                if any(term.lower() in definition.lower() for definition in word["definitions"])
            }
            current_results.intersection_update(local_results)
        return current_results
