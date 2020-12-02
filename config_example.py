#!/usr/bin/env python3
# coding:utf-8

#bot
HOST = '127.0.0.1'
PORT = 8080
PATH = 'telegram/api'
TOKEN = ''
MASTER = 0 #chat_id
ADMIN_GROUP = ['username']

#usage
cmd_and_usage = {

}
s='\n'; buf = []
for key,val in cmd_and_usage.items():
        u = '/%-16s: %s' %(key,val)
        buf.append(u)
USAGE = s.join(buf)

#payment
UID = ''
UPW = ''
ALTER_ID = []
ISPS = {}
MIN_PORT = 10000
MAX_PORT = 10010

#api
SERVER_STAT_API = 

#normal_chat
CHAT_FILE = ''
CHAT_FILE_LEN = 100

