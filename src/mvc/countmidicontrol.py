from multiprocessing import Queue
from threading import Timer

import rtmidi.midiconstants

from mvc.menuhost import MenuHost
from utils.utillog import MYLOG
from utils.utilmidi import KbdMidiIn
from utils.utilmidi import MIDI_MIN_VELO, MIDI_STD_VELO

_CTRL = rtmidi.midiconstants.CONTROL_CHANGE
_ON = rtmidi.midiconstants.NOTE_ON
_OFF = rtmidi.midiconstants.NOTE_OFF


class MidiCcToNote:
    """Convert MIDI CC to note ON/OFF messages.
    Used for expression pedal to send note ON/OF when pedal goes Down/Up """

    def __init__(self):
        self.__prev_msg: list[int] = [0, 0, 0]
        self.__sent_on = False

    def convert(self, msg: list[int]) -> list[int]:
        if msg[1] != self.__prev_msg[1] or msg[0] != self.__prev_msg[0]:
            self.__prev_msg = msg
            self.__sent_on = False
            return []

        # expression pedal goes down, hence value goes down
        if self.__prev_msg[2] > msg[2] and not self.__sent_on:
            self.__prev_msg = msg
            self.__sent_on = True
            return [0x90, msg[1], 100]

        # expression pedal goes up, hence value goes down
        if self.__prev_msg[2] < msg[2] and self.__sent_on:
            self.__prev_msg = msg
            self.__sent_on = False
            return [0x80, msg[1], 0]

        self.__prev_msg = msg
        return []


class CountMidiControl(MenuHost):
    """Count MIDI notes to increase number of messages MIDI pedal can send,
    tap, double tap, long tap - send notes with different velocity. Count algorithm:
    take the original note, count taps, +5 if the last tap is long,
    set velocity of note to counted value. After inactivity period ~0.6 seconds count is reset"""

    _COUNT_SEC: float = 0.600

    def __init__(self, midi_in: rtmidi.MidiIn | KbdMidiIn, queue: Queue):
        MenuHost.__init__(self, queue)
        self._p_count: int = midi_in.get_port_count()
        self._midi_in = midi_in
        self.__on_count: int = 0
        self.__off_count: int = 0
        self.__past_note: int = -1  # original MIDI note
        self.__midi_cc_to_note = MidiCcToNote()
        self._midi_in.set_callback(self._process_msg)

    def is_alive(self) -> bool:
        return self._midi_in.get_port_count() >= self._p_count

    # noinspection PyUnusedLocal
    def _process_msg(self, event, data=None) -> None:
        msg, _ = event
        assert msg and isinstance(msg, list) and all(isinstance(x, int) for x in msg), f"msg: {msg}, type: {type(msg)}"
        if msg[0] & 0xF0 == _CTRL:
            msg = self.__midi_cc_to_note.convert(msg)
        if not msg:
            return

        note_on: bool = msg[0] & 0xF0 == _ON
        note: int = msg[1]
        velo: int = msg[2]
        if note_on and velo < MIDI_MIN_VELO:
            return
        else:
            velo = MIDI_STD_VELO

        if self.__past_note != note:
            self.__on_count, self.__off_count, self.__past_note = 0, 0, note  # init counters for new note
            if note_on:
                MYLOG.debug(f"Sending non-counted MIDI note: {note}")  # new note ON, send it
                self._send(note, velo)

        if not note_on and self.__on_count == 0:
            return  # old OFF came before new ON, we ignore

        if note_on:
            self.__on_count += 1
        else:
            self.__off_count += 1

        Timer(CountMidiControl._COUNT_SEC, self.__count_enqueue,
              [self.__on_count, self.__off_count, note]).start()

    def __count_enqueue(self, on_count: int, off_count: int, note: int) -> None:
        # if we came here after a delay and note counts have changed, just return
        if (self.__past_note != note or self.__on_count != on_count
                or self.__off_count != off_count):
            return

        # note and count did not change for long time, we send MIDI
        count = self.__on_count
        if self.__on_count > self.__off_count:
            count += 5

        self.__on_count, self.__off_count, self.__past_note = 0, 0, -1
        MYLOG.debug(f"Sending counted MIDI note: {note}, {count}")
        self._send(note, count)
