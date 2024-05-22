from multiprocessing import Queue

import rtmidi.midiconstants

from mvc.menuhost import MenuHost
from utils.utilconfig import MIN_VELO, STD_VELO
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
        assert msg and isinstance(msg, list) and all(isinstance(x, int) for x in msg)

        note_on: bool = msg[0] & 0xF0 == rtmidi.midiconstants.NOTE_ON
        note: int = msg[1]
        velo: int = msg[2]
        if note_on and velo < MIN_VELO:
            return
        velo = STD_VELO
        str_note = f"{note}-{velo}"

        if velo < MIN_VELO:
            return
        velo = STD_VELO
        self._menuhost_send(f"{note}-{velo}")
