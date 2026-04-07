import os
from dotenv import load_dotenv
load_dotenv()
admin_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = {int(i.strip()) for i in admin_raw.split(",") if i.strip()}
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
# ФАЙЛ ХУЙНИ
TEXTS = {
    "ru": {
        "signNDA": "✍️ Подписать контракт о неразглашении",
        "nda": "Подпиши уебище",
        "wait_approval": "Спасибо за регистрацию! Администратор рассматривает вашу заявку. Пожалуйста, подождите немного, вы скоро получите уведомление.",
        "filesent": "Файл успешно отправлен 🚀",
        "choose_lang": "Выберите язык:",
        "choose_info": "Выберите, что хотите изменить:",
        "edit_info": "✏️ Редактировать информацию",
        "change_lang": "Язык",
        "change_name": "ФИО",
        "lang": "Язык",
        "birthdate": "Дата рождения",
        "registrationdate": "Дата регистрации",
        "change_birthdate": "Дату рождения",
        "lang_changed": "Язык успешно изменен!",
        "name_changed": "ФИО успешно изменено!",
        "birth_changed": "Дата рождения успешно изменена!",
        "ask_name": "Введите ваше ФИО:",
        "ask_birth": "Введите дату рождения в формате ДД.ММ.ГГГГ:",
        "registered": "Регистрация завершена!",
        "happy_birthday": "🎉 С Днём Рождения!",
        "new_year": "🎄 С Новым Годом!",
        "christmas": "✨ С Рождеством!",
        "independence": "С Днём Независимости Украины!",
        "constitution": "📜 С Днём Конституции Украины!",
        "easter": "🐣 С Пасхой!",
        "welcome_back": "С возвращением!",
        "faq_title": "❓ Часто задаваемые вопросы"
    },
    "ua": {
        "signNDA": "✍️ Підписати контракт про нерозголошення",
        "nda": "Подпиши уебище",
        "wait_approval": "Дякуємо за реєстрацію! Адміністратор розглядає ваш запит. Будь ласка, зачекайте, ви отримаєте сповіщення найближчим часом.",
        "filesent": "Файл успішно відправлен 🚀",
        "choose_lang": "Оберіть мову:",
        "choose_info": "Оберіть, що хочете змінити:",
        "edit_info": "✏️ Редагувати інформацію",
        "change_lang": "Мову",
        "change_name": "ПІБ",
        "lang": "Мова",
        "birthdate": "Дата народження",
        "registrationdate": "Дата реєстрації",
        "change_birthdate": "Дату народження",
        "lang_changed": "Мову успішно змінено!",
        "name_changed": "ПІБ успішно змінено!",
        "birth_changed": "Дата народження успішно змінена!",
        "ask_name": "Введіть ваше ПІБ:",
        "ask_birth": "Введіть дату народження у форматі ДД.ММ.РРРР:",
        "registered": "Реєстрація завершена!",
        "happy_birthday": "🎉 З Днем Народження!",
        "new_year": "🎄 З Новим Роком!",
        "christmas": "✨ З Різдвом!",
        "independence": "З Днем Незалежності України!",
        "constitution": "📜 З Днем Конституції України!",
        "easter": "🐣 З Великоднем!",
        "welcome_back": "З поверненням!",
        "faq_title": "❓ Часті питання"
    },
    "en": {
        "signNDA": "✍️ Sign a non-disclosure agreement",
        "nda": "Подпиши уебище",
        "wait_approval": "Thanks for registering! An administrator is reviewing your request. Please hang tight, you’ll be notified soon.",
        "filesent": "File sent successfully 🚀",
        "choose_lang": "Choose language:",
        "choose_info": "Select what you want to change:",
        "edit_info": "✏️ Edit Info",
        "change_lang": "Language",
        "change_name": "Name",
        "lang": "Language",
        "birthdate": "Birthdate",
        "registrationdate": "Registration Date",
        "change_birthdate": "Birthdate",
        "lang_changed": "Language successfully changed!",
        "name_changed": "Full name successfully changed!",
        "birth_changed": "Birthdate successfully changed!",
        "ask_name": "Enter your full name:",
        "ask_birth": "Enter birthdate in format DD.MM.YYYY:",
        "registered": "Registration completed!",
        "happy_birthday": "🎉 Happy Birthday!",
        "new_year": "🎄 Happy New Year!",
        "christmas": "✨ Merry Christmas!",
        "independence": "Happy Independence Day (Ukraine)!",
        "constitution": "📜 Happy Constitution Day (Ukraine)!",
        "easter": "🐣 Happy Easter!",
        "welcome_back": "Welcome back!",
        "faq_title": "❓ Frequently Asked Questions"
    }
}

MENU_BUTTONS = {
    "ru": {
        "btn_profile": "👤 Профиль",
        "btn_faq": "❓ Частые вопросы",
        "btn_test": "📝 Пройти тест",
        "btn_meeting": "📅 Запрос встречи",
        "btn_rate": "⭐ Оценить бота",
        "btn_admin": "⚙️ Админ"
    },
    "ua": {
        "btn_profile": "👤 Профіль",
        "btn_faq": "❓ Часті питання",
        "btn_test": "📝 Пройти тест",
        "btn_meeting": "📅 Запит зустрічі",
        "btn_rate": "⭐ Оцінити бота",
        "btn_admin": "⚙️ Адмін"
    },
    "en": {
        "btn_profile": "👤 Profile",
        "btn_faq": "❓ FAQ",
        "btn_test": "📝 Take Test",
        "btn_meeting": "📅 Request Meeting",
        "btn_rate": "⭐ Rate Bot",
        "btn_admin": "⚙️ Admin"
    }
}

def get_all_variants(btn_key: str):
    return [lang_dict[btn_key] for lang_dict in MENU_BUTTONS.values() if btn_key in lang_dict]

PROFILE_BTNS = get_all_variants("btn_profile")
FAQ_BTNS = get_all_variants("btn_faq")
TEST_BTNS = get_all_variants("btn_test")
MEETING_BTNS = get_all_variants("btn_meeting")
RATE_BTNS = get_all_variants("btn_rate")
ADMIN_BTNS = get_all_variants("btn_admin")