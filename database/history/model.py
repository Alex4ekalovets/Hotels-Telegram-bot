"""Модуль определяющий модель базы данных истории запросов.

db: Файл базы данных SQLite

Classes:
    BaseModel: Базовая модель БД
    User: Таблица с данным о пользователе
    Request: Таблица с данными о запросах пользователя
    Result: Таблица с данными о результатах поиска по запросам пользователя
"""
from peewee import (CharField, DateField, DateTimeField, FloatField,
                    ForeignKeyField, IntegerField, Model, SqliteDatabase)

db = SqliteDatabase("database/history/history.db")


class BaseModel(Model):
    """Класс наследник от peewee.Model, описывает базовую модель."""

    class Meta:
        """Класс Meta."""

        database = db


class User(BaseModel):
    """Класс, описывающий структуру таблицы users БД, содержащую информацию о пользователях.

    Attributes:
        user_id: id Telegram аккаунта пользователя
    """

    user_id = IntegerField(unique=True)

    class Meta:
        """Класс Meta."""

        table_name = "users"


class Request(BaseModel):
    """
    Класс, описывающий структуру таблицы requests БД, содержащую информацию о запросах пользователей.

    Attributes:
        user: Ссылка на пользователя (объект класса User, запись таблицы users) с соответствующим id
        command: Команда от пользователя, соответствующая типу запроса
        created_time: Дата и время создания запроса
        region_id: id города, в котором пользователь ищет отели
        city: Название города, в котором пользователь ищет отели
        results_size: Количество результатов поиска
        number_of_photos: Количество фотографий отеля
        min_price: Минимальная цена за ночь в отеле
        max_price: Максимальная цена за ночь в отеле
        check_in_date: Дата заезда
        check_out_date: Дата выезда
        min_distance: Минимальное расстояние до центра
        max_distance: Максимальное расстояние до центра
    """

    user = ForeignKeyField(User)
    command = CharField()
    created_time = DateTimeField()
    region_id = CharField()
    city = CharField()
    results_size = IntegerField()
    number_of_photos = IntegerField()
    min_price = IntegerField()
    max_price = IntegerField()
    check_in_date = DateField()
    check_out_date = DateField()
    min_distance = IntegerField()
    max_distance = IntegerField()

    class Meta:
        """Класс Meta."""

        table_name = "requests"


class Result(BaseModel):
    """Класс, описывающий структуру таблицы results БД, содержащую информацию о результатах запросов пользователей.

    Attributes:
        request_id: Ссылка на запрос (объект класса Request, запись таблицы requests) с соответствующим id
        name: Название отеля
        distance: Расстояние до центра
        price: Цена за ночь в отеле
        total: Общая стоимость проживания
    """

    request_id = ForeignKeyField(Request)
    name = CharField()
    distance = FloatField()
    price = CharField()
    total = CharField()

    class Meta:
        """Класс Meta."""

        table_name = "results"
