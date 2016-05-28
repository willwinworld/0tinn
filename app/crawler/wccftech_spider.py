# -*- coding:utf-8 -*-
import requests
import asyncio
from manager import app
from bs4 import BeautifulSoup
from app.game.models import Game_News
from app.util.helper import up_avatar


wccftech_url = 'http://wccftech.com/topic/games/page/1'
wccftech_header = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate, sdch",
"Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
"Connection":"keep-alive",
          "Host":"wccftech.com","Upgrade-Insecure-Requests":"1","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
          }
time_out = 20


@asyncio.coroutine
def upload_pic(url):
        res = up_avatar(url)
        if 'info' in res:
            return False
        else:
            return res['s_url']


@asyncio.coroutine
def deal_cells():
    for i in range(10):
        print("Try connect Wccftech, page:" + str(i))
        wccftech_url = 'http://wccftech.com/topic/games/page/' + str(i)
        resp = requests.get(wccftech_url, headers=wccftech_header, timeout=time_out)
        print("Complete")
        soup = BeautifulSoup(resp.content, "html.parser")
        cells = soup.find_all("div", class_="post")
        for c in cells:
            print("Action")
            s = BeautifulSoup(str(c), "html.parser")
            p = s.find("img")["src"]
            t = s.find("h2").text
            st = list(s.strings)[-1].strip()
            n_url = s.find("a")['href']
            ct, p = yield from get_content(n_url)
            pic = yield from upload_pic(p)
            if not pic:
                pic = p
            over = yield from gnews_save(t, st, ct, pic)
            if not over:
                break


@asyncio.coroutine
def get_content(n):
    print("Let us get content")
    resp_n = requests.get(n, headers=wccftech_header, timeout=time_out)
    soup_n = BeautifulSoup(resp_n.content, "html.parser")
    text = soup_n.find("div", class_="body")
    source = text.find_all("p")[2:]
    pic = text.find("img")["src"]
    ct = "".join(str(v) for v in source)
    return ct, pic


@asyncio.coroutine
def gnews_save(t, s, ct, p):
    gnews = Game_News(t, s, ct, p)
    print("Yeah save!!!!")
    with app.app_context():
        try:
            gnews.save()
            return True
        except:
            return False


def run_wccftech():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(deal_cells())
    loop.close()