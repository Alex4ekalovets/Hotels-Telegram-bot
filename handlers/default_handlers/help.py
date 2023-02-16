"""Модуль обработки команды help.

Functions:
    bot_help: Вывод команд бота
"""

from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=["help"])
def bot_help(message: Message) -> None:
    """Вывод справки по командам бота."""
    text = [f"{desk[:1]}/{command} - {desk[1:]}" for command, desk in DEFAULT_COMMANDS]
    text.insert(0, "Введите одну из предложенных команд:")
    bot.send_message(message.chat.id, "\n".join(text))
