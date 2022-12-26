from threading import Thread, Event

from buffer import LoopSimple
from buffer import OneLoopCtrl
from drum.basedrum import SimpleDrum
from song import Song
from song import SongPart
from utils.utilconfig import MAX_LEN


def test():
    from buffer._oneloopctrl import OneLoopCtrl
    from threading import Timer
    from drum.audiodrum import AudioDrum
    import time

    ctrl = ManyLoopCtrl(AudioDrum())
    drum = ctrl.get_drum()

    drum.prepare_drum(100_000)
    while not drum.get_length():
        time.sleep(0.1)

    duration: float = 7.5

    ctrl.get_play_event().set()
    Timer(duration, ctrl.stop_at_bound, [0]).start()
    time.sleep(duration)

    ctrl.get_play_event().set()
    Timer(duration, ctrl.stop_at_bound, [0]).start()
    time.sleep(duration)


test()
