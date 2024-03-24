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
    
    
async def date_to_format(event_date):
    now = datetime.now()

    if not event_date:
        next_day = now + timedelta(days=1)
        return [next_day.replace(hour=9, minute=0, second=0, microsecond=0).strftime('%d.%m.%Y %H:%M')]

    event_date = datetime.strptime(event_date, '%d.%m.%Y %H:%M')
    difference = event_date - now

    reminders = []
    if difference.days >= 7:
        reminders.append(event_date - timedelta(days=7))
    if difference.days >= 3:
        reminders.append(event_date - timedelta(days=3))
    if difference.days >= 1:
        reminders.append(event_date - timedelta(days=1))
    reminders.append(event_date - timedelta(hours=1))

    return reminders