from asyncio import Queue

from rtmidi import MidiIn
from rtmidi.midiconstants import CONTROL_CHANGE, NOTE_OFF, NOTE_ON

from menuhost.menuhost import MenuHost
from utils.util_menu import MIDI_MIN_VELO, MIDI_STD_VELO
from utils.util_midi import KbdMidiIn, get_in_port


class _MidiCcToNote:
    """Convert MIDI CC to note ON/OFF messages.
    Used for expression pedal to send note ON/OF when pedal goes Down/Up """

    def __init__(self):
        self.__prev_msg: tuple[int, int, int] = (0, 0, 0)
        self.__sent_on = False

    def convert(self, msg: list[int]) -> tuple[int, int, int] | None:
        if msg[1] != self.__prev_msg[1] or msg[0] != self.__prev_msg[0]:
            self.__prev_msg, self.__sent_on = msg, False
            return None

        # expression pedal goes down, value goes down
        if self.__prev_msg[2] > msg[2] and not self.__sent_on:
            self.__prev_msg, self.__sent_on = msg, True
            return NOTE_ON, msg[1], 127

        # expression pedal goes up, value goes down
        if self.__prev_msg[2] < msg[2] and self.__sent_on:
            self.__prev_msg, self.__sent_on = msg, False
            return NOTE_OFF, msg[1], 0

        self.__prev_msg = msg
        return None


class MidiAdapter:

    def __init__(self):
        self._midi_in: MidiIn | KbdMidiIn = get_in_port()
        self._p_count: int = self._midi_in.get_port_count()
        self._midi_in.set_callback(self.__process_msg)
        self._cc_converter = _MidiCcToNote()

    def is_broken(self) -> bool:
        return self._midi_in.get_port_count() < self._p_count

    def __process_msg(self, event, _=None) -> None:
        msg, _ = event
        if msg[0] & 0xF0 == CONTROL_CHANGE:
            msg = self._cc_converter.convert(msg)
        if not msg:
            return

        msg_type = msg[0] & 0xF0
        if msg_type not in [NOTE_ON, NOTE_OFF]:
            return

        note, velo = msg[1], msg[2]
        if msg_type == NOTE_ON:
            if velo < MIDI_MIN_VELO:
                return
            else:
                velo = MIDI_STD_VELO
        self._send_note(msg_type, note, velo)

    def _send_note(self, msg_type: int, note: int, velo: int) -> None:
        pass


class MidiControl(MidiAdapter, MenuHost):
    def __init__(self, queue: Queue):
        MenuHost.__init__(self, queue)
        MidiAdapter.__init__(self)

    # noinspection PyUnusedLocal
    def _send_note(self, msg_type: int, note: int, velo: int) -> None:
        self._send_command(note, velo)

    def is_broken(self) -> bool:
        return MidiAdapter.is_broken(self)
