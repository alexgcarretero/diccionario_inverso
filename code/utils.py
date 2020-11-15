import functools
import json
from datetime import datetime

from code.cache_manager.API import APIException


class HashableDict(dict):
    """
    A Hashable dict that is useful for set operations with dicts.
    """
    def __hash__(self):
        if "word" in self:
            return hash(self["word"])
        return hash(tuple(sorted(self.items())))


def log(message, level="LOG", end=None, start=None, show_log=True):
    """
    Logging function.

    Args:
        message (str): Message to log.
        level (str, optional): Level of the Log.
        end (str, optional): An append for the constructed log message.
        start (str, optional): An start for the constructed log message.
        show_log (bool, optional): If false, it wont show the message.
    """
    if not show_log:
        return

    if end is None:
        end = "\n"

    if start is None:
        start = ""

    print(f"{start}[{level}][{datetime.utcnow()}UTC]\t{message}", end=end)


def safe_execution(log_message=None, default=None):
    """
    Decorator that catches the Exceptions of the function to decorate and logs them, preventing system failures.

    Args:
        log_message (str, optional): An additional log message to show.
        default: The value to return if an exception occurs.
    """
    if log_message is None:
        log_message = ""

    def inner_safe_execution(function):
        @functools.wraps(function)
        def wrap_inner_safe_execution(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except (KeyError, IndexError, APIException, Exception) as ex:
                message = f"Exception ocurred in {function.__name__}.{log_message}\nMore info: {ex}"
                log(message, level="ERROR", start="\n")
                return default

        return wrap_inner_safe_execution

    return inner_safe_execution


@safe_execution(log_message="Loading data")
def load_data(file_to_load):
    """
    This function loads the file provided and returns the dict data in it.
    All the int keys will be transformed into int values.

    Args:
        file_to_load (str): The file to read the data from.

    Returns:
        dict: loaded data.
    """
    with open(file_to_load, "r", encoding="utf-8") as f:
        result = json.loads(f.read())

    processed_result = dict()
    for k in result:
        try:
            int_k = int(k)
            processed_result[int_k] = result[k]
        except ValueError:
            processed_result[k] = result[k]
    return processed_result


@safe_execution(log_message="Saving data", default=False)
def save_data(file_to_save, object_to_serialize):
    """
    This function saves the data in the file provided.

    Args:
        file_to_save (str): The file to write the data.
        object_to_serialize (dict): The data object.

    Returns:
        dict: loaded data.
    """
    with open(file_to_save, "w", encoding="utf-8") as f:
        f.write(json.dumps(object_to_serialize, indent=2, ensure_ascii=False))


class Formatter:
    CONSOLE_INTERFACE = "console"
    BOT_INTERFACE = "bot"
    VALID_INTERFACES = {CONSOLE_INTERFACE, BOT_INTERFACE}

    @staticmethod
    def flatten_text(input_text, sep=None):
        """
        This function 'flattens' the input text, removing accent marks and lowering it.

        Args:
            input_text (str): The text to be flattened
            sep (str): A separator that is going to be the replacement for commas.

        Returns:
            str: The 'flattened' text.
        """
        if sep is None:
            sep = " "
        replacements = [(',', sep), ('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ü', 'u')]

        output_text = input_text.lower()
        for char, replacement in replacements:
            output_text = output_text.replace(char, replacement)
        return output_text

    def _setup(self):
        functions = {
            self.CONSOLE_INTERFACE: self._format_word_console,
            self.BOT_INTERFACE: self._format_word_bot
        }

        self.format_word = functions[self.interface]

    def __init__(self, interface):
        if interface not in self.VALID_INTERFACES:
            raise Exception(f"Interface '{interface}' not supported")
        self.interface = interface
        self._setup()

    @staticmethod
    def _format_word_console(word, with_defs=True, raw=False):
        # It returns the console format.
        if raw:
            return word if with_defs else word['word']

        last_length = len(word['word'])
        formatted_word = f"\n{word['word']}\n{'=' * last_length}\n"

        if not with_defs:
            return formatted_word

        for i, definition in enumerate(word["definitions"], 1):
            formatted_definition = f"{i}\t{definition}\n"
            last_length = len(formatted_definition)
            formatted_word += formatted_definition

        return f"{formatted_word}\n{'=' * last_length}\n"

    @staticmethod
    def _format_word_bot(word, with_defs=True, raw=False):
        # It returns the bot format
        if raw:
            return word if with_defs else word['word']

        formatted_content = f"<b>{word['word']}</b>\n"

        if not with_defs:
            return formatted_content

        for i, definition in enumerate(word["definitions"], 1):
            formatted_definition = f"<i>{i}.\t{definition}</i>\n"
            formatted_content += formatted_definition

        return formatted_content
