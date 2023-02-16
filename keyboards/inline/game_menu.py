"""Модуль создания клавиатуры игрового меню."""
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def game_menu() -> InlineKeyboardMarkup:
    """Создание клавиатуры с игровым меню."""
    buttons = [
        [
            InlineKeyboardButton("🏁Начать", callback_data="start"),
            InlineKeyboardButton("🏆ТОП 10", callback_data="top"),
        ],
        [InlineKeyboardButton("Изменить имя", callback_data="change_name")],
    ]
    return InlineKeyboardMarkup(buttons)
