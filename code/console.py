from code.cache_manager.manager import CacheManager
from code.search_engine.search_engine import SearchEngine
from code.utils import log

# STRING CONSTANTS AND INTERFACE CONFIG

SEPARATOR = "===============================================================\n"
WELCOME = (
    f"{SEPARATOR}"
    "= BIENVENIDO AL DICCIONARIO INVERSO DE LA RAE VERSIÓN PYTHON =\n"
    "========= por: Alejandro García (🐦 @alexgcarretero) ==========\n"
    f"{SEPARATOR}"
)

WELCOME_MENU = (
    "\n\n"
    "======================= MENÚ PRINCIPAL =======================\n"
)

HELP_INV = (
    f"{SEPARATOR}"
    "==================== MODO BUSQUEDA INVERSA ====================\n"
    f"{SEPARATOR}"
    "Introduce una busqueda en la linea de comandos para realizar la búsqueda inversa.\n"
    "Para introducir un comando haz:\t'/comando'.\nLos comandos disponibles son:\n\n"
)

HELP_DIR = (
    f"{SEPARATOR}"
    "==================== MODO BUSQUEDA DIRECTA ====================\n"
    f"{SEPARATOR}"
    "Introduce una busqueda en la linea de comandos para realizar la búsqueda de dicha palabra.\n"
    "Para introducir un comando haz:\t'/comando'.\nLos comandos disponibles son:\n\n"
)

COMMANDS_INV = {
    "/salir": "Salir del modo 'Búsqueda Inversa' y volver al menú principal.",
    "/def": "Los resultados de la búsqueda inversa se devolverán con definiciones. Por defecto esto no ocurre.",
    "/nodef": "Los resultados de la búsqueda inversa se devolverán sin definiciones, sólo las palabras."
}

COMMANDS_DIR = {
    "/salir": "Salir del modo 'Búsqueda Directa' y volver al menú principal.",
}

MENU = [
    "Realizar una búsqueda inversa.",
    "Realizar una búsqueda normal en el diccionario.",
    "Ver cuántas palabras hay almacenadas (número).",
    "Ver cuántas definiciones hay almacenadas (número).",
    "Descargar todas las palabras del castellano.",
    "Descargar todas las definiciones de las palabras almacenadas.",
    "Salir y cerrar el programa."
]


def prompt(mode):
    return f"[MODO {mode}]>> "


# Global variables and functions
cache_manager = CacheManager()
search_engine = SearchEngine(cache_manager.definitions)


def inverse_search():
    print(HELP_INV)
    for command_number, (command, description) in enumerate(COMMANDS_INV.items(), 1):
        print(f"{command_number}\t{command}\t=>\t{description}")
    print(SEPARATOR)
    while (query := input(prompt("BÚSQUEDA INVERSA"))) != "/salir":
        if query[0] == "/":
            options = {'/def': True, '/nodef': False}
            if query in options:
                search_engine.set_with_definitions(options[query])
            else:
                log("No reconozco ese comando.", level="INFO")
        else:
            print("Resultados:")
            for result in search_engine.search(query):
                print(result)


def direct_search():
    print(HELP_DIR)
    for command_number, (command, description) in enumerate(COMMANDS_DIR.items(), 1):
        print(f"{command_number}\t{command}\t=>\t{description}")
    print(SEPARATOR)
    while (query := input(prompt("BÚSQUEDA DIRECTA"))) != "/salir":
        print(f"Resultados:\n{search_engine.consult(query)}")


def number_of_words():
    print(f"Hay {cache_manager.number_of_words()} palabras almacenadas en el sistema.")


def number_of_definitions():
    print(f"Hay {cache_manager.number_of_definitions()} definiciones totales almacenadas en el sistema.")


def fetch_words():
    cache_manager.manage_cache(force_words_update=True)


def fetch_definitions():
    cache_manager.manage_cache(force_definitions_update=True)
    search_engine.set_definitions(cache_manager.definitions)


MENU_SELECTOR = {
    1: inverse_search, 2: direct_search, 3: number_of_words,
    4: number_of_definitions, 5: fetch_words, 6: fetch_definitions,
    7: exit
}

if __name__ == "__main__":
    print(WELCOME)

    while True:
        print(WELCOME_MENU)
        for item_number, item in enumerate(MENU, 1):
            print(f"{item_number}\t{item}")

        print(SEPARATOR)
        menu_selection = input(prompt("MENU"))
        try:
            menu_selection = int(menu_selection)
            MENU_SELECTOR[menu_selection]()
        except (ValueError, KeyError) as e:
            log("Introduce un numero que se corresponda a una opción del menú.", level="INFO")
