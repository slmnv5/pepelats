import os
from multiprocessing import Process, Queue

from control.looper import Looper
from mvc.countmidicontrol import CountMidiControl
from mvc.pyscreen import PyScreen
from utils.utillog import MYLOG


# noinspection PyBroadException
def do_looper(q_looper: Queue, q_screen: Queue) -> None:
    # noinspection PyBroadException
    try:
        looper = Looper(q_looper, q_screen)
        looper.menu_client_start()
    except Exception as ex:
        MYLOG.exception(ex)
        os.system("killall -9 python")


# noinspection PyBroadException
def do_screen(q_screen: Queue) -> None:
    # noinspection PyBroadException
    try:
        scr_view = PyScreen(q_screen)
        scr_view.menu_client_start()
    except Exception as ex:
        MYLOG.exception(ex)
        os.system("killall -9 python")


def go() -> None:
    q_screen = Queue()  # screen update messages
    q_looper = Queue()  # looper control messages
    midi_ctrl = CountMidiControl(q_looper)

    p1 = Process(target=do_looper, args=(q_looper, q_screen), name="looper", daemon=True)
    p1.start()
    p2 = Process(target=do_screen, args=(q_screen,), name="screen", daemon=True)
    p2.start()

    midi_ctrl.start_menu_host()


if __name__ == "__main__":
    # noinspection PyBroadException
    try:
        go()
    except Exception as ex1:
        MYLOG.exception(ex1)
    finally:
        os.system("killall -9 python")
