from getopt import getopt, GetoptError
from code.bot.bot_config import TOKEN

USAGE = "USAGE:\tpython[3] bot.py [-t TOKEN] [-p PROXY_SERVER]"
PARSING_SCHEME = "p:t:"


def parse_options(arguments):
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
