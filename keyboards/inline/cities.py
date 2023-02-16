"""Модуль создания клавиатуры выбора города."""
from typing import Dict, List

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def clarify_city(cities: List[Dict]) -> InlineKeyboardMarkup:
    """Создание клавиатуры с перечнем городов."""
    buttons = [
        [InlineKeyboardButton(city["name"], callback_data="#".join((city["name"], city["id"])))] for city in cities
    ]
    buttons.append([InlineKeyboardButton("Найти заново", callback_data="again")])
    return InlineKeyboardMarkup(buttons)
