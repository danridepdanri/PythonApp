from email import message
import html
import os
import logging
from multiprocessing import context
import random
import telebot
from telegram import Update
from telegram.ext import MessageHandler, filters, CallbackContext
from datetime import datetime, timedelta
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from enum import Enum
import json
import datetime
from datetime import datetime
import pytz
import wikipediaapi
import requests
import sqlite3
from bs4 import BeautifulSoup
headers = {
    'User-Agent': 'YourBotName/1.0 (https://your-bot-website.com/)'
}
if not os.path.exists('voice_messages'):
    os.makedirs('voice_messages')
user_mood = {}



emoji_button2 = "🗑️"
emoji_button1 = "🤬"
# Настройки логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot("6019447827:AAHKxH3nkpKlYoXczNDCOlWahxsnaKadp8A")
user_states = {}
cooldowns = {}
cooldown_time =  10
# Добавьте хендлер для реагирования на все сообщения от определенного пользователя
START, PLAYING = range(2)
NUM_BOXES = 4
correct_number = random.randint(1, NUM_BOXES)
#wiki_wiki = wikipediaapi.Wikipedia('ru')  # Создайте объект Wikipedia для английской Википедии
idById = 0
conn = sqlite3.connect('nicknames.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS form (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        prefix TEXT
    )
