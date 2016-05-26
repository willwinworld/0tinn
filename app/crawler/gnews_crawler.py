# -*- coding:utf-8 -*-
import requests
from manager import app
from bs4 import BeautifulSoup
from app.game.models import Game_News
from app.util.helper import up_avatar

pics = []
title = []
news_url = []
sentence = []
content_en = []
content_cn = []
pcgamer_url = 'http://www.pcgamer.com/news/'
pcgame_header = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate, sdch",
"Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
"Connection":"keep-alive",
          "Host":"www.pcgamer.com","Upgrade-Insecure-Requests":"1","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
          }
time_out = 20
try:
    resp = requests.get(pcgamer_url, headers=pcgame_header, timeout=time_out)
except:
    pass
soup = BeautifulSoup(resp.content, "html.parser")


def n_filter(tag):
    return tag.has_attr("data-page") and "listingResult" in tag["class"]

def upload_pic(url):
        res = up_avatar(url)
        if 'info' in res:
            return False
        else:
             return res['s_url']

cells = soup.find_all(n_filter)
for c in cells:
    s = BeautifulSoup(str(c), "html.parser")
    p = s.find("figure")["data-original"]
    pic = upload_pic(p)
    if not pic:
        pic = p
    pics.append(pic)
    title.append(s.find("h3", class_="article-name").text)
    sentence.append(s.find("p", class_="synopsis").text)
    news_url.append(s.find("a")['href'])
for n in news_url:
    resp_n = requests.get(n, headers=pcgame_header, timeout=time_out)
    soup_n = BeautifulSoup(resp_n.content, "html.parser")
    text = soup_n.find("textplugin")
    soup_n.find("textplugin").contents[0].decompose()
    content_en.append(str(text))
for i in range(len(pics)):
    gnews = Game_News(title[i], sentence[i], content_en[i], pics[i])
    with app.app_context():
        try:
            gnews.save()
        except:
            pass
