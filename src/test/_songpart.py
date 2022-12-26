from threading import Timer

from buffer import OneLoopCtrl
from song import SongPart


def test():
    from drum.audiodrum import AudioDrum

    c1 = OneLoopCtrl(AudioDrum())
    c1.__is_rec = True
    Timer(3, c1.stop_at_bound, args=[0]).start()
    l1 = SongPart(c1)
    l1.play_buffer()
    c1.get_stop_event().clear()
    Timer(5, c1.stop_at_bound, args=[0]).start()
    l1.play_buffer()
    l1.set_ctrl(c1)


test()
