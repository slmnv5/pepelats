

from random import random

import numpy as np
import rtmidi

from drum.basedrum import BaseDrum
from utils.utilalsa import int_to_bytes
from utils.utilconfig import load_ini_section, ConfigName
from utils.utilmidi import FakeMidiOut, get_out_port


class MidiDrum(BaseDrum):
    """Sends MIDI messages MIDI out port in main.ini
    Sys-ex message is sent to set BPM in external drum machine.
    For later sync at start of each bar another SysEx is sent.
    """

    def __init__(self):
        BaseDrum.__init__(self)
        self._par = 0.2  # for MIDI drum it is probability to change program at bar start
        # ======== MIDI specific ===============
        dic = load_ini_section("MIDI")
        pname = dic.get(ConfigName.midi_out, "")
        self.port: rtmidi.MidiOut | FakeMidiOut
        self.name: str
        self.port, self.name = get_out_port(pname)

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
        port = f"{self.name}"
        is_ok = f"{self.port.is_port_open()}"
        return f"{base_info}\nport OK: {is_ok}/{port}"

    def randomize(self) -> None:
        self.port.send_message([0xF0, 0x5C, 0xF7])
        self.start()

    def play_fill(self, idx: int) -> None:
        self.port.send_message([0xF0, 0x5D, 0xF7])

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped:
            return
        if idx % self._bar_len == 0:
            if random() < self._par:
                self.randomize()
            self.port.send_message([0xF0, 0x5B, 0xF7])
