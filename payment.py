#!/usr/bin/env python3
# coding:utf-8
import json
import requests

class Bill():
    def __init__(self, cookie):
        self.headers = {
            'authority': 'www.xiuluohost.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.xiuluohost.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.xiuluohost.com/dashboard/addfunds',
            'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7',
            'cookie': cookie
    }

    def initCharge(self, method, amount):
        self.payload = 'payment=' + method + '&amount=' + str(amount)

    def charge(self):
        url = "https://www.xiuluohost.com/account/charge"
        r = requests.post(url, headers=self.headers, data=self.payload)
        resp = json.loads(r.text)
        if resp['code']:
            bill_id = resp['data']['bill_id']
            qrcode = "https://www.xiuluohost.com" + resp['data']['qrcode'].replace('\\','')
            return True, bill_id, qrcode
        else:
            return False, None, None

    def verify(self, bill_id):
        url = "https://xiuluohost.com/bill/verify/" + bill_id
        headers = {
            'authority': 'www.xiuluohost.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7',
        }
        r = requests.get(url,headers=headers)
        resp = json.loads(r.text)
        if resp['code']:
            return True
        else:
            return False
