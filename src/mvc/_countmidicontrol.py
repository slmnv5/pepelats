import logging
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from threading import Timer
from typing import List

from midi.midiportfactory import MidiPortFactory
from mvc.menucontrol import MenuControl, MenuLoader


def is_midi_cc(msg: List[int]) -> bool:
    return 0xB0 <= msg[0] <= 0xBF


def is_midi_note_on(msg: List[int]) -> bool:
    return 0x90 <= msg[0] <= 0x9F


def is_midi_note(msg: List[int]) -> bool:
    return 0x80 <= msg[0] <= 0x9F


class MidiCcToNote:
    """Convert MIDI control change to note ON/OFF messages.
    Useed for expression pedal to send note ON/OF when pedal goes Down/Up """

    def __init__(self):
        self.__prev_msg: List[int] = [80, 0, 0]
        self.__sent_on = False

    def convert(self, msg: List[int]):
        if msg[1] != self.__prev_msg[1]:
            self.__prev_msg: List[int] = msg
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


class CountMidiControl(MenuControl):
    """Count MIDI notes to increase number of messages MIDI pedal can send,
    tap, double tap, long tap - send notes with different velocity. Count algorithm:
    take the original note, count taps, +5 if the last tap is long,
    set velocity of note to counted value. After inactivity period ~0.6 sec. count is reset"""

    __count_sec: float = 0.600

    def __init__(self, in_port, send_conn: Connection, menu_loader: MenuLoader):
        MenuControl.__init__(self, send_conn, menu_loader)
        self.__in_port = in_port
        self.__on_count: int = 0
        self.__off_count: int = 0
        self.__past_count_note: int = 0  # mapped for count
        self.__past_note: int = -1  # original MIDI note
        self.__midi_cc_to_note = MidiCcToNote()

    def monitor(self) -> None:
        logging.info(f"Started {self.__class__.__name__}")
        while True:
            msg: List[int] = self.__in_port.receive()
            if is_midi_cc(msg):
                msg = self.__midi_cc_to_note.convert(msg)
            if not msg or not is_midi_note(msg):
                continue

            logging.debug(f"{self.__class__.__name__} got MIDI message: {msg}")
            note: int = msg[1]
            velo: int = msg[2]
            str_note = f"{note}:{velo}"
            is_on = is_midi_note_on(msg)
            if is_on and velo < 10:
                # this is counted note inserted in queue
                logging.info(f"Sending counted note: {str_note}")
                self._send(str_note)
                continue

            if is_on and self.__past_note != note:
                # do not sent same note many times, we count it below
                logging.info(f"Sending note: {str_note}")
                self._send(str_note)

            self.__past_note = note
            self.__update_count(note, is_on)
            Timer(CountMidiControl.__count_sec, self.__count_enqueue,
                  [self.__on_count, self.__off_count, note]).start()

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

    def __count_enqueue(self, on_count: int, off_count: int, note: int) -> None:
        # if we came here after a delay and note counts have changed we do not send
        self.__past_note = -1  # need reset as we ignore same notes
        if self.__past_count_note != note \
                or self.__on_count != on_count \
                or self.__off_count != off_count:
            return

        # note and count did not change for long, we send MIDI
        count = self.__on_count
        if self.__on_count > self.__off_count:
            count += 5

        self.__on_count = self.__off_count = 0
        event = [0x90, note, count]
        self.__in_port.put(event)

    def __str__(self):
        return f"{self.__class__.__name__} note={self.__past_count_note} " \
               f"on_count={self.__on_count} off_count={self.__off_count}"


if __name__ == "__main__":

    def test():
        from multiprocessing.dummy import Pipe
        import os

        logging.getLogger().setLevel(logging.INFO)
        recv_fake, send_fake = Pipe()
        port_name = os.getenv('PEDAL_PORT_NAME', "PedalCommands_out")
        in_port = MidiPortFactory().get_input()
        if not in_port:
            msg = f"Failed to open MIDI port for commands input: {port_name}"
            raise RuntimeError(msg)

        menu_loader = MenuLoader("config/menu", "play", "0")
        m_ctrl = CountMidiControl(in_port, send_fake, menu_loader)
        try:
            m_ctrl.monitor()  # will throw EOF when all mesages processed
        except EOFError:
            pass


    test()
