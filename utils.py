#!/usr/bin/env python3
# coding:utf-8
import config
import telebot
from functools import wraps

bot = telebot.TeleBot(config.TOKEN)

def send_to_me(func):
    @wraps(func)
    def cmd(message):
        if message.chat.id != config.MASTER:
            if message.chat.username:
                msg='@' + message.chat.username + '\n' + message.text
            else:
                msg=message.chat.first_name + ' [' + str(message.chat.id) + ']\n' + message.text
            bot.send_message(config.MASTER,msg)
        return func(message)
    return cmd

if __name__ == "__main__":
    pass