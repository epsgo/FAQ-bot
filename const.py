import os
from dotenv import load_dotenv
load_dotenv()
admin_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = {int(i.strip()) for i in admin_raw.split(",") if i.strip()}
TEXTS = {
    "ru": {
        "wait_approval":"Спасибо за регистрацию! Администратор рассматривает вашу заявку. Пожалуйста, подождите немного, вы скоро получите уведомление.",
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
        "meet_menu_title": "📅 С кем вы хотите провести мит?",
        "meet_btn_manager": "👔 С менеджером",
        "meet_btn_teamlead": "👑 С тимлидом",
        "meet_btn_mentor": "🎓 Запросить ментора",
        "meet_no_available": "❌ Сейчас нет доступных пользователей.",
        "meet_select_manager": "Выберите менеджера:",
        "meet_select_teamlead": "Выберите тимлида:",
        "meet_select_mentor": "🎓 Выберите менеджера для запроса ментора:",
        "meet_sent": "✅ Запрос на встречу отправлен!",
        "meet_mentor_sent": "✅ Запрос на ментора отправлен!",
        "meet_error": "❌ Не удалось отправить запрос. Попробуйте позже.",
        "meet_incoming_11": "📅 <b>{name}</b> хочет провести встречу 1:1 с вами.",
        "meet_incoming_mentor": "🎓 <b>{name}</b> запросил ментора на 1 смену.",
        "meet_btn_confirm": "✅ Принять",
        "meet_btn_decline": "❌ Отклонить",
        "meet_confirmed_by": "✅ <b>{name}</b> принял ваш запрос на встречу 1:1!",
        "meet_declined_by": "❌ <b>{name}</b> отклонил ваш запрос на встречу 1:1.",
        "meet_you_confirmed": "✅ Вы приняли запрос на встречу.",
        "meet_you_declined": "❌ Вы отклонили запрос на встречу.",
        "meet_back": "⬅️ Назад",
        "goodbye": "Хорошего дня! 😊",
    },
    "ua": {
        "wait_approval": "Дякуємо за реєстрацію! Адміністратор розглядає ваш запит. Будь ласка, зачекайте, ви отримаєте сповіщення найближчим часом.",
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
        "meet_menu_title": "📅 З ким ви хочете провести мітинг?",
        "meet_btn_manager": "👔 З менеджером",
        "meet_btn_teamlead": "👑 З тимлідом",
        "meet_btn_mentor": "🎓 Запросити ментора",
        "meet_no_available": "❌ Зараз немає доступних користувачів.",
        "meet_select_manager": "Оберіть менеджера:",
        "meet_select_teamlead": "Оберіть тімліда:",
        "meet_select_mentor": "🎓 Оберіть менеджера для запиту ментора:",
        "meet_sent": "✅ Запит на зустріч надіслано!",
        "meet_mentor_sent": "✅ Запит на ментора надіслано!",
        "meet_error": "❌ Не вдалося надіслати запит. Спробуйте пізніше.",
        "meet_incoming_11": "📅 <b>{name}</b> хоче провести зустріч 1:1 з вами.",
        "meet_incoming_mentor": "🎓 <b>{name}</b> запросив ментора на 1 зміну.",
        "meet_btn_confirm": "✅ Прийняти",
        "meet_btn_decline": "❌ Відхилити",
        "meet_confirmed_by": "✅ <b>{name}</b> прийняв ваш запит на зустріч 1:1!",
        "meet_declined_by": "❌ <b>{name}</b> відхилив ваш запит на зустріч 1:1.",
        "meet_you_confirmed": "✅ Ви прийняли запит на зустріч.",
        "meet_you_declined": "❌ Ви відхилили запит на зустріч.",
        "meet_back": "⬅️ Назад",
        "goodbye": "Гарного дня! 😊",
    },
    "en": {
        "wait_approval": "Thanks for registering! An administrator is reviewing your request. Please hang tight, you’ll be notified soon.",
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
        "meet_menu_title": "📅 Who would you like to have a meeting with?",
        "meet_btn_manager": "👔 With Manager",
        "meet_btn_teamlead": "👑 With Teamlead",
        "meet_btn_mentor": "🎓 Request Mentor",
        "meet_no_available": "❌ No users available right now.",
        "meet_select_manager": "Select a manager:",
        "meet_select_teamlead": "Select a teamlead:",
        "meet_select_mentor": "🎓 Select a manager for the mentor request:",
        "meet_sent": "✅ Meeting request sent!",
        "meet_mentor_sent": "✅ Mentor request sent!",
        "meet_error": "❌ Could not send the request. Try again later.",
        "meet_incoming_11": "📅 <b>{name}</b> wants to have a 1:1 meeting with you.",
        "meet_incoming_mentor": "🎓 <b>{name}</b> has requested a mentor for 1 shift.",
        "meet_btn_confirm": "✅ Confirm",
        "meet_btn_decline": "❌ Decline",
        "meet_confirmed_by": "✅ <b>{name}</b> confirmed your 1:1 meeting request!",
        "meet_declined_by": "❌ <b>{name}</b> declined your 1:1 meeting request.",
        "meet_you_confirmed": "✅ You confirmed the meeting request.",
        "meet_you_declined": "❌ You declined the meeting request.",
        "meet_back": "⬅️ Back",
        "goodbye": "Have a nice day! 😊",
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


ONBOARDING_STAGES = {
    1: {"day": 3,  "questions": [
        {"key": "q1", "type": "score"},
        {"key": "q2", "type": "score"},
        {"key": "q3", "type": "score"},
    ]},
    2: {"day": 7,  "questions": [
        {"key": "q4", "type": "score"},
        {"key": "q5", "type": "score"},
        {"key": "q6", "type": "text"},
    ]},
    3: {"day": 14, "questions": [
        {"key": "q7",  "type": "text"},
        {"key": "q8",  "type": "score"},
        {"key": "q9",  "type": "score"},
    ]},
    4: {"day": 30, "questions": [
        {"key": "q10", "type": "text"},
        {"key": "q11", "type": "yn"},
        {"key": "q12", "type": "text"},
    ]},
}

ONBOARDING_QUESTIONS = {
    "q1": {
        "ru": "Насколько ты почувствовал себя welcome / частью команды? (оцени от 1 до 5)",
        "ua": "Наскільки ти відчув себе welcome / частиною команди? (оціни від 1 до 5)",
        "en": "How welcomed / part of the team did you feel? (rate 1 to 5)",
    },
    "q2": {
        "ru": "Получил ли ты всё необходимое (доступы, информацию) вовремя? (оцени от 1 до 5)",
        "ua": "Чи отримав ти все необхідне (доступи, інформацію) вчасно? (оціни від 1 до 5)",
        "en": "Did you receive everything you needed (access, information) on time? (rate 1 to 5)",
    },
    "q3": {
        "ru": "Насколько понятно, какие от тебя ожидания в первые 1–3 месяца? (оцени от 1 до 5)",
        "ua": "Наскільки зрозуміло, які від тебе очікування в перші 1–3 місяці? (оціни від 1 до 5)",
        "en": "How clear are the expectations from you in the first 1–3 months? (rate 1 to 5)",
    },
    "q4": {
        "ru": "Насколько комфортно / безопасно задавать вопросы / просить помощи? (оцени от 1 до 5)",
        "ua": "Наскільки комфортно / безпечно ставити запитання / просити допомоги? (оціни від 1 до 5)",
        "en": "How comfortable / safe do you feel asking questions or asking for help? (rate 1 to 5)",
    },
    "q5": {
        "ru": "Соответствует ли реальная работа тому, о чём рассказывали на собеседовании? (оцени от 1 до 5)",
        "ua": "Чи відповідає реальна робота тому, про що розповідали на співбесіді? (оціни від 1 до 5)",
        "en": "Does the actual work match what was described during the interview? (rate 1 to 5)",
    },
    "q6": {
        "ru": "Что было самым полезным / приятным в онбординге?",
        "ua": "Що було найкориснішим / найприємнішим в онбордингу?",
        "en": "What was the most useful / pleasant part of the onboarding?",
    },
    "q7": {
        "ru": "Чего не хватило / что можно было бы сделать лучше?",
        "ua": "Чого не вистачило / що можна було б зробити краще?",
        "en": "What was missing / what could have been done better?",
    },
    "q8": {
        "ru": "Насколько ты сейчас уверен в том, что можешь успешно выполнять свою работу? (оцени от 1 до 5)",
        "ua": "Наскільки ти зараз впевнений у тому, що можеш успішно виконувати свою роботу? (оціни від 1 до 5)",
        "en": "How confident are you now that you can successfully perform your job? (rate 1 to 5)",
    },
    "q9": {
        "ru": "Рекомендовал бы ты приходить к нам работать друзьям? (оцени от 1 до 5)",
        "ua": "Чи рекомендував би ти приходити до нас працювати друзям? (оціни від 1 до 5)",
        "en": "Would you recommend working here to your friends? (rate 1 to 5)",
    },
    "q10": {
        "ru": "Как ты чувствуешь себя в команде сейчас? Насколько, по твоим ощущениям, тебе удалось интегрироваться?",
        "ua": "Як ти почуваєшся в команді зараз? Наскільки, за твоїми відчуттями, тобі вдалося інтегруватися?",
        "en": "How do you feel in the team now? How well do you feel you've integrated?",
    },
    "q11": {
        "ru": "Есть ли что-то, о чём ты стесняешься / боишься спросить у менеджера / коллег?",
        "ua": "Чи є щось, про що ти соромишся / боїшся запитати у менеджера / колег?",
        "en": "Is there anything you are hesitant / afraid to ask your manager or colleagues?",
    },
    "q12": {
        "ru": "Что тебе больше всего нравится в работе за этот первый месяц? А что оказалось сложнее / неожиданнее, чем ты думал?",
        "ua": "Що тобі найбільше подобається в роботі за цей перший місяць? А що виявилося складнішим / несподіванішим, ніж ти думав?",
        "en": "What do you like most about the work in this first month? What turned out to be harder / more unexpected than you thought?",
    },
}

ONBOARDING_TEXTS = {
    "ru": {
        "intro_day3":   "👋 Прошло 3 дня с момента твоего старта! Хотим узнать, как ты себя чувствуешь. Ответь, пожалуйста, на несколько коротких вопросов.",
        "intro_day7":   "📅 Прошла неделя! Несколько вопросов к тебе — это займёт пару минут.",
        "intro_day14":  "🗓 Две недели позади! Поделись впечатлениями — нам важна твоя обратная связь.",
        "intro_day30":  "🎉 Первый месяц позади! Несколько финальных вопросов — как ты себя чувствуешь в команде?",
        "thanks":       "✅ Спасибо за ответы! Твоя обратная связь очень важна для нас.",
        "yn_yes":       "✅ Да",
        "yn_no":        "❌ Нет",
        "yn_followup":  "Расскажи подробнее — что именно ты боишься спросить?",
        "alert_score":  "⚠️ Низкая оценка от сотрудника\n\n👤 {name} (ID: {user_id})\n📋 Вопрос: {question}\n⭐ Оценка: {answer}/5",
        "alert_text":   "⚠️ Тревожный ответ от сотрудника\n\n👤 {name} (ID: {user_id})\n📋 Вопрос: {question}\n💬 Ответ: {answer}",
        "alert_yn":     "⚠️ Сотрудник боится задавать вопросы\n\n👤 {name} (ID: {user_id})\n💬 Подробности: {answer}",
    },
    "ua": {
        "intro_day3":   "👋 Минуло 3 дні з моменту твого старту! Хочемо дізнатися, як ти себе почуваєш. Будь ласка, дай відповіді на кілька коротких запитань.",
        "intro_day7":   "📅 Минув тиждень! Кілька запитань до тебе — це займе пару хвилин.",
        "intro_day14":  "🗓 Два тижні позаду! Поділися враженнями — нам важливий твій зворотний зв'язок.",
        "intro_day30":  "🎉 Перший місяць позаду! Кілька фінальних запитань — як ти почуваєшся в команді?",
        "thanks":       "✅ Дякуємо за відповіді! Твій зворотний зв'язок дуже важливий для нас.",
        "yn_yes":       "✅ Так",
        "yn_no":        "❌ Ні",
        "yn_followup":  "Розкажи детальніше — що саме ти боїшся запитати?",
        "alert_score":  "⚠️ Низька оцінка від співробітника\n\n👤 {name} (ID: {user_id})\n📋 Питання: {question}\n⭐ Оцінка: {answer}/5",
        "alert_text":   "⚠️ Тривожна відповідь від співробітника\n\n👤 {name} (ID: {user_id})\n📋 Питання: {question}\n💬 Відповідь: {answer}",
        "alert_yn":     "⚠️ Співробітник боїться ставити запитання\n\n👤 {name} (ID: {user_id})\n💬 Подробиці: {answer}",
    },
    "en": {
        "intro_day3":   "👋 3 days have passed since you started! We'd love to know how you're feeling. Please answer a few short questions.",
        "intro_day7":   "📅 One week in! A few questions about your onboarding — it'll only take a couple of minutes.",
        "intro_day14":  "🗓 Two weeks done! Share your impressions — your feedback matters to us.",
        "intro_day30":  "🎉 First month complete! A few final questions — how are you feeling in the team?",
        "thanks":       "✅ Thank you for your answers! Your feedback is very important to us.",
        "yn_yes":       "✅ Yes",
        "yn_no":        "❌ No",
        "yn_followup":  "Tell us more — what exactly are you afraid to ask?",
        "alert_score":  "⚠️ Low rating from employee\n\n👤 {name} (ID: {user_id})\n📋 Question: {question}\n⭐ Score: {answer}/5",
        "alert_text":   "⚠️ Concerning response from employee\n\n👤 {name} (ID: {user_id})\n📋 Question: {question}\n💬 Answer: {answer}",
        "alert_yn":     "⚠️ Employee is afraid to ask questions\n\n👤 {name} (ID: {user_id})\n💬 Details: {answer}",
    },
}

ONBOARDING_NEGATIVE_KEYWORDS = [
    "плохо", "ужасно", "не нравится", "разочарован", "разочарована", "не устраивает",
    "стресс", "тяжело", "уволиться", "уйти", "не хочу", "не понимаю", "сложно",
    "проблема", "проблемы", "некомфортно", "не ожидал", "не ожидала", "обманули",
    "погано", "жахливо", "не подобається", "розчарований", "розчарована",
    "не влаштовує", "стрес", "важко", "звільнитись", "піти", "не хочу",
    "не розумію", "складно", "проблема", "проблеми", "некомфортно", "обманули",
    "bad", "terrible", "don't like", "disappointed", "unsatisfied",
    "stress", "hard", "quit", "leave", "don't want", "don't understand",
    "difficult", "problem", "uncomfortable", "misled", "lied",
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

NDA_INSTRUCTION = {
    "ua": (
        "✍️ <b>Інструкція: підписання договору про нерозголошення</b>\n\n"

        "<b>📂 Крок 1 — Відкрийте документ для редагування</b>\n"
        "Договір надається у форматі PDF. Для зручного заповнення даних конвертуйте його у Word:\n"
        "🔗 https://www.ilovepdf.com/ru/pdf_to_word\n\n"

        "<b>📋 Крок 2 — Заповніть свої дані у документі</b>\n\n"

        "🔢 <b>ІПН (номер картки платника податків)</b>\n"
        "Знайдіть: <code>1234567890</code>\n"
        "Замініть на свій ІПН — <i>20 місць</i>\n\n"

        "📅 <b>Дата підписання</b>\n"
        "Знайдіть: <code>«01» червня 2025 р.</code>\n"
        "Замініть на актуальну дату — <i>8 місць</i>\n\n"

        "👤 <b>ПІБ (українською)</b>\n"
        "Знайдіть: <code>ІВАНОВ ІВАН ІВАНОВИЧ</code>\n"
        "Замініть на своє ПІБ — <i>6 місць</i>\n\n"

        "🔤 <b>ПІБ (англійською)</b>\n"
        "Знайдіть: <code>IVANOV IVAN</code>\n"
        "Замініть на прізвище та ім'я латиницею — <i>6 місць</i>\n\n"

        "🏠 <b>Адреса прописки (укр)</b>\n"
        "Знайдіть: <code>Україна, 11111, Київ, вул. Хрещатик, буд. 1, кв. 1</code>\n"
        "Замініть на свою повну адресу — <i>3 місця</i>\n\n"

        "🌍 <b>Адреса прописки (англ)</b>\n"
        "Знайдіть: <code>Ukraine, 11111, Kyiv, Khreshchatyk str., bldg. 1, apt. 1</code>\n"
        "Замініть на свою адресу англійською — <i>3 місця</i>\n\n"

        "<b>📄 Крок 3 — Конвертуйте назад у PDF</b>\n"
        "Після заповнення збережіть документ та перетворіть його з Word у PDF:\n"
        "🔗 https://www.ilovepdf.com/ru/word_to_pdf\n\n"

        "<b>✍️ Крок 4 — Підпишіть PDF</b>\n"
        "Поставте підпис у <b>6 місцях</b> — внизу кожного з трьох договорів під своїми даними:\n"
        "🔗 https://www.ilovepdf.com/ru/sign-pdf\n\n"

        "<b>📤 Крок 5 — Надішліть готовий PDF своєму менеджеру</b>"
    ),
    "ru": (
        "✍️ <b>Инструкция: подписание договора о неразглашении</b>\n\n"

        "<b>📂 Шаг 1 — Откройте документ для редактирования</b>\n"
        "Договор предоставляется в формате PDF. Для удобного заполнения данных конвертируйте его в Word:\n"
        "🔗 https://www.ilovepdf.com/ru/pdf_to_word\n\n"

        "<b>📋 Шаг 2 — Заполните свои данные в документе</b>\n\n"

        "🔢 <b>ИНН (номер карты налогоплательщика)</b>\n"
        "Найдите: <code>1234567890</code>\n"
        "Замените на свой ИНН — <i>20 мест</i>\n\n"

        "📅 <b>Дата подписания</b>\n"
        "Найдите: <code>«01» червня 2025 р.</code>\n"
        "Замените на актуальную дату — <i>8 мест</i>\n\n"

        "👤 <b>ФИО (украинскими буквами)</b>\n"
        "Найдите: <code>ІВАНОВ ІВАН ІВАНОВИЧ</code>\n"
        "Замените на своё ФИО — <i>6 мест</i>\n\n"

        "🔤 <b>ФИО (английскими буквами)</b>\n"
        "Найдите: <code>IVANOV IVAN</code>\n"
        "Замените на фамилию и имя латиницей — <i>6 мест</i>\n\n"

        "🏠 <b>Адрес прописки (укр)</b>\n"
        "Найдите: <code>Україна, 11111, Київ, вул. Хрещатик, буд. 1, кв. 1</code>\n"
        "Замените на свой полный адрес — <i>3 места</i>\n\n"

        "🌍 <b>Адрес прописки (англ)</b>\n"
        "Найдите: <code>Ukraine, 11111, Kyiv, Khreshchatyk str., bldg. 1, apt. 1</code>\n"
        "Замените на адрес на английском — <i>3 места</i>\n\n"

        "<b>📄 Шаг 3 — Конвертируйте обратно в PDF</b>\n"
        "После заполнения сохраните документ и преобразуйте его из Word в PDF:\n"
        "🔗 https://www.ilovepdf.com/ru/word_to_pdf\n\n"

        "<b>✍️ Шаг 4 — Подпишите PDF</b>\n"
        "Поставьте подпись в <b>6 местах</b> — внизу каждого из трёх договоров под своими данными:\n"
        "🔗 https://www.ilovepdf.com/ru/sign-pdf\n\n"

        "<b>📤 Шаг 5 — Отправьте готовый PDF своему менеджеру</b>"
    ),
    "en": (
        "✍️ <b>Instructions: Signing the Non-Disclosure Agreement</b>\n\n"

        "<b>📂 Step 1 — Open the document for editing</b>\n"
        "The contract is provided in PDF format. To fill in your details more easily, convert it to Word first:\n"
        "🔗 https://www.ilovepdf.com/ru/pdf_to_word\n\n"

        "<b>📋 Step 2 — Fill in your details in the document</b>\n\n"

        "🔢 <b>Tax ID number (IPN)</b>\n"
        "Find: <code>1234567890</code>\n"
        "Replace with your Tax ID — <i>20 places</i>\n\n"

        "📅 <b>Signing date</b>\n"
        "Find: <code>June 01, 2025</code>\n"
        "Replace with the actual date — <i>8 places</i>\n\n"

        "👤 <b>Full name (Ukrainian)</b>\n"
        "Find: <code>ІВАНОВ ІВАН ІВАНОВИЧ</code>\n"
        "Replace with your full name in Ukrainian — <i>6 places</i>\n\n"

        "🔤 <b>Full name (English)</b>\n"
        "Find: <code>IVANOV IVAN</code>\n"
        "Replace with your surname and first name in Latin letters — <i>6 places</i>\n\n"

        "🏠 <b>Registered address (Ukrainian)</b>\n"
        "Find: <code>Україна, 11111, Київ, вул. Хрещатик, буд. 1, кв. 1</code>\n"
        "Replace with your full address in Ukrainian — <i>3 places</i>\n\n"

        "🌍 <b>Registered address (English)</b>\n"
        "Find: <code>Ukraine, 11111, Kyiv, Khreshchatyk str., bldg. 1, apt. 1</code>\n"
        "Replace with your address in English — <i>3 places</i>\n\n"

        "<b>📄 Step 3 — Convert back to PDF</b>\n"
        "After filling in your details, save the document and convert it from Word back to PDF:\n"
        "🔗 https://www.ilovepdf.com/ru/word_to_pdf\n\n"

        "<b>✍️ Step 4 — Sign the PDF</b>\n"
        "Place your signature in <b>6 spots</b> — at the bottom of each of the three contracts under your details:\n"
        "🔗 https://www.ilovepdf.com/ru/sign-pdf\n\n"

        "<b>📤 Step 5 — Send the signed PDF to your manager</b>"
    ),
}

PROFILE_BTNS = get_all_variants("btn_profile")
FAQ_BTNS = get_all_variants("btn_faq")
TEST_BTNS = get_all_variants("btn_test")
MEETING_BTNS = get_all_variants("btn_meeting")
RATE_BTNS = get_all_variants("btn_rate")
ADMIN_BTNS = get_all_variants("btn_admin")