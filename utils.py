#!/usr/bin/env python3
# coding:utf-8
import time
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

class Timer():
    def __init__(self):
        self.dict = {}
    
    def set(self, id, cd, times=0):
        self.dict[id] = [cd, times]
        
    def cancel(self, id):
        del self.dict[id]

    def start(self):
        del_list = []
        while True:
            for _ in range(len(del_list)):
                id = del_list.pop(0)
                del self.dict[id]

            for id, lmt in self.dict.items():
                if not lmt[0]:
                    del_list.append(id)
                    continue
                lmt[0] -= 1
            time.sleep(1)

    def checkAndReset(self, id, cd, times=0):
        if not self.dict.get(id):
            self.set(id,cd,times)
            return True
        else:
            if self.dict[id][1]:
                self.set(id,cd,self.dict[id][1]-1)
                return True
            else:
                return False
            
                
if __name__ == "__main__":
    pass