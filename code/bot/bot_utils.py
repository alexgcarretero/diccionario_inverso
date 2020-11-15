# Main utilities for the Telegram Bot
from getopt import getopt, GetoptError

from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from code.bot.bot_config import TOKEN

USAGE = "USAGE:\tpython[3] bot.py [-t TOKEN] [-p PROXY_SERVER]"
PARSING_SCHEME = "p:t:"


def parse_options(arguments):
    """
    This function parses the arguments of the script call and ensures a TOKEN is provided via arg or config file.

    Args:
        arguments (list): the script arguments
    Returns:
        A tuple with the parsed arguments.
    """
    parsed_input = {"-t": TOKEN, "-p": None}

    try:
        parameters, _ = getopt(arguments[1:], PARSING_SCHEME)
        for (option, parameter) in parameters:
            parsed_input[option] = parameter

        if not parsed_input["-t"]:
            raise GetoptError("The TOKEN is needed to run. Set it up via -t or in the bot_config file.")
    except GetoptError as e:
        print(str(e))
        print(USAGE)
        exit(-1)

    return parsed_input["-t"], parsed_input["-p"]


def inline_keyboard(*args):
    """
    This function generates an 'inline keyboard' for the Telegram Message to provide navigation between options in-chat.

    Args:
        *args (dicts): Each param in the args list represents a row in the keyboard.
                       The info in the dict represents a button of that row.

    Returns:
        InlineKeyboardMarkup: the formed keyboard.

    """
    keyboard = list()
    for elements in args:
        keyboard_row = list()
        for name, data in elements.items():
            keyboard_row.append(InlineKeyboardButton(text=name, callback_data=data))
        keyboard.append(keyboard_row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
