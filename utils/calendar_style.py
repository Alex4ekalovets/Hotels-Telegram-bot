"""Модуль изменяющий стиль календаря telegram_bot_calendar."""
from telegram_bot_calendar import DetailedTelegramCalendar
from telegram_bot_calendar.base import DAY

LSTEP = {"y": "год", "m": "месяц", "d": "день"}


class MyStyleCalendar(DetailedTelegramCalendar):
    """Класс MyStyleCalendar, изменяющий стиль календаря.

    Attributes:
        first_step: Изначальный вид календаря при его вызове (DAY - отображение дней)
        prev_button: Надпись на кнопке 'назад'
        next_button: Надпись на кнопке 'вперед'
        empty_nav_button: Надпись на кнопке 'действие недоступно'
        empty_month_button: Надпись на пустой кнопке месяца
        empty_year_button: Надпись на пустой кнопке года
        empty_day_button: Надпись на пустой кнопке дня
    """

    first_step = DAY
    prev_button = "⬅️"
    next_button = "➡️"
    empty_nav_button = "🚫"
    empty_month_button = ""
    empty_year_button = ""
    empty_day_button = "✖️"
