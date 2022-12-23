import logging
import sys
import time
import traceback
from multiprocessing import Pipe, Process
from multiprocessing import connection

from control import ExtendedCtrl
from mvc.controlfactory import ControlFactory
from mvc.menucontrol import MenuLoader
from utils.utilport import KbdMidiPort
from utils.config import ROOT_DIR
from utils.utilalsa import get_midi_in

root = logging.getLogger()
for handler in logging.root.handlers:
    logging.root.removeHandler(handler)

handler = None
file = ROOT_DIR + "/log.txt"
tmp = logging.WARN
if "--debug" in sys.argv:
    tmp = logging.DEBUG
    handler = logging.StreamHandler(sys.stdout)
elif "--info" in sys.argv:
    tmp = logging.INFO
    handler = logging.StreamHandler(sys.stdout)

fmt_str = '%(filename)s %(levelname)s - %(message)s'

logging.basicConfig(force=True, level=tmp, filename=file, filemode='a', format=fmt_str)
if handler:
    handler.setLevel(tmp)
    handler.setFormatter(logging.Formatter(fmt=fmt_str))
    root.addHandler(handler)

logging.critical("=============Starting log==============")


# c_handler = logging.StreamHandler()
# logging.getLogger().addHandler(c_handler)


# noinspection PyBroadException
def do_looper(recv_looper: connection.Connection, send_view: connection.Connection) -> None:
    looper = ExtendedCtrl(recv_looper, send_view)
    looper.process_messages()


# noinspection PyBroadException
def do_screenview(control_factory: ControlFactory) -> None:
    scr_view = control_factory.get_screen_control()
    scr_view.monitor()


def go() -> None:
    menu_loader = MenuLoader("config/menu", "play", "0")
    recv_view, send_view = Pipe(False)  # screen update messages
    recv_looper, send_looper = Pipe(False)  # looper control messages

    if "--kbd" in sys.argv:
        midi_in = KbdMidiPort()
    else:
        midi_in = get_midi_in()  # may throw

    control_factory = ControlFactory(midi_in, recv_view, send_looper, menu_loader)

    pr1 = Process(target=do_looper, args=(recv_looper, send_view), name="looper", daemon=True)
    pr1.start()

    pr2 = Process(target=do_screenview, args=(control_factory,), name="screen", daemon=True)
    pr2.start()

    time.sleep(2)  # wait other objects to start

    pedal_control = control_factory.get_pedal_control()

    if not pr1.is_alive():
        raise RuntimeError("Looper process did exit already")
    if not pr2.is_alive():
        raise RuntimeError("Screen thread did exit already")

    pedal_control.monitor()
    logging.error(f"============Wait==============")
    pr1.join()
    pr2.join()


if __name__ == "__main__":
    # noinspection PyBroadException
    try:
        go()
    except Exception:
        logging.error(f"============Error: {traceback.format_exc()}")
        sys.exit(2)
