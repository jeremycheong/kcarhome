#coding==utf-8

import requests
import os
import re
from bs4 import BeautifulSoup
import config as cfg

def htmlparser(url):#解析网页的函数
    r = requests.get(url, headers=cfg.headers)#get请求
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    content = r.text
    # return content
    soup = BeautifulSoup(content,"html.parser")
    k_classes = soup.find_all("div", "pro_big_b")
    for k_class in k_classes:
        print(k_class.find('a').get('href'))
        print(k_class.find('a').get_text())
    # print(k_classes)



if __name__ == '__main__':
    htmlparser(cfg.domain)

