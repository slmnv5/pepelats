from multiprocessing import Queue
from threading import Timer

from buffer.loopctrl import LoopCtrl
from buffer.loopsimple import LoopSimple
from drum.drumfactory import create_drum


def test_1():
    queue = Queue()
    drum = create_drum("PatternDrum")
    drum.start()
    ctrl = LoopCtrl(queue)
    ctrl.set_drum(drum)
    ctrl._set_is_rec(True)
    l1 = LoopSimple()
    print()
    print("LooCtl", ctrl)
    print("Loop", l1)
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    l1.play_buffer(ctrl)
    ctrl.stop_never()
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    l1.play_buffer(ctrl)
