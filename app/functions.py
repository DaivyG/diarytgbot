from datetime import datetime, timedelta

async def validate_date_time(date_time_str):
    try:
        event_date = datetime.strptime(date_time_str, '%d.%m.%Y %H:%M')
    except ValueError:
        return False

    now = datetime.now()
    if event_date <= now:
        return False

    return True


def next_day_foo():
    next_day = datetime.now() + timedelta(days=1)
    return next_day.replace(hour=9, minute=0, second=0, microsecond=0).strftime('%d.%m.%Y %H:%M')


def date_to_format(date_of_event, list_of_reminders=None):
    date_of_event = datetime.strptime(date_of_event, '%d.%m.%Y %H:%M')

    if list_of_reminders is None:
        next_day = datetime.now() + timedelta(days=1)
        return {'Сейчас': next_day.replace(hour=9, minute=0, second=0, microsecond=0)}

    dict_of_reminders = {}
    for i in list_of_reminders:
        if i.split()[1][0] == 'ч':
            dict_of_reminders[i] = date_of_event - timedelta(hours=int(i.split()[0]))
        else:
            dict_of_reminders[i] = date_of_event - timedelta(days=int(i.split()[0]))
    dict_of_reminders['Сейчас'] = date_of_event

    return dict_of_reminders

async def get_reminders(event_date):
    now = datetime.now()
    
    event_date = datetime.strptime(event_date, '%d.%m.%Y %H:%M')
    difference = event_date - now

    reminders = []
    if difference.days > 7:
        reminders.append('7 дней')
    if difference.days > 3:
        reminders.append('3 дня')
    if difference.days > 1:
        reminders.append('1 день')
    if difference.total_seconds() // (60 * 60 * 3) >= 3:
        reminders.append('3 часа')
    if difference.total_seconds() // (60 * 60) >= 1:
        reminders.append('1 час')

    return reminders


def format_time(input_str):
    if input_str.endswith('d'):
        days = int(input_str[:-1])
        if days == 1:
            return f"{days} день"
        elif 2 <= days <= 4:
            return f"{days} дня"
        else:
            return f"{days} дней"
    elif input_str.endswith('h'):
        hours = int(input_str[:-1])
        if hours == 1:
            return f"{hours} час"
        elif 2 <= hours <= 4:
            return f"{hours} часа"
        else:
            return f"{hours} часов"
    else:
        return False