from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.functions as func
import app.database as db
import app.keyboards as kb

#!!!!!!!Обязательно сделать проверку ввода даты и обработку ошибок то есть откат действия назад

admins = ['Dayviyo']

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    if message.from_user.username in admins:
        await message.answer('Приветствую! Что хотите сделать?', reply_markup=kb.admin_initial_keyboard)
    else:
        await message.answer('Приветствую! Что хотите сделать?', reply_markup=kb.initial_keyboard)


@router.message(F.text == 'Создать новое напоминание')
async def create_new_event(message: Message):
    await message.answer('Хорошо, выберите способ создания напоминания', reply_markup=kb.second_keyboard)


class New_event(StatesGroup):
    '''
    Класс для обработки новых событий
    '''
    text_of_event = State()
    date_and_time = State()
    frequency = State()
    author = State()


@router.message(F.text == 'Обычное создание')
async def usual_creating_first_step(message: Message, state: FSMContext):
    await state.set_state(New_event.author)
    await message.answer('Введите ваше имя')


@router.message(New_event.author)
async def usual_creating_second_step(message: Message, state: FSMContext):
    await state.update_data(author=message.text)
    await state.set_state(New_event.text_of_event)
    await message.answer('Введите описание события')


@router.message(New_event.text_of_event)
async def usual_creating_third_step(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(New_event.date_and_time)
    await message.answer('Введите дату и время события в формате "01.01.0001 01:01".')


@router.message(New_event.date_and_time)
async def usual_creating_fourh_step(message: Message, state: FSMContext):
    if not await func.validate_date_time(message.text):
        await message.answer('Что-то пошло не так.\nВозможно вы ошиблись при вводе формата даты, либо вписали дату, которая уже прошла. Попробуйте еще раз\n"01.01.0001 01:01"')
        await state.set_state(New_event.date_and_time)
        return
    
    await state.update_data(datetime=message.text)
    await state.set_state(New_event.frequency)
    await message.answer('Выберите цикличность события', reply_markup=kb.frequency_of_event_keyboard)


@router.message(New_event.frequency)
async def usual_creating_last_step(message: Message, state: FSMContext):
    await state.update_data(frequency=message.text, chat_id=message.chat.id)
    data = await state.get_data()

    try:
        await db.create_new_event(data)

        await message.answer(f'''Событие успешно создано со следующими параметрами:
        Имя создателя события: {data["author"]},
        Описание события: {data["text"]},
        Дата и время: {data["datetime"]},
        Цикличность повторения: {data["frequency"]}''')

        await state.clear()

    except Exception as e:
        print(f'Ошибка при создании события: {e}')
        await message.answer('Произошла ошибка при создании события. Пожалуйста, повторите попытку.')

@router.message(F.text == 'Быстрое создание')
async def fast_creating(message: Message):
    pass

@router.message(F.text == 'Админ панель')
async def adm_starting(message: Message):
    await message.answer('На данный момент доступны следующие функции:', reply_markup=kb.admin_second_keyboard)

# @router.message(F.text == 'Мои напоминания')
# async def new_event(message: Message):
#     await message.answer('Все ваши события на данный момент:', reply_markup=await kb.existing_events_keyboard())   #Нужно отсортировать список вывода событий от ближайшего к дальнейшему