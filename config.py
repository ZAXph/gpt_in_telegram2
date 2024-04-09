from telebot import *

system_content = ("Ты — дружелюбный помощник во всем! А так же можешь поддерживать диалог! А так же ты поддерживаешь "
                  "только русский язык.")
assistant_content = "Давай разберем по шагам: "
TOKEN = ""
modes = {"История": "Истории", "Кулинария": "Кулинарии", "Програмирование": "Програмировании"}
levels = {"Нормально": 0.7, "Неразбериха": 120}


def markup_create(parameter):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in parameter:
        markup.add(types.KeyboardButton(i))
    return markup


def markup_inline():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_save = telebot.types.InlineKeyboardButton(text="Продолжить?",
                                                     callback_data='next_gpt')
    keyboard.add(button_save)
    return keyboard


DB_NAME = 'db.sqlite'

MAX_TOKEN = 512
HEADERS = {"Content-Type": "application/json"}
GPT_LOCAL_URL = 'http://localhost:1234/v1/chat/completions'
