from multiprocessing import Queue

from mvc.menuhost import MenuHost
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class SimpleMidiControl(MenuHost):

    def __init__(self, midi_in, queue: Queue):
        MenuHost.__init__(self, queue)
        self._midi_in = midi_in
        self._midi_in.set_callback(self._process_msg)

    def start(self) -> None:
        super().start()

    # noinspection PyUnusedLocal
    def _process_msg(self, event, data=None) -> None:
        msg, _ = event
        assert msg and type(msg) == list and all(type(x) == int for x in msg)
        note = msg[1]
        velo = msg[2]
        self._menuhost_send(f"{note}-{velo}")
