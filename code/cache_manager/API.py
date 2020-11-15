# RAE API
import json

from requests import request


class APIException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __repr__(self):
        return f"APIException=({self.code=}, {self.message})"

    def __str__(self):
        return f"[CODE {self.code}]\t{self.message}"


class API:
    def __init__(self):
        self.auth_token = None

    @staticmethod
    def _prepare_response(response):
        response.encoding = "utf-8"
        return response.text

    def _request(self, url, params):
        headers = {"Authorization": f"Basic {self.auth_token}"} if self.auth_token else dict()
        try:
            response = request("get", url, params=params, headers=headers)
        except Exception as e:
            raise APIException(500, f"Something went wrong when doing the request.\n{e}")
        return response.status_code, API._prepare_response(response)


class WordsAPI(API):
    LETTERS = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"

    def __init__(self):
        super(WordsAPI, self).__init__()
        self.url = "https://www.listapalabras.com/palabras-con.php"

    def get_words(self, letter):
        """
        This function gathers all the words that start with the letter 'letter'.

        Args:
            letter: Letter that the words starts with.

        Returns:
            str: The html page that has all the information of the words list.

        Raises:
            APIException: If the response status code is not 200 OK
        """
        if letter.upper() not in self.LETTERS:
            raise APIException(500, f"Letter {letter} not a valid letter.")

        params = {"letra": letter.lower(), "total": "s"}
        response = self._request(self.url, params=params)
        if response[0] != 200:
            raise APIException(
                response[0],
                f"Something went wrong when retrieving the words with letter {letter}.\n{response[1]}"
            )
        return response[1]


class DictAPI(API):
    def __init__(self):
        super(DictAPI, self).__init__()
        self.base_url = "https://dle.rae.es/data"
        self.search_url = f"{self.base_url}/search"
        self.fetch_url = f"{self.base_url}/fetch"

        self.auth_token = "cDY4MkpnaFMzOmFHZlVkQ2lFNDM0"

    def _search_word(self, word):
        """
        This function prepares the word search, getting the RAE word id.

        Args:
            word: The word to be search later.

        Returns:
            list: word_ids for the words matching the word searched.

        Raises:
            APIException: If the response status code is not 200 OK
            APIException: If the response does not contain the 'id' info for the word
        """
        params = {"w": word}
        search_response = self._request(self.search_url, params)
        if search_response[0] != 200:
            raise APIException(
                search_response[0],
                f"Error when searching word '{word}'.\n{search_response[1]}"
            )

        word_ids = list()
        try:
            search_results = json.loads(search_response[1])["res"]
            if len(search_results) > 0:
                word_ids = list(result["id"] for result in search_results if word in result["header"])
        except (KeyError, IndexError) as e:
            raise APIException(
                500,
                f"Error when searching word '{word}' index.\n{e}"
            )
        return word_ids

    def get_definitions(self, word):
        """
        This is the word search definition. It gathers all the definitions for the wanted word.

        Args:
            word: The word to be searched.

        Returns:
            list: List of definitions for that word.

        Raises:
            APIException: If the response status code is not 200 OK
        """
        word_ids = self._search_word(word)
        if len(word_ids) == 0:
            return None

        definitions = list()
        for word_id in word_ids:
            params = {"id": word_id}
            response = self._request(self.fetch_url, params)
            if response[0] != 200:
                raise APIException(
                    response[0],
                    f"Error when getting the definitions of word '{word}'.\n{response[1]}"
                )
            definitions.append(response[1])
        return definitions
