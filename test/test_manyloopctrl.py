from threading import Timer
from time import sleep

from buffer.loopsimple import LoopSimple
from control.manyloopctrl import ManyLoopCtrl
from utils.utilalsa import make_sin_sound, correct_dtype


def test_1():
    ctrl = ManyLoopCtrl()
    ctrl.get_drum().load_drum_config(None, 100_000)
    sound = make_sin_sound(440, 7)
    sound = correct_dtype(sound)
    while not ctrl.get_drum().get_bar_len():
        sleep(0.1)

    assert ctrl.get_drum().get_bar_len() == 100_000
    print(f"==============>{ctrl}")

    loop = LoopSimple()
    loop._record_samples(sound, 0)
    ctrl.idx = len(sound)

    loop.trim_buffer(ctrl)
    Timer(5, ctrl.stop_at_bound, [0]).start()
    loop.play_buffer(ctrl)

    assert ctrl.get_drum().get_bar_len() == 100_000
