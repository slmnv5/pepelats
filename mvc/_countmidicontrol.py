# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from threading import Timer

import mido

from log.logger import LOGR
from utils import CmdTranslator


def is_midi_note_on(msg):
    return 0x90 <= msg.bytes()[0] <= 0x9f


def is_midi_ctrl_chg(msg):
    return 0xb0 <= msg.bytes()[0] <= 0xbf


def is_midi_note(msg):
    return 0x80 <= msg.bytes()[0] <= 0x9f


class MidiCcToNote:
    """Convert MIDI control change to note ON/OFF messages.
    Needed for expression pedal to send note ON/OF when pedal goes Down/Up
    Use this to convert expression pedal CC into note ON/OFF"""

    def __init__(self):
        self.__prev_msg = mido.Message.from_bytes([0x80, 0, 0])
        self.__sent_on = False

    def convert(self, msg):
        if is_midi_note(msg):
            self.__prev_msg = msg
            self.__sent_on = False
            return msg

        if not (is_midi_ctrl_chg(msg)):
            self.__prev_msg = msg
            self.__sent_on = False
            return None

        if msg.bytes()[1] != self.__prev_msg.bytes()[1]:
            self.__prev_msg = msg
            self.__sent_on = False
            return None

        # expression pedal goes down, hence value goes down
        if self.__prev_msg.bytes()[2] > msg.bytes()[2]:
            if not self.__sent_on:
                self.__prev_msg = msg
                self.__sent_on = True
                return mido.Message.from_bytes([0x90, msg.bytes()[1], 100])
            else:
                return None
        else:
            if self.__sent_on:
                self.__prev_msg = msg
                self.__sent_on = False
                return mido.Message.from_bytes([0x80, msg.bytes()[1], 0])
            else:
                return None


class CountMidiControl(CmdTranslator):
    """Count MIDI notes to increase number of messages MIDI pedal send,
    tap, double tap, long tap - send different notes. Count algorithm:
    --take the original note 60, find the mapped note 80
        --to mapped note add number of counted taps e.g. 80+2
        --add 5 if the last tap is long e.g. 80+2+5, send note 87
        --after inactivity period ~0.6 sec. count of taps set to zero"""

    count_restart_seconds = 0.600

    def __init__(self, in_port, send_conn: Connection, dir_name: str, map_name: str, map_id: str):
        CmdTranslator.__init__(self, send_conn, dir_name, map_name, map_id)
        self.__in_port = in_port
        self.__on_count: int = 0
        self.__off_count: int = 0
        self.__past_count_note: int = 0  # mapped for count
        self.__past_note: int = -1  # original MIDI note
        self.__midi_cc_to_note = MidiCcToNote()

    def monitor(self) -> None:
        LOGR.info(f"Started MidiConverter")
        while True:
            msg = self.__in_port.receive(block=True)
            msg = self.__midi_cc_to_note.convert(msg)
            if not msg:
                continue

            LOGR.debug(f"{self.__class__.__name__} got MIDI message: {msg}")
            note: int = msg.bytes()[1]
            vel: int = 100
            str_note = f"{note}:{vel}"

            is_on = is_midi_note_on(msg)
            if is_on and self.__past_note != note:
                # do not sent same note many times, we count it below
                LOGR.debug(f"Sending original note: {note}")
                self._translate_and_send(str_note)

            self.__past_note = note
            self.__update_count(note, is_on)
            on_count, off_count = self.__on_count, self.__off_count
            Timer(CountMidiControl.count_restart_seconds, self.__count_and_send,
                  [on_count, off_count, note]).start()

    def __update_count(self, note: int, is_on: bool) -> None:
        # if we got another note number, restart count
        if self.__past_count_note != note:
            self.__on_count = self.__off_count = 0
            self.__past_count_note = note

        if is_on:
            self.__on_count += 1
        else:
            # old OFF note may come before ON, we correct here
            if self.__on_count > 0:
                self.__off_count += 1

    def __count_and_send(self, on_count: int, off_count: int, note: int) -> None:
        # if we came here after a delay and note counts have changed we do not send
        self.__past_note = -1
        if self.__past_count_note != note \
                or self.__on_count != on_count \
                or self.__off_count != off_count:
            return

        # note and count did not change for long, we send MIDI
        count = self.__on_count
        if self.__on_count > self.__off_count:
            count += 5

        self.__on_count = self.__off_count = 0
        str_note = f"{note}:{count}"
        LOGR.debug(f"Sending counted note: {str_note}")
        self._translate_and_send(str_note)

    def __str__(self):
        return f"{self.__class__.__name__} note={self.__past_count_note} " \
               f"on_count={self.__on_count} off_count={self.__off_count}"


if __name__ == "__main__":
    pass
