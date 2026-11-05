import telebot
import random
import time
import os
import threading
import requests
from flask import Flask

# --- НАСТРОЙКИ ---
TOKEN = 'ТВОЙ_ТОКЕН_ЗДЕСЬ'  # ВСТАВЬ СВОЙ ТОКЕН В КАВЫЧКИ!
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

cooldowns = {}
COOLDOWN_TIME = 3600 # 1 час

# --- КАРТОЧКИ С ID ИГР ROBLOX ---
CARDS = [
    # ⚪ Обычные
    {"name": "Steal a Brainrot", "rarity": "Обычная", "id": "109983668079237"},
    {"name": "Adopt Me!", "rarity": "Обычная", "id": "920587237"},
    {"name": "Brookhaven RP", "rarity": "Обычная", "id": "4924922222"},
    {"name": "Grow a Garden", "rarity": "Обычная", "id": "124347175076625"},
    {"name": "Work at a Pizza Place", "rarity": "Обычная", "id": "192800"},

    # 🔵 Редкие
    {"name": "Blox Fruits", "rarity": "Редкая", "id": "2753915549"},
    {"name": "Murder Mystery 2", "rarity": "Редкая", "id": "142823291"},
    {"name": "Pet Simulator 99", "rarity": "Редкая", "id": "8737899170"},
    {"name": "Dress To Impress", "rarity": "Редкая", "id": "15101393012"},

    # 🟣 Эпические
    {"name": "DOORS", "rarity": "Эпическая", "id": "6516141723"},
    {"name": "99 Nights in the Forest", "rarity": "Эпическая", "id": "118026778465800"},
    {"name": "RIVALS", "rarity": "Эпическая", "id": "17625359962"},

    # 🟡 Легендарные
    {"name": "Tower of Hell", "rarity": "Легендарная", "id": "1962086868"},
    {"name": "The Strongest Battlegrounds", "rarity": "Легендарная", "id": "10701666824"},
    {"name": "Jailbreak", "rarity": "Легендарная", "id": "606849621"}
]

def get_random_card(user_id):
    chance = random.randint(1, 100)
    if chance <= 3: rarity = "Легендарная"
    elif chance <= 15: rarity = "Эпическая"
    elif chance <= 40: rarity = "Редкая"
    else: rarity = "Обычная"

    possible_cards = [card for card in CARDS if card["rarity"] == rarity]
    
    if possible_cards:
        chosen = random.choice(possible_cards)
        # Получаем картинку напрямую с сервера Roblox
        img_api_url = f"https://thumbnails.roblox.com/v1/games/icons?universeIds={chosen['id']}&size=512x512&format=Png&isCircular=false"
        
        try:
            response = requests.get(img_api_url, timeout=10).json()
            if response.get('data'):
                real_image_url = response['data'][0]['imageUrl']
                caption = f"✨ Вы получили карту!\nИмя: {chosen['name']}\nРедкость: {chosen['rarity']}"
                return real_image_url, caption
            else:
                return None, "Не удалось найти картинку для этой игры."
        except Exception as e:
            return None, f"Ошибка при загрузке картинки: {e}"
    
    return None, "Карт такой редкости нет."

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Напиши /card, чтобы открыть карточку!\n\nИли напиши /timer 60, чтобы бот сам выдал карту через 60 минут.")

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

    img_url, caption = get_random_card(user_id)
    
    if img_url:
        try:
            bot.send_photo(message.chat.id, img_url, caption=caption)
            cooldowns[user_id] = current_time
        except Exception:
            bot.send_message(message.chat.id, "Ошибка: не удалось отправить фото.")
    else:
        bot.send_message(message.chat.id, caption)

@bot.message_handler(commands=['timer'])
def set_timer(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "Напиши так: /timer 60 (где 60 - количество минут).")
            return
        
        minutes = int(args[1]) seconds = minutes * 60
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        bot.send_message(chat_id, f"⏰ Таймер установлен на {minutes} мин. Я сам выдам тебе карту, когда время выйдет!")
        
        def timer_thread():
            time.sleep(seconds)
            try:
                if user_id in cooldowns:
                    del cooldowns[user_id]
                
                img_url, caption = get_random_card(user_id)
                if img_url:
                    bot.send_photo(chat_id, img_url, caption=f"🔔 Таймер сработал! Ты получаешь карту:\n{caption}")
                    cooldowns[user_id] = time.time()
                else:
                    bot.send_message(chat_id, f"🔔 Таймер сработал! Но произошла ошибка: {caption}")
            except Exception:
                pass

        threading.Thread(target=timer_thread).start()
        
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка! Напиши число. Например: /timer 60")

@app.route('/')
def health():
    return "Bot is alive!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host='0.0.0.0', port=port)
