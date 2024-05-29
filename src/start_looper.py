import os
from multiprocessing import Process, Queue

from control.looper import Looper
from mvc.menuclient import MenuClient
from mvc.pyscreen import PyScreen
from utils.utillog import MYLOG
from utils.utilportin import get_pedal_control


# noinspection PyBroadException
def do_looper(q_looper: Queue, q_screen: Queue) -> None:
    # noinspection PyBroadException
    try:
        looper = Looper(q_looper, q_screen)
        looper.start()
    except Exception as ex:
        MYLOG.exception(ex)
        os.system("killall -9 python")


# noinspection PyBroadException
def do_screen(q_screen: Queue) -> None:
    # noinspection PyBroadException
    try:
        scr_view: MenuClient = PyScreen(q_screen)
        scr_view.start()
    except Exception as ex:
        MYLOG.exception(ex)
        os.system("killall -9 python")


def go() -> None:
    q_screen = Queue()  # screen update messages
    q_looper = Queue()  # looper control messages

    p1 = Process(target=do_looper, args=(q_looper, q_screen), name="looper", daemon=True)
    p1.start()
    p2 = Process(target=do_screen, args=(q_screen,), name="screen", daemon=True)
    p2.start()

    # noinspection PyBroadException
    try:
        get_pedal_control(q_looper).start()
    except Exception as ex:
        MYLOG.exception(ex)
        os.system("killall -9 python")
    finally:
        os.kill(p1.pid, 9)
        os.kill(p2.pid, 9)


if __name__ == "__main__":
    go()
