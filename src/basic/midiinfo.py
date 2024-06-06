import os
from typing import Callable

import keyboard
import rtmidi

from utils.utilconfig import load_ini_section, ConfigName
from utils.utillog import MYLOG

_IS_LINUX = os.name == "posix"
_HAS_KBD = os.environ.get('HAS_KBD', "").upper() in ["Y", "YES", "TRUE", "1"]


class KbdMidiIn:
    """Using keyboard keys instead of MIDI notes"""

    def __init__(self):
        dic = load_ini_section("MIDI")
        if not _IS_LINUX:
            notes_str = "1, 2, 3, 4, q, w"
        else:
            notes_str = dic.get(ConfigName.kbd_notes_linux, '')

        kbd_lst: list[str] = [x.strip() for x in notes_str.split(',')]
        if len(kbd_lst) != 6:
            raise RuntimeError(f"Option {ConfigName.kbd_notes_linux} in main.ini must have 6 values: {notes_str}")

        notes_str = dic.get(ConfigName.kbd_notes_midi, '')
        midi_lst = [x.strip() for x in notes_str.split(',')]
        if len(midi_lst) != 6:
            raise RuntimeError(f"Option {ConfigName.kbd_notes_midi} in main.ini must have 6 values: {notes_str}")
        if not all([x.isdigit() for x in midi_lst]):
            raise RuntimeError(f"Option {ConfigName.kbd_notes_midi} in main.ini must be 6 integers: {notes_str}")
        midi_lst = [int(x) for x in midi_lst]

        if not all([0 <= x < 128 for x in midi_lst]):
            raise RuntimeError(f"Option {ConfigName.kbd_notes_midi} in main.ini must be 0<=x<128: {notes_str}")

        self.__kbd_notes: dict[str, int] = dict(zip(kbd_lst, midi_lst))
        self._func: Callable[[tuple[list, any]], None] = self._fake_callback
        self._data: any = None
        self._pressed_key = False
        keyboard.on_press(callback=self.on_press, suppress=True)
        keyboard.on_release(callback=self.on_release, suppress=True)

    @staticmethod
    def is_port_open() -> bool:
        return True

    @staticmethod
    def get_port_count() -> int:
        return 0

    def set_callback(self, func, data=None) -> None:
        self._data = data
        self._func = func

    @staticmethod
    def _fake_callback(event: tuple[list[int], float]) -> None:
        pass

    # noinspection PyUnresolvedReferences
    def on_press(self, kbd_event):
        if kbd_event.name == "esc":
            keyboard.unhook_all()
            MYLOG.debug("Done unhook_all and exit !")
            # noinspection PyProtectedMember
            os._exit(1)
            return

        val = self.__kbd_notes.get(kbd_event.name, None)
        if val is not None and not self._pressed_key:
            msg = [0x90, val, 100]
            self._pressed_key = True
            self._func((msg, 0))

    def on_release(self, kbd_event):
        val = self.__kbd_notes.get(kbd_event.name, None)
        if val is not None and self._pressed_key:
            msg = [0x80, val, 0]
            self._pressed_key = False
            self._func((msg, 0))


def _get_in_port(pname: str = "") -> rtmidi.MidiIn | KbdMidiIn:
    midi_in: rtmidi.MidiIn = rtmidi.MidiIn()
    midi_in.close_port()
    p_count: int = midi_in.get_port_count()
    for k in range(p_count):
        port_name = midi_in.get_port_name(k)
        if pname in port_name:
            midi_in.open_port(k, name="In")
            if midi_in.is_port_open():
                return midi_in

    if _IS_LINUX and not _HAS_KBD:
        raise RuntimeError(f"Failed ot open MIDI IN port: {pname}")

    MYLOG.error(f"MIDI IN port is not open: {pname}, using computer keyboard")
    return KbdMidiIn()


class FakeMidiOut:

    def __init__(self):
        pass

    @staticmethod
    def is_port_open() -> bool:
        return True

    def close_port(self):
        pass

    @staticmethod
    def send_message(msg):
        if not msg or msg[0] == 0xF8 or msg[0] == 0xFE:
            return  # do not log too much

        MYLOG.info(f"~~~~~~~~~~~~Send MIDI message: {msg}")


def _get_out_port(pname: str = "") -> rtmidi.MidiOut | FakeMidiOut:
    midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
    midi_out.close_port()
    for k in range(midi_out.get_port_count()):
        port_name = midi_out.get_port_name(k)
        if pname in port_name:
            midi_out.open_port(k, name="Out")
            if midi_out.is_port_open():
                MYLOG.info(f"MIDI OUT port is open: {pname}")
                return midi_out

    MYLOG.error(f"MIDI OUT port is not open: {pname}, using fake port")
    return FakeMidiOut()


def show_out_ports(pname: str = "") -> str:
    midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
    port_lst = midi_out.get_ports()
    port_lst = [x.split(":")[0] for x in port_lst if "RtMidi" not in x and "Through" not in x]
    port_str = "\n".join(port_lst)
    return f"OUT: {pname} open: {midi_out.port.is_port_open()}\n{port_str}"


class MidiInfo:
    __instance = None

    def __new__(cls):
        """ creates a singleton object, if it is not created, else returns existing """
        if not cls.__instance:
            cls.__instance = super(MidiInfo, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

        dic: dict[str, str] = load_ini_section("MIDI")
        pname = dic.get(ConfigName.midi_in, "")
        self.MIDI_IN = _get_in_port(pname)

        pname = dic.get(ConfigName.midi_out, "")
        self.MIDI_OUT = _get_out_port(pname)

        # min note velocity to consider, counted notes have small velocity
        self.MIDI_MIN_VELO: int = 10
        # standard note velocity used in menu files, note louder than MIDI_MIN_VELO is converted to MIDI_STD_VELO
        self.MIDI_STD_VELO: int = 100

        dic = load_ini_section("MIDI")
        notes_str = dic.get(ConfigName.kbd_notes_midi, '')
        midi_lst = [x.strip() for x in notes_str.split(',')]
        if len(midi_lst) != 6:
            raise RuntimeError(f"Option {ConfigName.kbd_notes_midi} in main.ini must have 6 values: {notes_str}")

        if not all([x.isdigit() for x in midi_lst]):
            raise RuntimeError(f"Option {ConfigName.kbd_notes_midi} in main.ini must be 6 integers: {notes_str}")
        midi_lst = [int(x) for x in midi_lst]

        if not all([0 <= x < 128 for x in midi_lst]):
            raise RuntimeError(f"Option {ConfigName.kbd_notes_midi} in main.ini must be 0<=x<128: {notes_str}")

        self.MIDI_DICT: dict[int, str] = dict(zip(midi_lst, ['a', 'b', 'c', 'd', 'e', 'f']))
