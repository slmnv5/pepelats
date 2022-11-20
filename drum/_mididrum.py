import logging
import os
import time
from threading import Thread, Event
from typing import List

import mido
import numpy as np

from drum._fakedrum import FakeDrum
from utils import MockMidiPort
from utils import SD_RATE
from utils import open_midi_port

CL_STOP: mido.Message = mido.Message('stop')
CL_START: mido.Message = mido.Message('start')
SYSEX_PREFIX: List[int] = [33, 33]


def bpm_to_bar_seconds(bpm: float) -> float:
    return 60 * 4 / bpm


def bar_seconds_to_bpm(bar_seconds: float) -> float:
    return 60 * 4 / bar_seconds


TICKS_PER_BAR: int = 96
MAX_DELAY = 1


class MidiDrum(FakeDrum):
    def __init__(self):
        super().__init__()
        self.__start_at: float = 0
        self.__bpm: float = 0
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
        self.__sleep_time: float = 1  # sleep time in seconds
        self.__upd: float = 0  # update time
        self.__length: int = 0

        Thread(target=self.__send_clock, name="send_clock_thread", daemon=True).start()

    # MIDI sysex message that contains quarter notoes milli for tap tempo
    # This integer is stored in 7bit valuse MSB, LSB]
    def __sysex(self) -> List[int]:
        beat_milli = self.__length * 1000 / 4 / SD_RATE
        beat_milli = round(beat_milli)
        byte_str: str = f'{beat_milli:014b}'
        byte_lst = [int(byte_str[0: 7], 2), int(byte_str[7: 14], 2)]
        return byte_lst

    def get_fixed(self) -> str:
        return f"MIDI {self.__bpm:.2F}"

    def get_length(self) -> int:
        return self.__length

    def clear_drum(self) -> None:
        self.__length = 0
        self.__sleep_time = 0
        self.__play_event.clear()
        self.__out_port.send(CL_STOP)

    def prepare_drum(self, length: int) -> None:
        assert length > 0
        self.__length = length
        self.__out_port.send(CL_START.copy())
        bar_seconds = length / SD_RATE
        self.__bpm = bar_seconds_to_bpm(bar_seconds)
        self.__sleep_time = bar_seconds / TICKS_PER_BAR
        self.__play_event.set()
        self.__start_at = time.perf_counter()
        lst = SYSEX_PREFIX + self.__sysex()
        msg = mido.Message('sysex', data=lst)
        self.__out_port.send(msg)
        msg = mido.Message('start')
        self.__out_port.send(msg)
        logging.info(f"Sleep time for MIDI clock: {self.__sleep_time}")

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if not self.__length:
            return
        if not (idx % self.__length):
            self.__upd = self.__start_at = time.perf_counter()

    def __send_clock(self):
        while True:
            self.__play_event.wait()
            time.sleep(self.__sleep_time)
            msg = mido.Message('clock')
            self.__out_port.send(msg)


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
