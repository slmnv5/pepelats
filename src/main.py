import sys
from multiprocessing import Process
from multiprocessing import Queue
from time import sleep

from control.looper import Looper
from menuhost.countmidicontrol import CountMidiControl
from menuhost.menuhost import MenuHost
from screen.textscreen import TextScreen
from screen.webscreen import WebScreen
from utils.util_config import load_ini_section, LOCAL_IP
from utils.util_log import MY_LOG, NoMidiInputFound, ConfigError
from utils.util_name import AppName

q_scr = Queue()  # screen update messages
q_lpr = Queue()  # looper control messages

MY_LOG.set_screen_queue(q_scr)


def _do_looper(q_looper: Queue, q_screen: Queue) -> None:
    looper = Looper(q_looper, q_screen)
    looper.client_start()


def _do_screen(q_screen: Queue, choice: int) -> None:
    if choice:
        scr = WebScreen(q_screen)
    else:
        scr = TextScreen(q_screen)
    scr.client_start()


def do_start(midi_ctrl: MenuHost, q_screen: Queue, q_looper: Queue, choice: int) -> None:
    p1 = Process(target=_do_screen, args=[q_screen, choice], name="screen", daemon=True)
    p1.start()

    p2 = Process(target=_do_looper, args=[q_looper, q_screen], name="looper", daemon=True)
    p2.start()

    midi_ctrl.host_start()
    q_screen.put([AppName.client_stop])

    for k in range(3):
        if p1.is_alive() or p2.is_alive():
            MY_LOG.warning(f"Still running {k}:\tscreen: {p1.is_alive()}\tlooper: {p2.is_alive()}")
            sleep(10)


def go() -> None:
    try:
        midi_control = CountMidiControl(q_lpr)
        choice: int = load_ini_section("SCREEN", True).get(AppName.screen_type, 0)
        if choice and not LOCAL_IP:
            MY_LOG.error(f"Can not set screen type={choice} without WiFi connection")
            choice = 0
        do_start(midi_control, q_scr, q_lpr, choice)
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
