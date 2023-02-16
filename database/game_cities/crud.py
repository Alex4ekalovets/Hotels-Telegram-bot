"""Модуль для взаимодействия с базой данных игровой статистики игры Города.

Functions:
    get_city_from_db: Получает город из БД по первой букве из несыгранных
    save_max_player_scores: Сохраняет рекорд игрока и возвращает текущее количество очков
    get_top10_info: Возвращает ТОП10 игроков и место текущего игрока
    add_played_city_to_db: Добавляет сыгранный город в БД
    find_city_in_db: Находит город в БД
    find_in_played_cities: Находит город в сыгранных городах
    delete_played_cities_from_db: Удаляет все сыгранных города для данного игрока
    get_player: Проверяет наличие игрока в БД
    create_new_player: Создает нового игрока
    change_player_name: Изменяет игровое имя пользователя
    get_last_city: Получает название последнего сыгранного города
"""

from typing import Optional, Tuple

import peewee

from database.game_cities.model import City, City2Player, Player, db_game


def get_city_from_db(player_id: int, first_letter: str) -> Optional[str]:
    """Получает из БД случайный город по первой букве из несыгранных.

    :param player_id: Telegram id пользователя
    :param first_letter: Первая буква города, который необходимо вернуть
    :return: Случайный город со ссылкой на google maps или None
    """
    with db_game.atomic():
        player = Player.get(player_id=player_id)
        current_city = City2Player.alias()
        player_cities = current_city.select().where(current_city.player_id == player.id).alias("player_cities")
        random_city = (
            City.select()
            .join(player_cities, peewee.JOIN.LEFT_OUTER, on=(City.id == player_cities.c.city_id))
            .where(City.city.startswith(first_letter))
            .where(player_cities.c.player_id.is_null(True))
            .order_by(peewee.fn.Random())
            .get_or_none()
        )
    if random_city:
        add_played_city_to_db(player_id, random_city.city)
        map_link = f"https://www.google.com/maps/@{random_city.lat},{random_city.lng},12z"
        return f"[{random_city.city}]({map_link})\n"
    return None


def save_max_player_scores(player_id: int, win_scores: int = 0) -> int:
    """Сохраняет максимальное количество очков в БД и выводит набранные очки в текущей игре.

    :param player_id: Telegram id пользователя
    :param win_scores: Количество очков, которое дополнительно добавляется, если пользователь выиграл
    :return: Количество очков пользователя в текущей игре
    """
    with db_game.atomic():
        player = Player.get(player_id=player_id)
        scores = player.city2player.count() + win_scores
        player.max_scores = max(player.max_scores, scores)
        player.save()
    return scores


def get_top10_info(player_id: int) -> Tuple:
    """Возвращает ТОП10 игроков, Telegram-id текущего игрока и место текущего игрока.

    :param player_id: Telegram id пользователя
    :return: Кортеж (ТОП10 игроков, Telegram-id текущего игрока, место текущего игрока)
    """
    with db_game.atomic():
        top_10 = Player.select().order_by(Player.max_scores.desc(), Player.id).limit(10)
        player = Player.get(player_id=player_id)
        count_place = (
            Player.select()
            .where(
                (Player.max_scores > player.max_scores) | (
                    (Player.max_scores == player.max_scores) & (Player.id < player.id)
                )
            )
            .count()
        )
        return top_10, player, count_place


def add_played_city_to_db(player_id: int, city: str) -> None:
    """Добавляет сыгранный город в БД для текущего игрока.

    :param player_id: Telegram id пользователя
    :param city: Название города
    """
    with db_game.atomic():
        found_cities = City.select().where(City.city == city)
        player = Player.get(player_id=player_id)
        for found_city in found_cities:
            City2Player.create(city_id=found_city, player_id=player)


def find_city_in_db(city: str) -> bool:
    """Ищет город в БД.

    :param city: Название города
    :return: True, если город найден, иначе False
    """
    with db_game.atomic():
        found_cities = City.select().where(City.city == city).get_or_none()
    return True if found_cities else False


def find_in_played_cities(player_id: int, city: str) -> bool:
    """Ищет город в БД сыгранных городов для текущего пользователя.

    :param player_id: Telegram id пользователя
    :param city: Название города
    :return: True, если город найден, иначе False
    """
    with db_game.atomic():
        found_city = (
            City2Player.select()
            .join(City)
            .switch(City2Player)
            .join(Player)
            .where(Player.player_id == player_id)
            .where(City.city == city)
            .get_or_none()
        )
    return True if found_city else False


def delete_played_cities_from_db(player_id: int) -> None:
    """Удаляет все сыгранные города текущего пользователя.

    :param player_id: Telegram id пользователя
    """
    with db_game.atomic():
        player = Player.get(player_id=player_id)
        City2Player.delete().where(City2Player.player_id == player.id).execute()


def get_player(player_id: int) -> bool:
    """Ищет текущего игрока в БД игры.

    :param player_id: Telegram id пользователя
    :return: True, пользователь найден, иначе False
    """
    with db_game.atomic():
        player = Player.get_or_none(player_id=player_id)
    return True if player else False


def create_new_player(player_id: int, nickname: str) -> None:
    """Создает нового игрока в БД игры.

    :param player_id: Telegram id пользователя
    :param nickname: Игровое имя пользователя
    """
    with db_game.atomic():
        Player.create(player_id=player_id, nickname=nickname, max_scores=0)


def change_player_name(player_id: int, nickname: str) -> None:
    """Изменяет имя игрока.

    :param player_id: Telegram id пользователя
    :param nickname: Игровое имя пользователя
    """
    with db_game.atomic():
        player = Player.get(player_id=player_id)
        player.nickname = nickname
        player.save()


def get_last_city(player_id: int) -> Optional[str]:
    """Ищет последний сыгранный город.

    :param player_id: Telegram id пользователя
    :return: Название города или None, если еще нет сыгранных городов
    """
    with db_game.atomic():
        player = Player.get(player_id=player_id)
        last_city = (
            City.select()
            .join(City2Player)
            .where(City2Player.player_id == player.id)
            .order_by(City2Player.id.desc())
            .get_or_none()
        )
    if last_city:
        return last_city.city
    return None
