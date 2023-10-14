from multiprocessing import Queue
from threading import Timer

from buffer.loopctrl import LoopCtrl
from buffer.loopsimple import LoopSimple
from utils.utilfactory import create_drum


def test_1():
    queue = Queue()
    dr = create_drum("PatternDrum")
    dr.start_drum()
    c1 = LoopCtrl(queue, dr)
    c1._set_is_rec(True)
    l1 = LoopSimple()
    print()
    print("LooCtl", c1)
    print("Loop", l1)
    Timer(3, c1.stop_at_bound, args=[0]).start()
    l1.play_buffer(c1)
    c1.stop_never()
    Timer(3, c1.stop_at_bound, args=[0]).start()
    l1.play_buffer(c1)
