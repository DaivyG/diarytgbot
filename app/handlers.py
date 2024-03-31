from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.functions as func
import app.database as db
import app.keyboards as kb
import asyncio

#!!!!!!!Обязательно сделать проверку ввода даты и обработку ошибок то есть откат действия назад

admins = ['Dayviyo', 'iozephK']
router = Router()
list_of_users = []


@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Приветствую! Что хотите сделать?', reply_markup=[kb.initial_keyboard, kb.admin_initial_keyboard][message.from_user.username in admins])

    data = await db.look_at_db_users()
    if len(data) != 0:
        dict_of_status = {i[1]:i[-1] for i in data}
        username = message.from_user.username
        if username in dict_of_status.keys() and dict_of_status[username] == 'Еще не регистрировался':
            await db.add_chat_id_at_db_users(username, message.chat.id)
            print('Успешно добавлен чат id')
        

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
    recipients = State()


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
    '''
    Сохранение даты и времени
    '''
    if not await func.validate_date_time(message.text):
        await message.answer('Что-то пошло не так.\nВозможно вы ошиблись при вводе формата даты, либо вписали дату, которая уже прошла. Попробуйте еще раз\n"01.01.0001 01:01"')
        await state.set_state(New_event.date_and_time)
        return

    await state.update_data(datetime=message.text)
    await state.set_state(New_event.frequency)
    await message.answer('Выберите цикличность события', reply_markup=kb.frequency_of_event_keyboard)


@router.message(New_event.frequency)
async def usual_creating_third_step(message: Message, state: FSMContext):
    '''
    Сохранение цикличности
    '''
    await state.update_data(frequency=message.text)
    await message.answer('Выберите получателей события', reply_markup=await kb.add_users_keyboard(await db.look_at_db_users()))


@router.callback_query(F.data.split('-')[0] == 'add_user')
async def add_user_at_event_next_step(callback: CallbackQuery, state: FSMContext):
    global list_of_users

    if callback.data.split('-')[1] == 'all_users':
        await callback.answer()
        for i in await db.look_at_db_users():
            list_of_users.append(i[2])

    elif callback.data.split('-')[1] != 'next_step':
        await callback.answer()
        list_of_users.append(callback.data.split('-')[1])
        return

    if not list_of_users:
        await callback.answer()
        await callback.message.edit_text('Вы не выбрали ни одного пользователя', reply_markup=await kb.add_users_keyboard(await db.look_at_db_users()))
        return

    list_of_users = list(set(map(lambda x: x.capitalize(), list_of_users)))
    await callback.answer()
    await callback.message.edit_text(f'Переходим к следующему шагу. Вы выбрали следующих пользователей: {", ".join(list_of_users)}', reply_markup=None)
    await callback.message.answer('Введите описание события')
    await state.set_state(New_event.text_of_event)
    await state.update_data(recipients=list_of_users)

@router.message(New_event.text_of_event)
async def usual_creating_last_step(message: Message, state: FSMContext):
    '''
    Сохранение описания события, чата id и username автора
    '''
    global list_of_users
    await state.update_data(text=message.text, author=message.from_user.username)
    data = await state.get_data()

    try:
        author = data['author']
        text = data['text']
        frequency = data.setdefault('frequency', 'Единично')
        datetime = data.get('datetime')
        recipients = data.get('recipients')

        if recipients is None:
            recipients = await db.username_to_name(message.from_user.username)
            data['recipients'] = [recipients]

        else:
            recipients = [recipient.capitalize() for recipient in data['recipients']]
            recipients = ", ".join(recipients)

        if datetime is None:
            datetime = func.next_day_foo()

        if not await db.create_new_event(data):
            raise Exception
    
        await message.answer(f'''Событие успешно создано со следующими параметрами:
        Username создателя события: {author},
        Описание события: {text},
        Дата и время: {datetime},
        Цикличность повторения: {frequency},
        Получатели: {recipients}''', reply_markup=[kb.initial_keyboard, kb.admin_initial_keyboard][message.from_user.username in admins])



    except Exception as e:
        print(f'Ошибка при создании события: {e}')
        await message.answer(f'Произошла ошибка при создании события. Пожалуйста, повторите попытку.\n{e}')

    finally:
        await state.clear()
        list_of_users.clear()


@router.message(F.text == 'Админ панель')
async def adm_starting(message: Message):
    '''
    Функции админ панели
    '''
    if message.from_user.username in admins:
        await message.answer('На данный момент доступны следующие функции:', reply_markup=kb.admin_second_keyboard)

    else:
        await message.answer('Вам не доступна эта функция')


