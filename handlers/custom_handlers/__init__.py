"""Загружает модули обработчиков команд пользователя боту.

Modules:
    bestdeal: Модуль ввода дополнительных параметров для команды bestdeal
    clear_data_base: Модуль очистки баз данных
    common_search_handlers: Общий модуль обработки команд bestdeal, lowprice и highprice
    game_cities: Модуль игры "Города"
    history: Модуль истории запросов пользователя
"""

from . import (bestdeal, clear_data_base, common_search_handlers, game_cities,
               history)
