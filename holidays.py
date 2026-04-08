import asyncio
import random
from datetime import date, datetime, timedelta, time

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
    return julian_easter + timedelta(days=13)


async def wait_until(target: datetime):
    now = datetime.now()
    delay = (target - now).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)


async def holiday_checker(bot):
    while True:
        now = datetime.now()

        random_hour = random.randint(12, 21)
        random_minute = random.randint(0, 59)

        target_time = datetime.combine(
            now.date(),
            time(hour=random_hour, minute=random_minute)
        )

        if target_time <= now:
            target_time += timedelta(days=1)

        await wait_until(target_time)

        today = date.today()
        try:
            users = all_users()
        except Exception as e:
            print(f"[holiday_checker] Failed to fetch users: {e}")
            continue

        for user in users:
            if not user.get("is_approved"):
                continue

            user_id = user["user_id"]
            lang = user["language"]

            try:
                birthdate = date.fromisoformat(user["birthdate"])
            except Exception:
                continue

            try:
                if birthdate.day == today.day and birthdate.month == today.month:
                    await bot.send_message(user_id, TEXTS[lang]["happy_birthday"])

                if today.day == 1 and today.month == 1:
                    await bot.send_message(user_id, TEXTS[lang]["new_year"])

                if today.day == 25 and today.month == 12:
                    await bot.send_message(user_id, TEXTS[lang]["christmas"])

                if today.day == 24 and today.month == 8:
                    await bot.send_message(user_id, TEXTS[lang]["independence"])

                if today.day == 28 and today.month == 6:
                    await bot.send_message(user_id, TEXTS[lang]["constitution"])

                easter_date = get_orthodox_easter(today.year)
                if today == easter_date:
                    await bot.send_message(user_id, TEXTS[lang]["easter"])
            except Exception:
                continue
