"""Загружает дополнительные утилиты для работы бота.

Modules:
   calendar_style: Изменение стиля календаря
   city_translator: Перевод названия городов с русского на английский
   logging: Модуль настройки loguru
   set_bot_commands: Создание меню команд бота
"""

from . import calendar_style, city_translator, logging, set_bot_commands
from .logging import logger
