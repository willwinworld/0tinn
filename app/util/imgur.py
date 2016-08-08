# -*- coding:utf-8 -*-
import pyimgur

CLIENT_ID = '4f3c0ba3b72bc7c'
im = pyimgur.Imgur(CLIENT_ID)
header = {"Authorization": "Client-ID 4f3c0ba3b72bc7c"}
baseurl = 'https://api.imgur.com/3/'


def upload(u):
    link = ''
    try:
        resp = im.upload_image(url=u)
        link = resp.link
    except:
        link = u
    return link
