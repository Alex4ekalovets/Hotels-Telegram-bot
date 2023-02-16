"""Модуль запуска телеграмм бота."""

from telebot import custom_filters, types

import handlers
from loader import bot
from utils.set_bot_commands import set_default_commands

if __name__ == "__main__":
    set_default_commands(bot)
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()
