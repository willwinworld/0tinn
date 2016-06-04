# -*- coding:utf-8 -*-
import time
from .wccftech_spider import run_wccftech
from .gnews_crawler import run_gnews
from .dualshockers import run_dualshockers
from multiprocessing import Process

def run():
    p1 = Process(target=run_gnews)
    p2 = Process(target=run_wccftech)
    p4 = Process(target=run_dualshockers)
    p1.start()
    p2.start()
    p4.start()
    p1.join()
    p2.join()
    p4.join()

while True:
    run()
    time.sleep(10800)