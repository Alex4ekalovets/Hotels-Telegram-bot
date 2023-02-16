"""Общий модуль для команд bestdeal, lowprice и highprice.

Functions:
    start_hotels_search:
        Старт поиска отелей по одной из команд bestdeal, lowprice или highprice
    get_city_from_user:
        Получение названия города от пользователя
    select_city:
        Выбор города пользователем из предложенных
    start_calendar:
        Запускает календарь выбора даты заезда/выезда
    next_step_calendar:
        Листает календарь и сохраняет выбранную дату
    check_date:
        Пользователь проверяет дату, подтверждает или меняет
    ask_number_of_hotels:
        Запрашивает количество выводимых отелей
    enter_number_of_hotels:
        Ввод количества отелей пользователем
    select_number_of_hotels:
        Выбор количества отелей пользователем
    ask_number_of_photos:
        Запрашивает количество фотографий отеля
    select_number_of_photos:
        Выбор количества фотографий пользователем
    get_search_results:
        Возвращает пользователю результаты поиска
"""
from datetime import date, timedelta

import telebot
from telebot.types import CallbackQuery, Message

from config_data.config import COMMAND_MESSAGES
from database.api_requests.bestdeal import get_bestdeal_results
from database.api_requests.cities import find_city
from database.api_requests.highprice import get_highprice_results
from database.api_requests.lowprice import get_lowprice_results
from database.history.crud import add_request_to_db
from keyboards.inline import (change_date, clarify_city, number_of_hotels,
                              number_of_photos)
from loader import bot
from states.search_data import UserSearchState
from states.users import Users
from utils.calendar_style import LSTEP, MyStyleCalendar
from utils.city_translator import translate
from utils.logging import logger


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal"])
def start_hotels_search(message: Message) -> None:
    """В ответ на введенную команду поиска запрашивает название города."""
    user = Users(message.from_user.id)
    user.cmd_message = message
    logger.info(f"Command {user.cmd_message.text}", user_id=message.from_user.id)
    bot.set_state(message.from_user.id, UserSearchState.city, message.chat.id)
    user.next_delete_message = bot.send_message(message.from_user.id, "В каком городе найти отель? 🗺").id


@bot.message_handler(func=lambda message: message.text not in COMMAND_MESSAGES, state=UserSearchState.city)
def get_city_from_user(message: Message) -> None:
    """Получает название города от пользователя. Направляет перечень возвращенных сервером городов для уточнения.

    :except ConnectionError: При отсутствии ответа от сервера вызывается исключение
    """
    user = Users.get_user(message.from_user.id)
    user.city = translate(message.text)
    try:
        cities = find_city(user)
        if len(cities) > 0:
            bot.delete_message(message.chat.id, message.message_id)
            bot.delete_message(message.chat.id, user.next_delete_message)
            user.next_delete_message = bot.send_message(
                message.from_user.id, "Выберите город", reply_markup=clarify_city(cities)
            ).id
            bot.set_state(message.from_user.id, UserSearchState.verified_city, message.chat.id)
        else:
            bot.send_message(message.from_user.id, "❗️Город отсутствует в базе Hotels.com. Повторите запрос")
            start_hotels_search(user.cmd_message)
    except ConnectionError as exc:
        logger.error(f"{exc}", user_id=user.user_id)
        bot.send_message(message.chat.id, "Нет ответа от сервера📡. Повторите запрос позже")
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=lambda call: True, state=UserSearchState.verified_city)
def select_city(call: CallbackQuery) -> None:
    """Сохраняет выбранный пользователем город и запрашивает дату заезда."""
    user = Users.get_user(call.from_user.id)
    bot.delete_message(call.message.chat.id, user.next_delete_message)
    if call.data == "again":
        start_hotels_search(user.cmd_message)
        return
    city, user.region_id = call.data.split("#")
    bot.send_message(call.message.chat.id, f"📍Выбран город {city}")
    bot.set_state(call.from_user.id, UserSearchState.checkin_date, call.message.chat.id)
    user.next_delete_message = bot.send_message(call.message.chat.id, "📅Выберите дату заезда").id
    start_calendar(call)


