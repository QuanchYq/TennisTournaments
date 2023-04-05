import asyncio, sqlite3, datetime
import json
import types
import schedule
import time

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import BotBlocked

import libs

eventsdb = sqlite3.connect('events.db')
events = eventsdb.cursor()

bot_token = "5902246169:AAH6BRVP1ztgt_BjGtbQbbtUjgS3JvQmq6M"

bot = Bot(token=bot_token, parse_mode="HTML")
dp = Dispatcher(bot)


async def mail():
    users = libs.getUsers()
    todays_events = events.execute(f"SELECT * FROM events WHERE date(date) = '{datetime.date.today()}'").fetchall()
    for event in todays_events:
        message = libs.getEventMessage(event)
        for user in users:
            if user[9] != event[4] and user[9] != '':
                continue
            try:
                if event[11] == '':
                    await bot.send_message(user[1], message)
                else:
                    photos = json.loads(event[11])
                    media = []
                    for index, photo in enumerate(photos):
                        media.append(types.InputMediaPhoto(photo, message) if index == 0 else types.InputMediaPhoto(photo))
                    await bot.send_media_group(user[1], media)
                if event[12] != '':
                    files = json.loads(event[12])
                    media = []
                    for index, file in enumerate(files):
                        media.append(types.InputMediaDocument(file))
                    await bot.send_media_group(user[1], media)
            except BotBlocked as E:
                libs.removeUser(user[0])
            except:
                pass
            await asyncio.sleep(0.1)
    libs.usersVacuum()


# Schedule the mail() function to run every day at 00:10
schedule.every().day.at("15:35").do(asyncio.run, mail())

# Run the scheduler loop
while True:
    schedule.run_pending()
    time.sleep(1)
