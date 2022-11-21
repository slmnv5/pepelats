import logging
import sys
import traceback

from utils import open_midi_port

level = "WARN"
if "--debug" in sys.argv:
    level = "DEBUG"
if "--info" in sys.argv:
    level = "INFO"

logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(message)s', filename='log.txt', filemode='w')
logging.error('>>> Starting looper <<<')

import os
import time
from multiprocessing import Pipe, Process
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from kbdmidi import KbdMidiPort
from loop import ExtendedCtrl
from mvc import CountMidiControl
from mvc import MidiControl, ScreenView


def process_looper(recv_looper: Connection, send_view: Connection) -> None:
    looper = ExtendedCtrl(recv_looper, send_view)
    looper.process_messages()


def process_screenview(recv_view: Connection) -> None:
    scr_view = ScreenView(recv_view)
    scr_view.process_messages()


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
            logging.error(msg)
            raise RuntimeError(msg)

    Process(target=process_looper, args=(recv_looper, send_view), name="looper", daemon=True).start()

    Process(target=process_screenview, args=(recv_view,), name="screen", daemon=True).start()

    time.sleep(2)  # wait other objects to start
    if "--count" in sys.argv:  # will be counting notes in python controller
        m_ctrl = CountMidiControl(in_port, send_looper, "config/midi", "playing", "0")
    else:
        m_ctrl = MidiControl(in_port, send_looper, "config/midi", "playing", "0")

    m_ctrl.monitor()


if __name__ == "__main__":
    # noinspection PyBroadException
    try:
        go()
    except Exception:
        logging.error(f"Start looper, error: {traceback.format_exc()}")
