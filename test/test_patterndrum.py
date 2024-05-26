from multiprocessing import Queue
from threading import Timer

from buffer.loopctrl import LoopCtrl
from buffer.loopsimple import LoopSimple
from drum.drumfactory import create_drum

queue = Queue()
drum = create_drum("PatternDrum")
drum.set_config("Test.ini")
drum.set_bar_len(100_000)
drum.set_par(0)
drum.start()

ctrl = LoopCtrl(queue)
ctrl.set_drum(drum)
l1 = LoopSimple()
print("LooCtl", ctrl)
print("Loop", l1)


def test_1():
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    ctrl.stop_never()
    l1.play_buffer(ctrl)