def start_calendar(call: CallbackQuery) -> None:
    """Запускает календарь."""
    user = Users.get_user(call.from_user.id)
    calendar, step = MyStyleCalendar(
        locale="ru",
        min_date=user.check_in_date + timedelta(days=1),
        max_date=user.check_out_date,
        current_date=user.check_in_date + timedelta(days=1),
    ).build()
    bot.send_message(call.message.chat.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=MyStyleCalendar.func())
def next_step_calendar(calendar: CallbackQuery) -> None:
    """Сохраняет дату заезда или выезда, выбранную пользователем."""
    user = Users.get_user(calendar.from_user.id)
    result, key, step = MyStyleCalendar(
        locale="ru",
        min_date=user.check_in_date + timedelta(days=1),
        max_date=user.check_out_date,
    ).process(calendar.data)
    if not result and key:
        bot.edit_message_text(
            f"Выберите {LSTEP[step]}", calendar.message.chat.id, calendar.message.message_id, reply_markup=key
        )
    elif result:
        if bot.get_state(calendar.from_user.id, calendar.message.chat.id) == "UserSearchState:checkin_date":
            current_state = "checkin_date"
            user.check_in_date = result
        else:
            current_state = "checkout_date"
            user.check_out_date = result
        bot.edit_message_text(
            f'Вы выбрали дату {result.strftime("%d.%m.%Y")}',
            calendar.message.chat.id,
            calendar.message.message_id,
            reply_markup=change_date(current_state),
        )
        bot.set_state(calendar.from_user.id, UserSearchState.check_date, calendar.message.chat.id)


@bot.callback_query_handler(func=lambda call: True, state=UserSearchState.check_date)
def check_date(call: CallbackQuery) -> None:
    """Уточняет у пользователя правильность введенной даты, предлагает изменить или продолжить.

    Для команд /lowprice, /highprice запрашивает количество отелей.
    Для команды /bestdeal запрашивает минимальную стоимость за ночь.
    """
    user = Users.get_user(call.from_user.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data == "wrong checkin_date":
        user.check_in_date = date.today() - timedelta(days=1)
        user.check_out_date = None
        bot.set_state(call.from_user.id, UserSearchState.checkin_date, call.message.chat.id)
        start_calendar(call)
    elif call.data == "wrong checkout_date":
        bot.set_state(call.from_user.id, UserSearchState.checkout_date, call.message.chat.id)
        user.check_out_date = user.check_in_date + timedelta(days=28)
        start_calendar(call)
    elif call.data == "checkin_date":
        bot.delete_message(call.message.chat.id, user.next_delete_message)
        user.next_delete_message = bot.send_message(call.message.chat.id, "📅Выберите дату выезда").id
        bot.set_state(call.from_user.id, UserSearchState.checkout_date, call.message.chat.id)
        start_calendar(call)
    elif call.data == "checkout_date":
        bot.delete_message(call.message.chat.id, user.next_delete_message)
        bot.send_message(
            call.message.chat.id,
            f'📅Период проживания: c {user.check_in_date:"%d.%m.%Y"} по {user.check_out_date:"%d.%m.%Y"}',
        )
        if user.current_cmd != "/bestdeal":
            ask_number_of_hotels(user_id=call.from_user.id, chat_id=call.message.chat.id)
        else:
            user.next_delete_message = bot.send_message(
                call.message.chat.id, "🏠Введите минимальную стоимость проживания за ночь"
            ).id
            bot.set_state(call.from_user.id, UserSearchState.min_price, call.message.chat.id)


def ask_number_of_hotels(user_id: int, chat_id: int) -> None:
    """Запрашивает у пользователя количество отелей (результатов поиска)."""
    Users.get_user(user_id).next_delete_message = bot.send_message(
        chat_id, "Выберите количество результатов поиска или введите число от 1 до 10", reply_markup=number_of_hotels()
    ).id
    bot.set_state(user_id, UserSearchState.number_of_hotels, chat_id)


@bot.message_handler(func=lambda message: message.text not in COMMAND_MESSAGES, state=UserSearchState.number_of_hotels)
def enter_number_of_hotels(message: Message) -> None:
    """Получает введенное пользователем количество отелей."""
    user = Users.get_user(message.from_user.id)
    if message.text in (str(n) for n in range(1, 11)):
        user.results_size = int(message.text)
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, user.next_delete_message)
        bot.send_message(message.chat.id, f"🏨Показать результатов: {message.text}")
        ask_number_of_photos(user_id=message.from_user.id, chat_id=message.chat.id)
    else:
        bot.send_message(message.from_user.id, "❗️Неверное количество. Введите число от 1 до 10")


