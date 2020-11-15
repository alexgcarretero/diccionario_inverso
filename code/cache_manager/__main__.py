# Cache Reload as Script
import sys
from code.cache_manager.manager import CacheManager

USAGE = "USAGE:\tpython3 cache_manager [-w] [-d]"

if len(sys.argv[1:]) < 1 or len(sys.argv[1:]) > 2:
    print(USAGE)
else:
    force_words_update = False
    force_definitions_update = False

    for arg in sys.argv[1:]:
        if arg not in ("-w", "-d"):
            print(USAGE)
            break
        else:
            if arg == "-w":
                force_words_update = True
            else:
                force_definitions_update = True

    CacheManager().manage_cache(force_words_update=force_words_update,
                                force_definitions_update=force_definitions_update)
