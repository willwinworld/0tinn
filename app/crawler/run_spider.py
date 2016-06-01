# -*- coding:utf-8 -*-
from .wccftech_spider import run_wccftech
from .gnews_crawler import run_gnews
from .ign_spider import run_ign
from multiprocessing import Process

p1 = Process(target=run_gnews)
p2 = Process(target=run_wccftech)
p3 = Process(target=run_ign)
p1.start()
p2.start()
p3.start()
p1.join()
p2.join()
p3.join()
