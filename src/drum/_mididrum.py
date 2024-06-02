from __future__ import annotations

from random import random

import numpy as np

from drum.basedrum import BaseDrum
from utils.utilalsa import int_to_bytes
from utils.utilconfig import load_ini_section, ConfigName
from utils.utilportout import MidiOutWrap


class MidiDrum(BaseDrum):
    """Sends MIDI messages MIDI out port in main.ini
    Sys-ex message is sent to set BPM in external drum machine.
    For later sync at start of each bar a another SysEx is sent.
    """

    def __init__(self):
        BaseDrum.__init__(self)
        self._par = 0.2  # for MIDI drum it is probability to change program at bar start
        # ======== MIDI specific ===============
        self._mow = MidiOutWrap()
        dic = load_ini_section("MIDI")
        pname = dic.get(ConfigName.midi_out, "")
        self._mow.get_port(pname)

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        self._mow.port.send_message([0xB0, 8, round(volume * 127)])

    def set_bar_len(self, bar_len: int) -> None:
        super().set_bar_len(bar_len)
        lst = int_to_bytes(round(self._bpm * 100), 6)
        self._mow.port.send_message([0xF0, 0x5A] + lst + [0xF7])

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped:
            return
        if idx % self._bar_len == 0:
            if random() < self._par:
                self.randomize()
            self._mow.port.send_message([0xF0, 0x5B, 0xF7])

    def randomize(self) -> None:
        self._mow.port.send_message([0xF0, 0x5C, 0xF7])
        self.start()

    def play_fill(self, idx: int) -> None:
        self._mow.port.send_message([0xF0, 0x5D, 0xF7])

    def stop(self) -> None:
        self._mow.port.send_message([0xFC])
        super().stop()

    def show_param(self) -> str:
        base_info = super().show_param()
        port = f"{self._mow.name}"
        is_ok = f"{self._mow.port.is_port_open()}"
        config = self.get_config()
        return f"{base_info}\nport OK: {is_ok}/{port}\nconfig: {config}"
