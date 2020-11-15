#!/usr/bin/env bash
trap 'python3 code/bot/stop.py' INT TERM EXIT
python3 code/telegram_bot.py
