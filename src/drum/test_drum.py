import logging
from threading import Timer
from time import sleep

from buffer import LoopSimple
# noinspection PyProtectedMember
from buffer._oneloopctrl import OneLoopCtrl
from drum.audiodrum import AudioDrum
from drum.mididrum import MidiDrum, FakeMidiDrum
from utils.utilalsa import make_sin_sound

logging.basicConfig(level=logging.DEBUG)


def test_2():
    ctrl = OneLoopCtrl(FakeMidiDrum(None))
    drum = ctrl.get_drum()

    drum.prepare_drum(100_000)
    sound = make_sin_sound(440, 7.1)
    assert drum.get_length() == 100_000
    logging.debug(f"==============>{drum}")

    loop = LoopSimple(ctrl)
    loop._record_samples(sound, 0)
    ctrl.idx = len(sound)

    loop.trim_buffer()
    Timer(5, ctrl.stop_at_bound, [0]).start()
    loop.play_buffer()
    drum.clear_drum()
    assert drum.get_length() == 0


def test_1():
    ctrl = OneLoopCtrl(AudioDrum())
    drum = ctrl.get_drum()
    drum.prepare_drum(100_000)
    sound = make_sin_sound(440, 7.1)
    while not drum._length:
        sleep(0.1)

    assert drum.get_length() == 100_000
    logging.debug(f"==============>{drum}")

    loop = LoopSimple(ctrl)
    loop._record_samples(sound, 0)
    ctrl.idx = len(sound)

    loop.trim_buffer()
    Timer(5, ctrl.stop_at_bound, [0]).start()
    loop.play_buffer()
    drum.clear_drum()
    assert drum.get_length() == 0
