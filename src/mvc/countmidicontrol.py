from multiprocessing import Queue
from threading import Timer

import rtmidi.midiconstants

from mvc.menuhost import MenuHost
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class MidiCcToNote:
    """Convert MIDI CC to note ON/OFF messages.
    Used for expression pedal to send note ON/OF when pedal goes Down/Up """

    def __init__(self):
        self.__prev_msg: list[int] = [80, 0, 0]
        self.__sent_on = False

    def convert(self, msg: list[int]):
        if msg[1] != self.__prev_msg[1]:
            self.__prev_msg = msg
            self.__sent_on = False
            return None

        # expression pedal goes down, hence value goes down
        if self.__prev_msg[2] > msg[2]:
            if not self.__sent_on:
                self.__prev_msg = msg
                self.__sent_on = True
                return [0x90, msg[1], 100]
            else:
                return None
        else:
            if self.__sent_on:
                self.__prev_msg = msg
                self.__sent_on = False
                return [0x80, msg[1], 0]
            else:
                return None


class CountMidiControl(MenuHost):
    """Count MIDI notes to increase number of messages MIDI pedal can send,
    tap, double tap, long tap - send notes with different velocity. Count algorithm:
    take the original note, count taps, +5 if the last tap is long,
    set velocity of note to counted value. After inactivity period ~0.6 seconds count is reset"""

    __count_sec: float = 0.600

    def __init__(self, midi_in, queue: Queue):
        MenuHost.__init__(self, queue)
        self._midi_in = midi_in
        self.__on_count: int = 0
        self.__off_count: int = 0
        self.__past_note: int = -1  # original MIDI note
        self.__midi_cc_to_note = MidiCcToNote()
        self._midi_in.set_callback(self._process_msg)

    def start(self) -> None:
        super().start()

    # noinspection PyUnusedLocal
    def _process_msg(self, event, data=None) -> None:
        msg, deltatime = event
        assert msg and type(msg) == list and all(type(x) == int for x in msg), f"msg: {msg}, type: {type(msg)}"
        if msg[0] & 0xF0 == rtmidi.midiconstants.CONTROL_CHANGE:
            msg = self.__midi_cc_to_note.convert(msg)
        if not msg:
            return

        note: int = msg[1]
        velo: int = msg[2]
        str_note = f"{note}-{velo}"
        is_on = msg[0] & 0xF0 == rtmidi.midiconstants.NOTE_ON

        if is_on and self.__past_note != note:
            # do not send same note many times, we count it below
            my_log.debug(f"Sending non-counted note: {str_note}")
            self._menuhost_send(str_note)

        if self.__past_note != note:
            self.__on_count, self.__off_count = 0, 0
            self.__past_note = note

        if is_on:
            self.__on_count += 1
        elif self.__on_count > 0:  # old OFF note may come before new ON, we correct here
            self.__off_count += 1

        Timer(CountMidiControl.__count_sec, self.__count_enqueue,
              [self.__on_count, self.__off_count, note]).start()

    def __count_enqueue(self, on_count: int, off_count: int, note: int) -> None:
        # if we came here after a delay and note counts have changed we do not send
        if self.__past_note != note or self.__on_count != on_count or self.__off_count != off_count:
            return

        # note and count did not change for long time, we send MIDI
        count = self.__on_count
        if self.__on_count > self.__off_count:
            count += 5

        self.__on_count = self.__off_count = 0
        self.__past_note = -1
        str_note = f"{note}-{count}"
        self._menuhost_send(str_note)
