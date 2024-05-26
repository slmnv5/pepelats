from multiprocessing import Queue
from threading import Timer

from buffer.loopsimple import LoopSimple
from control.manyloopctrl import ManyLoopCtrl
from utils.utilalsa import make_sin_sound, correct_sound
from utils.utilaudio import SD_TYPE, SD_CH



def test_1():
    run_once("PatternDrum")
    run_once("EuclidDrum")
    run_once("MidiDrum")
    run_once("LoopDrum")


def run_once(drum_type: str) -> None:
    ctrl = ManyLoopCtrl(Queue())
    ctrl.set_drum(drum)
    ctrl.get_drum().set_bar_len(100_000)
    ctrl.get_drum().start()

    sound = make_sin_sound(440, 7)
    sound = correct_sound(sound, SD_CH, SD_TYPE)

    assert ctrl.get_drum().get_bar_len() == 100_000
    print(f"\n{drum_type}\n{ctrl}\n{ctrl.get_drum()}")

    loop = LoopSimple()
    loop.record_samples(sound, 0)
    ctrl.idx = len(sound)

    loop.trim_buffer(ctrl)
    Timer(5, ctrl.stop_at_bound, [0]).start()
    loop.play_buffer(ctrl)
