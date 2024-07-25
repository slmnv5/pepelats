from multiprocessing import Process
from multiprocessing import Queue
from time import sleep

from control.looper import Looper
from mvc.countmidicontrol import CountMidiControl
from mvc.menuhost import MenuHost
from mvc.textscreen import TextScreen
from serv.confighandler import web_config
from serv.webscreen import WebScreen
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
    if choice == 1:
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

    for k in range(12):
        if p1.is_alive() or p2.is_alive():
            MY_LOG.warning(f"Still running {k}\nscreen: {p1.is_alive()}\nlooper: {p2.is_alive()}\n")
            sleep(7)


if __name__ == "__main__":
    try:
        midi_control = CountMidiControl(q_lpr)
        ch: int = load_ini_section("SCREEN", True).get(AppName.screen_type, 0)
        do_start(midi_control, q_scr, q_lpr, ch)
    except ConfigError as ex:
        MY_LOG.warning(f"HTTP server starting at: {LOCAL_IP}:{CONFIG_PORT}")
        MY_LOG.warning(f"Edit local.ini file to correct: {ex}")
        web_config()
    except NoMidiInputFound as ex:
        MY_LOG.warning(ex)
        pname = load_ini_section("MIDI").get("midi_in", "")
        MY_LOG.error(f"Connect MIDI IN controller {pname} or connect computer keyboard")
        sleep(10)
    except Exception as ex:
        MY_LOG.exception(ex)
    finally:
        pass
