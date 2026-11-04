import telebot
import random
import time
import os
from flask import Flask

TOKEN = '9283760359:AAE9ZccRGZlyGekiJ1Vz5HTlUTMrCCHvg9Q'  # Вставь свой токен в кавычки!
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

cooldowns = {}
COOLDOWN_TIME = 3600

CARDS = [
    {"name": "Укради Брейнрот", "rarity": "Обычная", "url": "https://i.imgur.com/kY6h3p4.jpeg"},
    {"name": "Укради Яйцо", "rarity": "Редкая", "url": "https://i.imgur.com/B9Xq4kP.jpeg"},
    {"name": "Туалет Тауэр Дефенс", "rarity": "Эпическая", "url": "https://i.imgur.com/9r6Qx4d.jpeg"},
    {"name": "Бросить вещи и людей", "rarity": "Легендарная", "url": "https://i.imgur.com/yX7Hq2e.jpeg"}
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Напиши /card, чтобы открыть карточку!")

@bot.message_handler(commands=['card'])
def send_card(message):
    user_id = message.from_user.id
    current_time = time.time()
    if user_id in cooldowns:
        time_passed = current_time - cooldowns[user_id]
        if time_passed < COOLDOWN_TIME:
            remaining = int(COOLDOWN_TIME - time_passed)
            bot.send_message(message.chat.id, f"Подожди еще {remaining // 60} мин. {remaining % 60} сек.")
            return

    chance = random.randint(1, 100)
    if chance <= 3: rarity = "Легендарная"
    elif chance <= 15: rarity = "Эпическая"
    elif chance <= 40: rarity = "Редкая"
    else: rarity = "Обычная"

    possible_cards = [card for card in CARDS if rarity in card["rarity"]]
    if possible_cards:
        chosen = random.choice(possible_cards)
        try:
            bot.send_photo(message.chat.id, chosen["url"], caption=f"✨ Вы получили карту!\nИмя: {chosen['name']}\nРедкость: {chosen['rarity']}")
            cooldowns[user_id] = current_time
        except Exception:
            bot.send_message(message.chat.id, "Ошибка: не удалось загрузить картинку.")

@app.route('/')
def health():
    return "Bot is alive!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    import threading
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host='0.0.0.0', port=port)
