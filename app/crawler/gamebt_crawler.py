# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup

pics = []
news = []
title = []
sentence = []
content_en = []
content_cn = []
url = 'http://gamingbolt.com/category/news'
gt_url = 'http://translate.google.cn/#en/zh-CN/'
header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Encoding': 'gzip, deflate, sdch',
          'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
          'Connection': 'keep-alive',
          'Host': 'gamingbolt.com',
          'Upgrade-Insecure-Requests': '1',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
          }
time_out = 10
try:
    resp = requests.get(url, headers=header, timeout=time_out)
except:
    print("链接失败")
soup = BeautifulSoup(resp.content, "html.parser")
cells = soup.find_all("div", class_="pic")
for i in cells[0:20]:
    c = BeautifulSoup(str(i), "html.parser")

    # 查找并添加图片url
    pic = c.find("img")
    pics.append(pic["src"])

    # 查找并添加文章url
    a = c.find('a')
    news.append(a["href"])

for i in news:
    print("正在链接 >>>" + i)
    try:
        resp = requests.get(i, headers=header, timeout=time_out)
        soup = BeautifulSoup(resp.content, "html.parser")
        print(">>>>正在获取标题")
        title.append(soup.h1.text)
        print(">>>>正在获取句子")
        sentence.append(soup.h4.text)
        print(">>>>正在获取原文内容")
        s = soup.find("div", class_="content-area").text
        content_en.append(s.split("Tagged With")[0])
    except:
        print("链接失败.")

