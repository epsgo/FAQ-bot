import asyncio
from datetime import date, timedelta
from db import all_users
from const import TEXTS

def get_orthodox_easter(year: int) -> date:
    a = year % 4
    b = year % 7
    c = year % 19

    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7

    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1

    julian_easter = date(year, month, day)
    gregorian_easter = julian_easter + timedelta(days=13)
    return gregorian_easter

async def holiday_checker(bot):
    while True:
        today = date.today()
        users = all_users()
        for user in users:

            user_id = user["user_id"]
            birthdate = date.fromisoformat(user["birthdate"])
            lang = user["language"]

            if birthdate.day == today.day and birthdate.month == today.month:
                await bot.send_message(user_id, TEXTS[lang]["happy_birthday"])

            if today.day == 1 and today.month == 1:
                await bot.send_message(user_id, TEXTS[lang]["new_year"])

            if today.day == 7 and today.month == 1:
                await bot.send_message(user_id, TEXTS[lang]["christmas"])

            if today.day == 24 and today.month == 8:
                await bot.send_message(user_id, TEXTS[lang]["independence"])

            if today.day == 28 and today.month == 6:
                await bot.send_message(user_id, TEXTS[lang]["constitution"])

            easter_date = get_orthodox_easter(today.year)
            if today == easter_date:
                await bot.send_message(user_id, TEXTS[lang]["easter"])

        await asyncio.sleep(86400)  