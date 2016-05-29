# -*- coding:utf-8 -*-
import requests
import asyncio
from manager import app
from bs4 import BeautifulSoup
from app.game.models import Game_News
from app.util.helper import up_avatar

pcgamer_url = 'http://www.pcgamer.com/news/'
pcgame_header = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate, sdch",
"Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
"Connection":"keep-alive",
          "Host":"www.pcgamer.com","Upgrade-Insecure-Requests":"1","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
          }
time_out = 20
print("Try connect pcgamer.....")
resp = requests.get(pcgamer_url, headers=pcgame_header, timeout=time_out)
print("Complete")
soup = BeautifulSoup(resp.content, "html.parser")


def n_filter(tag):
    return tag.has_attr("data-page") and "listingResult" in tag["class"]

cells = soup.find_all(n_filter)


@asyncio.coroutine
def upload_pic(url):
        res = up_avatar(url)
        if 'info' in res:
            return False
        else:
            return res['s_url']


@asyncio.coroutine
def deal_cells():
    for c in cells:
        print("Action")
        s = BeautifulSoup(str(c), "html.parser")
        p = s.find("figure")["data-original"]
        print("Now upload pic")
        pic = yield from upload_pic(p)
        if not pic:
            pic = p
        t = s.find("h3", class_="article-name").text
        t = t.replace("/", "|")
        st = s.find("p", class_="synopsis").text
        n_url = s.find("a")['href']
        ct = yield from get_content(n_url)
        over = yield from gnews_save(t, st, ct, pic)
        if not over:
            break


@asyncio.coroutine
def get_content(n):
    print("Let us get content")
    resp_n = requests.get(n, headers=pcgame_header, timeout=time_out)
    soup_n = BeautifulSoup(resp_n.content, "html.parser")
    text = soup_n.find("textplugin")
    soup_n.find("textplugin").contents[0].decompose()
    return str(text)


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

def run_gnews():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(deal_cells())
    loop.close()