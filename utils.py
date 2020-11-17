#!/usr/bin/env python3
# coding:utf-8
import time
import random
import telebot
import datetime
from functools import wraps

import config
import natctl
import payment

bot = telebot.TeleBot(config.TOKEN)

def str_to_num(s):
    try:
        n = int(s)
    except ValueError:
        return False
    else:
        return n

def gen_cookie():
        today = datetime.date.today()
        date = str(today).replace('-','')
        upv2 = date + '%2C' + str(random.randint(1,10))
        cookie = 'uid=%s;upw=%s;upv2=%s' %(config.UID,config.UPW,upv2)
        return cookie

def send_to_me(func):
    @wraps(func)
    def cmd(message):
        if message.chat.id != config.MASTER:
            if message.chat.username:
                msg='@%s\n%s' %(message.chat.username,message.text)
            else:
                msg='%s[%d]\n%s' %(message.chait.first_name,message.chat.id,message.text)
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

class Flag():
    def __init__(self):
        self.dict = {
            'py': {}
        }
    
    def add(self, flag, id, args):
        self.dict[flag][id] = args
    
    def rm(self, flag, id):
        self.dict[flag].pop(id)

    def is_set(self, flag, id):
        if self.dict[flag].get(id):
            return True
        else:
            return False
    def get_val(self, flag, id):
        return self.dict[flag].get(id)

#callback func
def callback_reply(call):
    bot.answer_callback_query(call.id,'')
    time.sleep(1)
    bot.delete_message(call.message.chat.id,call.message.message_id)

def callback_isp(message, isp):
    if isp == 'Cancel':
        bot.send_message(message.chat.id, 'request canceled')
        return
    nat = natctl.Nat(gen_cookie(),config.MIN_PORT,config.MAX_PORT,*config.ALTER_ID,**config.ISPS)
    if not nat.set_isp(isp):
        bot.send_message(message.chat.id, 'error')
    bot.send_message(message.chat.id, 'done!')

def callback_py(message, method, flag):
    if method == 'cancel':
        bot.send_message(message.chat.id, 'request canceled')
        return
    flag.add('py',message.chat.id,method)
    bot.send_message(message.chat.id,'method: ' + method)
    bot.send_message(message.chat.id,'plz enter your top-up amount:')

#text handle func
def txt_py(message, flag, timer):
    method = flag.get_val('py',message.chat.id)
    amount = str_to_num(message.text)
    if not amount or amount <0:
        bot.send_message(message.chat.id,'invalid top-up amount, it should be an unsigned integer')
        bot.send_message(message.chat.id,'plz retry')
        return
    bot.send_message(message.chat.id,'PYing...')
    bot.send_message(message.chat.id,'method: '+ method + '\n' + 'amount: ' + message.text)
    
    if not timer.checkAndReset(message.chat.id,30,1):
        bot.send_message(message.chat.id,'too much request \nplz wait ' + str(timer.dict[message.chat.id][0]) + 's')
        return
    flag.rm('py',message.chat.id)
    bill = payment.Bill(gen_cookie())
    bill.initCharge(method,amount)
    ok,bill_id,bill_qrcode=bill.charge()
    if not ok:
        bot.send_message(message.chat.id,'error')
        return
    bot.send_message(message.chat.id,'invoce: '+ bill_id)
    bot.send_photo(message.chat.id,bill_qrcode)
    bot.send_message(message.chat.id,'plz complete this transaction in 30 minutes')
    bot.send_message(message.chat.id,'wait for verification..(20s later)\nor do that manually by /py_verify')
    time.sleep(20)
    for i in range(0,3):
        bot.send_message(message.chat.id,'verify(%d)..' %(i+1))
        ok = bill.verify(bill_id)
        if ok:
            bot.send_message(message.chat.id,'Finished. Thank you!')
            break
        time.sleep(8)