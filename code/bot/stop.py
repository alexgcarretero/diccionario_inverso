import sys

from telepot import Bot
from telepot.api import set_proxy

from code.bot import parse_options
from code.bot.bot_config import ADMIN


def stop(bot):
    for admin_id in ADMIN:
        bot.sendMessage(admin_id, "The bot interface is down. Please, check up the servers.")
    exit(0)


if __name__ == "__main__":
    token, proxy = parse_options(sys.argv)
    if proxy:
        set_proxy(proxy)
    stop(Bot(token))
