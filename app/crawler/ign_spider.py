# -*- coding:utf-8 -*-
import requests
import asyncio
from bs4 import BeautifulSoup
from manager import app
from app.game.models import Popular_games

url = "http://www.ign.com/?setccpref=US"
headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate, sdch",
"Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
"Connection":"keep-alive",
          "Host":"www.ign.com","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
          }
time_out = 20

print("Try to connect IGN")
resp = requests.get(url=url, headers=headers, timeout=time_out)
print("Connected")
soup = BeautifulSoup(resp.content, "html.parser")
topgames = soup.find_all("div", class_="topgames-module")


@asyncio.coroutine
def action():
    print("Get top games")
    top_colume = topgames[0].find_all("div", class_="column-game")
    for i in top_colume:
        topgame_title, topgame_scroe, rank = yield from deal_top(tag=i)
        topgame_result = yield from save("topgame", topgame_title, topgame_scroe, rank)
        if topgame_result:
            print("Save top game " + topgame_title + " success")
    print("Get upcoming games")
    upcoming_colume = topgames[1].find_all("div", class_="column-game")
    for i in upcoming_colume:
        upcoming_title, upcoming_date, rank = yield from deal_upcoming(tag=i)
        upcoming_result = yield from save("upcoming", upcoming_title, upcoming_date, rank)
        if upcoming_result:
            print("Save upcoming game " + upcoming_title + " success")


@asyncio.coroutine
def deal_top(tag):
    i = BeautifulSoup(str(tag), "html.parser")
    title = i.find("a", class_="game-title").text
    score = i.find("a", class_="rating").text
    rank = i.find("div", class_="list-count").text
    return title, score, rank


@asyncio.coroutine
def deal_upcoming(tag):
    i = BeautifulSoup(str(tag), "html.parser")
    title = i.find("a", class_="game-title").text
    date = i.find("div", class_="date").text
    rank = i.find("div", class_="list-count").text
    return title, date, rank


@asyncio.coroutine
def save(label, name, ds, rank):
    print("Try save game rank")
    with app.app_context():
        g = Popular_games.query.filter_by(label=label).filter_by(rank=rank).first()
        if g is None:
            g = Popular_games(name, ds, label, rank)
            try:
                g.save()
                return True
            except:
                return False
        else:
            if g.name == name:
                return True
            else:
                g.name = name
                g.ds = ds
                try:
                    g.save()
                    return True
                except:
                    return False


def run_ign():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(action())
    loop.close()
