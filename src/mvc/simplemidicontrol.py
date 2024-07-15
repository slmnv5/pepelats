from multiprocessing import Queue

import rtmidi.midiconstants

from basic.midiinfo import KbdMidiIn, get_in_port
from mvc._menuhost import MenuHost


class SimpleMidiControl(MenuHost):

    def __init__(self, queue: Queue):
        MenuHost.__init__(self, queue)
        self._midi_in: rtmidi.MidiIn | KbdMidiIn = get_in_port()
        self._p_count: int = self._midi_in.get_port_count()
        self._midi_in.set_callback(self._process_msg)

    def _is_alive(self) -> bool:
        return super()._is_alive() and self._midi_in.get_port_count() >= self._p_count

    # noinspection PyUnusedLocal
    def _process_msg(self, event, data=None) -> None:
        msg, _ = event
        assert msg and isinstance(msg, list) and all(isinstance(x, int) for x in msg)

        note_on: bool = msg[0] & 0xF0 == rtmidi.midiconstants.NOTE_ON
        note: int = msg[1]
        velo: int = msg[2]
        if (note_on and velo < self.min_velo) or not note_on:
            return
        velo = self.std_velo
        str_note = f"{note}-{velo}"
        self._send(note, velo)
