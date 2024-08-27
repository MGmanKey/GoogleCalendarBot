import telebot
from telebot import types
import sqlite3
import random

import settings
import server

# for bot
token = settings.token
bot = telebot.TeleBot(token)

# DB

# Body


@bot.message_handler(func=lambda m: True)                #получение сообщений из бота
def processing(message):
    usr_info = message.from_user
    chat_info = message.chat
    info = f"user info: {usr_info}\nchat info:{chat_info}"
    print(info)
    text = message.text.lower()
    print(text, message.chat.id, settings.myChatId)
    if text == "события" and message.chat.id == settings.myChatId:
        bot.send_message(message.chat.id, server.getEvents())


# start
if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as ex:
            print(ex)
            bot.polling(none_stop=True)
