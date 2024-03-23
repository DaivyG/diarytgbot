from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder

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


admin_second_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Посмотреть базу данных')],
    [KeyboardButton(text='Добавить человека в базу данных')],
    [KeyboardButton(text='Удалить человека из базы данных')]
])


# ##сделать вывод списка тех событий которые должны состояться
# events = []

# async def existing_events_keyboard():
#     keyboard = InlineKeyboardBuilder()
#     for event in events:
#         keyboard.add(InlineKeyboardButton(text=event, callback_data='event')) ##Сделать поиск по id
#     return keyboard.adjust(2).as_markup()