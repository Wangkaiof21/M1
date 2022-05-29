import requests
import json

def send_ding(self, text, title, messageUrl):
    __headers = {'Content-Type': 'application/json;charset=utf-8'}
    url = 'https://oapi.dingtalk.com/robot/send?access_token=24a07bab1bad3756399be5b6c97a1a159f36239fa503283abed368c5f86a2f29'
    json_text = {
        "msgtype": "link",
        "link": {
            "text": text,
            "title": title,
            "picUrl": "",
            "messageUrl": messageUrl
        }
    }
    json_text = json.dumps(json_text).encode(encoding='UTF8')
    r = requests.post(self.url, json_text, headers=self.__headers).content
    return r
