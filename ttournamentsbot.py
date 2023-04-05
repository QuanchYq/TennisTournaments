import asyncio
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor


import json
import keyboards as kb
import libs
eventsdb = sqlite3.connect('events.db')
events = eventsdb.cursor()

bot_token = "5902246169:AAH6BRVP1ztgt_BjGtbQbbtUjgS3JvQmq6M"
bot_username = "ttournamentsbot"
channel_id = -1001979363819

bot = Bot(token=bot_token, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

# acquire the lock to prevent other tasks from modifying the list at the same time
lock = asyncio.Lock()


# States
class Tournament(StatesGroup):
    name = State()
    date = State()
    link = State()
    category = State()
    price = State()
    addition = State()
    organizer_name = State()
    organizer_phone = State()
    place = State()
    comments = State()
    photos = State()
    files = State()
    end = State()
class PostRewriting(StatesGroup):
    content = State()
class User(StatesGroup):
    set_category = State()
class Search(StatesGroup):
    date1 = State()
    date2 = State()


async def start_command(message: types.Message, state: FSMContext):
    await state.finish()
    libs.newUser(message.chat.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
    keyboard = kb.start_a if libs.isAdmin(message.chat.id) == 1 else kb.start
    await message.answer("👋🏻 Привет!\n\n💠 Я бот для проведения турниров по настольному теннису. Я могу помочь вам <i><b>создать новый турнир</b></i> или <i><b>посмотреть уже существующие.</b></i>\n\nЧтобы начать, нажмите кнопку: <b>\nПредлагать турнир</b> 💬\nили <b>Турниры 🏓</b>", reply_markup=keyboard)


async def suggest_tournament(message: types.Message):
    await Tournament.name.set()
    await message.answer("<b>Называние турнира:</b>\n<i>Например: Grand Slam</i>")


async def tournaments(message: types.Message, state: FSMContext):
    await state.finish()
    async with state.proxy() as data:
        data['page'] = 1
    await message.answer("<b>🏓 Турниры:</b>", reply_markup=kb.getEvents(1))

async def set_category(message: types.Message, state: FSMContext):
    await User.set_category.set()
    await message.answer("<b>Напишите свою категорию:</b>")

async def interval_search(message: types.Message, state: FSMContext):
    await Search.date1.set()
    await message.answer("<b>Введи дату дату/время первого:</b>\n<i>(Например: 26.03.23 14:00)</i>")

async def register_date1(message: types.Message, state: FSMContext):
    if libs.is_valid_date(message.text):
        async with state.proxy() as data:
            data['date1'] = message.text
            await Search.date2.set()
            await message.answer("<b>✅ Мы сохранили ваш ответ!</b>\n<b>Введи дату дату/время второго:</b>\n<i>(Например: 26.03.23 14:00)</i>", reply_markup=kb.cancelButton)
    else:
        await message.answer("<b>⚠️ Некорректный форматы даты</b>\n<i>(Пример: 26.03.23 14:00)</i>")

async def register_date2(message: types.Message, state: FSMContext):
    if libs.is_valid_date(message.text):
        async with state.proxy() as data:
            data['date2'] = message.text
            await state.reset_state()
            await message.answer(f"<b>🏓 Турниры:</b>\n<i>{data['date1']}-{data['date2']}</i>", reply_markup=kb.getEvents(1, date1=data['date1'], date2=data['date2']))
    else:
        await message.answer("<b>⚠️ Некорректный форматы даты</b>\n<i>(Пример: 26.03.23 14:00)</i>")

async def get_category(message: types.Message, state: FSMContext):
    await state.finish()
    libs.setCategory(message.chat.id, message.text)
    await message.answer("<b>✅ Мы сохранили вашу категорию, теперь вы получите уведомлении о турнирах только с этой категории!</b>")

async def process_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data[(await state.get_state()).split(":")[1]] = message.text
        await message.answer("<b>✅ Мы сохранили ваш ответ!</b>\n<i>Если ошибка напишите еще раз</i>", reply_markup=kb.continueButton)

async def process_date(message: types.Message, state: FSMContext):
    if libs.is_valid_date(message.text):
        async with state.proxy() as data:
            data['date'] = message.text
            await message.answer("<b>✅ Мы сохранили ваш ответ!</b>\n<i>Если ошибка напишите еще раз</i>", reply_markup=kb.continueButton)
    else:
        await message.answer("<b>⚠️ Некорректный форматы даты</b>\n<i>(Пример: 26.03.23 14:00)</i>")



async def process_organizer_name(message: types.Message, state: FSMContext):
    libs.setName(message.chat.id, message.text)
    async with state.proxy() as data:
        data['organizer_name'] = message.text
        await message.answer("<b>✅ Мы сохранили вашу имя!</b>\n<i>Если ошибка напишите еще раз</i>", reply_markup=kb.continueButton)


async def process_organizer_phone(message: types.Message, state: FSMContext):
    libs.setPhone(message.chat.id, message.text)
    async with state.proxy() as data:
        data['organizer_phone'] = message.text
        await message.answer("<b>✅ Мы сохранили ваш номер!</b>\n<i>Если ошибка напишите еще раз</i>", reply_markup=kb.continueButton)


async def process_photos(message: types.Message, state: FSMContext):
    # Limit of photos
    photo_limit = 1
    async with lock:
        async with state.proxy() as data:
            photo = message.photo[-1].file_id
            if (not 'photos' in data) or data['photos'] == '':
                photo_list = [photo]
            else:
                photo_list = json.loads(data['photos'])
                if len(photo_list) >= photo_limit:
                    await message.answer(f"<b>⚠️ Максимальное количество фото: {photo_limit}</b>", reply_markup=kb.continueOrDeletePhotos)
                    return True
                photo_list.append(photo)
            data['photos'] = json.dumps(photo_list)
            await message.answer(f"<b>✅ Мы сохранили фото! ({len(photo_list)} фото)</b>",
                                 reply_markup=kb.continueOrDeletePhotos)


async def photo_mismatch(message: types.Message):
    await message.answer("<b>⚠️ Принимается только фото!</b>\n<i>(нельзя документы, тексты)</i>", reply_markup=kb.continueButton)


async def process_files(message: types.Message, state: FSMContext):
    # Limit of files
    file_limit = 1
    async with lock:
        async with state.proxy() as data:
            photo = message.document.file_id
            if (not 'files' in data) or data['files'] == '':
                file_list = [photo]
            else:
                file_list = json.loads(data['files'])
                if len(file_list) >= file_limit:
                    await message.answer(f"<b>⚠️ Максимальное количество файлов: {file_limit}</b>", reply_markup=kb.continueOrDeleteFiles)
                    return True
                file_list.append(photo)
            data['files'] = json.dumps(file_list)
            await message.answer(f"<b>✅ Мы сохранили файл! ({len(file_list)} файл)</b>",
                                 reply_markup=kb.continueOrDeleteFiles)


async def file_mismatch(message: types.Message):
    await message.answer("<b>⚠️ Принимается только файлы!</b>\n<i>(нельзя фото, тексты)</i>",
                         reply_markup=kb.continueButton)

async def rewritten_post(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['content'] = message.text
        await message.answer(f"<b>✅ Мы сохранили ваш ответ!</b>\n<i>Если ошибка напишите еще раз</i>",
                         reply_markup=kb.confirmPublicateRewrittenPost(data['event_id']))

async def send_to_moderators(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("<b>✅ Отправлено</b>")
    async with state.proxy() as data:
        libs.newEvent(data['name'], data['date'], data['link'], data['category'], data['price'], data['addition'],
                      data['organizer_name'], data['organizer_phone'], data['place'], data['comments'],
                      data['photos'], data['files'])
    admins = libs.getAdmins()
    for admin in admins:
        try:
            await bot.send_message(admin[0], "🔔<b> Новый турнир</b>")
        except:
            pass
        await asyncio.sleep(0.5)
    await state.finish()


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    await callback_query.message.edit_text("🛑 Остановлено\nМеню: /start")


async def delete_photos(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['photos'] = ''
        await callback_query.message.edit_text("Все фото удалены!\nОтправьте новые:", reply_markup=kb.continueButton)


async def delete_files(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['files'] = ''
        await callback_query.message.edit_text("Все файлы удалены!\nОтправьте новые:")


async def get_events(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['page'] = callback_query.data.split('|')[1]
        await callback_query.message.edit_text("<b>🏓 Турниры:</b>", reply_markup=kb.getEvents(int(data['page']) if 'page' in data else 1))


async def event(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    async with state.proxy() as data:
        event_id = callback_query.data.split('|')[1]
        event = libs.getEvent(event_id)
        files_count = 0 if event[11] == "" else len(json.loads(event[11]))
        photos_count = 0 if event[12] == "" else len(json.loads(event[12]))
        keyboard = kb.getAdminEventButton(data['page'] if 'page' in data else 1, event_id) if libs.isAdmin(callback_query.from_user.id) == 1 else kb.getUserEventButton(data['page'] if 'page' in data else 1, event_id)
        await callback_query.message.edit_text(libs.getEventMessage(event, True), reply_markup=keyboard, disable_web_page_preview=True)


async def confirm_deleting(callback_query: types.CallbackQuery):
    event_id = callback_query.data.split('|')[1]
    event = libs.getEvent(event_id)
    await callback_query.message.edit_text(f"*️⃣ Удалить турнир <b>{event[1]}?</b>", reply_markup=kb.confirmDelete(event_id))


async def delete_event(callback_query: types.CallbackQuery, state: FSMContext):
    event_id = callback_query.data.split('|')[1]
    libs.removeEvent(event_id)
    async with state.proxy() as data:
        data['page'] = 1
    await callback_query.message.edit_text("<b>🏓 Турниры:</b>", reply_markup=kb.getEvents(1))


async def confirm_publishing(callback_query: types.CallbackQuery):
    event_id = callback_query.data.split('|')[1]
    event = libs.getEvent(event_id)
    await callback_query.message.edit_text(f"*️⃣ Публикировать турнир <b>{event[1]}?</b>", reply_markup=kb.confirmPublicate(event_id))


async def publish_event(callback_query: types.CallbackQuery, state: FSMContext):
    event_id = callback_query.data.split('|')[1]
    event = libs.getEvent(event_id)
    async with state.proxy() as data:
        data['page'] = 1
        message = data['content'] if await state.get_state() == 'PostRewriting:content' else libs.getEventMessage(event)
    if event[11] == '':
        await bot.send_message(channel_id, message)
    else:
        photos = json.loads(event[11])
        media = []
        for index, photo in enumerate(photos):
            media.append(types.InputMediaPhoto(photo, message) if index == 0 else types.InputMediaPhoto(photo))
        await bot.send_media_group(channel_id, media)
    if event[12] != '':
        files = json.loads(event[12])
        media = []
        for index, file in enumerate(files):
            media.append( types.InputMediaDocument(file))
        await bot.send_media_group(channel_id, media)
    await state.finish()

    await callback_query.message.edit_text(libs.getEventMessage(event, True), reply_markup=kb.getAdminEventButton(data['page'] if 'page' in data else 1, event_id))
    await callback_query.answer("✅ Опубликовано")

async def rewrite_event(callback_query: types.CallbackQuery, state: FSMContext):
    await PostRewriting.content.set()
    async with state.proxy() as data:
        data['event_id'] = callback_query.data.split('|')[1]
        await callback_query.message.edit_text("Напишите новый текст: ", reply_markup=kb.getBackButton(data['event_id']))



async def get_media(callback_query: types.CallbackQuery):
    event_id = callback_query.data.split('|')[2]
    media_type = callback_query.data.split('|')[1]
    event = libs.getEvent(event_id)

    input_media = []
    if media_type == 'photos':
        if event[11] == '':
            await callback_query.answer("⚠️Количество фото 0")
            return True
        photos = json.loads(event[11])
        for photo in photos:
            input_media.append(types.InputMediaPhoto(media=photo))
    elif media_type == 'files':
        if event[12] == '':
            await callback_query.answer("⚠️Количество файлов 0")
            return True
        files = json.loads(event[12])
        for file in files:
            input_media.append(types.InputMediaDocument(media=file))
    await callback_query.message.answer_media_group(input_media)


async def edit_event(callback_query: types.CallbackQuery):
    event_id = callback_query.data.split('|')[1]
    await callback_query.message.edit_reply_markup(kb.getEditEventButton(event_id))


# ----------------- Message handlers
dp.register_message_handler(start_command, commands=['start'], state='*')
dp.register_message_handler(suggest_tournament, lambda message: message.text == "Предлагать турнир 💬", state='*')
dp.register_message_handler(set_category, lambda message: message.text == "Установить категорию ⚙️", state='*')
dp.register_message_handler(interval_search, lambda message: message.text == "Поиск по интервалам 🔍", state='*')
dp.register_message_handler(register_date1, state=Search.date1)
dp.register_message_handler(register_date2, state=Search.date2)
dp.register_message_handler(get_category, state=User.set_category)
dp.register_message_handler(tournaments, lambda message: message.text == 'Турниры 🏓', state='*')
dp.register_message_handler(process_answer, state=[Tournament.name, Tournament.link, Tournament.category, Tournament.price, Tournament.addition, Tournament.place, Tournament.comments])
dp.register_message_handler(process_date, state=Tournament.date)
dp.register_message_handler(process_organizer_name, state=Tournament.organizer_name)
dp.register_message_handler(process_organizer_phone, state=Tournament.organizer_phone)
dp.register_message_handler(process_photos, content_types=['photo'], state=Tournament.photos)
dp.register_message_handler(photo_mismatch, state=Tournament.photos)
dp.register_message_handler(process_files, content_types=['document'], state=Tournament.files)
dp.register_message_handler(file_mismatch, state=Tournament.files)
dp.register_message_handler(rewritten_post, state=PostRewriting.content)

# ----------------- Callback Query handlers
dp.register_callback_query_handler(send_to_moderators, lambda c: c.data and c.data == 'send', state="*")
dp.register_callback_query_handler(cancel, lambda c: c.data and c.data == 'cancel', state='*')
dp.register_callback_query_handler(delete_photos, lambda c: c.data and c.data == 'deletePhotos', state='*')
dp.register_callback_query_handler(delete_files, lambda c: c.data and c.data == 'deleteFiles', state='*')
dp.register_callback_query_handler(get_events, lambda c: c.data and c.data.startswith('getEvents'), state='*')
dp.register_callback_query_handler(event, lambda c: c.data and c.data.startswith('event'), state='*')
dp.register_callback_query_handler(confirm_deleting, lambda c: c.data and c.data.startswith('confirmDeleteEvent'), state='*')
dp.register_callback_query_handler(delete_event, lambda c: c.data and c.data.startswith('deleteEvent'), state='*')
dp.register_callback_query_handler(confirm_publishing, lambda c: c.data and c.data.startswith('confirmPublicateEvent'), state='*')
dp.register_callback_query_handler(publish_event, lambda c: c.data and c.data.startswith('publicateEvent'), state='*')
dp.register_callback_query_handler(rewrite_event, lambda c: c.data and c.data.startswith('rewriteEvent'), state='*')
dp.register_callback_query_handler(get_media, lambda c: c.data and c.data.startswith('getMedia'), state='*')
dp.register_callback_query_handler(edit_event, lambda c: c.data and c.data.startswith('editEvent'), state='*')


@dp.callback_query_handler(lambda c: c.data and (c.data == 'cont' or c.data.startswith("editField")), state='*')
async def process_continue(callback_query: types.CallbackQuery, state: FSMContext):
    answers = {
        "Tournament:name": "<b>Дата/время турнира:</b>\n<i>(Например: 26.03.23 14:00)</i>",
        "Tournament:link": "<b>Категория  турнира:</b>\n<i>(Например: Открытый турнир, Мастер, Grand slam)</i>",
        "Tournament:category": "<b>Сумма взноса:</b>\n<i>(Например: 1000, 5000)</i>",
        "Tournament:organizer_phone": "<b>Место проведения турнира:</b>\n<i>(Например: Алматы, проспект Абылай хана, 1)</i>",
    }
    answers_with_continue = {
        "Tournament:date": "<b>Ссылка турнира:</b>\n<i>(Подробности по <u>ссылке</u>)</i>",
        "Tournament:place": "<b>Другие комментарии:</b>",
        "Tournament:comments": "<b>Фото:</b>\n<i>(Например фото с место турнира)</i>",
        "Tournament:price": "<b>Что входит:</b>",
        "Tournament:photos": "<b>Файлы:</b>\n<i>(Положение о турнире)</i>"
    }
    state_dict = {
        'name': Tournament.name,
        'date': Tournament.date,
        'link': Tournament.link,
        'category': Tournament.category,
        'price': Tournament.price,
        'addition': Tournament.addition,
        'organizer_name': Tournament.organizer_name,
        'organizer_phone': Tournament.organizer_phone,
        'place': Tournament.place,
        'comments': Tournament.comments,
        'photos': Tournament.photos,
        'files': Tournament.files,
        'end': Tournament.end
    }

    async with state.proxy() as data:
        if 'event_id' in data and data['event_id']:
            field = (await state.get_state()).split(":")[1]
            libs.updateEvent(data['event_id'], field, data[field] if field in data else '')
            await callback_query.message.edit_text("✅ Редактировано", reply_markup=kb.getBackButton(data['event_id']))
            await state.finish()
            return True
        if callback_query.data.startswith("editField"):
            state_type = callback_query.data.split("|")[1]
            data['event_id'] = callback_query.data.split("|")[2]
            if state_type == 'name':
                await Tournament.name.set()
                await callback_query.message.edit_text("<b>Называние турнира:</b>\n<i>Например: Grand Slam</i>")
                return True
            await state_dict[state_type].set()
            await Tournament.previous()
        current_state = await state.get_state()

        if current_state in answers:
            await callback_query.message.edit_text(answers[current_state])
            await Tournament.next()
        elif current_state in answers_with_continue:
            await callback_query.message.edit_text(answers_with_continue[current_state], reply_markup=kb.continueButton)
            await Tournament.next()
            data[(await state.get_state()).split(":")[1]] = ''
        elif current_state == "Tournament:addition":
            await Tournament.organizer_name.set()
            name = libs.getName(callback_query.from_user.id)
            data['organizer_name'] = name
            if name == "":
                await callback_query.message.edit_text("<b>Имя организатора:</b>")
            else:
                await callback_query.message.edit_text(
                    f"✅ Оставьте имя организатора как {name} или отправьте другую: ",
                    reply_markup=kb.continueButton)
        elif current_state == "Tournament:organizer_name":
            await Tournament.organizer_phone.set()
            phone = libs.getPhone(callback_query.from_user.id)
            data['organizer_phone'] = phone
            if phone == "":
                await callback_query.message.edit_text("<b>Телефон организатора:</b>\n<i>(Например: +7 702 345 6789)</i>")
            else:
                await callback_query.message.edit_text(
                    f"✅ Оставьте телефон организатор как {phone} или отправьте другую: ", reply_markup=kb.continueButton)
        elif current_state == "Tournament:files":
            photos_count = 0 if data['photos'] == "" else len(json.loads(data['photos']))
            files_count = 0 if data['files'] == "" else len(json.loads(data['files']))
            await callback_query.message.edit_text(
                f"<b>Название:</b> {data['name']}\n<b>Дата:</b> {data['date']}\n<b>Ссылка:</b> {data['link']}\n<b>Категория:</b> {data['category']}\n<b>Сумма взноса:</b> {data['price']}\n<b>Что входит:</b> {data['addition']}\n<b>Имя организатор:</b> {data['organizer_name']}\n<b>Телефон организатора: </b> {data['organizer_phone']}\n<b>Место проведения:</b> {data['place']}\n<b>Другие комментарии:</b> {data['comments']}\n<b>Фото:</b> {photos_count} фото\n<b>Файл:</b> {files_count} файл", reply_markup=kb.confirmButton, disable_web_page_preview=True)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
