"""Модуль игры Города (по команде game).

Functions:
    start_game_question:
        Предлагает пользователю начать игру
    text_to_markdown_style:
        Преобразует текст в стиль MarkdownV2
    get_top10_markdownv2:
        Получает текст с ТОП10 игроков в стиле MarkdownV2
    send_game_answer:
        Отвечает на команду пользователя game
    get_user_name:
        Получает от пользователя игровое имя
    change_user_name:
        Изменяет игровое имя пользователя
    select_menu_item:
        Выбор пункта меню пользователем
    play_game:
        Продолжает или останавливает игру
    check_players_city:
        Проверяет город, введенный пользователем
    get_next_city:
        Получает следующий город
    get_last_letter:
        Получает последнюю букву последнего города
"""
from typing import Optional

from telebot.types import CallbackQuery, Message, ReplyKeyboardRemove

from config_data.config import COMMAND_MESSAGES
from database.game_cities import crud
from keyboards.inline.game_menu import game_menu
from keyboards.reply.quit_game import quit_game
from loader import bot
from states.search_data import UserSearchState


def start_game_question(chat_id: int, user_id: int) -> None:
    """Выводит игровое меню."""
    bot.send_message(chat_id, 'Готовы начать игру "Города"?', reply_markup=game_menu())
    bot.set_state(user_id, UserSearchState.game_cities, chat_id)


def text_to_markdown_style(text: str) -> str:
    """Преобразует текст в стиль MarkdownV2."""
    markdown_text = []
    for letter in text:
        if letter in {"_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"}:
            letter = "\\" + letter
        markdown_text.append(letter)
    return "".join(markdown_text)


def get_top10_markdownv2(user_id: int) -> str:
    """Формирует топ 10 игроков."""
    top_players, current_player, current_player_place = crud.get_top10_info(player_id=user_id)
    top_10_text = ["ТОП 10 ЛУЧШИХ ИГРОКОВ\n"]
    max_name_size = 19
    places = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for player_place, player in enumerate(top_players):
        separator = "👉" if player.player_id == user_id else "  "
        spaces = " " * (max_name_size + 1 - len(player.nickname))
        top_10_text.append(f"`{places[player_place]}{separator}{player.nickname}{spaces}{str(player.max_scores)}\n`")
    if current_player_place > 10:
        place = str(current_player_place)
        spaces = " " * (max_name_size + 3 - len(current_player.nickname) - len(place))
        empty_string = text_to_markdown_style("...\n")
        top_10_text.append(f"{empty_string}"
                           f"`{place}👉{current_player.nickname}{spaces}{str(current_player.max_scores)}\n`")
    return "".join(top_10_text)


@bot.message_handler(commands=["game"])
def send_game_answer(message: Message) -> None:
    """Запрашивает игровое имя при первом запуске или выводит игровое меню."""
    if crud.get_player(player_id=message.from_user.id):
        start_game_question(chat_id=message.chat.id, user_id=message.from_user.id)
    else:
        bot.send_message(message.chat.id, "Введите свое игровое имя:")
        bot.set_state(message.from_user.id, UserSearchState.game_name, message.chat.id)


@bot.message_handler(func=lambda message: message.text not in COMMAND_MESSAGES, state=UserSearchState.game_name)
def get_user_name(message: Message) -> None:
    """Создает игрока в БД и выводит игровое меню."""
    max_player_name = 19
    player_name = (
        message.text[0: max_player_name - 3] + "..." if len(message.text) > max_player_name else message.text
    )
    crud.create_new_player(player_id=message.from_user.id, nickname=text_to_markdown_style(player_name))
    start_game_question(chat_id=message.chat.id, user_id=message.from_user.id)


@bot.message_handler(func=lambda message: message.text not in COMMAND_MESSAGES, state=UserSearchState.game_change_name)
def change_user_name(message: Message) -> None:
    """Изменяет игровое имя."""
    crud.change_player_name(player_id=message.from_user.id, nickname=message.text)
    start_game_question(chat_id=message.chat.id, user_id=message.from_user.id)


@bot.callback_query_handler(func=lambda call: True, state=UserSearchState.game_cities)
def select_menu_item(call: CallbackQuery) -> None:
    """Отвечает на выбор пользователем пункта игрового меню."""
    if call.data == "start":
        bot.send_message(call.message.chat.id, "Вы начинаете. Введите город", reply_markup=quit_game())
        bot.set_state(call.from_user.id, UserSearchState.game_cities_start, call.message.chat.id)
    elif call.data == "change_name":
        bot.send_message(call.message.chat.id, "Введите новое игровое имя:")
        bot.set_state(call.from_user.id, UserSearchState.game_change_name, call.message.chat.id)
    elif call.data == "top":
        bot.send_message(call.message.chat.id, get_top10_markdownv2(call.from_user.id), parse_mode="MarkdownV2")


@bot.message_handler(
    func=lambda message: message.text not in COMMAND_MESSAGES, state=UserSearchState.game_cities_start
)
def play_game(message: Message) -> None:
    """Продолжает или завершает игру с выводом и сохранением результата."""
    if message.text == "🏳️Сдаюсь":
        scores = crud.save_max_player_scores(player_id=message.from_user.id)
        bot.send_message(message.chat.id, f"Вы набрали {scores} очков", reply_markup=ReplyKeyboardRemove())
        crud.delete_played_cities_from_db(player_id=message.from_user.id)
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(
            message.chat.id,
            check_players_city(message.from_user.id, message.text),
            parse_mode="Markdown",
            reply_markup=quit_game(),
        )


def check_players_city(player_id: int, city: str) -> str:
    """Проверяет введенный пользователем город и возвращает следующий город."""
    first_letter = get_last_letter(player_id)
    if city[0] != first_letter and first_letter is not None:
        return f"Введите город на букву {first_letter}"
    elif not crud.find_city_in_db(city=city):
        return "Такого города не существует"
    elif crud.find_in_played_cities(player_id=player_id, city=city):
        return "Этот город уже был"
    else:
        crud.add_played_city_to_db(player_id=player_id, city=city)
        return get_next_city(player_id=player_id)


def get_next_city(player_id: int) -> str:
    """Получает город на последнюю букву предыдущего города из несыгранных или сообщает о победе игрока."""
    first_letter = get_last_letter(player_id=player_id)
    city = crud.get_city_from_db(player_id=player_id, first_letter=first_letter)
    if city:
        last_letter = get_last_letter(player_id=player_id)
        return city + f"Вам на {last_letter}"
    else:
        crud.save_max_player_scores(player_id=player_id, win_scores=500)
        crud.delete_played_cities_from_db(player_id=player_id)
        return f"Я больше не знаю городов на букву {first_letter}. Вы выиграли"


def get_last_letter(player_id: int) -> Optional[str]:
    """Получает последнюю букву последнего города."""
    city = crud.get_last_city(player_id)
    if city:
        last_letter = city[-1].upper()
        if last_letter in "ЪЬ":
            last_letter = city[-2].upper()
        return last_letter
    return None
