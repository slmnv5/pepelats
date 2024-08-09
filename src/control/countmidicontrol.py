from multiprocessing import Queue
from threading import Timer

from rtmidi.midiconstants import NOTE_ON

from control.midicontrol import MidiAdapter
from menu.menuhost import MenuHost
from utils.util_log import MY_LOG


class CountMidiControl(MidiAdapter, MenuHost):
    """Count MIDI notes to increase number of messages MIDI pedal can send,
    tap, double tap, long tap - send notes with different velocity. Count algorithm:
    take the original note, count taps, +5 if the last tap is long,
    set velocity of note to counted value. After inactivity period ~0.6 seconds count is reset"""

    _COUNT_SEC: float = 0.600

    def __init__(self, queue: Queue):
        MenuHost.__init__(self, queue)
        MidiAdapter.__init__(self)
        self.__on_count: int = 0
        self.__off_count: int = 0
        self.__past_note: int = -1  # original MIDI note

    def _send_note(self, msg_type: int, note: int, velo: int) -> None:
        note_on: bool = msg_type == NOTE_ON
        if self.__past_note != note:
            self.__on_count, self.__off_count, self.__past_note = 0, 0, note  # init counters for new note
            if note_on:
                MY_LOG.debug(f"Sending non-counted MIDI note: {note}")  # new note ON, send it
                self._send_command(note, velo)
            elif self.__on_count == 0:
                return  # old OFF came before new ON, ignore2

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

        # note and count did not change for long time, calculate velocity
        new_velo = self.__on_count
        if self.__on_count > self.__off_count:
            new_velo += 5  # long hold on the last tap

        self.__on_count, self.__off_count, self.__past_note = 0, 0, -1
        MY_LOG.debug(f"Sending counted MIDI note: {note}, {new_velo}")
        self._send_command(note, new_velo)

    def is_broken(self) -> bool:
        return self._midi_in.get_port_count() < self._p_count
