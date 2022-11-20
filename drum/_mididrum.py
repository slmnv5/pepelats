import logging
import os
import time
from threading import Thread, Event
from typing import List, Tuple

import mido
import numpy as np

from drum._fakedrum import FakeDrum
from utils import MockMidiPort
from utils import SD_RATE
from utils import open_midi_port

SYSEX_PREFIX: List[int] = [33, 33]


def bpm_qtr_milli(bar_seconds: float) -> Tuple[float, int]:
    bpm = 60 * 4 / bar_seconds
    return bpm, round(bar_seconds / 4 * 1000)  # millis


# MIDI sysex message that contains quarter notoes milli for tap tempo
# This integer is stored in 7bit valuse MSB, LSB]
def sysex(qtr_milli: int) -> List[int]:
    byte_str: str = f'{qtr_milli:014b}'
    byte_lst = [int(byte_str[0: 7], 2), int(byte_str[7: 14], 2)]
    return byte_lst


TICKS_PER_QTR: int = 24
MAX_DELAY = 1


class MidiDrum(FakeDrum):
    def __init__(self):
        super().__init__()
        self.__length: int = 0
        self.__qtr_milli: int = 0
        self.__bpm: float = 0
        self.__slp: float = 1  # sleep time in seconds

        self.__updt: float = 0  # update time
        self.__strt: float = 0  # start time
        self.__cnt: int = 0  # count bars since start

        if os.name != "posix":
            self.__out_port = MockMidiPort()
        else:
            port_name = os.getenv('CLOCK_PORT_NAME', "DrumClock_in")
            self.__out_port = open_midi_port(port_name, is_input=False)
            if not self.__out_port:
                msg = f"Failed to open MIDI port for clock output: {port_name}"
                logging.error(msg)
                raise RuntimeError(msg)

        self.__play_event: Event = Event()
        assert not self.__play_event.is_set(), "Event must be clear in ctor"

        Thread(target=self.__send_clock, name="send_clock_thread", daemon=True).start()

    def __send_clock(self):
        while True:
            self.__play_event.wait()
            now = time.perf_counter()
            self.__cnt += 1
            planned = self.__strt + self.__slp * self.__cnt
            wait = planned - now
            if wait > 0:
                time.sleep(wait)
            self.__out_port.send(mido.Message('clock'))

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self.__length:
            if not (idx % self.__length):
                self.__updt = self.__strt = time.perf_counter()
                self.__cnt = 0

    def get_fixed(self) -> str:
        return f"{self}"

    def get_length(self) -> int:
        return self.__length

    def clear_drum(self) -> None:
        self.__length = 0
        self.__slp = 0
        self.__play_event.clear()
        self.__out_port.send(mido.Message('stop'))

    def prepare_drum(self, length: int) -> None:
        assert length > 0
        self.__length = length
        self.__out_port.send(mido.Message('start'))
        self.__bpm, self.__qtr_milli = bpm_qtr_milli(length / SD_RATE)
        self.__slp = self.__qtr_milli / TICKS_PER_QTR / 1000
        self.__play_event.set()
        lst = SYSEX_PREFIX + sysex(self.__qtr_milli)
        self.__out_port.send(mido.Message('sysex', data=lst))
        self.__out_port.send(mido.Message('start'))
        logging.info(f"Sleep time for MIDI clock: {self.__slp}")

    def __str__(self):
        return f"Milli:{self.__qtr_milli} BPM:{self.__bpm:.2F}"


if __name__ == "__main__":
    def test(use_midi: bool):
        from loop._loopsimple import LoopSimple
        from loop._oneloopctrl import OneLoopCtrl
        from threading import Timer
        from drum import RealDrum
        from utils import make_sin_sound

        drum = MidiDrum() if use_midi else RealDrum()

        sound = make_sin_sound(440, 7.1)
        drum.prepare_drum(100_000)
        while not drum.get_length():
            time.sleep(0.1)

        ctrl = OneLoopCtrl(drum)
        loop = LoopSimple(ctrl)
        loop._record_samples(sound, 0)  # record in the middle of loop
        ctrl.idx = len(sound)
        print("======== start =============")
        loop.trim_buffer()
        Timer(7.1, ctrl.stop_at_bound, [0]).start()
        loop.play_buffer()


    test(True)
    test(False)
