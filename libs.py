from datetime import datetime
import sqlite3
import json

usersdb = sqlite3.connect('users.db')
users = usersdb.cursor()
eventsdb = sqlite3.connect('events.db')
events = eventsdb.cursor()


def newUser(uid, fname, lname, uname):
    dtime = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    users.execute(
        f"INSERT OR IGNORE INTO users VALUES (NULL, '{uid}', '{fname}', '{lname}', '{uname}', '{dtime}', '0', '', '', '')")
    usersdb.commit()


# Check if user is admin
def isAdmin(uid):
    users.execute(f"SELECT admin from users WHERE userid = '{uid}' LIMIT 1")
    return users.fetchone()[0]


def setName(uid, name):
    users.execute(f"UPDATE users SET name = '{name}' where userid = '{uid}'")
    usersdb.commit()


def setPhone(uid, phone):
    users.execute(f"UPDATE users SET phone = '{phone}' where userid = '{uid}'")
    usersdb.commit()

def setCategory(uid, category):
    users.execute(f"UPDATE users SET category = '{category}' where userid = '{uid}'")
    usersdb.commit()


def getName(uid):
    users.execute(f"SELECT name from users WHERE userid = '{uid}' LIMIT 1")
    return users.fetchone()[0]


def getPhone(uid):
    users.execute(f"SELECT * from users WHERE userid = '{uid}' LIMIT 1")
    return users.fetchone()[8]


def newEvent(name, date, link, category, price, addition, organizator_name, organizator_phone, place, comments, photos,
             files):
    events.execute(
        f"INSERT OR IGNORE INTO events VALUES (NULL, '{name}', '{datetime.strptime(date, '%d.%m.%y %H:%M')}', '{link}', '{category}', '{price}', '{addition}', '{organizator_name}', '{organizator_phone}', '{place}', '{comments}', '{photos}', '{files}')")
    eventsdb.commit()


def getUsers():
    return users.execute("SELECT * FROM users").fetchall()


def getAdmins():
    return users.execute("SELECT userid FROM users WHERE admin = '1'").fetchall()


def usersVacuum():
    users.execute("VACUUM")
    return True


def removeUser(user_id):
    users.execute(f"DELETE from users where userid = {user_id}")
    usersdb.commit()
    return True


def getEvent(event_id):
    events.execute(f"SELECT * from events WHERE id = '{event_id}' LIMIT 1")
    return events.fetchone()


def removeEvent(event_id):
    events.execute(f"DELETE from events where id = {event_id}")
    eventsdb.commit()
    return True

def updateEvent(event_id, field, value):
    events.execute(f"UPDATE events SET {field} = '{value}' where id = '{event_id}'")
    eventsdb.commit()

def getEventMessage(event, media_count=False):
    message = f'🏆 Новый турнир🏆'
    message += f'\n\n📅 <b>{event[2]}</b>\n📍 <b>{event[9]}</b>'
    message += f"\n\n<b>Присоединяйтесь</b> к турниру - <b>{event[1]}</b> "
    if event[10] != '':
        message += f'[{event[10]}]'
    message += f'\n\n🎖 <b>Категория:</b> {event[4]}.'
    message += f'\n💰 <b>Взнос:</b> {event[5]}₽. '
    if event[6] != '':
        message += f'{event[6]}'
    if event[3] != '':
        message += f'\n\n🔗 Подробности по <i><u><a href="{event[3]}">ссылке</a></u></i>'
    message += f"\n\n👨‍💼 <code>{event[7]}</code>\n"
    message += f"📞 <code>{event[8]}</code>"
    if media_count:
        files_count = 0 if event[11] == "" else len(json.loads(event[11]))
        photos_count = 0 if event[12] == "" else len(json.loads(event[12]))
        message += f"\n\n----------------------------\n<b>Фото:</b> {files_count} фото\n<b>Файл:</b> {photos_count} файл"
    return message


def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, '%d.%m.%y %H:%M')
        return True
    except ValueError:
        return False