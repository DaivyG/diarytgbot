from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

'''
Клавиатура для команды старт
'''
initial_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать новое напоминание')],
    [KeyboardButton(text='Мои напоминания')]
], resize_keyboard=True, one_time_keyboard=True)


'''
Клавиатура для команды старт для админа
'''
admin_initial_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать новое напоминание')],
    [KeyboardButton(text='Мои напоминания')],
    [KeyboardButton(text='Админ панель')]
], resize_keyboard=True, one_time_keyboard=True)


'''
Клавиатура после нажатия на "создать новое напоминание"
'''
second_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Быстрое создание')],
    [KeyboardButton(text='Обычное создание')]
], resize_keyboard=True, one_time_keyboard=True)


'''
Клавиатура для выбора цикличности
'''
frequency_of_event_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Единично')],
    [KeyboardButton(text='Ежедневно'), KeyboardButton(text='Еженедельно')],
    [KeyboardButton(text='Ежемесячно'), KeyboardButton(text='Ежегодно')]
], resize_keyboard=True, one_time_keyboard=True)


'''
Клавиатура для админ панели
'''
admin_second_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Посмотреть базу данных пользователей', callback_data='look_in_db')],
    [InlineKeyboardButton(text='Добавить человека в базу данных пользователей', callback_data='add_at_db')],
    [InlineKeyboardButton(text='Удалить человека из базы данных пользователей', callback_data='del_from_db')]
], resize_keyboard=True)


async def all_users_keyboard(users):
    '''
    Клавиатура для вывода "Посмотреть базу данных пользователей"
    '''
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.add(InlineKeyboardButton(text=str(user[2]), callback_data=f'non_clickable'))
    return keyboard.adjust(2).as_markup()


async def add_users_keyboard(users):
    '''
    Клавиатура для добавления пользователей в напоминание "Добавить пользователя в базу данных"
    '''
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.add(InlineKeyboardButton(text=str(user[2]), callback_data=f'add_user-{user[2]}'))
    keyboard.add(InlineKeyboardButton(text='Все пользователи', callback_data='add_user-all_users'))
    keyboard.add(InlineKeyboardButton(text='Далее', callback_data='add_user-next_step'))
    return keyboard.adjust(2).as_markup()


# ##сделать вывод списка тех событий которые должны состояться
# events = []

# async def existing_events_keyboard():
#     keyboard = InlineKeyboardBuilder()
#     for event in events:
#         keyboard.add(InlineKeyboardButton(text=event, callback_data='event')) ##Сделать поиск по id
#     return keyboard.adjust(2).as_markup()