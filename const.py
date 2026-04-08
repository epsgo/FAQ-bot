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
        "faq_title": "❓ Часто задаваемые вопросы",
        "rate_choose_type": "Пожалуйста, выберите действие:",
        "rate_btn_rate": "⭐ Оценить",
        "rate_btn_bug": "🐞 Сообщить об ошибке",
        "rate_btn_idea": "💡 Предложить идею",
        "rate_ask_stars": "Оцените бота ⭐",
        "rate_ask_text_bug": "Опишите ошибку, с которой вы столкнулись:",
        "rate_ask_text_idea": "Поделитесь своей идеей или предложением:",
        "rate_ask_good": "Что вам понравилось?",
        "rate_ask_bad": "Что можно улучшить?",
        "rate_text_only": "Пожалуйста, отправьте текстовое сообщение.",
        "rate_thanks": "Спасибо! Ваш отзыв отправлен 🚀",
        "test_start": "📝 Тест начинается! Ответьте на каждый вопрос текстом. Всего 22 вопроса.",
        "test_thanks": "✅ Тест завершён! Спасибо за ваши ответы. Результаты сохранены.",
        "test_text_only": "Пожалуйста, отправьте текстовый ответ.",
        "test_cancel_btn": "❌ Выйти с теста",
        "test_cancelled_discarded": "Тест прерван.",
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
        "faq_title": "❓ Часті питання",
        "rate_choose_type": "Будь ласка, оберіть дію:",
        "rate_btn_rate": "⭐ Оцінити",
        "rate_btn_bug": "🐞 Повідомити про помилку",
        "rate_btn_idea": "💡 Запропонувати ідею",
        "rate_ask_stars": "Оцініть бота ⭐",
        "rate_ask_text_bug": "Опишіть помилку, з якою ви зіткнулися:",
        "rate_ask_text_idea": "Поділіться своєю ідеєю або пропозицією:",
        "rate_ask_good": "Що вам сподобалось?",
        "rate_ask_bad": "Що можна покращити?",
        "rate_text_only": "Будь ласка, надішліть текстове повідомлення.",
        "rate_thanks": "Дякуємо! Ваш відгук надіслано 🚀",
        "test_start": "📝 Тест починається! Відповідайте на кожне питання текстом. Всього 22 питання.",
        "test_thanks": "✅ Тест завершено! Дякуємо за ваші відповіді. Результати збережено.",
        "test_text_only": "Будь ласка, надішліть текстову відповідь.",
        "test_cancel_btn": "❌ Вийти з тесту",
        "test_cancelled_discarded": "Тест перервано.",
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
        "faq_title": "❓ Frequently Asked Questions",
        "rate_choose_type": "Please choose an action:",
        "rate_btn_rate": "⭐ Rate",
        "rate_btn_bug": "🐞 Report Bug",
        "rate_btn_idea": "💡 Suggest Idea",
        "rate_ask_stars": "Rate the bot ⭐",
        "rate_ask_text_bug": "Describe the bug you encountered:",
        "rate_ask_text_idea": "Share your idea or suggestion:",
        "rate_ask_good": "What did you like?",
        "rate_ask_bad": "What can be improved?",
        "rate_text_only": "Please send a text message.",
        "rate_thanks": "Thank you! Your feedback has been sent 🚀",
        "test_start": "📝 The test is starting! Answer each question with text. 22 questions total.",
        "test_thanks": "✅ Test completed! Thank you for your answers. Results have been saved.",
        "test_text_only": "Please send a text answer.",
        "test_cancel_btn": "❌ Exit Test",
        "test_cancelled_discarded": "Test cancelled.",
    }
}

