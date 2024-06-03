from multiprocessing import Queue
from threading import Timer, Thread
from time import sleep

from control.songctrl import SongCtrl
from song.loopsimple import LoopSimple
from song.songpart import SongPart
from utils.utilconfig import ConfigName


def test_1():
    queue = Queue()
    ctrl = SongCtrl(queue, "PatternDrum")
    t = Thread(target=ctrl.menu_client_start, name="process queue", args=[])
    t.start()  # start processing message queue

    part = SongPart()
    print("SongCtrl", ctrl)
    print("Part", part)

    assert ctrl.get_drum().get_bar_len() == 0
    ctrl._set_is_rec(True)
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    part.play_loop(ctrl)  # recording from mic
    while not ctrl.get_drum().get_bar_len():
        sleep(1)  # wait for another thread to create drum

    assert ctrl.get_drum().get_bar_len()
    ctrl._drum_randomize()
    ctrl.stop_never()
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    part.play_loop(ctrl)  # playing recorded sound + drum
    queue.put([ConfigName.menu_client_stop])
    assert ctrl.get_drum().get_bar_len() == part.length


def test_2():
    queue = Queue()
    ctrl = SongCtrl(queue, "EuclidPtrnDrum")
    t = Thread(target=ctrl.menu_client_start, name="process queue", args=[])
    t.start()  # start processing message queue

    loop = LoopSimple()
    print("SongCtrl", ctrl)
    print("Loop", loop)

    assert ctrl.get_drum().get_bar_len() == 0
    ctrl._set_is_rec(True)
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    loop.play_loop(ctrl)  # recording from mic
    while not ctrl.get_drum().get_bar_len():
        sleep(1)  # wait for another thread to create drum

    ctrl._drum_randomize()
    assert ctrl.get_drum().get_bar_len()
    ctrl.stop_never()
    Timer(3, ctrl.stop_at_bound, args=[0]).start()
    loop.play_loop(ctrl)  # playing recorded sound + drum
    queue.put([ConfigName.menu_client_stop])
    assert ctrl.get_drum().get_bar_len() == loop.length
