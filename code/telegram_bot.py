import signal
import sys
from time import sleep
from uuid import uuid4

from telepot import Bot, glance, message_identifier
from telepot.api import set_proxy
from telepot.exception import TelegramError
from telepot.loop import MessageLoop

from code.bot.bot_utils import parse_options, inline_keyboard
from code.bot.bot_config import ADMIN, SLEEP_TIME, BOT_CONFIG_FILE
from code.bot.stop import stop
from code.cache_manager.manager import CacheManager
from code.search_engine.search_engine import SearchEngine
from code.utils import Formatter, load_data, log, safe_execution


# Signal Handler
def signal_handler(sig, frame):
    stop(bot, settings=chat_context)
    exit()


# Command functions
def _handle_inverse_results(inverse_search_results, current_index):
    word_content = search_engine.consult(inverse_search_results[current_index])
    keyboard = None

    if (query_length := len(inverse_search_results)) > 1:
        preview_index = (current_index - 1 + query_length) % query_length
        next_index = (current_index + 1) % query_length

        preview_word = inverse_search_results[preview_index]
        next_word = inverse_search_results[next_index]

        keyboard = inline_keyboard({
            preview_word: f"{current_uuid}:{preview_index}",
            next_word: f"{current_uuid}:{next_index}"
        })
    return word_content, keyboard


def _inverse_search(chat_id, query):
    word_results = search_engine.search(query, with_defs=False, raw=True)
    if chat_id in chat_context:
        chat_context[chat_id]["/encuentra"]["last_query_result"] = word_results
    else:
        chat_context[chat_id] = {"/encuentra": {"last_query_result": word_results, "last_message": None}}

    try:
        last_message_identifier = tuple(chat_context[chat_id]["/encuentra"]["last_message"])
        bot.deleteMessage(last_message_identifier)
    except (TypeError, TelegramError) as e:
        log(e, level="ERROR")

    if len(word_results) == 0:
        msg = bot.sendMessage(chat_id, "No he encontrado ningún resultado.")
    else:
        content, keyboard = _handle_inverse_results(word_results, 0)
        msg = bot.sendMessage(chat_id, content, parse_mode="HTML", reply_markup=keyboard)
    chat_context[chat_id]["/encuentra"]["last_message"] = message_identifier(msg)


def _direct_search(chat_id, query):
    bot.sendMessage(chat_id, search_engine.consult(query), parse_mode="HTML")


def _system_statistics(chat_id, query):
    msg = (
        f"En el sistema hay un total de <b>{cache_manager.number_of_words()}</b> <i>palabras</i>.\n"
        f"En el sistema hay un total de <b>{cache_manager.number_of_definitions()}</b> <i>definiciones</i>.\n"
        f"La letra por la que <b>empiezan más palabras</b> es la <i>{cache_manager.max_words_letter()}</i>.\n"
    )
    bot.sendMessage(chat_id, msg, parse_mode="HTML")


def _show_help(chat_id, query):
    msg = (
        "<b> Menú de ayuda </b>\n"
        "Los comandos disponibles son los siguientes:\n"
        "<b><i>/ayuda</i></b>\t:\tMuestra este menú.\n\n"
        "<b><i>/encuentra</i></b>\t:\tRealiza una búsqueda inversa en todo el diccionario.\n"
        "\t<i>Ejemplo:\t/encuentra parecido marfil</i>\n"
        "\tY entre las respuestas te aparecerá <b>ebúrneo</b>.\n\n"
        "<b><i>/busca</i></b>\t:\tBusca una palabra en el diccionario de forma normal, "
        "devolviéndote sus definiciones.\n"
        "\t<i>Ejemplo:\t/busca ebúrneo</i>\n\n"
        "<b><i>/definiciones</i></b>\t:\tTe responde con diversas estadisticas del sistema.\n\n"
        "<b><i>/contacto</i></b>\t:\tEnvía un mensaje a los administradores del bot para dudas o sugerencias.\n"
        "\t<i>Ejemplo:\t/contacto Muy buenas tardes.</i>\n"
        "\tY le enviará el mensaje 'Muy buenas tardes.' a los administradores\n"
    )
    bot.sendMessage(chat_id, msg, parse_mode="HTML")


def _contact_admin(chat_id, message):
    message_info = f"El usuario con ID '{chat_id}' dice:"
    for admin_id in ADMIN:
        bot.sendMessage(admin_id, message_info)
        bot.sendMessage(admin_id, message)
    msg = "Mensaje enviado correctamente a los administradores."
    bot.sendMessage(chat_id, msg)


def _init_chat(chat_id, query):
    # chat_context[chat_id] = {"/encuentra": {"last_message": None, "last_query_result": list()}}
    msg = "Bienvenido al bot!\nSi no sabes muy bien qué hacer haz <i>/ayuda</i> para ver qué puedo hacer."
    bot.sendMessage(chat_id, msg, parse_mode="HTML")


# Chat handle functions
@safe_execution()
def manage_messages(input_message):
    content_type, _, chat_id = glance(input_message)

    command_handler = {
        "/start": _init_chat,
        "/ayuda": _show_help,
        "/busca": _direct_search,
        "/encuentra": _inverse_search,
        "/estadisticas": _system_statistics,
        "/contacto": _contact_admin,
    }
    log(f"{content_type, input_message[content_type], chat_id=}", level="INFO")

    if content_type == "text":
        content = input_message[content_type].split()
        command = content[0]
        query = ' '.join(content[1:])
        command_handler.get(command, lambda *args: "No entiendo ese comando.")(chat_id, query)
    else:
        bot.sendMessage(chat_id, "Sólo admito entrada por texto.")


@safe_execution()
def manage_callback(input_message):
    query_id, chat_id, query_data = glance(input_message, flavor="callback_query")
    query_data = query_data.split(":")
    if query_data[0] != current_uuid:
        return

    last_query_result = chat_context[chat_id]["/encuentra"]["last_query_result"]
    last_message_identifier = tuple(chat_context[chat_id]["/encuentra"]["last_message"])

    current_index = int(query_data[1])
    content, keyboard = _handle_inverse_results(last_query_result, current_index)
    bot.editMessageText(last_message_identifier, content, parse_mode="HTML", reply_markup=keyboard)


# Main
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    token, proxy = parse_options(sys.argv)
    if proxy:
        set_proxy(proxy)

    bot = Bot(token)
    cache_manager = CacheManager()
    search_engine = SearchEngine(cache_manager.definitions, Formatter("bot"))

    chat_context = load_data(BOT_CONFIG_FILE)
    current_uuid = str(uuid4())

    log("Bot running...", level="INFO")
    MessageLoop(bot, {"chat": manage_messages, "callback_query": manage_callback}).run_as_thread()
    while True:
        sleep(SLEEP_TIME)
