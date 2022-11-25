import os
import sys
import time
import traceback
from multiprocessing import Pipe, Process
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from control import ExtendedCtrl
from kbdmidi import KbdMidiPort
from mvc import CountMidiControl
from mvc import MidiControl, ScreenView
from utils.log import LOGGER
from utils.utilalsa import open_midi_port
from utils.utilother import kill_python


def process_looper(recv_looper: Connection, send_view: Connection) -> None:
    # noinspection PyBroadException
    try:
        looper = ExtendedCtrl(recv_looper, send_view)
        looper.process_messages()
    except Exception:
        LOGGER.error(f"process_looper: filed, error: {traceback.format_exc()}")
        kill_python()


def process_screenview(recv_view: Connection) -> None:
    # noinspection PyBroadException
    try:
        scr_view = ScreenView(recv_view)
        scr_view.process_messages()
    except Exception:
        LOGGER.error(f"process_screenview: filed, error: {traceback.format_exc()}")
        kill_python()


def go() -> None:
    recv_view, send_view = Pipe(False)  # screen update messages
    recv_looper, send_looper = Pipe(False)  # looper control messages

    if "--kbd" in sys.argv:
        in_port = KbdMidiPort()
    else:
        port_name = os.getenv('PEDAL_PORT_NAME', "PedalCommands_out")
        in_port = open_midi_port(port_name, is_input=True)
        if not in_port:
            msg = f"Failed to open MIDI port for commands input: {port_name}"
            raise RuntimeError(msg)

    Process(target=process_looper, args=(recv_looper, send_view), name="looper", daemon=True).start()

    Process(target=process_screenview, args=(recv_view,), name="screen", daemon=True).start()

    time.sleep(2)  # wait other objects to start
    if "--count" in sys.argv:  # will be counting notes in python controller
        m_ctrl = CountMidiControl(in_port, send_looper, "config/midicontrol", "playing", "0")
    else:
        m_ctrl = MidiControl(in_port, send_looper, "config/midicontrol", "playing", "0")

    m_ctrl.monitor()


if __name__ == "__main__":
    # noinspection PyBroadException
    try:
        go()
    except Exception:
        LOGGER.error(f"Start looper, error: {traceback.format_exc()}")
