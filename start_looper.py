import os
import sys
import time
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

import mido

from kbdmidi import KbdMidiPort
from log.logger import LOGR
from loop import ExtendedCtrl
from mvc import CountMidiControl
from mvc import MidiControl, ScreenView

MIDI_PORT_NAME = "MIDI_PORT_NAME"


def process_looper(recv_looper: Connection, send_view: Connection) -> None:
    looper = ExtendedCtrl(recv_looper, send_view)
    looper.process_messages()


def process_screenview(recv_view: Connection) -> None:
    scr_view = ScreenView(recv_view)
    scr_view.process_messages()


def open_midi_port(name: str, is_input: bool):
    # noinspection PyUnresolvedReferences
    port_list = mido.get_input_names() if is_input else mido.get_output_names()
    for port_name in port_list:
        if name in port_name:
            LOGR.info(f"opening: {port_name} input: {is_input}")
            if is_input:
                # noinspection PyUnresolvedReferences
                return mido.open_input(port_name)
            else:
                # noinspection PyUnresolvedReferences
                return mido.open_output(port_name)


def go() -> None:
    recv_view, send_view = Pipe(False)  # screen update messages
    recv_looper, send_looper = Pipe(False)  # looper control messages

    if "--kbd" in sys.argv:
        in_port = KbdMidiPort()
    else:
        port_name = os.getenv(MIDI_PORT_NAME, "PedalCommands_out")
        in_port = open_midi_port(port_name, is_input=True)
        if not in_port:
            msg = f"Failed to open MIDI port for commands input: {port_name}"
            LOGR.error(msg)
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
    go()
