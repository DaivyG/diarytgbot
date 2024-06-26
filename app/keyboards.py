from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

'''
Клавиатура для команды старт
'''
initial_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мои напоминания')],
    [KeyboardButton(text='Быстрое создание напоминания')],
    [KeyboardButton(text='Обычное создание напоминания')],
    [KeyboardButton(text='Список событий')]
], resize_keyboard=True, one_time_keyboard=True)


'''
Клавиатура для команды старт для админа
'''
admin_initial_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мои напоминания')],
    [KeyboardButton(text='Быстрое создание напоминания')],
    [KeyboardButton(text='Обычное создание напоминания')],
    [KeyboardButton(text='Список событий')],
    [KeyboardButton(text='Админ панель')]
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
    Клавиатура для просмотра своих событий
    '''
    keyboard = InlineKeyboardBuilder()
    if events == 'У вас нет напоминаний' or events == 'Пользователь не найден':
        keyboard.add(InlineKeyboardButton(text=events, callback_data='None'))
        return keyboard.as_markup()

    for event in events:
        keyboard.add(InlineKeyboardButton(text=str(event[0]), callback_data=f'look_at_my_event-{event[1]}'))

    return keyboard.adjust(2).as_markup()


'''
Клавиатура показывающая возможные действия под выбранным событием
'''
my_events_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить', callback_data='edit_my_event'),
    InlineKeyboardButton(text='Удалить', callback_data='delete_my_event')]
])

'''
Клавиатура после нажатия "Изменить информацию в событии"
'''
edit_my_event_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Текст', callback_data='change_full_text')], 
    [InlineKeyboardButton(text='Дату и время', callback_data='change_datetime')],
    [InlineKeyboardButton(text='Предварительные напоминания', callback_data='change_reminders')],
    [InlineKeyboardButton(text='Цикличность', callback_data='change_frequency')], 
    [InlineKeyboardButton(text='Адресаты', callback_data='add_recipient')], 
    [InlineKeyboardButton(text='Удалить', callback_data='delete_my_event')]
])


async def edit_users_keyboard(users):
    '''
    Клавиатура для редактирования пользователей к событию
    '''
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.add(InlineKeyboardButton(text=str(user[2]), callback_data=f'_add_user-{user[2]}'))
    keyboard.add(InlineKeyboardButton(text='Все пользователи', callback_data='_add_user-all_users'))
    keyboard.add(InlineKeyboardButton(text='Далее', callback_data='_add_user-next_step'))
    return keyboard.adjust(2).as_markup()


async def del_users_keyboard(users):
    '''
    Клавиатура для удаления пользователя из базы данных 
    '''
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.add(InlineKeyboardButton(text=str(user[2]), callback_data=f'del_user-{user[2]}'))
    keyboard.add(InlineKeyboardButton(text='Все пользователи', callback_data='del_user-all_users'))
    keyboard.add(InlineKeyboardButton(text='Далее', callback_data='del_user-next_step'))
    return keyboard.adjust(2).as_markup()


async def get_reminders_keyboard(reminders):
    '''
    Клавиатура для выбора напоминаний
    '''
    keyboard = InlineKeyboardBuilder()

    # Добавляем кнопки для каждого напоминания
    for reminder in reminders:
        keyboard.add(InlineKeyboardButton(text=reminder, callback_data=f'reminders_keyboard-{reminder}'))

    # Добавляем кнопки "Произвольное количество часов" и "Произвольное количество дней" по отдельности
    keyboard.row(InlineKeyboardButton(text='Произвольное количество часов', callback_data='reminders_keyboard-free_h'))
    keyboard.row(InlineKeyboardButton(text='Произвольное количество дней', callback_data='reminders_keyboard-free_d'))

    # Добавляем кнопки "Все напоминания" и "Далее" в один ряд
    keyboard.row(InlineKeyboardButton(text='Все напоминания', callback_data='reminders_keyboard-all_reminders'), InlineKeyboardButton(text='Далее', callback_data='reminders_keyboard-next_step'))

    return keyboard.as_markup()


'''
Клавиатура после создания нового события
'''
my_events_inline_keyboard_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить', callback_data='edit_my_event'),
    InlineKeyboardButton(text='Удалить', callback_data='delete_my_event')],
    [InlineKeyboardButton(text='Напомнить заранее', callback_data='change_reminders')]
])


async def event_keyboard(id_):
    '''
    Клавиатура для кнопки показа всех напоминаний
    '''
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Изменить', callback_data=f'edit_my_event_2-{id_}'))
    keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=f'delete_my_event_2-{id_}'))
    return keyboard.as_markup()