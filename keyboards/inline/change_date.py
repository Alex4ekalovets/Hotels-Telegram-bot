"""Модуль создания клавиатуры изменения даты."""

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def change_date(state: str) -> InlineKeyboardMarkup:
    """Создание клавиатуры для сохранения или изменения выбранной в календаре даты."""
    keyboard = InlineKeyboardMarkup()
    key_wrong_date = InlineKeyboardButton(text="Изменить дату", callback_data=" ".join(("wrong", state)))
    key_next = InlineKeyboardButton(text="Продолжить", callback_data=state)
    keyboard.add(key_wrong_date, key_next)
    return keyboard
