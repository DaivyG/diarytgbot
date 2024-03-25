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


@router.message(F.text == 'Быстрое создание')
async def fast_creating_first_step(message: Message, state: FSMContext):
    await state.set_state(New_event.text_of_event)
    await message.answer('Введите описание события')


@router.message(F.text == 'Обычное создание')
async def usual_creating_first_step(message: Message, state: FSMContext):
    await state.set_state(New_event.date_and_time)
    await message.answer('Введите дату и время события в формате "01.01.0001 01:01".')


@router.message(New_event.date_and_time)
async def usual_creating_second_step(message: Message, state: FSMContext):
    if not await func.validate_date_time(message.text):
        await message.answer('Что-то пошло не так.\nВозможно вы ошиблись при вводе формата даты, либо вписали дату, которая уже прошла. Попробуйте еще раз\n"01.01.0001 01:01"')
        await state.set_state(New_event.date_and_time)
        return
    
    await state.update_data(datetime=message.text)
    await state.set_state(New_event.frequency)
    await message.answer('Выберите цикличность события', reply_markup=kb.frequency_of_event_keyboard)


@router.message(New_event.frequency)
async def usual_creating_third_step(message: Message, state: FSMContext):
    await state.update_data(frequency=message.text)
    await state.set_state(New_event.text_of_event)
    await message.answer('Введите описание события')


@router.message(New_event.text_of_event)
async def usual_creating_last_step(message: Message, state: FSMContext):
    await state.update_data(text=message.text, chat_id=message.chat.id, author=message.from_user.username)
    data = await state.get_data()

    try:
        author = data['author']
        text = data['text']
        frequency = data.setdefault('frequency', 'Единично')
        datetime = data.get('datetime')

        if datetime is None:
            datetime = func.next_day_foo()

        await db.create_new_event(data)
        await message.answer(f'''Событие успешно создано со следующими параметрами:
        Имя создателя события: {author},
        Описание события: {text},
        Дата и время: {datetime},
        Цикличность повторения: {frequency}''')

    except Exception as e:
        print(f'Ошибка при создании события: {e}')
        await message.answer('Произошла ошибка при создании события. Пожалуйста, повторите попытку.')

    finally:
        await state.clear()


@router.message(F.text == 'Админ панель')
async def adm_starting(message: Message):
    if message.from_user.username in admins:
        await message.answer('На данный момент доступны следующие функции:', reply_markup=kb.admin_second_keyboard)
    
    else:
        await message.answer('Вам не доступна эта функция')


@router.callback_query(F.data == 'look_in_db')
async def look_at_db(callback: CallbackQuery):
    await callback.answer('Вы выбрали посмотреть пользователей')
    await callback.message.edit_text('На данный момент список пользователей следующий:', reply_markup=await kb.all_users(await db.look_at_db_users()))


class New_user(StatesGroup):
    username = State()
    name = State()


@router.callback_query(F.data == 'add_at_db')
async def add_at_db_first(callback: CallbackQuery, state: FSMContext):
    await state.set_state(New_user.username)
    await callback.answer('Вы выбрали добавить пользователя')
    await callback.message.answer('Пожалуйста, введите username нового пользователя')


@router.message(New_user.username)
async def add_at_db_second(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await state.set_state(New_user.name)
    await message.answer('Теперь введите имя пользователя')


@router.message(New_user.name)
async def add_at_db_last(message: Message, state: FSMContext):
    await state.update_data(name=message.text.lower())
    data = await state.get_data()

    try:
        await db.add_at_db_users(data)

        await message.answer(f'Сохранение успешно! Пользователь {data["name"]} сохранен с никнеймом {data["username"]}')
        print('Пользователь успешно сохранен')

    except Exception as e:
        print(f'Ошибка {e}')

    finally:
        await state.clear()


class Delete_user(StatesGroup):
    name = State()

@router.callback_query(F.data == 'del_from_db')
async def del_from_db_first(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Delete_user.name)
    await callback.answer('Вы выбрали удалить пользователя')
    await callback.message.answer('Пожалуйста, введите имя пользователя, которого хотите удалить')


@router.message(Delete_user.name)
async def del_from_db_last(message: Message, state: FSMContext):
    await state.update_data(name=message.text.lower())
    data = await state.get_data()

    try:
        await db.del_from_db_users(data)

        await message.answer(f'Удаление успешно! Пользователь с именем {data["name"]} удален')

    except Exception as e:
        print(f'Ошибка {e}')

    finally:
        await state.clear()

# @router.message(F.text == 'Мои напоминания')
# async def new_event(message: Message):
#     await message.answer('Все ваши события на данный момент:', reply_markup=await kb.existing_events_keyboard())   #Нужно отсортировать список вывода событий от ближайшего к дальнейшему