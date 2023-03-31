import math
import sqlite3
from datetime import datetime

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

eventsdb = sqlite3.connect('events.db')
events = eventsdb.cursor()

# START BUTTON
suggest = KeyboardButton('Предлагать турнир 💬')
tournaments = KeyboardButton('Турниры 🏓')
set_category = KeyboardButton('Установить категорию ⚙️')
interval_search = KeyboardButton('Поиск по интервалам 🔍')

start = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add(interval_search).add(suggest, tournaments, set_category)
start_a = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add(interval_search).add(suggest, tournaments, set_category)

cancelButton = InlineKeyboardMarkup(row_width=2).insert(InlineKeyboardButton("⛔️ Отменить", callback_data='cancel'))

continueButton = InlineKeyboardMarkup(row_width=2)
continueButton.insert(InlineKeyboardButton("⛔️ Отменить", callback_data='cancel'))
continueButton.insert(InlineKeyboardButton("Продолжить ➡️", callback_data='cont'))

continueOrDeletePhotos = InlineKeyboardMarkup(row_width=2)
continueOrDeletePhotos.insert(InlineKeyboardButton("⛔️ Отменить", callback_data='cancel'))
continueOrDeletePhotos.insert(InlineKeyboardButton("Удалить все фото 🗑", callback_data='deletePhotos'))
continueOrDeletePhotos.insert(InlineKeyboardButton("Продолжить ➡️", callback_data='cont'))

continueOrDeleteFiles = InlineKeyboardMarkup(row_width=2)
continueOrDeleteFiles.insert(InlineKeyboardButton("⛔️ Отменить", callback_data='cancel'))
continueOrDeleteFiles.insert(InlineKeyboardButton("Удалить все файлы 🗑", callback_data='deleteFiles'))
continueOrDeleteFiles.insert(InlineKeyboardButton("Продолжить ➡️", callback_data='cont'))

confirmButton = InlineKeyboardMarkup(row_width=2)
confirmButton.insert(InlineKeyboardButton("✅ Отправить", callback_data='send')).insert(
    InlineKeyboardButton("⛔️ Отменить", callback_data='cancel'))


def getBackButton(event_id):
    backButton = InlineKeyboardMarkup(row_width=2)
    backButton.add(InlineKeyboardButton("⬅ Назад", callback_data=f'event|{str(event_id)}'))
    return backButton

