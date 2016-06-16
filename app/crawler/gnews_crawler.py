# -*- coding:utf-8 -*-
import requests
from manager import app
from bs4 import BeautifulSoup
from app.game.models import Game_News
from app.util.helper import up_avatar
from app.extensions import celery

pcgame_header = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate, sdch",
"Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
"Connection":"keep-alive",
          "Host":"www.pcgamer.com","Upgrade-Insecure-Requests":"1","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
          }
time_out = 20
print("Try connect pcgamer.....")


def n_filter(tag):
    return tag.has_attr("data-page") and "listingResult" in tag["class"]


def upload_pic(url):
        res = up_avatar(url)
        if 'info' in res:
            return False
        else:
            return res['linkurl']


def get_content(n):
    print("正在获取内容")
    resp_n = requests.get(n, headers=pcgame_header, timeout=time_out)
    soup_n = BeautifulSoup(resp_n.content, "html.parser")
    text = soup_n.find("textplugin")
    soup_n.find("textplugin").contents[0].decompose()
    return str(text)


def gnews_save(t, s, ct, p):
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
    pcgamer_url = 'http://www.pcgamer.com/news/page/1/'
    print("正在链接:" + pcgamer_url)
    resp = requests.get(pcgamer_url, headers=pcgame_header, timeout=time_out)
    print("链接完成")
    soup = BeautifulSoup(resp.content, "html.parser")
    cells = soup.find_all(n_filter)
    for c in cells:
        print("开始获取信息")
        s = BeautifulSoup(str(c), "html.parser")
        p = s.find("figure")["data-original"]
        print("正在尝试上传图片")
        pic = upload_pic(p)
        if not pic:
            pic = p
        t = s.find("h3", class_="article-name").text
        t = t.replace("/", "|")
        t = t.replace("&", "and")
        t = t.replace("?", " ")
        st = s.find("p", class_="synopsis").text
        n_url = s.find("a")['href']
        ct = get_content(n_url)
        print('获取信息完成')
        over = gnews_save(t, st, ct, pic)
        if not over:
         break
