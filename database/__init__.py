"""Загружает модули взаимодействия с БД и API.

Modules:
    api_requests: Модуль взаимодействия с API сайта Hotels.com
    history: Модуль взаимодействия с БД истории запросов
    game_cities: Модуль взаимодействия с БД игровой статистики игры Города
"""

from database import api_requests, game_cities, history
