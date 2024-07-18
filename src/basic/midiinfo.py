import os

import keyboard
import rtmidi

from utils.utilconfig import load_ini_section, ConfigName
from utils.utillog import MyLog

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
        self._func = None
        self._data: any = None
        self._pressed_key = False
        keyboard.on_press(callback=self.on_press, suppress=True)
        keyboard.on_release(callback=self.on_release, suppress=True)
        self._port_count: int = 1

    @staticmethod
    def is_port_open() -> bool:
        return True

    def get_port_count(self) -> int:
        return self._port_count

    def set_callback(self, func, data=None) -> None:
        self._data = data
        self._func = func

    # noinspection PyUnresolvedReferences
    def on_press(self, kbd_event):
        if kbd_event.name == "esc":
            keyboard.unhook_all()
            MyLog().debug("Done unhook_all")
            self._port_count = 0

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

        MyLog().info(f"~~~~~~~~~~~~Send MIDI message: {msg}")


class MidiInfo:
    __instance = None

    def __new__(cls):
        """ creates a singleton object """
        if not cls.__instance:
            cls.__instance = super(MidiInfo, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        MyLog().warning(f"=========== Created MidiInfo in process id: {os.getpid()} ==========")
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


def get_in_port() -> rtmidi.MidiIn | KbdMidiIn:
    dic: dict[str, str] = load_ini_section("MIDI")
    pname = dic.get(ConfigName.midi_in, "")
    midi_in: rtmidi.MidiIn = rtmidi.MidiIn()
    midi_in.close_port()
    p_count: int = midi_in.get_port_count()
    for k in range(p_count):
        port_name = midi_in.get_port_name(k)
        if pname in port_name:
            midi_in.open_port(k, name="In")
            if midi_in.is_port_open():
                MyLog().info(f"Found requested MIDI IN port: {port_name}")
                return midi_in

    if _IS_LINUX and not _HAS_KBD:
        raise RuntimeError(f"Failed to open MIDI IN port: {pname}")

    MyLog().error(f"MIDI IN port is not open: {pname}, using computer keyboard")
    return KbdMidiIn()


def get_out_port() -> rtmidi.MidiOut | FakeMidiOut:
    dic: dict[str, str] = load_ini_section("MIDI")
    pname = dic.get(ConfigName.midi_out, "")

    midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
    midi_out.close_port()
    for k in range(midi_out.get_port_count()):
        port_name = midi_out.get_port_name(k)
        if pname in port_name:
            midi_out.open_port(k, name="Out")
            if midi_out.is_port_open():
                MyLog().info(f"Found requested MIDI OUT port: {port_name}")
                return midi_out

    MyLog().error(f"MIDI OUT port is not open: {pname}, using fake port")
    return FakeMidiOut()
