# Script that handles unexpected shutdowns as far as possible.
import sys

from telepot import Bot
from telepot.api import set_proxy

from code.bot.bot_utils import parse_options
from code.bot.bot_config import ADMIN, BOT_CONFIG_FILE
from code.utils import save_data, log


def stop(bot, settings=None):
    """

    Args:
        bot (telepot.Bot): A telegram Bot
        settings(dict, optional): Information that is used by the bot and is wanted to be saved in disk for persistence.
    """
    if settings:
        save_data(BOT_CONFIG_FILE, settings)
        log("Saving bot data...", level="INFO")

    for admin_id in ADMIN:
        bot.sendMessage(admin_id, "The bot interface is down. Please, check up the servers.")
    exit(0)


if __name__ == "__main__":
    token, proxy = parse_options(sys.argv)
    if proxy:
        set_proxy(proxy)
    stop(Bot(token))
