"""Модуль с информацией о текущем запросе пользователя."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional


class Users:
    """Класс User, описывающий пользователя и текущий поисковый запрос.

    current_cmd: Текущая команда поиска пользователя
    creation_instance_time: Дата и время создания экземпляра класса
    cmd_message: Объект класса telebot.types.Message последнего сообщения с командой пользователя
    next_delete_message: Номер сообщения, которое требует удаления
    user_id: Telegram id пользователя
    request: Объект класса Request. Последний запрос пользователя. Используется для добавления результатов поиска
    region_id: id города, выбранного пользователем
    city: Название введенного пользователем города
    results_size: Количество результатов поиска
    number_of_photos: Количество фотографий отеля
    min_price: Минимальная стоимость за ночь, введенная пользователем
    max_price: Максимальная стоимость за ночь, введенная пользователем
    check_in_date: Дата заселения
    check_out_date: Дата выезда
    total_days: Общее количество дней
    min_distance: Минимальное расстояние до центра, введенное пользователем
    max_distance: Максимальное расстояние до центра, введенное пользователем
    all_users: Словарь со всеми пользователями бота
    """

    all_users: Dict = dict()

    def __init__(self, user_id: int) -> None:
        """Создает экземпляр класса User."""
        self.__current_cmd: Optional[str] = None
        self.creation_instance_time: date = datetime.now()
        self.cmd_message: Any = None
        self.next_delete_message: Optional[int] = None
        self.user_id: int = user_id
        self.request = None

        self.region_id: str = ""
        self.city: str = ""
        self.results_size: int = 0
        self.number_of_photos: int = 0

        self.__min_price: int = 1
        self.__max_price: int = 1
        self.__check_in_date: date = date.today() - timedelta(days=1)
        self.__check_out_date: Any = None
        self.__total_days: int = 0
        self.__min_distance: int = 0
        self.__max_distance: int = 0
        Users.add_user(user_id, self)

    @classmethod
    def get_user(cls, user_id: int) -> Any:
        """Получает существующего пользователя или создает нового."""
        if cls.all_users.get(user_id) is None:
            return Users(user_id)
        return cls.all_users.get(user_id)

    @classmethod
    def add_user(cls, user_id: int, user: Users) -> None:
        """Добавляет пользователя в список пользователей."""
        cls.all_users[user_id] = user

    @property
    def current_cmd(self) -> str:
        """Геттер текущей команды пользователя."""
        if self.__current_cmd:
            return self.__current_cmd
        return self.cmd_message.text

    @current_cmd.setter
    def current_cmd(self, command: str) -> None:
        """Сеттер текущей команды пользователя."""
        self.__current_cmd = command

    @property
    def min_price(self) -> int:
        """Геттер минимальной стоимости за ночь."""
        return min(self.__max_price, self.__min_price)

    @min_price.setter
    def min_price(self, price: int) -> None:
        """Сеттер минимальной стоимости за ночь."""
        if price > 1:
            self.__min_price = price

    @property
    def max_price(self) -> int:
        """Геттер максимальной стоимости за ночь."""
        return max(self.__max_price, self.__min_price)

    @max_price.setter
    def max_price(self, price: int) -> None:
        """Сеттер максимальной стоимости за ночь."""
        if price > 1:
            self.__max_price = price

    @property
    def min_distance(self) -> int:
        """Геттер минимального расстояния от центра."""
        if self.__min_distance > self.__max_distance:
            return self.__max_distance
        return self.__min_distance

    @min_distance.setter
    def min_distance(self, distance: int) -> None:
        """Сеттер минимального расстояния от центра."""
        self.__min_distance = distance

    @property
    def max_distance(self) -> int:
        """Геттер максимального расстояния до це центра."""
        if self.__min_distance > self.__max_distance:
            return self.__min_distance
        return self.__max_distance

    @max_distance.setter
    def max_distance(self, distance: int) -> None:
        """Сеттер максимального расстояния до центра."""
        self.__max_distance = distance

    @property
    def check_in_date(self) -> date:
        """Геттер даты заселения."""
        return self.__check_in_date

    @check_in_date.setter
    def check_in_date(self, user_date: date) -> None:
        """Сеттер даты заселения."""
        self.__check_in_date = user_date
        self.__check_out_date = user_date + timedelta(days=28)

    @property
    def check_out_date(self) -> date:
        """Геттер даты выезда."""
        return self.__check_out_date

    @check_out_date.setter
    def check_out_date(self, user_date: Optional[date]) -> None:
        """Сеттер даты выезда."""
        self.__check_out_date = user_date

    @property
    def total_days(self) -> int:
        """Геттер общего количества дней."""
        self.__total_days = (self.check_out_date - self.check_in_date).days
        return self.__total_days
