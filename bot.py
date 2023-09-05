import telebot
from telebot import types
import requests
from googletrans import Translator

bot = telebot.TeleBot('TOKEN_BOT')

user_states = {}
translator = Translator()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_states[user_id] = 'waiting_image'
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    item = types.KeyboardButton("Создать изображение")
    markup.add(item)
    bot.send_message(message.chat.id, "Привет! Я бот, который создает изображения по тексту. Нажмите кнопку 'Создать изображение' для начала.", reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_image')
def create_image(message):
    if message.text.lower() == "создать изображение":
        user_id = message.from_user.id
        user_states[user_id] = 'waiting_text'
        bot.send_message(message.chat.id, "Введите текст для генерации изображения(на любом языке):")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, нажмите кнопку 'Создать изображение' для начала.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_text')
def generate_image(message):
    api_url = 'https://clipdrop-api.co/text-to-image/v1'
    api_key = 'API_KEY'

    text_to_translate = message.text
    translated_text = translator.translate(text_to_translate, src='auto', dest='en').text

    headers = {'x-api-key': api_key}
    files = {'prompt': (None, translated_text)}

    response = requests.post(api_url, headers=headers, files=files)

    if response.ok:
        bot.send_photo(message.chat.id, response.content)
    else:
        bot.send_message(message.chat.id, "Ошибка запроса: " + str(response.status_code))

    user_id = message.from_user.id
    user_states[user_id] = 'waiting_image'

if __name__ == '__main__':
    bot.polling(none_stop=True)
