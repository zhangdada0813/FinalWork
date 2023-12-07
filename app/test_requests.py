import requests
import json
login_url = "https://api.mall.jsshyc.com/login2"
params = {
    "token": "",
    "source": 2,
    "device_id": "358035084692361"
}
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": "128",
    "Host": "api.mall.jsshyc.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/3.11.0"
}
# account_list = self.config.phone_account_list
account = {"PHONE_ACCOUNT":"15161212422","PHONE_PASSWORD":"212422"}
data = {"password": account['PHONE_PASSWORD'], "login_type": 2, "mobile": account['PHONE_ACCOUNT'], "captcha_code": "",
        "system_code": "BUYER_SYSTEM", "source": 2, "token": ""}

data = json.dumps(data)
response = requests.post(login_url, params=params, data=data, headers=headers)
print(response.json())