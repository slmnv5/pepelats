from multiprocessing import Queue
from threading import Timer

from buffer.loopctrl import LoopCtrl
from drum.drumfactory import create_drum
from song.songpart import SongPart


def test_1():
    queue = Queue()
    drum = create_drum("PatternDrum")
    ctrl = LoopCtrl(queue)
    ctrl.set_drum(drum)
    ctrl._set_is_rec(True)
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    loop = SongPart()
    loop.play(ctrl)
    ctrl.stop_never()
    Timer(5, ctrl.stop_at_bound, args=[0]).start()
    loop.play(ctrl)
