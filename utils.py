#!/usr/bin/env python3
# coding:utf-8
import time
import json
import random
import telebot
import datetime
from functools import wraps

import config
import natctl
#import payment

GB = 1024**3
MB = 1024**2
KB = 1024

bot = telebot.TeleBot(config.TOKEN)

def str_to_num(s):
    try:
        n = int(s)
    except ValueError:
        return 0
    else:
        return n

def get_time_str(t):
    time_arr = datetime.datetime.utcfromtimestamp(t)
    time_str = time_arr.strftime("%Y-%m-%d %H:%M:%S")
    return time_str

def load_json_str(s):
    try:
        data = json.loads(s)
    except json.decoder.JSONDecodeError:
        data = {}
    else:
        return data

def select_max_measure(num):
    if  num / KB < 1:
        count = num; measure = 'B'
    elif num / MB < 1:
        count = num/KB; measure = 'KB'
    else:
        count = round(num/MB,1); measure = 'MB'
    return count, measure

def gen_cookie():
        today = datetime.date.today()
        date = str(today).replace('-','')
        upv2 = date + '%2C' + str(random.randint(1,10))
        cookie = 'uid=%s;upw=%s;upv2=%s' %(config.UID,config.UPW,upv2)
        return cookie

def send_to_me(flag, ignore_mute=False):
    def cmd(func):
        @wraps(func)
        def send(message):
            if ignore_mute:
                is_mute = False
            else:
                is_mute = flag.is_set('mute',message.chat.id)
            if not(message.chat.id == config.MASTER or is_mute):
                if message.chat.username:
                    msg='@%s\n%s' %(message.chat.username,message.text)
                else:
                    msg='%s[%d]\n%s' %(message.chat.first_name,message.chat.id,message.text)
                bot.send_message(config.MASTER,msg)
            return func(message)
        return send
    return cmd

def permit(*group):
    def cmd(func):
        @wraps(func)
        def limit(message):
            if message.chat.username in group:
                bot.send_message(message.chat.id,'you are in admin group!')
                return func(message)
            else:
                bot.send_message(message.chat.id,'no permission!')
                return
        return limit
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
            'py': {},
            'mute': {}
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
    bot.send_message(message.chat.id,'plz enter your top-up amount, or enter -1 to cancel')

#text handle func
def txt_py(message, flag, timer):
    method = flag.get_val('py',message.chat.id)
    amount = str_to_num(message.text)
    if amount == -1:
        flag.rm('py',message.chat.id)
        bot.send_message(message.chat.id,'request canceled')
        return
    if amount <= 0:
        bot.send_message(message.chat.id,'invalid top-up amount, it should be an unsigned integer')
        bot.send_message(message.chat.id,'plz retry')
        return
    bot.send_message(message.chat.id,'PYing...')
    bot.send_message(message.chat.id,'method: '+ method + '\n' + 'amount: ' + message.text)
    
    if not timer.checkAndReset(message.chat.id,30,1):
        bot.send_message(message.chat.id,'too much request \nplz wait ' + str(timer.dict[message.chat.id][0]) + 's')
        return
    flag.rm('py',message.chat.id)
    """
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
    """
    bot.send_message(message.chat.id,'this function was disabled')