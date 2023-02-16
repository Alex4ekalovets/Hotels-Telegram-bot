"""Модуль обработки команды start.

Functions:
    bot_start: Запуск бота
"""

import random

from telebot.types import Message

from handlers.default_handlers.help import bot_help
from loader import bot


@bot.message_handler(commands=["start"])
def bot_start(message: Message) -> None:
    """Запуск бота."""
    user_name = message.from_user.first_name
    answers = [
        f"Добрый день, {user_name}! Я помогу Вам подобрать отель!",
        "Здравствуйте! Какой отель Вас интересует?",
        "Добрый день! Я бот-помощник по поиску отелей! Давайте подберем вариант для Вас!",
    ]
    bot.send_message(message.chat.id, random.choice(answers))
    bot_help(message)
