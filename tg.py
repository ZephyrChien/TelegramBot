#!/usr/bin/env python3
# coding:utf-8
import time
import flask
import utils
import config
import random
import telebot
import threading

import payment
import natctl

app = flask.Flask(__name__)
bot = telebot.TeleBot(config.TOKEN)
timer = utils.Timer()
timer_thread = threading.Thread(target=timer.start,daemon=True)
timer_thread.start()
txt_flag = utils.Flag()

#cmd list
@bot.message_handler(commands=['help'])
@utils.send_to_me
def cmd_help(message):
    bot.send_message(message.chat.id,config.USAGE)

@bot.message_handler(commands=['start'])
@utils.send_to_me
def cmd_start(message):
    bot.send_message(message.chat.id,'Ciallo')
    bot.send_message(message.chat.id,'with this bot, you can:')
    bot.send_message(message.chat.id,config.USAGE)

@bot.message_handler(commands=['nat'])
@utils.send_to_me
def cmd_nat_stat(message):
    nat = natctl.Nat(utils.gen_cookie(),config.MIN_PORT,config.MAX_PORT,*config.ALTER_ID,**config.ISPS)
    if not nat.get_config():
        bot.send_message(message.chat.id,'error')
        return
    s = '\n'; buf = []
    for key,val in nat.config.items():
        if key != 'isp':  
            forwarding = '%-5s -> %-5s' %(key,val)
        else:
            forwarding = 'ISP: ' + val
        buf.append(forwarding)
    msg = s.join(buf)
    bot.send_message(message.chat.id,msg)

@bot.message_handler(commands=['nat_edit_outer'])
@utils.send_to_me
def cmd_nat_edit_outer(message):
    nat = natctl.Nat(utils.gen_cookie(),config.MIN_PORT,config.MAX_PORT,*config.ALTER_ID,**config.ISPS)
    if not nat.get_config():
        bot.send_message(message.chat.id,'error')
        return
    msg = 'current ISP: ' + nat.config.get('isp')
    markup = telebot.types.InlineKeyboardMarkup()
    call_back_flag = 'ISP_' #flag
    btn1 = telebot.types.InlineKeyboardButton('CMCC', callback_data=call_back_flag+'CMCC')
    btn2 = telebot.types.InlineKeyboardButton('CTCC', callback_data=call_back_flag+'CTCC')
    btn3 = telebot.types.InlineKeyboardButton('CUCC', callback_data=call_back_flag+'CUCC')
    btn4 = telebot.types.InlineKeyboardButton('Cancel', callback_data=call_back_flag+'Cancel')
    markup.add(btn1,btn2,btn3,btn4)
    bot.send_message(message.chat.id,msg,reply_markup=markup)
    
@bot.message_handler(commands=['nat_edit_mapper'])
@utils.send_to_me
def cmd_nat_edit_mapper(message):
    cmd_args=message.text.split(' ')
    if len(cmd_args) != 3:
        bot.send_message(message.chat.id,'plz follow this format: /nat_edit_mapper <src> <dst>')
        return
    src = utils.str_to_num(cmd_args[1])
    dst = utils.str_to_num(cmd_args[2])
    if (not src) or (src < 0) or (src < config.MIN_PORT) or (src > config.MAX_PORT):
        bot.send_message(message.chat.id,'invalid src')
        return
    if (not dst) or (dst < 0) or (dst > 65535):
        bot.send_message(message.chat.id,'invalid dst')
        return

    nat = natctl.Nat(utils.gen_cookie(),config.MIN_PORT,config.MAX_PORT,*config.ALTER_ID,**config.ISPS)
    if not nat.set_port_forward(src,dst):
        bot.send_message(message.chat.id,'error')
    bot.send_message(message.chat.id,'done!')
    

@bot.message_handler(commands=['py'])
@utils.send_to_me
def cmd_py(message):
    markup = telebot.types.InlineKeyboardMarkup()
    call_back_flag = 'PY_' #flag
    btn1 = telebot.types.InlineKeyboardButton('alipay', callback_data=call_back_flag+'alipay')
    btn2 = telebot.types.InlineKeyboardButton('wxpay', callback_data=call_back_flag+'wxpay')
    btn3 = telebot.types.InlineKeyboardButton('cancel', callback_data=call_back_flag+'cancel')
    markup.add(btn1,btn2,btn3)
    bot.send_message(message.chat.id,'choose payment method:',reply_markup=markup)

@bot.message_handler(commands=['py_verify'])
@utils.send_to_me
def cmd_py_verify(message):
    cmd_args = message.text.split(' ')
    if len(cmd_args) != 2:
        bot.send_message(message.chat.id,'plz follow this format: /py_verify bill_id')
        return
    if len(cmd_args[1]) != 16 or not cmd_args[1].startswith('1C0'):
        bot.send_message(message.chat.id,'bill_id invalid')
        return
    bill = payment.Bill('')
    ok = bill.verify(cmd_args[1])
    if ok:
        bot.send_message(message.chat.id,'Finished. Thank you!')
    else:
        bot.send_message(message.chat.id,'Not paid yet')

@bot.message_handler(content_types=['text'])
@utils.send_to_me
def common(message):
    if txt_flag.is_set('py',message.chat.id):
        utils.txt_py(message,txt_flag,timer)
    else:
        with open(config.CHAT_FILE,'r') as chat_file:
            line = chat_file.readlines()[random.randint(0,config.CHAT_FILE_LEN -1)]
            bot.send_message(message.chat.id,line.rstrip())

#callback
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data
    if data.startswith('ISP_'):
        utils.callback_isp(call.message,data.replace('ISP_',''))
    elif data.startswith('PY_'):
        utils.callback_py(call.message,data.replace('PY_',''),txt_flag)
    
    utils.callback_reply(call)


#webhook
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''

@app.route(config.PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

if __name__ == "__main__":
    app.run(host=config.HOST,port=config.PORT,debug=True)
