"""Модуль создания клавиатуры с количеством отелей."""
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def number_of_hotels() -> InlineKeyboardMarkup:
    """Создание клавиатуры с количеством отелей для вывода в результатах."""
    buttons = [
        [
            InlineKeyboardButton("1", callback_data=1),
            InlineKeyboardButton("3", callback_data=3),
            InlineKeyboardButton("5", callback_data=5),
            InlineKeyboardButton("10", callback_data=10),
        ]
    ]
    return InlineKeyboardMarkup(buttons)