''')
conn.commit()

# Функция для извлечения префикса пользователя из базы данных
def get_prefix(user_id):
    cursor.execute("SELECT prefix FROM form WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

# Функция для добавления пользователя в таблицу 'form'
def add_user_to_form(user_id, prefix):
    cursor.execute("INSERT INTO form (user_id, prefix) VALUES (?, ?)", (user_id, prefix))
    conn.commit()

# Закрываем соединение с базой данных
conn.close()
@bot.message_handler(commands=['kick'])
def kick_user(message):
    user_id = message.from_user.id
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if len(message.text.split()) >= 2:
            user_to_kick = message.text.split()[1]
            # Проверьте, имеет ли пользователь право использовать эту команду
            if user_id == 514518947:  # Замените на идентификатор авторизованного пользователя
                # Извлеките префикс из базы данных
                prefix = get_prefix(user_to_kick)  # Замените на функцию извлечения данных из вашей базы данных
                if prefix:
                    # Отправьте сообщение с командой /kick пользователю
                    bot.send_message(user_to_kick, f"/kick {user_to_kick} // {prefix}")

                    # Создайте инлайн-клавиатуру для принятия или отклонения формы
                    keyboard = InlineKeyboardMarkup()
                    accept_button = InlineKeyboardButton("Принять форму", callback_data=f"accept_form_{user_to_kick}")
                    reject_button = InlineKeyboardButton("Отказать форму", callback_data=f"reject_form_{user_to_kick}")
                    keyboard.add(accept_button, reject_button)

                    # Отправьте сообщение в группу
                    bot.send_message(message.chat.id, f"@{user_to_kick} Вас кикнули! :)", reply_markup=keyboard)
                else:
                    bot.send_message(message.chat.id, "Префикс пользователя не найден в базе данных.")
            else:
                bot.send_message(message.chat.id, "У вас нет прав на использование этой команды.")
        else:
            bot.send_message(message.chat.id, "Использование: /kick @имя_пользователя")
    else:
        bot.send_message(message.chat.id, "Эта команда доступна только в группах и супергруппах.")

# Добавьте обработчик обратного вызова для принятия или отклонения формы
@bot.callback_query_handler(func=lambda call: call.data.startswith(("accept_form_", "reject_form_")))
def handle_form_response(call):
    user_id = call.from_user.id
    if user_id == 514518947:  # Замените на идентификатор авторизованного пользователя
        response = call.data.split("_")
        user_to_kick = response[2]
        if response[0] == "accept_form":
            # Обработайте случай, когда форма принимается
            bot.send_message(call.message.chat.id, f"Форма @{user_to_kick} принята!")
        elif response[0] == "reject_form":
            # Обработайте случай, когда форма отклоняется
            bot.send_message(call.message.chat.id, f"Форма @{user_to_kick} отклонена.")
    else:
        bot.send_message(call.message.chat.id, "У вас нет прав на обработку этой формы.")

# Добавьте команду для добавления пользователя в таблицу 'form'
@bot.message_handler(commands=['add_form'])
def add_form(message):
    user_id = message.from_user.id
    if user_id == 514518947:  # Замените на идентификатор авторизованного пользователя
        if len(message.text.split()) >= 2:
            user_to_add = message.text.split()[1]
            pref = message.text.split()[2]
            # Добавьте пользователя в таблицу 'form' в базе данных
            add_user_to_form(user_to_add, pref)  # Замените на функцию вставки данных в вашу базу данных
            bot.send_message(message.chat.id, f"@{user_to_add} добавлен в таблицу 'form'.")
        else:
            bot.send_message(message.chat.id, "Использование: /add_form @имя_пользователя")
    else:
        bot.send_message(message.chat.id, "У вас нет прав на использование этой команды.")
@bot.message_handler(commands=['rnd'])
def get_random_nickname(message):
    user_id = message.from_user.id
    if user_id in cooldowns and (datetime.now() - cooldowns[user_id]).total_seconds() < 180:
        remaining_time = 180 - (datetime.now() - cooldowns[user_id]).total_seconds()
        bot.send_message(message.chat.id, f"Подождите {int(remaining_time)} секунд перед повторным использованием команды.")
    else:
        cooldowns[user_id] = datetime.now()
        conn = sqlite3.connect('nicknames.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nickname FROM name ORDER BY RANDOM() LIMIT 1")
    
    
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        if result:
            random_nickname = result[0]
            bot.send_message(message.chat.id, f"Случайный никнейм: {random_nickname}")
        else:
            bot.send_message(message.chat.id, "Никнеймы ещё не были добавлены. Используйте /add_nickname для добавления.")
@bot.message_handler(commands=['add_nickname'])
def add_nickname(message):
        args = message.text.split('*', 3) 
        nickname = args[2]
        conn = sqlite3.connect('nicknames.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO name (nickname) VALUES (?)", (nickname,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"Никнейм '{nickname}' добавлен.")
@bot.message_handler(commands=['wiki'])  # Добавляем обработчик для команды /wiki
def wiki_search(update: Update) -> None:
    search_query = update.text[6:] # Get text from the user's message

    # Perform a search on Wikipedia using the custom User-Agent header
    url = f'https://ru.wikipedia.org/wiki/{search_query}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        first_paragraph = soup.find('p').get_text()

        # Provide a link to the Wikipedia page
        article_link = f'https://ru.wikipedia.org/wiki/{search_query}'

        # Send the response back to the user
        response_text = f'Первый абзац запрашиваемой статьи:\n{first_paragraph}\n\nLink: {article_link}'
        bot.send_message(update.chat.id, response_text)
    else:
        bot.send_message(update.chat.id, 'Article not found. Please try another query.')
@bot.message_handler(commands=['set_mood'])
def set_mood(message):
    if message.from_user.id == 514518947:
         args = message.text.split(' ', 2) 
         user_id = message.from_user.id
         if len(args) < 3:
            bot.send_message(message.chat.id, "Используйте команду /set_mood в формате: /set_mood @username новое_настроение")
            return
         username = args[1]
         new_mood = args[2]
         user_mood[user_id] = {"username": username, "mood": new_mood}
        
         bot.send_message(message.chat.id, f"Ссылка на ваше настроение сохранена: {user_mood[user_id]}")
    else: 
        bot.send_message(message.chat.id, f"В доступе отказано")
@bot.message_handler(commands=['mood'])
def mood(message):
    user_id = 514518947  # ID пользователя, для которого вы хотите показать настроение
    if user_id in user_mood:
        mood_link = user_mood[user_id]["mood"]  # Получаем настроение из словаря
        bot.send_message(message.chat.id, f"Настроение создателя как: {mood_link}")
    else:
        bot.send_message(message.chat.id, "Настроение создателя не установлено.")
@bot.message_handler(commands=['help'])
def help(message):
        
        bot.send_message(message.chat.id, f"""Доступные команды:\n
        /start - запуск бота
        /set_mood - установка настроения
        /mood - отображение настроения
        /cs - созвать в кс
        /box - небольшая игра
        /add_jokes - добавление шуток
        /help - помощь
        /rofl - шутки и послать ганка в мусорку""")    
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == 514518947:
        
        user_name = message.from_user.username
        bot.send_message(message.chat.id, f'''Deploy v.4.0.5
        Upd. - permission on /rofl
        + joke on all users on rofl
        + main func for user 556316729 on /rofl are upd
        ''')
        idById = message.chat.id
        print(idById)
       
    elif message.from_user.id == 556316729:
        bot.send_message(message.chat.id, "Руслана Александровна, проверьте личные сообщения")
        user_name = message.from_user.username

        # Отправляем сообщение в ЛС пользователю
        bot.send_message(message.from_user.id,
                         f"Вы написали в группе комманду /start \nА вот ваш лапулик решил сделать приятно, это вам от вашего кодера лапулика \nP/S: он не попокодер :) \n открой ссылочку: ")
    elif message.from_user.id == 1289540422:
        bot.send_message(message.chat.id, "Балдеев отвали")
    else: 
       bot.send_message(message.chat.id, f'Привет, {message.from_user.username} Я бот для этого чата, я обновляюсь очень часто. Вот кстати мой функционал:\n rofl - команда для шуток, так же можно выбросить Ганка в мусорку')
@bot.message_handler(commands=['text'])
def text(message):
     args = message.text.split('*', 3) 
     user_id = message.from_user.id
     if len(args) < 2:
        bot.send_message(message.chat.id, "Чет не то, удачи")
        return
     text = args[2]
     
    
     bot.send_message(-1001908270243, f"{text}")
@bot.message_handler(commands=['music'])   
def music(message):
     args = message.text.split(' ', 3) 
     user_id = message.from_user.id
     if len(args) < 3:
        bot.send_message(message.chat.id, "Чет не то, удачи")
        return
     music = args[2]
     replay = int(args[3])
     if replay == 0:

        bot.send_message(-1001908270243, f"Сейчас играет: {music}")
     elif replay == 1:
         bot.send_message(-1001908270243, f"Сейчас играет на повторе: {music}")
def start_game(user_id):
    # Генерируем новый правильный номер для каждой новой игры
    correct_number = random.randint(1, NUM_BOXES)
    user_states[user_id] = {"state": PLAYING, "correct_number": correct_number}        
def end_game(user_id):
  
    del user_states[user_id]
@bot.message_handler(commands=['add_jokes'])
def add_jokes(message):
        bot.send_message(message.chat.id, "Введите новую шутку:")
        bot.register_next_step_handler(message, process_new_joke)   
@bot.message_handler(commands=['box'])
def box(message):
    user_id = message.from_user.id

    if user_id in cooldowns and (datetime.now() - cooldowns[user_id]).total_seconds() < cooldown_time:
        remaining_time = cooldown_time - (datetime.now() - cooldowns[user_id]).total_seconds()
        bot.send_message(message.chat.id, f"Подождите {int(remaining_time)} секунд перед повторным использованием команды.")
    else:
        cooldowns[user_id] = datetime.now()
        start_game(user_id)
        
        markup = types.InlineKeyboardMarkup(row_width=3)
        for i in range(1, 5):
            button_text = f"📦 Коробка {i}"
            button = types.InlineKeyboardButton(button_text, callback_data=f"box_{i}")
            markup.add(button)
        
        bot.send_message(message.chat.id, "Выберите коробку:", reply_markup=markup)
@bot.callback_query_handler(func=lambda call: True)
def check_choice(call):
    user_id = call.from_user.id
    sticker_id1 = 'CAACAgQAAxkBAAEKaJtlFaNf688hGMCYvKPRlQEUs07r5gACvQ0AAvKAIVBa2Qxq82G8kzAE'
    sticker_id2 = 'CAACagQAAxkBAAEKaJ5lFaNlOPLMzzuZfqG1W7QyJ9TooQACNwkAAjhC8FDVwuIl_DqVEjAE'
    if call.data == 'rofl_button1' and call.from_user.id == 556316729:
        bot.send_message(call.message.chat.id, "@Fighter_Invisible_Front, беги, сковородка за тобой")
        bot.send_sticker(call.message.chat.id, sticker_id1)
    elif call.data == 'rofl_button2' and call.from_user.id == 556316729:
        bot.send_message(call.message.chat.id, "@GANK91, @hhhwwmm вас отправили в мусорку")
        bot.send_sticker(call.message.chat.id, sticker_id2)
   
    else:
        choice = call.data.split('_')[1]
        if user_id in user_states and user_states[user_id]["state"] == PLAYING:
            correct_number = user_states[user_id]["correct_number"]
            if choice == str(correct_number):
                bot.answer_callback_query(call.id, text="Правильно! Вы нашли правильную коробку!")
            else:
                bot.answer_callback_query(call.id, text="Неправильно. Попробуйте ещё раз!")
        
            end_game(user_id)
        else:
            bot.answer_callback_query(call.id, text="Игра не активна. Нажмите /box, чтобы начать новую игру.")
@bot.message_handler(commands=['rofl'])
def rofl(message):
    
    if message.from_user.id == 556316729:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button1 = types.InlineKeyboardButton(emoji_button1, callback_data='rofl_button1')
        button2 = types.InlineKeyboardButton(emoji_button2, callback_data='rofl_button2')
        keyboard.add(button1, button2)
        bot.send_message(message.chat.id, "Руслана Александровна, приветствую", reply_markup=keyboard)
        jokes = load_jokes()  # Загружаем шутки из JSON-файла
        if jokes:
            random_joke = random.choice(jokes)

            bot.send_message(message.chat.id, random_joke)
    else: 
        jokes = load_jokes()  # Загружаем шутки из JSON-файла
        if jokes:
            random_joke = random.choice(jokes)

            bot.send_message(message.chat.id, random_joke)
        else:
            bot.send_message(message.chat.id, "У меня нет шуток. Добавьте их командой /add_joke")
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    sticker_id1 = 'CAACAgQAAxkBAAEKaJtlFaNf688hGMCYvKPRlQEUs07r5gACvQ0AAvKAIVBa2Qxq82G8kzAE'
    sticker_id2 = 'CAACagQAAxkBAAEKaJ5lFaNlOPLMzzuZfqG1W7QyJ9TooQACNwkAAjhC8FDVwuIl_DqVEjAE'
    if message.text == emoji_button1 and message.from_user.id == 556316729:
        
        bot.send_message(message.chat.id, "@Fighter_Invisible_Front, беги, сковородка за тобой")
    elif message.text == emoji_button2 and message.from_user.id == 556316729:
        bot.send_sticker(message.chat.id, sticker_id2)
        bot.send_message(message.chat.id, "@GANK91, @hhhwwmm вас отправили в мусорку")
    elif message.text == emoji_button2 and message.from_user.id == 1143880107:
        bot.send_sticker(message.chat.id, sticker_id2)
        bot.send_message(message.chat.id, "Хаха, лох на Захаре, сам себя выкинул")
def is_valid_time():
    # Устанавливаем часовой пояс Москвы
    moscow_tz = pytz.timezone('Europe/Moscow')
    
    # Получаем текущее время в Московском времени
    current_time = datetime.datetime.now(moscow_tz).time()
    
    # Устанавливаем время начала и окончания периода
    start_time = datetime.time(17, 0)  # 17:00
    end_time = datetime.time(21, 0)    # 21:00
    
    # Проверяем, находится ли текущее время в допустимом диапазоне
    return start_time <= current_time < end_time
def process_new_joke(message):
    new_joke = message.text
    jokes = load_jokes()
    jokes.append(new_joke)
    save_jokes(jokes)
    bot.send_message(message.chat.id, "Шутка добавлена.")
def load_jokes():
    try:
        with open('jokes.json', 'r', encoding='utf-8', errors='ignore') as file:
            data = json.load(file)
            return data.get('jokes', [])
    except FileNotFoundError:
        return []
def save_jokes(jokes):
    with open('jokes.json', 'w', encoding='utf-8') as file:
        json.dump({'jokes': jokes}, file, ensure_ascii=False, indent=4)
if __name__ == "__main__":
    
    bot.polling(context)
