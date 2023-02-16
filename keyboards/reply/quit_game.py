"""Модуль создания клавиатуры остановки игры."""
from telebot.types import ReplyKeyboardMarkup


def quit_game() -> ReplyKeyboardMarkup:
    """Создает кнопку для окончания игры."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("🏳️Сдаюсь")
    return keyboard
