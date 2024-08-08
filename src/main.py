import sys
from multiprocessing import Process
from multiprocessing import Queue
from time import sleep

from control.looper import Looper
from menuhost.countmidicontrol import CountMidiControl
from screen.textscreen import TextScreen
from screen.webscreen import WebScreen
from utils.util_config import LOCAL_IP, load_ini_section
from utils.util_log import MY_LOG, NoMidiInputFound, ConfigError
from utils.util_name import AppName

q_scr = Queue()  # screen update messages
q_lpr = Queue()  # looper control messages

scr_type: int = load_ini_section("SCREEN", True).get(AppName.screen_type, 0)

if ("--web" in sys.argv or scr_type == 1) and LOCAL_IP:
    SCREEN_TYPE: int = 1  # show state on web page
    MY_LOG.set_screen_queue(q_scr)
else:
    SCREEN_TYPE: int = 0  # text terminal


def _do_looper(q_looper: Queue, q_screen: Queue) -> None:
    looper = Looper(q_looper, q_screen)
    looper.client_start()


def _do_screen(q_screen: Queue) -> None:
    if SCREEN_TYPE and LOCAL_IP:
        scr = WebScreen(q_screen)
    else:
        scr = TextScreen(q_screen)
    scr.client_start()


def go() -> None:
    try:
        midi_ctrl = CountMidiControl(q_lpr)
        p1 = Process(target=_do_screen, args=[q_scr], name="screen", daemon=True)
        p1.start()

        p2 = Process(target=_do_looper, args=[q_lpr, q_scr], name="looper", daemon=True)
        p2.start()

        midi_ctrl.host_start()

        for k in range(5):
            if p1.is_alive() or p2.is_alive():
                MY_LOG.warning(f"Still running {k}:\tscreen: {p1.is_alive()}\tlooper: {p2.is_alive()}")
                sleep(5)

        sys.exit(0)
    except NoMidiInputFound as ex:
        MY_LOG.warning(f"Missing computer keyboard, missing MIDI: {ex}")
        sys.exit(1)
    except ConfigError as ex:
        MY_LOG.error(f"Edit local.ini file to correct error: {ex}")
        sys.exit(2)
    except Exception as ex:
        MY_LOG.exception(ex)
        sys.exit(3)
    finally:
        pass


if __name__ == "__main__":
    go()
