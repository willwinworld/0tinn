# -*- coding:utf-8 -*-
import requests
from manager import app
from bs4 import BeautifulSoup
from app.game.models import Game_News
from app.util.helper import up_avatar
from app.extensions import celery

time_out = 20


def upload_pic(url):
        res = up_avatar(url)
        if 'info' in res:
            return False
        else:
            return res['linkurl']


def get_content(n):
    print("正在获取内容")
    resp_n = requests.get(n, timeout=time_out)
    soup_n = BeautifulSoup(resp_n.content, "html.parser")
    text = soup_n.find("div", class_="post-alt")
    pic = text.find("img")["src"]
    ct = str(text.find("div", class_="entry"))
    return ct, pic


def gnews_save(t, s, ct, p):
    print(type(t), type(s), type(ct), type(p))
    gnews = Game_News(t, s, ct, p)
    print("尝试存储")
    with app.app_context():
        try:
            gnews.save()
            print("储存成功")
            return True
        except:
            return False

@celery.task
def run():
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
        ct, p = get_content(n_url)
        print('获取信息完成，正在尝试上传图片')
        pic = upload_pic(p)
        if not pic:
            pic = p
            print('上传失败')
        over = gnews_save(t, st, ct, pic)
        if not over:
         break