@router.callback_query(F.data == 'look_in_db')
async def look_at_db(callback: CallbackQuery):
    await callback.answer('Вы выбрали посмотреть пользователей')
    await callback.message.edit_text('На данный момент список пользователей следующий:', reply_markup=await kb.all_users_keyboard(await db.look_at_db_users()))
    await callback.message.answer('Что еще хотите сделать?', reply_markup=[kb.initial_keyboard, kb.admin_initial_keyboard][callback.from_user.username in admins])


class New_user(StatesGroup):
    username = State()
    name = State()


@router.callback_query(F.data == 'add_at_db')
async def add_at_db_first(callback: CallbackQuery, state: FSMContext):
    await state.set_state(New_user.name)
    await callback.answer('Вы выбрали добавить пользователя')
    await callback.message.answer('Пожалуйста, введите имя нового пользователя')


@router.message(New_user.name)
async def add_at_db_last(message: Message, state: FSMContext):
    await state.update_data(name=message.text.lower())
    await message.answer('Теперь введите username пользователя. Начала никнейма должно начинаться с "@".')
    await state.set_state(New_user.username)


@router.message(New_user.username)
async def add_at_db_second(message: Message, state: FSMContext):
    if all(char.isalpha() and char.isascii() for char in message.text) is False and message.text[0] == '@':
        await state.set_state(New_user.username)
        await message.answer('Что-то пошло не так. Проверьте корректность введенного username. Ввод должен начинаться со знака "@".')
        return

    await state.update_data(username=message.text)
    data = await state.get_data()

    try:
        if not await db.add_at_db_users(data):
            raise Exception
        
        await message.answer(f'Сохранение успешно! Пользователь {data["name"].capitalize()} сохранен с никнеймом {data["username"]}', reply_markup=[kb.initial_keyboard, kb.admin_initial_keyboard][message.from_user.username in admins])
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
    '''
    Сохранение имени для удаления пользователя из таблицы users
    '''
    await state.update_data(name=message.text.lower())
    data = await state.get_data()

    try:
        await db.del_from_db_users(data)

        await message.answer(f'Удаление успешно! Пользователь с именем {data["name"].capitalize()} удален', reply_markup=[kb.initial_keyboard, kb.admin_initial_keyboard][message.from_user.username in admins])

    except Exception as e:
        print(f'Ошибка {e}')

    finally:
        await state.clear()


@router.message(F.text == 'Мои напоминания')
async def admin_panel(message: Message):
    data = await db.look_at_db_events(message.from_user.username)
    await message.answer('На данный момент у вас следующие напоминания: ', reply_markup=await kb.look_at_my_events(data))
    await message.answer('При нажатии на любое из напоминаний вам высветиться полная информация о нем', reply_markup=[kb.initial_keyboard, kb.admin_initial_keyboard][message.from_user.username in admins])


@router.callback_query(F.data.split('-')[0] == 'look_at_my_event')
async def select_one_of_events(callback: CallbackQuery):
    global _id
    try:
        await callback.answer()
        info, recipients, frequency = await db.look_at_cur_event(callback.data.split('-')[1])

        unpacked_data = [item for sublist in info for item in sublist]
        unpacked_recipients = [item[0] for item in recipients]

        _id = unpacked_data[0]
        full_text = unpacked_data[1]
        small_text = unpacked_data[2]
        datetime_of_creating = unpacked_data[3]
        author_username = unpacked_data[4]
        datetime_of_event = unpacked_data[5]

        recipients = ', '.join(unpacked_recipients)

        await callback.message.answer(text=f'''Полный текст события: {full_text},
Краткое описание события: {small_text},
Время создания события: {datetime_of_creating},
Время самого события: {datetime_of_event},
Цикличность события: {frequency},
Автор события: {author_username},
Получатели события: {recipients}''', reply_markup=kb.my_events_inline_keyboard)


    except Exception as e:
        await callback.message.answer(text=f'Что-то пошло не так при просмотре базы данных: {e}')


