"""Модуль определяющий модель базы данных игры Города.

db_game: Файл базы данных SQLite

Classes:
    BaseModel: Базовая модель БД
    City: Класс, определяющий таблицу с городами
    Player: Класс, определяющий таблицу с игроками
    City2Player: Класс, определяющий таблицу соответствия игроков названным в игре городам
"""

from peewee import (BigIntegerField, CharField, ForeignKeyField, IntegerField,
                    Model, SqliteDatabase)

db_game = SqliteDatabase("database/game_cities/game.db")


class BaseModel(Model):
    """Класс наследник от peewee.Model, описывает базовую модель."""

    class Meta:
        """Класс Meta."""

        database = db_game


class City(BaseModel):
    """Класс, описывающий структуру таблицы cities БД, содержащую информацию о городе.

    Attributes:
        country_en: Название страны на английском
        region_en: Название региона на английском
        city_en: Название города на английском
        country: Название страны на русском
        region: Название региона на русском
        city: Название города на русском
        lat: Широта (города)
        lng = Долгота (города)
        population: Население города
    """

    country_en = CharField()
    region_en = CharField()
    city_en = CharField()
    country = CharField()
    region = CharField()
    city = CharField()
    lat = CharField()
    lng = CharField()
    population = IntegerField

    class Meta:
        """Класс Meta."""

        table_name = "cities"


class Player(BaseModel):
    """Класс, описывающий структуру таблицы players БД, содержащую информацию об игроке.

    Attributes:
        player_id: id Telegram аккаунта пользователя
        max_scores: Максимальное количество очков игрока
        nickname: Игровое имя пользователя
    """

    player_id = BigIntegerField(unique=True)
    max_scores = IntegerField()
    nickname = CharField()

    class Meta:
        """Класс Meta."""

        table_name = "players"


class City2Player(BaseModel):
    """Класс, описывающий структуру таблицы city2player БД.

    Таблица связывает названные в игре города с игроками.

    Attributes:
        city_id: Ссылка на город (объект класса City, запись таблицы cities) с соответствующим id
        player_id: Ссылка на город (объект класса Player, запись таблицы players) с соответствующим id
    """

    city_id = ForeignKeyField(City, backref="city2player")
    player_id = ForeignKeyField(Player, backref="city2player")

    class Meta:
        """Класс Meta."""

        table_name = "city2player"
