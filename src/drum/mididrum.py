from random import random

import numpy as np
import rtmidi

from utils.util_midi import FakeMidiOut, get_out_port
from drum.basedrum import BaseDrum
from utils.util_alsa import int_to_bytes


class MidiDrum(BaseDrum):
    """Sends MIDI messages MIDI out port in main.ini
    Sys-ex message is sent to set BPM in external drum machine.
    For later sync at start of each bar another SysEx is sent.
    """

    def __init__(self):
        BaseDrum.__init__(self)
        self._param = 0.2  # for MIDI drum it is probability to change program at bar start
        self.port: rtmidi.MidiOut | FakeMidiOut = get_out_port()

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        self.port.send_message([0xB0, 8, round(volume * 127)])

    def set_bar_len(self, bar_len: int) -> None:
        super().set_bar_len(bar_len)
        lst = int_to_bytes(round(self._bpm * 100), 6)
        self.port.send_message([0xF0, 0x5A] + lst + [0xF7])

    def stop(self) -> None:
        self.port.send_message([0xFC])
        super().stop()

    def show_param(self) -> str:
        base_info = super().show_param()
        is_ok = f"{self.port.is_port_open()}"
        return f"{base_info}\nport OK: {is_ok}"

    def randomize(self) -> None:
        self.port.send_message([0xF0, 0x5C, 0xF7])
        self.start()

    def play_fill(self) -> None:
        self.port.send_message([0xF0, 0x5D, 0xF7])

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped:
            return
        if idx % self._bar_len == 0:
            if random() < self._param:
                self.randomize()
            self.port.send_message([0xF0, 0x5B, 0xF7])