@bot.callback_query_handler(func=lambda call: True, state=UserSearchState.number_of_hotels)
def select_number_of_hotels(call: CallbackQuery) -> None:
    """Получает выбранное пользователем количество отелей."""
    Users.get_user(call.from_user.id).results_size = int(call.data)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, f"🏨Показать результатов: {call.data}")
    ask_number_of_photos(user_id=call.from_user.id, chat_id=call.message.chat.id)


def ask_number_of_photos(user_id: int, chat_id: int) -> None:
    """Запрашивает количество фотографий."""
    bot.send_message(chat_id, "Выберите количество фотографий отеля", reply_markup=number_of_photos())
    bot.set_state(user_id, UserSearchState.number_of_photo, chat_id)


@bot.callback_query_handler(func=lambda call: True, state=UserSearchState.number_of_photo)
def select_number_of_photos(call: CallbackQuery) -> None:
    """Получает выбранное пользователем количество фотографий."""
    user = Users.get_user(call.from_user.id)
    user.number_of_photos = int(call.data)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, f"🌇Показать фотографий отеля: {call.data}")
    bot.delete_state(call.from_user.id, call.message.chat.id)
    get_search_results(chat_id=call.message.chat.id, user_id=call.from_user.id)


def get_search_results(chat_id: int, user_id: int) -> None:
    """Возвращает результаты поиска.

    :except TypeError: Вызывает исключение, если результаты по запросу пользователя отсутствуют
    :except ConnectionError: Вызывает исключение, если соединение с сервером отсутствует
    """
    user = Users.get_user(user_id)
    add_request_to_db(user)
    try:
        if user.current_cmd == "/lowprice":
            user.next_delete_message = bot.send_message(chat_id, "🔍Выполняется поиск самых дешёвых отелей⌛️").id
            results = get_lowprice_results(user)
        elif user.current_cmd == "/highprice":
            user.next_delete_message = bot.send_message(chat_id, "🔍Выполняется поиск самых дорогих отелей⌛️").id
            results = get_highprice_results(user)
        else:
            user.next_delete_message = bot.send_message(chat_id, "🔍Выполняется поиск лучшего предложения⌛️").id
            results, flag = get_bestdeal_results(user)
            if not flag:
                bot.send_message(
                    chat_id,
                    "По вашему запросу ничего не найдено, показаны результаты "
                    "только в соответствии с указанным диапазоном стоимости",
                )
        bot.delete_message(chat_id, user.next_delete_message)
        for result in results:
            if user.number_of_photos != 0:
                bot.send_media_group(
                    user_id,
                    [
                        telebot.types.InputMediaPhoto(photo, caption=result[0], parse_mode="Markdown")
                        if index == 0
                        else telebot.types.InputMediaPhoto(photo)
                        for index, photo in enumerate(result[1])
                    ],
                )
            else:
                bot.send_message(chat_id, result[0], parse_mode="Markdown", disable_web_page_preview=True)
        logger.success(f"Command {user.current_cmd} completed successfully", user_id=user_id)
    except TypeError as exc:
        logger.info(f"{exc}", user_id=user_id)
        bot.send_message(chat_id, "По Вашему запросу ничего не найдено️☹️. Измените параметры поиска")
        bot.delete_message(chat_id, user.next_delete_message)
    except ConnectionError as exc:
        logger.error(f"{exc}", user_id=user_id)
        bot.send_message(chat_id, "Нет ответа от сервера📡. Повторите запрос позже")
        bot.delete_message(chat_id, user.next_delete_message)
