"""Модуль создания клавиатуры действий с запросами пользователя."""
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def request_action(request_id: int) -> InlineKeyboardMarkup:
    """Создание клавиатуры для действий с запросами пользователя из истории запросов."""
    keyboard = InlineKeyboardMarkup()
    key_repeat = InlineKeyboardButton(text="Повторить", callback_data=" ".join(("repeat", str(request_id))))
    key_show_results = InlineKeyboardButton(text="Результаты", callback_data=" ".join(("results", str(request_id))))
    keyboard.add(key_repeat, key_show_results)
    return keyboard
