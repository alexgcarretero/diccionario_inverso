import sys
from time import sleep

from telepot import Bot, glance
from telepot.api import set_proxy
from telepot.loop import MessageLoop

from code.bot import parse_options
from code.bot.bot_config import ADMIN, SLEEP_TIME
from code.cache_manager.manager import CacheManager
from code.search_engine.search_engine import SearchEngine
from code.utils import Formatter


def _inverse_search(query, chat_id, *args):
    return search_engine.search(query, with_defs=per_chat_context[chat_id]["defs"])


def _direct_search(query, *args):
    return search_engine.consult(query)


def _number_of_words(*args):
    return f"En el sistema hay un total de {cache_manager.number_of_words()} palabras."


def _number_of_definitions(*args):
    return f"En el sistema hay un total de {cache_manager.number_of_definitions()} palabras."


def _show_help(*args):
    return (
        "<b> Menú de ayuda </b>\n"
        "Los comandos disponibles son los siguientes:\n"
        "<b><i>/ayuda</i></b>\t:\tMuestra este menú.\n\n"
        "<b><i>/encuentra</i></b>\t:\tRealiza una búsqueda inversa en todo el diccionario.\n"
        "\t<i>Ejemplo:\t/encuentra parecido marfil</i>\n"
        "\tY entre las respuestas te aparecerá <b>ebúrneo</b>.\n"
        "\tPor defecto se devuelven <b>SÓLO</b> las palabras coincidentes, sin las definiciones.\n"
        "\tPara cambiar esto ejecuta el comando <b><i>/def</i></b> de la siguiente forma:\n"
        "<i>/def on</i>\t:\tActiva la inserción de definiciones en la respuesta.\n"
        "<i>/def off</i>\t:\tDesactiva la inserción de definiciones en la respuesta.\n\n"
        "<b><i>/busca</i></b>\t:\tBusca una palabra en el diccionario de forma normal, "
        "devolviéndote sus definiciones.\n"
        "\t<i>Ejemplo:\t/busca ebúrneo</i>\n\n"
        "<b><i>/palabras</i></b>\t:\tTe responde el número de palabras almacenadas en el sistema.\n\n"
        "<b><i>/definiciones</i></b>\t:\tTe responde el número de definiciones almacenadas en el sistema.\n\n"
        "<b><i>/contacto</i></b>\t:\tEnvía un mensaje a los administradores del bot para dudas o sugerencias.\n"
        "\t<i>Ejemplo:\t/contacto Muy buenas tardes.</i>\n"
        "\tY le enviará el mensaje 'Muy buenas tardes.' a los administradores\n"
    )


def _contact_admin(message, chat_id):
    message_info = f"El usuario con ID '{chat_id}' dice:"
    for admin_id in ADMIN:
        bot.sendMessage(admin_id, message_info)
        bot.sendMessage(admin_id, message)
    return "Mensaje enviado correctamente a los administradores."


def _init_chat(text, chat_id, *args):
    per_chat_context[chat_id] = {"defs": False}
    return "Bienvenido al bot!\nSi no sabes muy bien qué hacer haz <i>/ayuda</i> para ver qué puedo hacer."


def _change_def_per_chat(value, chat_id, *args):
    if value not in ("on", "off"):
        return f"'{value}' no es una opción valida para el comando /def"
    set_value = True if value == "on" else False
    per_chat_context[chat_id]["defs"] = set_value
    return "Configuración establecida."


def manage_messages(input_message):
    def treat_input_query(input_query):
        content = input_query.split()
        output_command = content[0]
        output_query = ' '.join(content[1:])
        return output_command, Formatter.flatten_text(output_query)

    content_type, _, chat_id = glance(input_message)

    command_handler = {
        "/start": _init_chat,
        "/ayuda": _show_help,
        "/busca": _direct_search,
        "/encuentra": _inverse_search,
        "/palabras": _number_of_words,
        "/definiciones": _number_of_definitions,
        "/contacto": _contact_admin,
        "/def": _change_def_per_chat
    }

    print(content_type, input_message[content_type], chat_id)

    if content_type == "text":
        command, query = treat_input_query(input_message[content_type])

        query_result = command_handler.get(command, lambda *args: "No entiendo ese comando.")(query, chat_id)
        bot.sendMessage(chat_id, query_result, parse_mode="HTML")
    else:
        bot.sendMessage(chat_id, "Sólo admito entrada por texto.")


if __name__ == "__main__":
    token, proxy = parse_options(sys.argv)
    if proxy:
        set_proxy(proxy)

    bot = Bot(token)
    cache_manager = CacheManager()
    search_engine = SearchEngine(cache_manager.definitions, Formatter("bot"))
    per_chat_context = dict()

    print("Bot running...")
    MessageLoop(bot, {"chat": manage_messages}).run_as_thread()
    while True:
        sleep(SLEEP_TIME)
