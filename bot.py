import telebot
import random
import time

# Твой токен
TOKEN = '9283760359:AAE9ZccRGZlyGekiJ1Vz5HTlUTMrCCHvg9Q'
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения времени последнего открытия (user_id: время)
cooldowns = {}
COOLDOWN_TIME = 3600 # 1 час в секундах

CARDS = [
    {"name": "Укради Брейнрот", "rarity": "⚪ Обычная", "url": "https://i.imgur.com/kY6h3p4.jpeg"},
    {"name": "Укради Брейнрот 2", "rarity": "⚪ Обычная", "url": "https://i.imgur.com/8QO9R7w.jpeg"},
    {"name": "Укради Яйцо", "rarity": "🔵 Редкая", "url": "https://i.imgur.com/B9Xq4kP.jpeg"},
    {"name": "Туалет Тауэр Дефенс", "rarity": "🟣 Эпическая", "url": "https://i.imgur.com/9r6Qx4d.jpeg"},
    {"name": "Бросить вещи и людей", "rarity": "🟡 Легендарная", "url": "https://i.imgur.com/yX7Hq2e.jpeg"}
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Напиши /card, чтобы открыть карточку! Ждать нужно 1 час.")

@bot.message_handler(commands=['card'])
def send_card(message):
    user_id = message.from_user.id
    current_time = time.time()

    # Проверяем, есть ли юзер в кулдауне
    if user_id in cooldowns:
        time_passed = current_time - cooldowns[user_id]
        if time_passed < COOLDOWN_TIME:
            remaining = int(COOLDOWN_TIME - time_passed)
            minutes = remaining // 60
            seconds = remaining % 60
            bot.send_message(message.chat.id, f"⏳ Подожди еще {minutes} мин. {seconds} сек. прежде чем открывать новую карту!")
            return

    # Если кулдаун прошел (или его не было) — выдаем карту
    chance = random.randint(1, 100)
    
    if chance <= 3: rarity = "Легендарная"
    elif chance <= 15: rarity = "Эпическая"
    elif chance <= 40: rarity = "Редкая"
    else: rarity = "Обычная"

    possible_cards = [card for card in CARDS if rarity in card["rarity"]]
    
    if possible_cards:
        chosen = random.choice(possible_cards)
        try:
            bot.send_photo(
                message.chat.id, 
                chosen["url"], 
                caption=f"✨ Вы получили карту!\nИмя: {chosen['name']}\nРедкость: {chosen['rarity']}"
            )
            # Записываем время открытия
            cooldowns[user_id] = current_time
        except Exception:
            bot.send_message(message.chat.id, "Ошибка: не удалось загрузить картинку.")

print("Бот запущен!")
bot.polling(none_stop=True)
