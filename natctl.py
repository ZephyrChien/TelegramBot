#!/usr/bin/env python3
# coding:utf-8
import json
import requests

class Nat():
    def __init__(self, cookie, min_port, max_port, *alterId, **ISPs):
        self.cookie = cookie
        self.min_port = min_port
        self.max_port = max_port
        self.alterId = alterId
        self.ISPs = ISPs
        self.config = {}
    
    def get_config(self):
        url = 'https://www.xiuluohost.com/nat/view_v2/' + str(self.alterId[0])
        headers = {
            'authority': 'www.xiuluohost.com',
            'content-length' : '0',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'origin': 'https://www.xiuluohost.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.xiuluohost.com/instance/control/'+ str(self.alterId[1]),
            'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7',
            'cookie': self.cookie
        }
        r = requests.post(url,headers=headers)
        resp = json.loads(r.text)
        if not resp.get('code'):
            return False
        data = resp.get('data')
        for isp, ip in self.ISPs.items():
            if ip == data['outer_ip']:
                self.config['isp'] = isp
        for port in range(self.min_port,self.max_port+1):
            src = str(port)
            dst = data['port_config'][src]['port_forward']
            self.config[src] = dst
        return True

    def set_isp(self, isp):
        url = 'https://www.xiuluohost.com/nat/save_output_route/' + str(self.alterId[0])
        payload = 'output_route=' + self.ISPs[isp]
        headers = {
            'authority': 'www.xiuluohost.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.xiuluohost.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.xiuluohost.com/instance/control/'+ str(self.alterId[1]),
            'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7',
            'cookie': self.cookie
        }
        r = requests.post(url, headers=headers, data=payload)
        resp = json.loads(r.text)
        if resp.get('code'):
            return True
        return False
    
    def set_port_forward(self, src, dst):
        url = 'https://www.xiuluohost.com/nat/edit'
        payload = 'src_port=%d&dst_port=%d&dst_ip_id=%d&action=save' %(src,dst,self.alterId[0])
        headers = {
            'authority': 'www.xiuluohost.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.xiuluohost.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.xiuluohost.com/instance/control/'+ str(self.alterId[1]),
            'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7',
            'cookie': self.cookie
        }
        r = requests.post(url, headers=headers, data=payload)
        resp = json.loads(r.text)
        if resp.get('code'):
            return True
        return False

            
