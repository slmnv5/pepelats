from multiprocessing import Queue
from threading import Timer

from control.loopctrl import LoopCtrl
from song.loopsimple import LoopSimple
from drum.drumfactory import create_drum

queue = Queue()
drum = create_drum("PatternDrum")
drum.set_config("Test.ini")
drum.set_bar_len(100_000)
drum.set_par(0)
drum.start()

ctrl = LoopCtrl(queue)
ctrl.set_drum(drum)
loop = LoopSimple()
print("LooCtl", ctrl)
print("Loop", loop)


def test_1():
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    ctrl.stop_never()
    loop.play(ctrl)
