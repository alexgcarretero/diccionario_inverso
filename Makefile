export PYTHONPATH=.

install:
	python3 -m pip install -r requirements.txt

console:
	python3 code/console.py

bot:
	./scripts/launch_bot.sh

remove_defs:
	rm data/definiciones/*.json

fetch:
	python3 code/cache_manager -w -d

fetch_words:
	python3 code/cache_manager -w

fetch_defs:
	python3 code/cache_manager -d
