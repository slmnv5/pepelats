import logging
from threading import Timer

from buffer import LoopSimple
from buffer._oneloopctrl import OneLoopCtrl


def test1():
    from drum.audiodrum import AudioDrum

    c1 = OneLoopCtrl(AudioDrum())
    c1.set_is_rec(True)
    Timer(2, c1.stop_at_bound, args=[0]).start()
    l1 = LoopSimple(c1)
    l1.play_buffer()
    c1.get_stop_event().clear()
    Timer(3, c1.stop_at_bound, args=[0]).start()
    l1.play_buffer()
    logging.debug(f"Volume: {l1}")


test1()
