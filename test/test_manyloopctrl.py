# noinspection PyProtectedMember
from control._manyloopctrl import ManyLoopCtrl


def test_1():
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


test_1()