TEST_QUESTIONS = [
    {
        "ru": "Что такое Unidentified Driving Events? Опишите, как они появляются в логбуке водителя и какой порядок действий необходимо выполнить для их обработки.",
        "ua": "Що таке Unidentified Driving Events? Опишіть, як вони з'являються у логбуку водія та який порядок дій необхідно виконати для їх обробки.",
        "en": "What are Unidentified Driving Events? Describe how they appear in a driver's logbook and what steps must be taken to handle them.",
    },
    {
        "ru": "Сертификация логбука. Почему водитель обязан сертифицировать свой логбук?",
        "ua": "Сертифікація логбуку. Чому водій зобов'язаний сертифікувати свій логбук?",
        "en": "Logbook certification. Why is a driver required to certify their logbook?",
    },
    {
        "ru": "Что такое Bill of Lading (BOL)? Опишите его назначение и какую информацию он обычно содержит.",
        "ua": "Що таке Bill of Lading (BOL)? Опишіть його призначення та яку інформацію він зазвичай містить.",
        "en": "What is a Bill of Lading (BOL)? Describe its purpose and what information it typically contains.",
    },
    {
        "ru": "Как водителю выполнить полное переподключение к грузовику (ELD устройству)? Опишите пошаговый процесс.",
        "ua": "Як водієві виконати повне перепідключення до вантажівки (ELD пристрою)? Опишіть покроковий процес.",
        "en": "How does a driver perform a full reconnection to the truck (ELD device)? Describe the step-by-step process.",
    },
    {
        "ru": "Кто такой ко-драйвер (co-driver)? Опишите его роль и объясните, как добавить ко-драйвера в приложении.",
        "ua": "Хто такий ко-драйвер (co-driver)? Опишіть його роль та поясніть, як додати ко-драйвера у додатку.",
        "en": "Who is a co-driver? Describe their role and explain how to add a co-driver in the app.",
    },
    {
        "ru": "Опишите полный процесс подключения водителя к грузовику через ELD-систему. Укажите все необходимые шаги и проверки.",
        "ua": "Опишіть повний процес підключення водія до вантажівки через ELD-систему. Вкажіть усі необхідні кроки та перевірки.",
        "en": "Describe the full process of connecting a driver to a truck through the ELD system. Specify all necessary steps and checks.",
    },
    {
        "ru": "Как водитель может отправить свои данные в FMCSA через приложение? Опишите доступные способы и последовательность действий.",
        "ua": "Як водій може надіслати свої дані до FMCSA через додаток? Опишіть доступні способи та послідовність дій.",
        "en": "How can a driver send their data to FMCSA through the app? Describe the available methods and the sequence of actions.",
    },
    {
        "ru": "Опишите три способа, с помощью которых водитель может сертифицировать свои логи в приложении.",
        "ua": "Опишіть три способи, за допомогою яких водій може сертифікувати свої логи у додатку.",
        "en": "Describe the three ways a driver can certify their logs in the app.",
    },
    {
        "ru": "Кто такие Shipper и Receiver? Объясните их роли в процессе перевозки.",
        "ua": "Хто такі Shipper та Receiver? Поясніть їхні ролі у процесі перевезення.",
        "en": "Who are the Shipper and Receiver? Explain their roles in the transportation process.",
    },
    {
        "ru": "Что такое ELD (Electronic Logging Device)? Опишите его назначение и основные функции.",
        "ua": "Що таке ELD (Electronic Logging Device)? Опишіть його призначення та основні функції.",
        "en": "What is an ELD (Electronic Logging Device)? Describe its purpose and main functions.",
    },
    {
        "ru": "Какие часовые пояса используются на территории США? Перечислите основные.",
        "ua": "Які часові пояси використовуються на території США? Перелічіть основні.",
        "en": "What time zones are used in the United States? List the main ones.",
    },
    {
        "ru": "Что такое IFTA (International Fuel Tax Agreement)? Объясните его назначение и как он используется.",
        "ua": "Що таке IFTA (International Fuel Tax Agreement)? Поясніть його призначення та як він використовується.",
        "en": "What is IFTA (International Fuel Tax Agreement)? Explain its purpose and how it is used.",
    },
    {
        "ru": "Как водитель может создать событие (event) в приложении? Опишите процесс.",
        "ua": "Як водій може створити подію (event) у додатку? Опишіть процес.",
        "en": "How can a driver create an event in the app? Describe the process.",
    },
    {
        "ru": "Что такое HOS? Объясните основные правила и ограничения.",
        "ua": "Що таке HOS? Поясніть основні правила та обмеження.",
        "en": "What is HOS? Explain the main rules and limitations.",
    },
    {
        "ru": "Опишите основные типы нарушений HOS. Приведите примеры.",
        "ua": "Опишіть основні типи порушень HOS. Наведіть приклади.",
        "en": "Describe the main types of HOS violations. Provide examples.",
    },
    {
        "ru": "Что такое DOT-инспекция и как она проходит? Опишите процесс и что проверяется.",
        "ua": "Що таке DOT-інспекція та як вона проходить? Опишіть процес і що перевіряється.",
        "en": "What is a DOT inspection and how does it proceed? Describe the process and what is checked.",
    },
    {
        "ru": "Что такое правило Split Sleeper Berth? Объясните его логику и как водитель может его использовать.",
        "ua": "Що таке правило Split Sleeper Berth? Поясніть його логіку та як водій може ним користуватися.",
        "en": "What is the Split Sleeper Berth rule? Explain its logic and how a driver can use it.",
    },
    {
        "ru": "Что такое Intermediate Logs? Объясните, когда и зачем они создаются.",
        "ua": "Що таке Intermediate Logs? Поясніть, коли та навіщо вони створюються.",
        "en": "What are Intermediate Logs? Explain when and why they are created.",
    },
    {
        "ru": "Как создать профиль водителя в системе? Опишите основные шаги.",
        "ua": "Як створити профіль водія у системі? Опишіть основні кроки.",
        "en": "How do you create a driver profile in the system? Describe the main steps.",
    },
    {
        "ru": "Как создать профиль грузовика (vehicle) в системе? Опишите процесс.",
        "ua": "Як створити профіль вантажівки (vehicle) у системі? Опишіть процес.",
        "en": "How do you create a truck (vehicle) profile in the system? Describe the process.",
    },
    {
        "ru": "Кто такие car haulers? Опишите особенности их работы.",
        "ua": "Хто такі car haulers? Опишіть особливості їхньої роботи.",
        "en": "Who are car haulers? Describe the specifics of their work.",
    },
    {
        "ru": "Что такое Recap (recap hours)? Объясните, как водитель может использовать это правило в своей работе.",
        "ua": "Що таке Recap (recap hours)? Поясніть, як водій може використовувати це правило у своїй роботі.",
        "en": "What is Recap (recap hours)? Explain how a driver can use this rule in their work.",
    },
]

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