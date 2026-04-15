import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from db import get_pending_reminders, mark_reminder_sent, get_user
from const import TEXTS

logger = logging.getLogger(__name__)


def t(lang: str, key: str, **kwargs) -> str:
    text = TEXTS[lang][key]
    return text.format(**kwargs) if kwargs else text


async def meeting_reminder_scheduler(bot: Bot):
    while True:
        try:
            await asyncio.sleep(300)  
            
            meetings = get_pending_reminders()
            now = datetime.now()
            
            for meeting in meetings:
                if not meeting.get("meeting_datetime"):
                    continue
                
                try:
                    meeting_dt_str = meeting["meeting_datetime"]
                    meeting_dt = datetime.strptime(meeting_dt_str, "%d.%m.%Y %H:%M")
                    
                    time_until_meeting = meeting_dt - now
                    minutes_until = time_until_meeting.total_seconds() / 60
                    
                    if 55 <= minutes_until <= 65:
                        requester_id = meeting["requester_id"]
                        target_id = meeting["target_id"]
                        
                        requester = get_user(requester_id)
                        target = get_user(target_id)
                        
                        if requester:
                            req_lang = requester["language"]
                            target_name = target["full_name"] if target else "Unknown"
                            try:
                                await bot.send_message(
                                    requester_id,
                                    t(req_lang, "meet_reminder", name=target_name, datetime=meeting_dt_str),
                                    parse_mode="HTML"
                                )
                            except Exception as e:
                                logger.error(f"Не удалось отправить напоминание requester {requester_id}: {e}")
                        
                        if target:
                            tgt_lang = target["language"]
                            requester_name = requester["full_name"] if requester else "Unknown"
                            try:
                                await bot.send_message(
                                    target_id,
                                    t(tgt_lang, "meet_reminder", name=requester_name, datetime=meeting_dt_str),
                                    parse_mode="HTML"
                                )
                            except Exception as e:
                                logger.error(f"Не удалось отправить напоминание target {target_id}: {e}")
                        
                        mark_reminder_sent(meeting["id"])
                        logger.info(f"Напоминание о встрече {meeting['id']} отправлено")
                
                except ValueError as e:
                    logger.error(f"Ошибка парсинга даты встречи {meeting.get('id')}: {e}")
                except Exception as e:
                    logger.error(f"Ошибка при обработке встречи {meeting.get('id')}: {e}")
        
        except Exception as e:
            logger.error(f"Ошибка в meeting_reminder_scheduler: {e}", exc_info=True)
