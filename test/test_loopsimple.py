from multiprocessing import Queue
from threading import Timer

from control.loopctrl import LoopCtrl
from song.loopsimple import LoopSimple
from drum.drumfactory import create_drum


def test_1():
    queue = Queue()
    drum = create_drum("PatternDrum")
    drum.start()
    ctrl = LoopCtrl(queue)
    ctrl.set_drum(drum)
    ctrl._set_is_rec(True)
    loop = LoopSimple()
    print()
    print("LooCtl", ctrl)
    print("Loop", loop)
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    loop.play_loop(ctrl)
    ctrl.stop_never()
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    loop.play_loop(ctrl)
