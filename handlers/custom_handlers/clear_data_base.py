"""Модуль для очистки баз данных History и Game_cities по команде clear.

Functions:
    ask_password: Запрашивает пароль администратора
    get_password: Получает и проверяет пароль
    clear_db: Очищает БД
"""
from telebot.types import Message

from config_data.config import ADMIN_ID, ADMIN_PASSWORD
from database.game_cities.model import City2Player, Player, db_game
from database.history.model import Request, Result, User, db
from loader import bot
from states.search_data import UserSearchState
from utils.logging import logger


@bot.message_handler(func=lambda message: message.from_user.id == int(ADMIN_ID), commands=["clear"])
def ask_password(message: Message) -> None:
    """Запрашивает пароль администратора при совпадении Telegram id с id администратора."""
    bot.send_message(message.chat.id, "Введите пароль администратора")
    bot.set_state(message.from_user.id, UserSearchState.get_password, message.chat.id)


@bot.message_handler(state=UserSearchState.get_password)
def get_password(message: Message) -> None:
    """Получает пароль и спрашивает, какую БД очистить."""
    if message.text == ADMIN_PASSWORD:
        bot.send_message(message.chat.id, "Какую БД очистить? (1 - История, 2 - Игровая статистика, 3 - все)")
        bot.set_state(message.from_user.id, UserSearchState.choice_db, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Неверный пароль")
        bot.delete_state(message.from_user.id, message.chat.id)
        ask_password(message)


@bot.message_handler(state=UserSearchState.choice_db)
def clear_db(message: Message) -> None:
    """В соответствии с выбором администратора очищает соответствующую базу данных."""
    if message.text == "1":
        db.drop_tables([User, Result, Request], safe=True)
        db.create_tables([User, Result, Request], safe=True)
        bot.send_message(message.chat.id, "БД с историей запросов пользователей очищена")
        logger.info("Cleared db History", user_id=message.from_user.id)
    elif message.text == "2":
        db_game.drop_tables([Player, City2Player])
        db_game.create_tables([Player, City2Player], safe=True)
        bot.send_message(message.chat.id, "БД с игровой статистикой пользователей очищена")
        logger.info("Cleared db Game", user_id=message.from_user.id)
    elif message.text == "3":
        db.drop_tables([User, Result, Request], safe=True)
        db.create_tables([User, Result, Request], safe=True)
        db_game.drop_tables([Player, City2Player])
        db_game.create_tables([Player, City2Player], safe=True)
        bot.send_message(
            message.chat.id, "Базы данных с историей запросов и с игровой статистикой пользователей очищены"
        )
        logger.info("Cleared db Game and History", user_id=message.from_user.id)
    else:
        bot.send_message(message.chat.id, "Неправильный ввод, повторите команду /clear")
    bot.delete_state(message.from_user.id, message.chat.id)
