# Diccionario Inverso Castellano

En este repositorio se ofrece una herramienta que
recopila todas las palabras del castellano y sus definiciones,
así como dos interfaces diferentes para acceder a los servicios.

Una de estas interfaces (y la recomendada) es un **Bot de Telegram**, disponible en
[@DiccionarioInversoBot](https://t.me/DiccionarioInversoBot).

La otra interfaz es a través de **consola de comandos**, para lo cual se requiere `python3` y `pip3` 
con las librerias descritas en el archivo `requirements.txt`.

A través del archivo `Makefile` se proveen comandos tales como:

* Instalar las librerias necesarias con `make install`.
* Lanzar la interfaz de consola con `make consola`.
* Eliminar todos los datos almacenados con ``make remove_defs``.
* Recargar todos los datos con ``make fetch``.
* Recargar las palabras almacenadas con ``make fetch_words``.
* Recargar las definiciones almacenadas con ``make fetch_defs``. (Esto tardará mucho).

## [El bot: @DiccionarioInversoBot](https://t.me/DiccionarioInversoBot)
La interfaz del bot se compone principalmente de 2 comandos, de los que puedes obtener más información a través del
comando ***/ayuda***.

1. ***/encuentra***: Realiza la búsqueda inversa, acompañandolo de los términos de la búsqueda. Y te devolverá un
mensaje a través del cual podrás navegar entre los distintos resultados.

2. ***/busca***: Realiza una búsqueda directa, o tradicional. Te devolverá la definición del diccionario de la
RAE de dicha palabra.

3. ***/estadisticas***: Te devuelve unas estadisticas generales del sistema: número de palabras y definiciones; y la
letra por la que empiezan más palabras.

Adicionalmente, se presenta también el comando ***/contacto*** para enviar mensajes a los administradores, tanto
para propuestas de mejora como para posibles dudas.


## La consola

Al iniciar la interfaz de consola de comandos, se nos presentará un menú con selección numérica.

Por defecto, el modo *búsqueda inversa* sólo devolverá las palabras correspondientes a los resultados de búsqueda,
si quieres que también se ofrezcan las definiciones, debes ejecutar el comando ``/def`` para encender las definiciones y
``/nodef`` para apagarlo y volver a los valores por defecto.

Para salir de los modos *búsqueda directa o tradicional* y *búsqueda inversa* hay que escribir el comando ``/salir``.

Desde el menú también se ofrece la posibilidad de actualizar las palabras y definiciones almacenadas en el sistema.
Para más información sobre esto te sugiero que revises el código, en ``code/cache_manager/cache_manager.py``.


## El código
El repositorio se divide principalmente en 2 carpetas: los datos del sistema en `data`, y el código en `code`.

### Data
* ``palabras.json``: Todas las palabras indexadas por la letra que empiezan.
* ``definiciones/{letra}.json``: Todas las definiciones, indexadas por la palabra que definen.
Sólo contiene las palabras que empiezan por la letra `letra`.
* ``definiciones.json``: Todas las definiciones, indexadas por la palabra que definen y la letra por la que
empieza la palabra.
* ``bot_settings.json``: Archivo de persistencia de datos para el bot de telegram.

### Code
El código se compone de 3 módulos y 4 archivos, de los que cabe destacar:
* `config.py`: Donde se encuentra la configuración global de todo el sistema,
principalmente para la localización de los ficheros.
* `console.py` y `telegram_bot.py`: los scripts principales de cada una de las interfaces.
  * Para ejecutar la consola de comandos basta con ``python3 console.py``
  * Para ejecutar el bot de telegram, es necesario un TOKEN, que se puede proveer tanto en el
  fichero `code/bot/bot_config.py` como por argumento al ejecutar el script, el cual también admite un proxy.
  
  ```
  python3 telegram_bot.py [-t TOKEN] [-p PROXY_SERVER]
  ```

* `bot/`: Funciones auxiliares para el funcionamiento del bot, así como su propia configuración.
* `cache_manager/`: Manejo de las APIS de la RAE y gestión de recopilación de palabras y definiciones.
* `search_engine/`: Toda la lógica de la búsqueda de palabras y definiciones en los datos del sistema.