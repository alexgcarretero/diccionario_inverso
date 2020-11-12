import os
from re import match

from code.cache_manager.API import WordsAPI, DictAPI
from code.cache_manager.parser import parse_word, parse_definitions
from code.config import *
from code.utils import log, load_data, save_data


# Manager
class CacheManager:
    @staticmethod
    def _get_fetched_letters():
        regex = r"(.)\.json"
        return set(z.groups()[0] for element in os.listdir(DEFS_DIR) if (z := match(regex, element)))

    def __init__(self):
        self.words = self._load_words(show_log=False)
        self.definitions = self._fetch_definitions(show_log=False)
        self.words_number, self.definitions_number = self._get_numbers()

    def manage_cache(self, force_words_update=False, force_definitions_update=False):
        if not os.path.exists(WORDS_FILE) or force_words_update:
            log("Descargando todas las palabras del castellano.", level="INFO")
            self.words = self._fetch_words()

        if not os.path.exists(DEFS_FILE) or force_definitions_update:
            log("Recopilando todas las definiciones del castellano.", level="INFO")
            self.definitions = self._fetch_definitions()

    def _get_numbers(self):
        words_number = sum(len(words) for words in self.words.values())
        definitions_number = sum(
            sum(len(definitions_list) for definitions_list in definitions_dict.values())
            for definitions_dict in self.definitions.values()
        )
        return words_number, definitions_number

    def number_of_words(self):
        return self.words_number

    def number_of_definitions(self):
        return self.definitions_number

    # Fetchers
    @staticmethod
    def _fetch_words(show_log=True):
        words_dict = dict()
        words_api = WordsAPI()

        for letter in words_api.LETTERS:
            log(f"Ahora con la letra:\t{letter}", show_log=show_log)
            words = parse_word(words_api.get_words(letter))
            words_dict[letter].union(words)
        save_data(WORDS_FILE, words_dict)
        return words_dict

    def _load_words(self, force_update=False, show_log=True):
        if not os.path.exists(WORDS_FILE) or force_update:
            return self._fetch_words(show_log=show_log)
        return load_data(WORDS_FILE)

    def _load_definitions(self, force_update=False, show_log=True):
        if not os.path.exists(DEFS_FILE) or force_update:
            return self._fetch_definitions(show_log=show_log)
        return load_data(DEFS_FILE)

    def _fetch_definitions(self, show_log=True):
        definition_dict = dict()

        fetched_letters = self._get_fetched_letters()
        missing_letters = set(ALL_LETTERS) - fetched_letters
        for letter in missing_letters:
            definition_dict[letter] = self._fetch_definitions_per_letter(letter)

        for letter in fetched_letters:
            json_file = f"{DEFS_DIR}/{letter}.json"
            definition_dict[letter] = load_data(json_file)
        log("Serializando todas las definiciones...", show_log=show_log)
        save_data(DEFS_FILE, definition_dict)
        return definition_dict

    def _fetch_definitions_per_letter(self, letter, show_log=True):
        letter_definitions = dict()
        dict_api = DictAPI()

        total_words = len(self.words[letter])
        log_counter = total_words // 20

        log(f"Descargando las definiciones de la letra:\t{letter}", show_log=show_log)
        log(f"Son {total_words} palabras.", show_log=show_log)

        for count, word in enumerate(self.words[letter]):
            if count % log_counter == 0:
                log(f"{count} de {total_words}", end=", ", show_log=show_log)
                definitions = parse_definitions(dict_api.get_definitions(word))
                letter_definitions[word] = definitions
        log(f"Serializando las definiciones de la letra '{letter}'...", start="\n", show_log=show_log)
        save_data(f"{DEFS_DIR}/{letter}.json", letter_definitions)
        return letter_definitions
