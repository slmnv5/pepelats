import logging
import os
import time
from threading import Thread, Event

import mido
import numpy as np

from drum._fakedrum import FakeDrum
from utils import MockMidiPort
from utils import SD_RATE
from utils import open_midi_port

CL_STOP = mido.Message('stop')
CL_START = mido.Message('start')
CL_TICK = mido.Message('clock')


def int_to_midi(k: int) -> mido.Message:
    byte_str: str = f'{k:028b}'
    byte_lst = [0xF0]
    byte_lst.extend(bytes(int(byte_str[i: i + 7], 2) for i in range(0, len(byte_str), 7)))
    byte_lst.append(0xF7)
    msg = mido.Message.from_bytes(byte_lst)
    return msg


def bpm_to_bar_seconds(bpm: float) -> float:
    return 60 * 4 / bpm


def midi_clock(midi_output, bpm):
    pulse_rate = 60.0 / (bpm.value * 24)
    while True:
        midi_output.send(CL_TICK)
        t1 = time.perf_counter()
        time.sleep(pulse_rate * 0.8)
        t2 = time.perf_counter()
        while (t2 - t1) < pulse_rate:
            t2 = time.perf_counter()


TICKS_PER_BAR: int = 96
MAX_DELAY = 1


class MidiDrum(FakeDrum):
    def __init__(self):
        super().__init__()
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
        self.__sleep_time: float = 1  # sleep time in seconds
        self.__upd: float = 0  # update time
        self.__length: int = 0

        Thread(target=self.__send_clock, name="send_clock_thread", daemon=True).start()

    def get_fixed(self) -> str:
        return "MIDI"

    def get_length(self) -> int:
        return self.__length

    def clear_drum(self) -> None:
        self.__length = 0
        self.__sleep_time = 0
        self.__play_event.clear()
        self.__out_port.send(CL_STOP)

    def prepare_drum(self, length: int) -> None:
        self.__length = length
        self.__play_event.set()
        self.__out_port.send(CL_START)
        self.__sleep_time = (length / SD_RATE) / TICKS_PER_BAR
        logging.info(f"Sleep time for MIDI clock: {self.__sleep_time}")

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if not self.get_length():
            return
        if not self.__play_event.is_set():
            self.__upd = time.monotonic()
            self.__out_port.send(CL_START)
            self.__play_event.set()
        elif not idx:
            self.__upd = time.monotonic()

    def __send_clock(self):
        while True:
            self.__play_event.wait()
            self.__upd = self.__upd + self.__sleep_time
            now = time.monotonic()
            wait = self.__upd - now
            if wait > 0:
                time.sleep(wait)
            self.__out_port.send(CL_TICK)
            if wait > MAX_DELAY:
                self.__play_event.clear()
                self.__out_port.send(CL_STOP)


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