@router.callback_query(F.data == 'save_my_event')
async def save_my_event(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Сохранение прошло успешно!', reply_markup=[kb.initial_keyboard, kb.admin_initial_keyboard][callback.from_user.username in admins]) # ????????????????????????????????


@router.callback_query(F.data == 'edit_my_event')
async def edit_my_event(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(text='Что именно хотите изменить?', reply_markup=kb.edit_my_event_keyboard)


class Edit_event(StatesGroup):
    change_full_text = State()
    change_datetime = State()
    change_frequency = State()
    add_recipient = State()
    delete_recipient = State()
    delete_reminder = State()

@router.callback_query(F.data == 'change_full_text')
async def change_full_text_first(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        await callback.message.answer(text='Введите полный текст для данного события')
        await state.set_state(Edit_event.change_full_text)

    except Exception as e:
        print(f'Что-то пошло не так {e}')
        await callback.message.answer(f'Что-то пошло не так: {e}')

@router.message(Edit_event.change_full_text)
async def change_full_text_last(message: Message, state: FSMContext):
    try:
        await state.update_data(text=message.text)
        data = await state.get_data()
        
        await db.change_full_text(data['text'], _id)

        await message.answer('Изменение прошло успешно!', reply_markup=[kb.initial_keyboard, kb.admin_initial_keyboard][message.from_user.username in admins])
    
    except Exception as e:
        await message.answer(f'Что-то пошло не так: {e}')
    
    finally:
        await state.clear()

@router.callback_query(F.data == 'change_datetime')
async def change_datetime_first(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        await callback.message.answer(text='Введите новые дату и время в соответствии с форматом "01.01.0001 01:01"')
        await state.set_state(Edit_event.change_datetime)

    except Exception as e:
        callback.message.answer(f'Что-то пошло не так {e}')

@router.message(Edit_event.change_datetime)
async def change_datetime_last(message: Message, state: FSMContext):
    try:
        if not await func.validate_date_time(message.text):
            await message.answer('Что-то пошло не так.\nВозможно вы ошиблись при вводе формата даты, либо вписали дату, которая уже прошла. Попробуйте еще раз\n"01.01.0001 01:01"')
            await state.set_state(Edit_event.change_datetime)
            return
        
        await state.update_data(datetime=message.text)
        data = await state.get_data()
        
        if await db.change_datetime(data['datetime'], _id):
            await message.answer('Изменение прошло успешно!', reply_markup=[kb.initial_keyboard, kb.admin_initial_keyboard][message.from_user.username in admins])
            await state.clear()
            return
        
        raise Exception('Ошибка при изменении даты и времени события')

    except Exception as e:
        message.answer(f'Что-то пошло не так: {e}')


@router.callback_query(F.data == 'change_frequency')
async def change_frequency_first(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        await state.set_state(Edit_event.change_frequency)
        await callback.message.answer(text='Пожалуйста, выберите нужную цикличность события', reply_markup=kb.frequency_of_event_keyboard)

    except Exception as e:
        await callback.message.answer(f'Ошибка: {e}')


@router.message(Edit_event.change_frequency)
async def change_frequency_last(message: Message, state: FSMContext):
    try:
        data = await state.update_data(frequency=message.text)

        if await db.change_frequency(data['frequency'], _id):
            await message.answer('Цикличность успешно изменена')
            return
        
        raise Exception('Что-то пошло не так')

    except Exception as e:
        await message.answer(f'Произошла ошибка {e}')

    finally:
        await state.clear()


@router.callback_query(F.data == 'add_recipient')
async def add_recipient_first(callback: CallbackQuery):
    try:
        await callback.answer()
        await callback.message.answer('Пожалуйста, выберите получател(я/ей), котор(ого/ых) хотите добавить', reply_markup=await kb.edit_users_keyboard(await db.look_at_db_users()))

    except Exception as e:
        await callback.message.answer(f'Произошла ошибка {e}')


@router.callback_query(F.data.split('-')[0] == '_add_user')
async def edit_recipients_at_event_second(callback: CallbackQuery, state: FSMContext):
    global list_of_users

    if callback.data.split('-')[1] == 'all_users':
        await callback.answer()
        for i in await db.look_at_db_users():
            list_of_users.append(i[2])

    elif callback.data.split('-')[1] != 'next_step':
        await callback.answer()
        list_of_users.append(callback.data.split('-')[1])
        return

    list_of_users = list(set(map(lambda x: x.capitalize(), list_of_users)))
    await callback.answer()
    await callback.message.edit_text(f'Сохраняем изменения. Вы выбрали следующих пользователей: {", ".join(list_of_users)}', reply_markup=None)
    await state.update_data(recipients=list_of_users)

    try:
        data = await state.get_data()
        if await db.edit_recipients(callback.from_user.username, data['recipients'], _id):
            await callback.message.answer('Изменения успешно сохранены!')
            return

        raise Exception('Ошибка во время добавления получателя')

    except Exception as e:
        await callback.message.answer(f'Что-то пошло не так: {e}')

    finally:
        list_of_users.clear()


@router.callback_query(F.data == 'delete_my_event')
async def delete_reminder(callback: CallbackQuery):
    '''
    Удаление события
    '''
    try:
        await callback.answer()
        if await db.delete_my_event(_id):
            await callback.message.answer('Удаление успешно выполнено', reply_markup=[kb.initial_keyboard, kb.admin_initial_keyboard][callback.from_user.username in admins])
            
    except Exception as e:
        await callback.message.answer(f'Произошла ошибка: {e}')