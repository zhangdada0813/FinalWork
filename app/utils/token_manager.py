
import json
import requests
import random

import execjs
import sys
sys.path.append("E:\\python\\spider\\改价\\校园直采_查询端\\app")
from handler.configHandler import ConfigHandler
class TokenManager():
    def __init__(self):
        # self.token = self.generate_token()
        self.config = ConfigHandler()
    def generate_token(self):
        headers = {
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua": "^\\^",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "sec-ch-ua-platform": "^\\^Windows^^",
            "Origin": "http://seller.jsshyc.com",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "http://seller.jsshyc.com/",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"
        }
        url = "https://api.seller.jsshyc.com/login2"
        params = {
            "token": "undefined",
            "source": "1"
        }
        data = {"username": self.config.pc_account, "password": self.config.pc_password, "source": 1}
        data = json.dumps(data)
        response = requests.post(url, headers=headers, params=params, data=data)


        token = response.json()['result']['token']
        return token

    def generate_random_pc_token(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://seller.sq12315.com',
            'Referer': 'https://seller.sq12315.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        url = 'https://api.seller.sq12315.com/login'
        params = {
            "token": "undefined",
            "source": "1"
        }
        with open("E:\\python\\spider\\FinalWork\\app\\utils\\loader.js", encoding="utf-8") as fin:
            js_text = fin.read()
        context1 = execjs.compile(js_text)
        account_list = self.config.pc_account_list
        account = random.choice(account_list)
        data = {"username":account['PC_ACCOUNT'], "password":context1.call("get_signed_password",account['PC_PASSWORD'] ), "source": 1}
        data = json.dumps(data)
        response = requests.post(url, headers=headers, params=params, data=data)
        # print(response.json())
        token = response.json()['result']['token']
        return token
    def generate_random_phone_token(self):

        login_url = "https://api.mall.sq12315.com/login2"
        params = {
            "token": "",
            "source": 2,
            "device_id": "358035084692361"
        }
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": "128",
            "Host": "api.mall.sq12315.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.11.0"
        }
        account_list = self.config.phone_account_list
        account = random.choice(account_list)
        print(account)
        data = {"password": account['PHONE_PASSWORD'], "login_type": 2, "mobile": account['PHONE_ACCOUNT'], "captcha_code": "",
                "system_code": "BUYER_SYSTEM", "source": 2, "token": ""}

        data = json.dumps(data)
        response = requests.post(login_url, params=params, data=data, headers=headers)
        print(response.json())
        token = response.json()['result']['token']
        return token

if __name__ == "__main__":
    tm = TokenManager()
    print(tm.generate_random_phone_token())