def getEditEventButton(event_id):
    editEventButton = InlineKeyboardMarkup(row_width=2)
    editEventButton.insert(InlineKeyboardButton("Название", callback_data=f'editField|name|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Дата", callback_data=f'editField|date|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Ссылка", callback_data=f'editField|link|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Категория", callback_data=f'editField|category|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Взнос", callback_data=f'editField|price|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Что входит", callback_data=f'editField|insertition|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Организатор", callback_data=f'editField|organizer_name|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Телефон организатора", callback_data=f'editField|organizer_phone|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Место проведения", callback_data=f'editField|place|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Комментарии", callback_data=f'editField|comments|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Фото", callback_data=f'editField|photos|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("Файлы", callback_data=f'editField|files|{str(event_id)}'))
    editEventButton.insert(InlineKeyboardButton("⬅ Назад", callback_data=f'event|{str(event_id)}'))
    return editEventButton

def getAdminEventButton(page, event_id):
    getAdminEventButton = InlineKeyboardMarkup(row_width=4)
    getAdminEventButton.insert(InlineKeyboardButton("❌ Удалить", callback_data=f'confirmDeleteEvent|{str(event_id)}'))
    getAdminEventButton.insert(InlineKeyboardButton("◀️ Назад", callback_data=f'getEvents|{str(page)}'))
    getAdminEventButton.add(InlineKeyboardButton("✅ Публикировать", callback_data=f'confirmPublicateEvent|{str(event_id)}'))
    getAdminEventButton.insert(InlineKeyboardButton("✏️ Редактировать", callback_data=f'editEvent|{str(event_id)}'))
    getAdminEventButton.insert(InlineKeyboardButton("🖼 Фото", callback_data=f'getMedia|photos|{str(event_id)}'))
    getAdminEventButton.insert(InlineKeyboardButton("📁 Файлы", callback_data=f'getMedia|files|{str(event_id)}'))
    return getAdminEventButton
def getUserEventButton(page, event_id):
    getUserEventButton = InlineKeyboardMarkup(row_width=4)
    getUserEventButton.insert(InlineKeyboardButton("◀️ Назад", callback_data=f'getEvents|{str(page)}'))
    getUserEventButton.insert(InlineKeyboardButton("🖼 Фото", callback_data=f'getMedia|photos|{str(event_id)}'))
    getUserEventButton.insert(InlineKeyboardButton("📁 Файлы", callback_data=f'getMedia|files|{str(event_id)}'))
    return getUserEventButton


def confirmDelete(event_id):
    confirmButton = InlineKeyboardMarkup(row_width=4)
    confirmButton.insert(InlineKeyboardButton("❌ Удалить", callback_data=f'deleteEvent|{str(event_id)}'))
    confirmButton.insert(InlineKeyboardButton("✅ Оставить", callback_data=f'event|{str(event_id)}'))
    return confirmButton


def confirmPublicate(event_id):
    confirmButton = InlineKeyboardMarkup(row_width=4)
    confirmButton.insert(InlineKeyboardButton("🗞 Публикировать", callback_data=f'publicateEvent|{str(event_id)}'))
    confirmButton.insert(InlineKeyboardButton("🖋 Переписать", callback_data=f'rewriteEvent|{str(event_id)}'))
    confirmButton.insert(InlineKeyboardButton("✅ Оставить", callback_data=f'event|{str(event_id)}'))
    return confirmButton

def confirmPublicateRewrittenPost(event_id):
    confirmButton = InlineKeyboardMarkup(row_width=4)
    confirmButton.insert(InlineKeyboardButton("🗞 Публикировать переписанный пост", callback_data=f'publicateEvent|{str(event_id)}'))
    confirmButton.add(InlineKeyboardButton("✅ Оставить", callback_data=f'event|{str(event_id)}'))
    return confirmButton

def getEvents(page, perpage=9, identificator='getEvents', date1=False, date2=False):
    if date1 and date2:
        perpage = 20
    pp = perpage + 1
    mp = perpage - 1
    offset = (page - 1) * perpage

    if date1 and date2:
        date1_str = datetime.strptime(date1, '%d.%m.%y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
        date2_str = datetime.strptime(date2, '%d.%m.%y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
        maxpage = math.ceil(events.execute(f"SELECT COUNT(*) from events WHERE date BETWEEN '{date1_str}' AND '{date2_str}'").fetchone()[0] / perpage)
        print(f"SELECT COUNT(*) from events WHERE date BETWEEN '{date1_str}' AND '{date2_str}'")
        results = events.execute(f"SELECT * from events WHERE date BETWEEN '{date1_str}' AND '{date2_str}' LIMIT {offset}, {pp}").fetchall()
    else:
        maxpage = math.ceil(events.execute('SELECT COUNT(*) from events').fetchone()[0] / perpage)
        results = events.execute(f'SELECT * from events LIMIT {offset}, {pp}').fetchall()

    count = len(results)
    if count == 0:
        pass
    key = 0

    events_kb = InlineKeyboardMarkup(row_width=3)
    k = 0
    for i in results:
        if k % 3 == 0:
            events_kb.add(InlineKeyboardButton(f"{i[1]}", callback_data='event|{}'.format(i[0])))
        else:
            events_kb.insert(InlineKeyboardButton(f"{i[1]}", callback_data='event|{}'.format(i[0])))
        k += 1
        if key == mp:
            break
        key += 1

    pagination = []
    pp = perpage + 1
    if page > 2:
        pagination.append(InlineKeyboardButton('1 ...', callback_data=f'{identificator}|1'))
        pagination.append(InlineKeyboardButton('<<', callback_data=f'{identificator}|{page - 1}'))
    elif page > 1:
        pagination.append(InlineKeyboardButton('<<', callback_data=f'{identificator}|{page - 1}'))
    pagination.append(InlineKeyboardButton('• {} •'.format(page), callback_data='_'))
    if count == pp:
        pagination.append(InlineKeyboardButton('>>', callback_data=f'{identificator}|{page + 1}'))
    if page < (maxpage - 1):
        pagination.append(
            InlineKeyboardButton('...{}'.format(maxpage), callback_data=f'{identificator}|{maxpage}'))
    events_kb.row(*pagination)
    return events_kb
