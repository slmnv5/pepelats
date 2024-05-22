from __future__ import annotations

from random import random

import numpy as np

from drum.basedrum import BaseDrum
from utils.utilalsa import int_to_bytes
from utils.utilconfig import load_ini_section, find_path, ConfigName
from utils.utillog import get_my_log
from utils.utilportout import MidiOutWrap

my_log = get_my_log(__name__)


class MidiDrum(BaseDrum):
    """Sends MIDI messages MIDI out port in main.ini
    Sys-ex message is sent to set BPM in external drum machine.
    For later sync at start of each bar a another SysEx is sent.
    """

    def __init__(self):
        BaseDrum.__init__(self)
        self._ptn_lst = [x for x in range(32)]
        self._par = 0.2  # for MIDI drum it is probability to change program at bar start
        # ======== MIDI specific ===============
        self._mow = MidiOutWrap()
        dic = load_ini_section(find_path(ConfigName.main_ini), "MIDI")
        pname = dic.get(ConfigName.midi_out, "")
        tmp: bool = self._mow.get_port(pname)
        assert tmp, "MIDI out port must be open. It may be a fake port just for logging"

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        self._mow.port.send_message([0xB0, 8, round(volume * 127)])

    def _set_bar_len(self, bar_len: int) -> None:
        super()._set_bar_len(bar_len)
        lst = int_to_bytes(round(self._bpm * 100), 6)
        self._mow.port.send_message([0xF0, 0x5A] + lst + [0xF7])

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if not self._bar_len or self._is_stopped:
            return
        if idx % self._bar_len == 0:
            if random() < self._par:
                self.randomize()
            self._mow.port.send_message([0xF0, 0x5B, 0xF7])

    def randomize(self) -> None:
        super().randomize()
        self._ptn_idx = self._ptn_lst[self._ptn_idx]
        self._mow.port.send_message([0xC0, self._ptn_lst[self._ptn_idx]])

    def stop(self) -> None:
        self._mow.port.send_message([0xFC])
        super().stop()

    def show_param(self) -> str:
        base_info = super().show_param()
        port = f"{self._mow.name}"
        is_ok = f"{self._mow.port.is_port_open()}"
        config = self.get_config()
        return f"{base_info}\nport OK: {is_ok}/{port}\nconfig: {config}"

    def get_header(self) -> str:
        return f"{self}:{self._ptn_idx}/{len(self._ptn_lst)}:{self.get_config()}"

    def get_config(self) -> str:
        return ""

    def set_config(self, config: str = None) -> None:
        return

    def show_config(self) -> str:
        return ""

    def iterate_config(self, steps: int) -> None:
        pass
