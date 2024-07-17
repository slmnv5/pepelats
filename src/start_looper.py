from multiprocessing import Process, Queue

from control.looper import Looper
from mvc.countmidicontrol import CountMidiControl
from mvc.textscreen import TextScreen
from serv.webscreen import WebScreen
from utils.utilconfig import SCREEN_TYPE
from utils.utillog import MyLog


def do_looper(q_looper: Queue, q_screen: Queue) -> None:
    looper = Looper(q_looper, q_screen)
    looper.menu_client_start()


# noinspection PyBroadException
def do_screen(q_screen: Queue) -> None:
    if SCREEN_TYPE == 'web':
        scr = WebScreen(q_screen)
    else:
        scr = TextScreen(q_screen)
    scr.menu_client_start()


if __name__ == "__main__":
    # noinspection PyBroadException
    try:
        q_scr = Queue()  # screen update messages
        q_lpr = Queue()  # looper control messages
        midi_ctrl = CountMidiControl(q_lpr)

        p1 = Process(target=do_looper, args=[q_lpr, q_scr], name="looper", daemon=True)
        p1.start()
        p2 = Process(target=do_screen, args=[q_scr], name="screen", daemon=True)
        p2.start()

        midi_ctrl.start_menu_host()
    except Exception as ex:
        MyLog().exception(ex)
    finally:
        print("Exit done")
