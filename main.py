import telebot
from telebot import types
import random
import time
import threading
import schedule
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sqlite3
from user_logger import log_user_data, read_logs

bot = telebot.TeleBot('8394851015:AAGlhiH0MH55SwnDqLxpItVfSkZKDx_o9go')

# Хранение данных о настроении пользователей
user_data = {}
mood_data = {}

# Чтение сообщений из файлов
def read_messages(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.readlines()

def read_mentalhelp_messages(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    entries = content.strip().split("\n\n")
    messages = []

    for entry in entries:
        lines = entry.split("\n")
        author = lines[0].split(":")[1].strip()
        text = lines[1].split(":")[1].strip()
        link = lines[2].split(":")[1].strip() if "Ссылка:" in lines[2] else None
        photo = lines[3].split(":")[1].strip() if "Фото:" in lines[3] else None
        messages.append((author, text, link, photo))

    return messages

# Сообщения для отправки
messages = read_messages('mess.txt')
positive_messages = read_messages('messpositive.txt')
negative_messages = read_messages('messnegative.txt')
mentalhelp_messages = read_mentalhelp_messages('mentalhelp.txt')

# Функция для отправки запланированных сообщений
def send_scheduled_messages():
    now = datetime.now().strftime("%H:%M")
    for user_id, data in user_data.items():
        if 'reminder_time' in data and data['reminder_time'] == now:
            # Отправка случайного сообщения из mess.txt
            random_message = random.choice(messages).strip()
            bot.send_message(user_id, random_message)

            # Отправка сообщения /mentalstate
            send_mood_message(user_id, f'Какое у тебя настроение сейчас?')

def send_mood_message(user_id, message):
    markup = types.InlineKeyboardMarkup(row_width=4)
    btn1 = types.InlineKeyboardButton("🟢", callback_data="mood_green")
    btn2 = types.InlineKeyboardButton("🟡", callback_data="mood_yellow")
    btn3 = types.InlineKeyboardButton("🟠", callback_data="mood_orange")
    btn4 = types.InlineKeyboardButton("🔴", callback_data="mood_red")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(user_id, message, reply_markup=markup)

def send_message_with_image(user_id, message, author=None, link=None, image_path=None):
    full_message = message
    if author:
        full_message += f"\n\nАвтор: {author}"
    if link:
        full_message += f"\nСсылка: {link}"

    if image_path:
        with open(image_path, 'rb') as img:
            bot.send_photo(user_id, img, caption=full_message)
    else:
        bot.send_message(user_id, full_message)

# Планировщик задач
def schedule_messages():
    schedule.every().day.at("20:00").do(send_scheduled_messages)
    schedule.every().day.at("21:00").do(send_scheduled_messages)
    schedule.every().day.at("22:00").do(send_scheduled_messages)
    schedule.every().day.at("23:00").do(send_scheduled_messages)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def main(message):
    global user_data
    cat1 = open('cat1.jpg', 'rb')
    bot.send_photo(message.chat.id, cat1)
    # Проверяем, есть ли данные о настроениях для текущего пользователя
    if message.from_user.id not in mood_data:
        mood_data[message.from_user.id] = {}

        # Генерируем тестовые данные за последний месяц
        today = datetime.now().date()
        for i in range(30):  # Данные за последние 30 дней
            mood_data[message.from_user.id][today - timedelta(days=i)] = random.choice(
                ['green', 'yellow', 'orange', 'red'])
    user_name = user_data.get(message.from_user.id, {}).get('name', message.from_user.first_name)
    time.sleep(2)
    bot.send_message(message.chat.id, f'Привет, {user_name} 👋\n\nЯ бот для поддержки твоего эмоционального состояния.')
    time.sleep(5)
    bot.send_message(message.chat.id,
                     'Каждый вечер я буду интересоваться твоим настроением.\nЯ умею распознавать 4 настроения:\n\n'
                     '🟢 — день был великолепен, лучше и представить нельзя\n'
                     '🟡 — вариант для хорошего дня, в котором были небольшие неприятности\n'
                     '🟠 — день мог бы быть сильно лучше, но еще не все потеряно\n'
                     '🔴 — день был хуже некуда, тебе срочно нужна поддержка')
    time.sleep(9)
    bot.send_message(message.chat.id,
                     'Если ты выберешь 🟠 и 🔴 настроение, тогда и начнется самое интересное 🙃\n\n'
                     'Я подберу тебе ободряющее сообщение от другого пользователя, у которого настроение '
                     'было отличным — и он захотел поделиться им с тобой')
    time.sleep(7)
    bot.send_message(message.chat.id,
                     'И наоборот — если у тебя выдался 🟢 и 🟡 день, '
                     'то ты сможешь написать свое позитивное сообщение.\n\n'
                     'Когда твое сообщение пройдет модерацию, я буду показывать его тем, кому это сейчас важно')
    time.sleep(7)
    bot.send_message(message.chat.id, 'Вот такая простая магия ✨')
    time.sleep(2)
    bot.send_message(message.chat.id,
                     'Давай познакомимся с тобой поближе! Не переживай — '
                     'ты сможешь отредактировать эти данные позднее 🙃')

    # Создание inline клавиатуры с двумя кнопками
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Это моё имя", callback_data="confirm_name")
    btn2 = types.InlineKeyboardButton("Ввести другое", callback_data="enter_other_name")
    markup.add(btn1, btn2)

    time.sleep(3)
    bot.send_message(message.chat.id, f'Тебя зовут {user_name}? Подтверди своё имя или введи другое',
                     reply_markup=markup)
    # Добавление тестовых данных о настроении за последние 7 дней
    if message.from_user.id not in mood_data:
        mood_data[message.from_user.id] = {}
    today = datetime.now().date()
    test_moods = ['green', 'yellow', 'orange', 'red', 'green', 'yellow', 'orange']
    for i in range(7):
        mood_data[message.from_user.id][today - timedelta(days=i)] = test_moods[i]

# Обработчик команды /mentalstate
@bot.message_handler(commands=['mentalstate'])
def mentalstate(message):
    send_mood_message(message.chat.id, f'Какое у тебя настроение сейчас?')

# Обработчик callback запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global user_data
    user_id = call.from_user.id
    user_name = user_data.get(user_id, {}).get('name', call.from_user.first_name)

    if call.data.startswith("mood_"):
        mood = call.data.split("_")[-1]
        if user_id not in mood_data:
            mood_data[user_id] = {}
        mood_data[user_id][datetime.now().date()] = mood

        # Логирование настроения
        log_user_data(user_id, user_name, mood)

        if mood in ["green", "yellow"]:
            mood_messages = read_messages('messpositive.txt')
        else:
            mood_messages = read_messages('messnegative.txt')

        message = random.choice(mood_messages)
        bot.send_message(call.message.chat.id, message)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        if mood in ["orange", "red"]:
            help_message = random.choice(mentalhelp_messages)
            author, text, link, photo = help_message
            send_message_with_image(call.message.chat.id, text, author=author, link=link, image_path=photo)


@bot.message_handler(commands=['allstats'])
def all_statistics(message):
    logs = read_logs()
    if not logs:
        bot.send_message(message.chat.id, "Данных пока нет 🥺")
        return

    bot.send_message(message.chat.id, "Вот данные о всех пользователях:")
    bot.send_message(message.chat.id, "".join(logs[-10:]))  # Вывод последних 10 записей


@bot.message_handler(commands=['feedback'])
def main(message):
    bot.send_message(message.chat.id,
                     'Если ты вдруг не нашёл ответ на свой вопрос или столкнулся с трудностями, '
                     'можешь написать разработчику лично — @tokiogus ☺️')

@bot.message_handler(commands=['isbotworking'])
def main(message):
    bot.send_message(message.chat.id, 'Сейчас бот работает исправно.\n\nНе переживай 🥺')

@bot.message_handler(commands=['fillform'])
def main(message):
    bot.send_message(message.chat.id, 'Спасибо, что помогаешь! Ниже ссылка на форму. Пройди ее — '
                                      'и я буду делиться твоей поддержкой с другими пользователями:\n'
                                      'https://docs.google.com/forms/d/e/'
                                      '1FAIpQLSdK_VNOuWz8TGQdsawfi1wuhXHv9zBHK75JsHSecXwDMcjGEg/viewform?usp=sf_link')

@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, f'Запутался 🥺? Смотри, вот, что я умею:\n\n'
                                      f'/start — начать общение с ботом\n\n'
                                      f'/fillform — написать сообщение со словами поддержки для грустных людей\n\n'
                                      f'/stata — тут можно посмотреть свой календарь настроений за прошедшие дни. '
                                      f'Выясни свои самые зеленые и красные дни!\n\n'
                                      f'/mentalstate - так ты можешь отметить своё настроение за день\n\n'
                                      f'/feedback — написать разработчикам напрямую. '
                                      f'Они рады любым жалобам и предложениям\n\n'
                                      f'/isbotworking — проверить, работает ли бот\n\n'
                                      f'/help — помощь')
def handle_mental_help(message):
    help_message = random.choice(mentalhelp_messages)
    author, text, link, photo = help_message
    if photo:
        send_message_with_image(message.chat.id, text, author=author, link=link, image_path=photo)
    else:
        send_message_with_image(message.chat.id, text, author=author, link=link)

def get_new_name(message):
    user_id = message.from_user.id
    user_name = message.text
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['name'] = user_name
    bot.send_message(message.chat.id, f'Приятно познакомиться, {user_name}!')
    ask_for_reminder_time(message)

def ask_for_reminder_time(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("20:00", callback_data="set_time_20:00")
    btn2 = types.InlineKeyboardButton("21:00", callback_data="set_time_21:00")
    btn3 = types.InlineKeyboardButton("22:00", callback_data="set_time_22:00")
    btn4 = types.InlineKeyboardButton("23:00", callback_data="set_time_23:00")
    markup.add(btn1, btn2, btn3, btn4)
    time.sleep(2)
    bot.send_message(message.chat.id, 'В котором часу тебе напоминать о настроении?', reply_markup=markup)

def send_initial_commands(message):
    global user_data
    user_name = user_data.get(message.from_user.id, {}).get('name', message.from_user.first_name)
    time.sleep(3)
    bot.send_message(message.chat.id, f'Давай быстренько расскажу тебе, что я умею:\n\n'
                                      f'/start — начать общение с ботом\n\n'
                                      f'/fillform — написать сообщение со словами поддержки для грустных людей\n\n'
                                      f'/stata — тут можно посмотреть свой календарь настроений за прошедшие дни. '
                                      f'Выясни свои самые зеленые и красные дни!\n\n'
                                      f'/mentalstate - так ты можешь отметить своё настроение за день\n\n'
                                      f'/feedback — написать разработчикам напрямую. '
                                      f'Они рады любым жалобам и предложениям\n\n'
                                      f'/isbotworking — проверить, работает ли бот\n\n'
                                      f'/help — помощь')
    bot.send_message(message.chat.id,
                     f'Давай создадим твоё первое сообщение для тех, у кого был плохой день.\n\n'
                     f'Нажимай на ссылку ниже — по ней откроется небольшая форма. '
                     f'Помни, что твоё сообщение прочитает человек, которому нужна максимальная поддержка 🙌\n\n'
                     f'https://docs.google.com/forms/d/e/'
                     f'1FAIpQLSdK_VNOuWz8TGQdsawfi1wuhXHv9zBHK75JsHSecXwDMcjGEg/viewform?usp=sf_link')

# Обработчик команды /stata
@bot.message_handler(commands=['stata'])
def send_statistics(message):
    user_id = message.from_user.id
    if user_id not in mood_data:
        bot.send_message(message.chat.id, "Пока что я не могу проанализировать твоё настроение 🥺")
        return

    bot.send_message(message.chat.id, "Подгружаю статистику, немного терпения")

    moods = mood_data[user_id].values()

    mood_colors = {'green': '#2baf80', 'yellow': '#cec576', 'orange': '#cd7a36', 'red': '#cb5f5f'}
    mood_labels = {'green': 'Отличный', 'yellow': 'Хороший', 'orange': 'Так себе', 'red': 'Плохой'}
    mood_count = {mood: list(moods).count(mood) for mood in mood_colors}

    # Создание круговой диаграммы
    labels = [mood_labels[mood] for mood in mood_colors]
    sizes = [mood_count[mood] for mood in mood_colors]
    colors = [mood_colors[mood] for mood in mood_colors]
    explode = (0.05, 0.05, 0.05, 0.05)  # "Выдвигаем" куски диаграммы

    plt.figure(figsize=(12, 10), facecolor='#202938')  # Задаем цвет фона
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140,
            textprops={'fontsize': 14, 'color': 'white', 'weight': 'bold'})  # Настройки текста внутри диаграммы
    plt.title("Круг настроений: какой у тебя был день?\n", color='#9f94ce', fontsize=24, weight='bold')  # Заголовок диаграммы
    plt.axis('equal')  # Отображение диаграммы в виде круга

    # Сохранение и отправка диаграммы
    plt.savefig('mood_pie_chart.png')
    pie_chart_img = open('mood_pie_chart.png', 'rb')
    bot.send_photo(message.chat.id, pie_chart_img)
    pie_chart_img.close()

@bot.message_handler()
def info(message):
    bot.send_message(message.chat.id, 'Не знаю эту команду 🙃\n\nНапиши /help, чтобы получить список команд')

# Запуск планировщика в отдельном потоке
threading.Thread(target=schedule_messages).start()
import telebot
from telebot import types
import random
import time
import threading
import schedule
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sqlite3

bot = telebot.TeleBot('7453970157:AAHTVEjsV0N9riIDpK4hnOR0LsHsHWFnetY')

# Хранение данных о настроении пользователей
user_data = {}
mood_data = {}

# Чтение сообщений из файлов
def read_messages(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.readlines()

def read_mentalhelp_messages(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    entries = content.strip().split("\n\n")
    messages = []

    for entry in entries:
        lines = entry.split("\n")
        author = lines[0].split(":")[1].strip()
        text = lines[1].split(":")[1].strip()
        link = lines[2].split(":")[1].strip() if "Ссылка:" in lines[2] else None
        photo = lines[3].split(":")[1].strip() if "Фото:" in lines[3] else None
        messages.append((author, text, link, photo))

    return messages

# Сообщения для отправки
messages = read_messages('mess.txt')
positive_messages = read_messages('messpositive.txt')
negative_messages = read_messages('messnegative.txt')
mentalhelp_messages = read_mentalhelp_messages('mentalhelp.txt')

# Функция для отправки запланированных сообщений
def send_scheduled_messages():
    now = datetime.now().strftime("%H:%M")
    for user_id, data in user_data.items():
        if 'reminder_time' in data and data['reminder_time'] == now:
            # Отправка случайного сообщения из mess.txt
            random_message = random.choice(messages).strip()
            bot.send_message(user_id, random_message)

            # Отправка сообщения /mentalstate
            send_mood_message(user_id, f'Какое у тебя настроение сейчас?')

def send_mood_message(user_id, message):
    markup = types.InlineKeyboardMarkup(row_width=4)
    btn1 = types.InlineKeyboardButton("🟢", callback_data="mood_green")
    btn2 = types.InlineKeyboardButton("🟡", callback_data="mood_yellow")
    btn3 = types.InlineKeyboardButton("🟠", callback_data="mood_orange")
    btn4 = types.InlineKeyboardButton("🔴", callback_data="mood_red")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(user_id, message, reply_markup=markup)

def send_message_with_image(user_id, message, author=None, link=None, image_path=None):
    full_message = message
    if author:
        full_message += f"\n\nАвтор: {author}"
    if link:
        full_message += f"\nСсылка: {link}"

    if image_path:
        with open(image_path, 'rb') as img:
            bot.send_photo(user_id, img, caption=full_message)
    else:
        bot.send_message(user_id, full_message)

# Планировщик задач
def schedule_messages():
    schedule.every().day.at("20:00").do(send_scheduled_messages)
    schedule.every().day.at("21:00").do(send_scheduled_messages)
    schedule.every().day.at("22:00").do(send_scheduled_messages)
    schedule.every().day.at("23:00").do(send_scheduled_messages)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def main(message):
    global user_data
    cat1 = open('cat1.jpg', 'rb')
    bot.send_photo(message.chat.id, cat1)
    # Проверяем, есть ли данные о настроениях для текущего пользователя
    if message.from_user.id not in mood_data:
        mood_data[message.from_user.id] = {}

        # Генерируем тестовые данные за последний месяц
        today = datetime.now().date()
        for i in range(30):  # Данные за последние 30 дней
            mood_data[message.from_user.id][today - timedelta(days=i)] = random.choice(
                ['green', 'yellow', 'orange', 'red'])
    user_name = user_data.get(message.from_user.id, {}).get('name', message.from_user.first_name)
    time.sleep(2)
    bot.send_message(message.chat.id, f'Привет, {user_name} 👋\n\nЯ бот для поддержки твоего эмоционального состояния.')
    time.sleep(5)
    bot.send_message(message.chat.id,
                     'Каждый вечер я буду интересоваться твоим настроением.\nЯ умею распознавать 4 настроения:\n\n'
                     '🟢 — день был великолепен, лучше и представить нельзя\n'
                     '🟡 — вариант для хорошего дня, в котором были небольшие неприятности\n'
                     '🟠 — день мог бы быть сильно лучше, но еще не все потеряно\n'
                     '🔴 — день был хуже некуда, тебе срочно нужна поддержка')
    time.sleep(9)
    bot.send_message(message.chat.id,
                     'Если ты выберешь 🟠 и 🔴 настроение, тогда и начнется самое интересное 🙃\n\n'
                     'Я подберу тебе ободряющее сообщение от другого пользователя, у которого настроение '
                     'было отличным — и он захотел поделиться им с тобой')
    time.sleep(7)
    bot.send_message(message.chat.id,
                     'И наоборот — если у тебя выдался 🟢 и 🟡 день, '
                     'то ты сможешь написать свое позитивное сообщение.\n\n'
                     'Когда твое сообщение пройдет модерацию, я буду показывать его тем, кому это сейчас важно')
    time.sleep(7)
    bot.send_message(message.chat.id, 'Вот такая простая магия ✨')
    time.sleep(2)
    bot.send_message(message.chat.id,
                     'Давай познакомимся с тобой поближе! Не переживай — '
                     'ты сможешь отредактировать эти данные позднее 🙃')

    # Создание inline клавиатуры с двумя кнопками
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Это моё имя", callback_data="confirm_name")
    btn2 = types.InlineKeyboardButton("Ввести другое", callback_data="enter_other_name")
    markup.add(btn1, btn2)

    time.sleep(3)
    bot.send_message(message.chat.id, f'Тебя зовут {user_name}? Подтверди своё имя или введи другое',
                     reply_markup=markup)
    # Добавление тестовых данных о настроении за последние 7 дней
    if message.from_user.id not in mood_data:
        mood_data[message.from_user.id] = {}
    today = datetime.now().date()
    test_moods = ['green', 'yellow', 'orange', 'red', 'green', 'yellow', 'orange']
    for i in range(7):
        mood_data[message.from_user.id][today - timedelta(days=i)] = test_moods[i]

# Обработчик команды /mentalstate
@bot.message_handler(commands=['mentalstate'])
def mentalstate(message):
    send_mood_message(message.chat.id, f'Какое у тебя настроение сейчас?')

# Обработчик callback запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global user_data
    user_id = call.from_user.id
    user_name = user_data.get(user_id, {}).get('name', call.from_user.first_name)

    if call.data.startswith("mood_"):
        mood = call.data.split("_")[-1]
        if user_id not in mood_data:
            mood_data[user_id] = {}
        mood_data[user_id][datetime.now().date()] = mood

        # Проверка на наличие имени пользователя
        if not user_name:
            user_name = f"User_{user_id}"

        # Логирование настроения
        try:
            log_user_data(user_id, user_name, mood)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка записи данных: {str(e)}")

        # Отправка сообщений в зависимости от настроения
        if mood in ["green", "yellow"]:
            mood_messages = read_messages('messpositive.txt')
        else:
            mood_messages = read_messages('messnegative.txt')

        message = random.choice(mood_messages)
        bot.send_message(call.message.chat.id, message)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        # Отправка сообщения поддержки, если настроение плохое
        if mood in ["orange", "red"]:
            help_message = random.choice(mentalhelp_messages)
            author, text, link, photo = help_message
            send_message_with_image(call.message.chat.id, text, author=author, link=link, image_path=photo)


@bot.message_handler(commands=['feedback'])
def main(message):
    bot.send_message(message.chat.id,
                     'Если ты вдруг не нашёл ответ на свой вопрос или столкнулся с трудностями, '
                     'можешь написать разработчику лично — @tokiogus ☺️')

@bot.message_handler(commands=['isbotworking'])
def main(message):
    bot.send_message(message.chat.id, 'Сейчас бот работает исправно.\n\nНе переживай 🥺')

@bot.message_handler(commands=['fillform'])
def main(message):
    bot.send_message(message.chat.id, 'Спасибо, что помогаешь! Ниже ссылка на форму. Пройди ее — '
                                      'и я буду делиться твоей поддержкой с другими пользователями:\n'
                                      'https://docs.google.com/forms/d/e/'
                                      '1FAIpQLSdK_VNOuWz8TGQdsawfi1wuhXHv9zBHK75JsHSecXwDMcjGEg/viewform?usp=sf_link')

@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, f'Запутался 🥺? Смотри, вот, что я умею:\n\n'
                                      f'/start — начать общение с ботом\n\n'
                                      f'/fillform — написать сообщение со словами поддержки для грустных людей\n\n'
                                      f'/stata — тут можно посмотреть свой календарь настроений за прошедшие дни. '
                                      f'Выясни свои самые зеленые и красные дни!\n\n'
                                      f'/mentalstate - так ты можешь отметить своё настроение за день\n\n'
                                      f'/feedback — написать разработчикам напрямую. '
                                      f'Они рады любым жалобам и предложениям\n\n'
                                      f'/isbotworking — проверить, работает ли бот\n\n'
                                      f'/help — помощь')
def handle_mental_help(message):
    help_message = random.choice(mentalhelp_messages)
    author, text, link, photo = help_message
    if photo:
        send_message_with_image(message.chat.id, text, author=author, link=link, image_path=photo)
    else:
        send_message_with_image(message.chat.id, text, author=author, link=link)

def get_new_name(message):
    user_id = message.from_user.id
    user_name = message.text
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['name'] = user_name
    bot.send_message(message.chat.id, f'Приятно познакомиться, {user_name}!')
    ask_for_reminder_time(message)

def ask_for_reminder_time(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("20:00", callback_data="set_time_20:00")
    btn2 = types.InlineKeyboardButton("21:00", callback_data="set_time_21:00")
    btn3 = types.InlineKeyboardButton("22:00", callback_data="set_time_22:00")
    btn4 = types.InlineKeyboardButton("23:00", callback_data="set_time_23:00")
    markup.add(btn1, btn2, btn3, btn4)
    time.sleep(2)
    bot.send_message(message.chat.id, 'В котором часу тебе напоминать о настроении?', reply_markup=markup)

def send_initial_commands(message):
    global user_data
    user_name = user_data.get(message.from_user.id, {}).get('name', message.from_user.first_name)
    time.sleep(3)
    bot.send_message(message.chat.id, f'Давай быстренько расскажу тебе, что я умею:\n\n'
                                      f'/start — начать общение с ботом\n\n'
                                      f'/fillform — написать сообщение со словами поддержки для грустных людей\n\n'
                                      f'/stata — тут можно посмотреть свой календарь настроений за прошедшие дни. '
                                      f'Выясни свои самые зеленые и красные дни!\n\n'
                                      f'/mentalstate - так ты можешь отметить своё настроение за день\n\n'
                                      f'/feedback — написать разработчикам напрямую. '
                                      f'Они рады любым жалобам и предложениям\n\n'
                                      f'/isbotworking — проверить, работает ли бот\n\n'
                                      f'/help — помощь')
    bot.send_message(message.chat.id,
                     f'Давай создадим твоё первое сообщение для тех, у кого был плохой день.\n\n'
                     f'Нажимай на ссылку ниже — по ней откроется небольшая форма. '
                     f'Помни, что твоё сообщение прочитает человек, которому нужна максимальная поддержка 🙌\n\n'
                     f'https://docs.google.com/forms/d/e/'
                     f'1FAIpQLSdK_VNOuWz8TGQdsawfi1wuhXHv9zBHK75JsHSecXwDMcjGEg/viewform?usp=sf_link')

# Обработчик команды /stata
@bot.message_handler(commands=['stata'])
def send_statistics(message):
    user_id = message.from_user.id
    if user_id not in mood_data:
        bot.send_message(message.chat.id, "Пока что я не могу проанализировать твоё настроение 🥺")
        return

    bot.send_message(message.chat.id, "Подгружаю статистику, немного терпения")

    moods = mood_data[user_id].values()

    mood_colors = {'green': '#2baf80', 'yellow': '#cec576', 'orange': '#cd7a36', 'red': '#cb5f5f'}
    mood_labels = {'green': 'Отличный', 'yellow': 'Хороший', 'orange': 'Так себе', 'red': 'Плохой'}
    mood_count = {mood: list(moods).count(mood) for mood in mood_colors}

    # Создание круговой диаграммы
    labels = [mood_labels[mood] for mood in mood_colors]
    sizes = [mood_count[mood] for mood in mood_colors]
    colors = [mood_colors[mood] for mood in mood_colors]
    explode = (0.05, 0.05, 0.05, 0.05)  # "Выдвигаем" куски диаграммы

    plt.figure(figsize=(12, 10), facecolor='#202938')  # Задаем цвет фона
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140,
            textprops={'fontsize': 14, 'color': 'white', 'weight': 'bold'})  # Настройки текста внутри диаграммы
    plt.title("Круг настроений: какой у тебя был день?\n", color='#9f94ce', fontsize=24, weight='bold')  # Заголовок диаграммы
    plt.axis('equal')  # Отображение диаграммы в виде круга

    # Сохранение и отправка диаграммы
    plt.savefig('mood_pie_chart.png')
    pie_chart_img = open('mood_pie_chart.png', 'rb')
    bot.send_photo(message.chat.id, pie_chart_img)
    pie_chart_img.close()

@bot.message_handler()
def info(message):
    bot.send_message(message.chat.id, 'Не знаю эту команду 🙃\n\nНапиши /help, чтобы получить список команд')

# Запуск планировщика в отдельном потоке
threading.Thread(target=schedule_messages).start()

bot.polling(none_stop=True)

bot.polling(none_stop=True)
