"""Модуль, обрабатывающий команду пользователя history для вывода истории запросов.

Functions:
    send_history_answer: В ответ на команду history выводит историю запросов пользователя
    history_request_action: Выводит результаты поиска отелей или повторяет запрос
"""

from telebot.types import CallbackQuery, Message

from database.history.crud import get_requests_from_db, get_results_from_db
from handlers.custom_handlers.common_search_handlers import get_search_results
from keyboards.inline.history_request_action import request_action
from loader import bot
from states.search_data import UserSearchState
from states.users import Users
from utils.logging import logger


@bot.message_handler(commands=["history"])
def send_history_answer(message: Message) -> None:
    """Выводит историю запросов пользователя."""
    logger.info(f"Command {message.text}", user_id=message.from_user.id)
    requests = get_requests_from_db(message.from_user.id)
    for request in requests:
        text = (
            f"{request.command}\n"
            f'{request.created_time.strftime("%Y-%m-%d %H:%M:%S")}\n'
            f"Город: {request.city}\n"
            f"Даты: {request.check_in_date} - {request.check_out_date}\n"
        )
        if request.command == "/bestdeal":
            additional_text = (
                f"Цены, $: "
                f"{request.min_price} - {request.max_price}\n"
                f"Расстояние, миль: "
                f"{request.min_distance} - {request.max_distance}"
            )
            text += additional_text
        bot.send_message(message.chat.id, text, reply_markup=request_action(request.id))
    bot.set_state(message.from_user.id, UserSearchState.history_request_action, message.chat.id)


@bot.callback_query_handler(func=lambda call: True, state=UserSearchState.history_request_action)
def history_request_action(call: CallbackQuery) -> None:
    """Повторяет запрос пользователя или выводит результаты поиска по запросу."""
    action, request_id = call.data.split()
    if action == "repeat":
        user = Users(call.from_user.id)
        request = get_requests_from_db(user.user_id, request_id=int(request_id))
        user.current_cmd = request.command
        user.region_id = request.region_id
        user.city = request.city
        user.results_size = request.results_size
        user.number_of_photos = request.number_of_photos
        user.min_price = request.min_price
        user.max_price = request.max_price
        user.check_in_date = request.check_in_date
        user.check_out_date = request.check_out_date
        user.min_distance = request.min_distance
        user.max_distance = request.max_distance
        get_search_results(chat_id=call.message.chat.id, user_id=call.from_user.id)
    else:
        results = get_results_from_db(call.from_user.id, request_id)
        for result in results:
            text = (
                f"{result.name}\n"
                f"Расстояние, миль: {result.distance}\n"
                f"Цена: {result.price}\n"
                f"Общая стоимость: {result.total}"
            )
            bot.send_message(call.message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)
