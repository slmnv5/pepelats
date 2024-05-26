from multiprocessing import Queue
from threading import Timer

from buffer.loopctrl import LoopCtrl
from buffer.loopsimple import LoopSimple
from drum.drumfactory import DrumFactory

queue = Queue()
drum = DrumFactory.create_drum("EuclidDrum")
drum.set_config("Test.ini")
drum.set_bar_len(88_000)
drum.set_par(0)
drum.start()

c1 = LoopCtrl(queue, drum)
l1 = LoopSimple()
print("LooCtl", c1)
print("Loop", l1)


def test_1():
    Timer(3, c1.stop_at_bound, args=[0]).start()
    c1.stop_never()
    l1.play_buffer(c1)
