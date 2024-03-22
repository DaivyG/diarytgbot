from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder

initial_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать новое напоминание')],
    [KeyboardButton(text='Мои напоминания')]
], resize_keyboard=True)



# ##сделать вывод списка тех событий которфе должны состояться
# events = []

# async def existing_events_keyboard():
#     keyboard = InlineKeyboardBuilder()
#     for event in events:
#         keyboard.add(InlineKeyboardButton(text=event, callback_data='event')) ##Сделать поиск по id
#     return keyboard.adjust(2).as_markup()
