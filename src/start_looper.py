import os
import sys
import time
import traceback
from multiprocessing import Pipe, Process
from multiprocessing import connection
from threading import Thread

from rtmidi.midiutil import open_midiinput

from control import ExtendedCtrl
from mvc.menucontrol import MenuLoader
from utils.log import LOGGER
from utils.myrtmidi import MyRtmidi


# noinspection PyBroadException
def do_looper(recv_looper: connection.Connection, send_view: connection.Connection) -> None:
    try:
        looper = ExtendedCtrl(recv_looper, send_view)
        looper.process_messages()
    except Exception:
        LOGGER.error(f"process_looper, error: {traceback.format_exc()}")


# noinspection PyBroadException
def do_screenview(recv_view: connection.Connection, send_looper: connection.Connection) -> None:
    try:
        from mvc.ccscreen import CcScreen
        scr_view = CcScreen(recv_view, send_looper, menu_loader)
    except Exception:
        LOGGER.warn("Error loading C++ shared library 'touchscr5.so'. Useing old python viewer")
        from mvc.pyscreen import PyScreen
        scr_view = PyScreen(recv_view)

    try:
        scr_view.process_messages()
    except Exception:
        LOGGER.error(f"process_screenview, error: {traceback.format_exc()}")


menu_loader = MenuLoader("config/menu", "play", "0")


def go() -> None:
    if "--kbd" in sys.argv:
        from utils.utilkbd import KbdMidiPort
        midi_in = KbdMidiPort()
    else:
        port_name = os.getenv('PEDAL_PORT_NAME', "PedalCommands_out")
        midi_in, _ = open_midiinput(port_name, interactive=False)  # may throw
        midi_in = MyRtmidi(midi_in)  # adapter classs

    recv_view, send_view = Pipe(False)  # screen update messages
    recv_looper, send_looper = Pipe(False)  # looper control messages

    if "--count" in sys.argv:  # will be counting notes in python controller
        from mvc import CountMidiControl
        m_ctrl = CountMidiControl(midi_in, send_looper, menu_loader)
    else:
        from mvc import MidiControl
        m_ctrl = MidiControl(midi_in, send_looper, menu_loader)

    pr1 = Process(target=do_looper, args=(recv_looper, send_view), name="looper", daemon=True)
    pr1.start()

    pr2 = Thread(target=do_screenview, args=(recv_view, send_looper), name="screen", daemon=True)
    pr2.start()

    time.sleep(2)  # wait other objects to start

    # start only if other process started
    if pr1.is_alive() and pr2.is_alive():
        m_ctrl.monitor()
    else:
        sys.exit(1)


if __name__ == "__main__":
    # noinspection PyBroadException
    try:
        go()
    except Exception:
        LOGGER.error(f"Start looper, error: {traceback.format_exc()}")
        sys.exit(2)
