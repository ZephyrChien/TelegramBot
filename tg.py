#!/usr/bin/env python3
# coding:utf-8
import time
import flask
import utils
import config
import payment
import telebot
import threading

app = flask.Flask(__name__)
bot = telebot.TeleBot(config.TOKEN)
timer = utils.Timer()
timer_thread = threading.Thread(target=timer.start,daemon=True)
timer_thread.start()

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

@bot.message_handler(commands=['sub'])
@utils.send_to_me
def cmd_sub(message):
    bot.send_message(message.chat.id,'cmcc: ')
    bot.send_message(message.chat.id,'ctcc: ')

@bot.message_handler(commands=['py'])
@utils.send_to_me
def cmd_py(message):
    uid = config.UID
    upw = config.UPW
    cmd_args=message.text.split(' ')
    if len(cmd_args) != 3:
        bot.send_message(message.chat.id,'plz follow this format: /py alipay(or wxpay) 5')
        return
    elif cmd_args[1] not in ['alipay','wxpay']:
        bot.send_message(message.chat.id,'only support alipay or wxpay')
        return
    else:
        try:
            amount = int(cmd_args[2])
        except ValueError:
            bot.send_message(message.chat.id,'amount should be an unsigned integer')
            return
        else:
            if amount <= 0:
                bot.send_message(message.chat.id,'amount should be an unsigned integer')
                return
    bot.send_message(message.chat.id,'PYing...')
    bot.send_message(message.chat.id,'method: '+ cmd_args[1] + '\n' + 'amount: ' + cmd_args[2])
    
    if not timer.checkAndReset(message.chat.id,30,1):
        bot.send_message(message.chat.id,'too much request \nplz wait ' + str(timer.dict[message.chat.id][0]) + 's')
        return
    
    bill = payment.Bill(uid,upw)
    bill.initCharge(cmd_args[1],cmd_args[2])
    ok,bill_id,bill_qrcode=bill.charge()
    if not ok:
        bot.send_message(message.chat.id,'error')
        return
    bot.send_message(message.chat.id,bill_id)
    bot.send_photo(message.chat.id,bill_qrcode)
    bot.send_message(message.chat.id,'plz complete this transaction in 30 minutes')
    time.sleep(20)
    for _ in range(0,3):
        ok = bill.verify(bill_id)
        if ok:
            bot.send_message(message.chat.id,'Finished. Thank you!')
            break
        time.sleep(5)


@bot.message_handler(content_types=['text'])
@utils.send_to_me
def common(message):
    bot.send_message(message.chat.id,'errr..')

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
