import os
from re import match

from code.cache_manager.API import WordsAPI, DictAPI
from code.cache_manager.parser import parse_word, parse_definitions
from code.config import *
from code.utils import log, load_data, save_data


# Manager
class CacheManager:
    """
    The cache manager handles all the requests for words and definitions and then stores them into
    json files for persistence.

    It can load the content of that file to have a faster startup.
    """
    @staticmethod
    def _get_fetched_letters():
        regex = r"(.)\.json"
        return set(z.groups()[0] for element in os.listdir(DEFS_DIR) if (z := match(regex, element)))

    def __init__(self):
        self.words = self._load_words(show_log=False)
        self.definitions = self._load_definitions(show_log=False)

    def manage_cache(self, force_words_update=False, force_definitions_update=False):
        """
        This is the main function of the cache manager. It handles the reload of the cache info (a.k.a the json files)
        Note that the reload of definitions will take a while to perform, there are many words.

        Args:
            force_words_update (bool, optional): It indicates if the words file must be reloaded via Words API.
            force_definitions_update (bool, optional): It indicates if the definitions file must be reloaded
                                                       via Dict API.
        """
        if not os.path.exists(WORDS_FILE) or force_words_update:
            log("Descargando todas las palabras del castellano.", level="INFO")
            self.words = self._fetch_words()

        if not os.path.exists(DEFS_FILE) or force_definitions_update:
            log("Recopilando todas las definiciones del castellano.", level="INFO")
            self.definitions = self._fetch_definitions()

    def number_of_words(self, letter=None):
        """
        This function calculates the total number of words stored in the system.
        It provides the option to get the number of words that starts only with one letter.

        Args:
            letter (str, optional): The letter to recover the number of words.

        Returns:
            int: The number of words that starts with the letter 'letter'.
        """
        if letter is None:
            return sum(len(words) for words in self.definitions.values())
        return len(self.definitions[letter])

    def number_of_definitions(self, letter=None):
        """
        This function calculates the total number of definitions stored in the system.
        It provides the option to get the number of definitions of the words that starts only with one letter.

        Args:
            letter (str, optional): The letter to recover the number of definitions.

        Returns:
            int: The number of definitions of the words that starts with the letter 'letter'.
        """
        if letter is None:
            return sum(
                sum(len(definitions_list) for definitions_list in definitions_dict.values())
                for definitions_dict in self.definitions.values()
            )
        return sum(len(defs) for defs in self.definitions[letter].values())

    def max_words_letter(self):
        """
        Returns:
            int: The letter who has the maximum number of words stored in the system.
        """
        return max(self.definitions.keys(), key=lambda letter: self.number_of_words(letter=letter))

    # Fetchers: where all the API Calls are made and stored into the JSON files.
    def _load_words(self, force_update=False, show_log=True):
        if not os.path.exists(WORDS_FILE) or force_update:
            return self._fetch_words(show_log=show_log)
        return load_data(WORDS_FILE)

    def _load_definitions(self, force_update=False, show_log=True):
        if not os.path.exists(DEFS_FILE) or force_update:
            return self._fetch_definitions(show_log=show_log)
        return load_data(DEFS_FILE)

    @staticmethod
    def _fetch_words(show_log=True):
        """
        This method uses the WordsAPI to recover all the words in the language.

        Returns:
            dict: all the words indexed by first letter.
        """
        words_dict = dict()
        words_api = WordsAPI()

        for letter in words_api.LETTERS:
            log(f"Ahora con la letra:\t{letter}", show_log=show_log)
            words = parse_word(words_api.get_words(letter))
            words_dict[letter].union(words)
        save_data(WORDS_FILE, words_dict)
        return words_dict

    def _fetch_definitions(self, show_log=True):
        """


        It only uses the API for the letters that are not fetched yet.
        If you want to fetch all the definitions you must delete the Json files under the DEFS_DIR directory.

        Returns:
            dict: all the definitions indexed by word's first letter and word (e.g ['1st_letter']['word']).
        """
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
        """
        This method uses the DictAPI to recover all the definitions for the stored words that
        starts with letter 'letter'.

        Args:
            letter (str): The letter to recover word's definitions.

        Returns:
            dict: all the definition list indexed by word.
        """
        letter_definitions = dict()
        dict_api = DictAPI()

        total_words = len(self.words[letter])
        log_counter = total_words // 20

        log(f"Descargando las definiciones de la letra:\t{letter}", show_log=show_log)
        log(f"Son {total_words} palabras.", show_log=show_log)

        for count, word in enumerate(self.words[letter]):
            if count % log_counter == 0:
                log(f"{count} de {total_words}", show_log=show_log)
            definitions = parse_definitions(dict_api.get_definitions(word))
            letter_definitions[word] = definitions
        log(f"Serializando las definiciones de la letra '{letter}'...", start="\n", show_log=show_log)
        save_data(f"{DEFS_DIR}/{letter}.json", letter_definitions)
        return letter_definitions
