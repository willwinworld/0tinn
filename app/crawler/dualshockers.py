# -*- coding:utf-8 -*-
import requests
import asyncio
from manager import app
from bs4 import BeautifulSoup
from app.game.models import Game_News
from app.util.helper import up_avatar

time_out = 20


@asyncio.coroutine
def upload_pic(url):
        res = up_avatar(url)
        if 'info' in res:
            return False
        else:
            return res['linkurl']


@asyncio.coroutine
def deal_cells():
    dualshockers_url = 'http://www.dualshockers.com'
    print("正在链接:" + dualshockers_url)
    resp = requests.get(dualshockers_url,  timeout=time_out)
    print("链接完成")
    soup = BeautifulSoup(resp.content, "html.parser")
    cells = soup.find_all("div", class_="post-inner")
    for c in cells:
        print("开始获取信息")
        s = BeautifulSoup(str(c), "html.parser")
        t = s.find("h2").text
        t = t.replace("/", "|")
        t = t.replace("&", "and")
        t = t.replace("?", " ")
        st = s.find("p").text
        n_url = s.find("a")['href']
        ct, p = yield from get_content(n_url)
        print('获取信息完成，正在尝试上传图片')
        pic = yield from upload_pic(p)
        if not pic:
            pic = p
            print('上传失败')
        over = yield from gnews_save(t, st, ct, pic)
        if not over:
          continue


@asyncio.coroutine
def get_content(n):
    print("正在获取内容")
    resp_n = requests.get(n, timeout=time_out)
    soup_n = BeautifulSoup(resp_n.content, "html.parser")
    text = soup_n.find("div", class_="post-alt")
    pic = text.find("img")["src"]
    ct = text.find("div", class_="entry")
    return ct, pic


@asyncio.coroutine
def gnews_save(t, s, ct, p):
    gnews = Game_News(t, s, ct, p)
    print("尝试存储")
    with app.app_context():
       # try:
            gnews.save()
            print("储存成功")
        #    return True
        #except:
        #    return False


def run_dualshockers():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(deal_cells())
    loop.close()
