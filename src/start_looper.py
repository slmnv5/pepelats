import logging
import os
import sys
import time
import traceback
from multiprocessing import Pipe, Process
from multiprocessing import connection

from rtmidi.midiutil import open_midiinput

from control import ExtendedCtrl
from mvc.controlfactory import ControlFactory
from mvc.menucontrol import MenuLoader
from utils.config import ROOT_DIR
from utils.utilport import MyRtmidi

file = ROOT_DIR + "/log.txt"
tmp = "WARN"
if "--debug" in sys.argv:
    tmp = "DEBUG"
elif "--info" in sys.argv:
    tmp = "INFO"

logging.basicConfig(level=tmp, filename=file, filemode='a', format='%(name)s - %(levelname)s - %(message)s')
logging.critical("=============Starting log==============")


# noinspection PyBroadException
def do_looper(recv_looper: connection.Connection, send_view: connection.Connection) -> None:
    try:
        looper = ExtendedCtrl(recv_looper, send_view)
        looper.process_messages()
    except Exception:
        logging.error(f"process_looper, error: {traceback.format_exc()}")


# noinspection PyBroadException
def do_screenview(control_factory: ControlFactory) -> None:
    try:
        scr_view = control_factory.get_screen_control()
        scr_view.monitor()
    except Exception:
        logging.error(f"process_screenview, error: {traceback.format_exc()}")


def go() -> None:
    menu_loader = MenuLoader("config/menu", "play", "0")
    recv_view, send_view = Pipe(False)  # screen update messages
    recv_looper, send_looper = Pipe(False)  # looper control messages

    if "--kbd" in sys.argv:
        from utils.utilport import KbdMidiPort

        midi_in = KbdMidiPort()
    else:
        port_name = os.getenv('PEDAL_PORT_NAME', "PedalCommands_out")
        midi_in, _ = open_midiinput(port_name, interactive=False)  # may throw
        midi_in = MyRtmidi(midi_in)  # adapter classs

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


if __name__ == "__main__":
    # noinspection PyBroadException
    try:
        go()
    except Exception:
        logging.error(f"Start looper, error: {traceback.format_exc()}")
        sys.exit(2)
