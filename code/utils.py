import functools
import json

from code.cache_manager.API import APIException


class HashableDict(dict):
    def __hash__(self):
        if "word" in self:
            return hash(self["word"])
        return hash(tuple(sorted(self.items())))


def log(message, level="LOG", end=None, start=None, show_log=True):
    if not show_log:
        return

    if end is None:
        end = "\n"

    if start is None:
        start = ""

    print(f"{start}[{level}]\t{message}", end=end)


def safe_execution(log_message=None, default=None):
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
    with open(file_to_load, "r", encoding="utf-8") as f:
        result = json.loads(f.read())
    return result


@safe_execution(log_message="Saving data", default=False)
def save_data(file_to_save, object_to_serialize):
    with open(file_to_save, "w", encoding="utf-8") as f:
        f.write(json.dumps(object_to_serialize, indent=2, ensure_ascii=False))
    return True


class Formatter:
    CONSOLE_INTERFACE = "console"
    BOT_INTERFACE = "bot"
    VALID_INTERFACES = {CONSOLE_INTERFACE, BOT_INTERFACE}

    @staticmethod
    def flatten_text(input_text):
        output_text = input_text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o")
        output_text.replace("ú", "u").replace("ü", "u")
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
    def _format_word_console(word, with_defs=True):
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
    def _format_word_bot(word, with_defs=True):
        formatted_word = f"<b>{word['word']}</b>\n"

        if not with_defs:
            return formatted_word

        for i, definition in enumerate(word["definitions"], 1):
            formatted_definition = f"<i>{i}.\t{definition}</i>\n"
            formatted_word += formatted_definition

        return formatted_word
