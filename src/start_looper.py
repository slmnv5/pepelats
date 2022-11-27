import os
import sys
import time
import traceback
from multiprocessing import Pipe, Process
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from rtmidi.midiutil import open_midiinput

from control import ExtendedCtrl
from kbdmidi import KbdMidiPort
from mvc import CountMidiControl
from mvc import MidiControl, ScreenView
from utils.log import LOGGER
from utils.myrtmidi import MyRtmidi


def process_looper(recv_looper: Connection, send_view: Connection) -> None:
    # noinspection PyBroadException
    try:
        looper = ExtendedCtrl(recv_looper, send_view)
        looper.process_messages()
    except Exception:
        LOGGER.error(f"process_looper: filed, error: {traceback.format_exc()}")


def process_screenview(recv_view: Connection) -> None:
    # noinspection PyBroadException
    try:
        scr_view = ScreenView(recv_view)
        scr_view.process_messages()
    except Exception:
        LOGGER.error(f"process_screenview: filed, error: {traceback.format_exc()}")


def go() -> None:
    recv_view, send_view = Pipe(False)  # screen update messages
    recv_looper, send_looper = Pipe(False)  # looper control messages

    if "--kbd" in sys.argv:
        in_port = KbdMidiPort()
    else:
        port_name = os.getenv('PEDAL_PORT_NAME', "PedalCommands_out")
        in_port, _ = open_midiinput(port_name, interactive=False)
        in_port = MyRtmidi(in_port)

    pr1 = Process(target=process_looper, args=(recv_looper, send_view), name="looper", daemon=True)
    pr1.start()

    pr2 = Process(target=process_screenview, args=(recv_view,), name="screen", daemon=True)
    pr2.start()

    time.sleep(2)  # wait other objects to start
    if "--count" in sys.argv:  # will be counting notes in python controller
        m_ctrl = CountMidiControl(in_port, send_looper, "config/midicontrol", "playing", "0")
    else:
        m_ctrl = MidiControl(in_port, send_looper, "config/midicontrol", "playing", "0")

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
