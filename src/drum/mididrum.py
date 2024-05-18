from __future__ import annotations

from multiprocessing import Queue
from random import random
from threading import Thread

import numpy as np

from drum.basedrum import BaseDrum
from utils.utilalsa import int_to_bytes
from utils.utilconfig import find_path, load_ini_section, ConfigName
from utils.utillog import get_my_log
from utils.utilother import FileFinder
from utils.utilportout import MidiOutWrap

my_log = get_my_log(__name__)


class MidiDrum(BaseDrum):
    """Sends MIDI messages as configured in midi.ini
    Sys-ex message may be sent (_bpm_msg) to set up and start drum machine.
    For later sync at start of each bar a message (_bar_msg) is sent.
    List of all control messages is below.
    """

    _MSG_LIST = ['_bar_msg', '_bpm_msg', '_volume_msg', '_progs_list', '_stop_msg', '_prog_msg']
    _KEY_LIST = ["BPM", "VOLUME", "PROG", "FILL_BYTES"]

    def __init__(self):
        BaseDrum.__init__(self)
        self._par = 0.2  # for MIDI drum it is probability to change program at bar start
        self._dname = find_path("config/drum/midi")
        self._ff = FileFinder(self._dname, True, ".ini")
        assert self._ff.get_item()
        # ======== MIDI specific ===============
        self._midi_out = MidiOutWrap()
        self._ptn = 0  # pattern/program number from _ptn_lst
        self._stopped: bool = True
        self._simple_msg_dic: dict[str, list[list[int] | int]] = dict()  # list of plain MID messages
        self._param_msg_dic: dict[str, any] = dict()  # list of messages to be evaluated
        self._queue = Queue()
        Thread(target=self._send_msg, daemon=True).start()

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        self._queue.put("_volume_msg")

    def _send_msg(self) -> None:
        while True:
            msg = self._queue.get()
            if msg in self._simple_msg_dic:
                my_log.debug(f"Simple message: {msg}")
                self._send_midi(self._simple_msg_dic[msg])
            elif msg in self._param_msg_dic:
                local_vars = {"BPM": self._bpm, "VOLUME": self._volume,
                              "PROG": self._ptn, "FILL_BYTES": self._fill_bytes}
                evaluated_msg = self._eval(self._param_msg_dic[msg], local_vars)
                my_log.debug(f"Evaluated message: {evaluated_msg}")
                if evaluated_msg:
                    self._send_midi(evaluated_msg)
            else:
                my_log.info(f"Not found MIDI message: {msg}")

    @staticmethod
    def _eval(expr: str, local_vars: dict[str, any]) -> list[any]:
        if not expr:
            return list()
        # noinspection PyBroadException
        try:
            return eval(expr, None, local_vars)
        except Exception as ex:
            my_log.error(f"Evaluation error: {ex} in expression: {expr}")
            return list()

    def get_config(self) -> str:
        return self._ff.get_item()

    def set_config(self, config: str) -> None:
        self._ff.idx_from_item(config)

    def _set_bar_len(self, bar_len: int) -> None:
        super()._set_bar_len(bar_len)
        self._queue.put("_bpm_msg")

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if not self._bar_len or self._stopped:
            return
        if idx % self._bar_len == 0:
            if random() < self._par:
                self.random_drum()
            self._queue.put("_bar_msg")

    def random_drum(self) -> None:
        super().random_drum()
        self._ptn = self._ptn_lst[self._ptn_idx]
        self._queue.put("_prog_msg")

    def _send_midi(self, msg: list[list[int] | int]) -> None:
        assert isinstance(msg, list) and all(type(x) in [list, int] for x in msg), f"Message: {msg}"
        if msg and isinstance(msg[0], int):
            self._midi_out.port.send_message(msg)
        else:
            for m in [x for x in msg if x and isinstance(x[0], int)]:
                self._midi_out.port.send_message(m)

    @staticmethod
    def _fill_bytes(param: float, byte_count: int) -> list[int]:
        param = round(param)
        lst = int_to_bytes(param, byte_count)
        return lst

    def load_drum_config(self, bar_len: int = None) -> None:
        self.stop_drum()
        fname = self._ff.get_full_name()
        dic = load_ini_section(fname, "MIDI")
        pname = dic.get(ConfigName.midi_out)
        self._midi_out.get_port(pname)
        self._make_evals(bar_len)

    def _make_evals(self, bar_len: int):
        fname = self._ff.get_full_name()
        dic: dict[str, str] = load_ini_section(fname, "MESSAGES")
        self._param_msg_dic.clear()
        self._simple_msg_dic.clear()

        for k, v in [(x, y) for (x, y) in dic.items() if x in self._MSG_LIST and y]:
            has_params = any(x in v for x in self._KEY_LIST)
            if has_params:
                try:
                    compiled_msg = compile(v, '<string>', 'eval')
                    self._param_msg_dic[k] = compiled_msg
                except Exception as ex:
                    my_log.error(f"Error: {ex} in param. evaluation of: {k}:{v}")
            else:
                evaluated_msg = self._eval(v, dict())
                if not evaluated_msg:
                    my_log.error(f"Failed simple evaluation of: {k}:{v}")
                else:
                    self._simple_msg_dic[k] = evaluated_msg
        bar_len = self._bar_len if bar_len is None else bar_len
        self._set_bar_len(bar_len)
        self._ptn_lst = self._simple_msg_dic.get("_progs_list", None)
        if not self._ptn_lst:
            self._ptn_lst = list(range(128))
        my_log.info(f"Loaded MIDI drum, simple messages: {self._simple_msg_dic}")
        my_log.info(f"Loaded MIDI drum, parameter message keys: {list(self._param_msg_dic.keys())}")

    def stop_drum(self) -> None:
        self._queue.put("_stop_msg")
        super().stop_drum()
        self._stopped = True

    def start_drum(self) -> None:
        """ To start drums in time we use _bar_msg """
        self._stopped = False

    def show_drum_config(self) -> str:
        return self._ff.get_str()

    def iterate_drum_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def show_drum_param(self) -> str:
        base_info = super().show_drum_param()
        port = f"{self._midi_out.name}"
        is_ok = f"{self._midi_out.port.is_port_open()}"
        config = self.get_config()
        return f"{base_info}\nport OK: {is_ok}/{port}\nconfig: {config}"

    def get_drum_header(self) -> str:
        return f"{self}:{self._ptn}/{len(self._ptn_lst)}:{self.get_config()}"
