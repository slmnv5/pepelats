import logging

from drum.audiodrum import AudioDrum

logging.getLogger().setLevel(logging.DEBUG)


def test_1():
    from buffer import LoopSimple
    from buffer._oneloopctrl import OneLoopCtrl
    from threading import Timer
    from utils.utilalsa import make_sin_sound
    from time import sleep
    logging.basicConfig(level=logging.DEBUG)
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
    logging.debug("======== start =============")
    loop.trim_buffer()
    Timer(5, ctrl.stop_at_bound, [0]).start()
    loop.play_buffer()
    drum.clear_drum()
    assert drum.get_length() == 0



