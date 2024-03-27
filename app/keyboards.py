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


async def look_at_my_events(events):
    '''
    Клавиатура для нажатия на свои события
    '''
    keyboard = InlineKeyboardBuilder()
    for event in events:
        keyboard.add(InlineKeyboardButton(text=str(event[0]), callback_data=f'look_at_my_event-{event[0]}'))

    return keyboard.adjust(2).as_markup()


'''
Клавиатура показывающая возможные действия под выбранным событием
'''
my_events_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить информацию в событии', callback_data='edit_my_event')],
    [InlineKeyboardButton(text='Сохранить событие', callback_data='save_my_event')],
    [InlineKeyboardButton(text='Удалить событие', callback_data='delete_my_event')]
])

'''
Клавиатура после нажатия "Изменить информацию в событии"
'''
edit_my_event_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить текст события', callback_data='change_full_text')], 
    [InlineKeyboardButton(text='Изменить дату и время события', callback_data='change_datetime')],
    [InlineKeyboardButton(text='Изменить цикличность напоминания', callback_data='change_frequency')],
    [InlineKeyboardButton(text='Добавить адресата', callback_data='add_recipient')],
    [InlineKeyboardButton(text='Удалить адресата', callback_data='delete_recipient')],
    [InlineKeyboardButton(text='Удалить напоминание', callback_data='delete_reminder')]
])