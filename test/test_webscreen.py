import time
from multiprocessing import Queue
from threading import Timer

from screen.webscreen import WebScreen
from utils.util_name import AppName


def test_1():
    q1 = Queue()
    ws = WebScreen(q1)
    start = time.time()
    Timer(5, q1.put, [[AppName.client_stop]]).start()
    ws.client_start()

    end = time.time()
    assert 5 < (end - start) < 10
