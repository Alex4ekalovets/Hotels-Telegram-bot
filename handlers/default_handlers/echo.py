"""Модуль обработки случайных сообщений пользователя.

Functions:
    bot_echo: Ответ бота на случайное сообщение пользователя
"""

import re

from telebot.types import Message

from config_data.config import COMMAND_MESSAGES
from loader import bot


@bot.message_handler(func=lambda message: message.text not in COMMAND_MESSAGES, content_types="text", state=None)
def bot_echo(message: Message) -> None:
    """Ответ бота на сообщения пользователя."""
    user_name = message.from_user.first_name
    hello_answer = f"Здравствуйте, {user_name}! Чем я могу Вам помочь? /help"
    unknown_message_answer = "Прошу прощения, я Вас не понимаю." " Введите команду /help или воспользуйтесь меню."
    if re.search(pattern=r"привет", string=message.text.lower()):
        bot.send_message(message.chat.id, hello_answer)
    else:
        bot.send_message(message.chat.id, unknown_message_answer)
