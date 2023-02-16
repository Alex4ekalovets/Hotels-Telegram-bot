"""Модуль создания клавиатуры с количеством фотографий."""
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def number_of_photos() -> InlineKeyboardMarkup:
    """Создание клавиатуры с количеством фотографий отеля."""
    buttons = [
        [InlineKeyboardButton(str(number), callback_data=number) for number in range(1, 6)],
        [InlineKeyboardButton("Не показывать", callback_data="0")],
    ]
    return InlineKeyboardMarkup(buttons)
