from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


import app.database as db

initial_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать новое напоминание')],
    [KeyboardButton(text='Мои напоминания')]
], resize_keyboard=True, one_time_keyboard=True)

admin_initial_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать новое напоминание')],
    [KeyboardButton(text='Мои напоминания')],
    [KeyboardButton(text='Админ панель')]
], resize_keyboard=True, one_time_keyboard=True)


second_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Быстрое создание')],
    [KeyboardButton(text='Обычное создание')]
], resize_keyboard=True, one_time_keyboard=True)


frequency_of_event_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Единично')],
    [KeyboardButton(text='Ежедневно'), KeyboardButton(text='Еженедельно')],
    [KeyboardButton(text='Ежемесячно'), KeyboardButton(text='Ежегодно')]
], resize_keyboard=True, one_time_keyboard=True)


admin_second_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Посмотреть базу данных пользователей', callback_data='look_in_db')],
    [InlineKeyboardButton(text='Добавить человека в базу данных пользователей', callback_data='add_at_db')],
    [InlineKeyboardButton(text='Удалить человека из базы данных пользователей', callback_data='del_from_db')]
], resize_keyboard=True)


async def all_users(users):
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.add(InlineKeyboardButton(text=str(user[2]), callback_data=f'user-{user[2]}'))
    return keyboard.adjust(2).as_markup()


# async def add_user(users):
#     keyboard = InlineKeyboardBuilder()
#     for user in users:
#         keyboard.add(InlineKeyboardButton(text=str(user[1]), callback_data=f'user-{user[2]}'))
#     return keyboard.adjust(2).as_markup()



# ##сделать вывод списка тех событий которые должны состояться
# events = []

# async def existing_events_keyboard():
#     keyboard = InlineKeyboardBuilder()
#     for event in events:
#         keyboard.add(InlineKeyboardButton(text=event, callback_data='event')) ##Сделать поиск по id
#     return keyboard.adjust(2).as_markup()