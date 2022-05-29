# -*- coding:utf-8 -*-
import requests



def mytrans(str):
    data = {
        'doctype': 'json',
        'type': 'AUTO',
        'i': str
    }
    url = "http://fanyi.youdao.com/translate"
    r = requests.get(url, params=data)
    # print(r.text)
    result = r.json()
    # return result
    return result["translateResult"][0][0]["tgt"]