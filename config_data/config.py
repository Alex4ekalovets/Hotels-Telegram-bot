"""Модуль загружает токен телеграм бота, ключ Rapid_API, ID и пароль админа телеграм бота, список команд бота."""

import os
from typing import Any

from dotenv import find_dotenv, load_dotenv

if find_dotenv():
    load_dotenv()
else:
    exit("Переменные окружения не загружены т.к отсутствует файл .env")


BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY: Any = os.getenv("RAPID_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
DEFAULT_COMMANDS = (
    ("help", "🛎помощь по командам бота"),
    ("lowprice", "📉вывод самых дешёвых отелей в городе"),
    ("highprice", "📈вывод самых дорогих отелей в городе"),
    ("bestdeal", "📊вывод отелей, наиболее подходящих по цене и расположению от центра"),
    ("history", "🗄вывод истории поиска отелей"),
    ("game", "🗺играть в города"),
)
COMMAND_MESSAGES = ["/" + DEFAULT_COMMANDS[command][0] for command in range(0, len(DEFAULT_COMMANDS))]
COMMAND_MESSAGES.extend(["/start", "/clear"])
