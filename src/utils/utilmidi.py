import os
from typing import Callable

import keyboard
import rtmidi

from utils.utilconfig import load_ini_section, ConfigName
from utils.utillog import MYLOG

_keyboard = load_ini_section("KEYBOARD")
tmp = _keyboard.get(ConfigName.kbd_notes_linux, '')
if os.name != "posix":
    tmp = "1, 2, 3, 4, q, w"
tmp = [x.strip() for x in tmp.split(',')]
if len(tmp) != 6:
    raise RuntimeError(f"Option kbd_notes_linux in main.ini must have 6 values, found: {tmp}")
KBD_NOTES: list[str] = tmp

# ==================================
tmp = _keyboard.get(ConfigName.kbd_notes_midi, '')
tmp = [x.strip() for x in tmp.split(',')]
if len(tmp) != 6:
    raise RuntimeError(f"kbd_notes_midi in main.ini must have 6 values, found: {tmp}")

if not all([x.isdigit() for x in tmp]):
    raise RuntimeError(f"kbd_notes_midi in main.ini must be 6 integers, found: {tmp}")
tmp = [int(x) for x in tmp]

if not all([0 <= x < 128 for x in tmp]):
    raise RuntimeError(f"kbd_notes_midi in main.ini must be 0<=x<128, found: {tmp}")

MIDI_DICT: dict[int, str] = dict(zip(tmp, ['a', 'b', 'c', 'd', 'e', 'f']))

# ==================================
# min note velocity to consider, counted notes have small velocity
MIDI_MIN_VELO: int = 10
_midi = load_ini_section("MIDI")
# noinspection PyBroadException
try:
    MIDI_MIN_VELO = int(_midi.get(ConfigName.midi_min_velocity, '10'))
except Exception as ex:
    MIDI_MIN_VELO = 10
    MYLOG.error(f"Failed loading from main.ini file: {ConfigName.midi_min_velocity}, error: {ex}")

# standard note velocity used in menu files, note louder than MIDI_MIN_VELO is converted to MIDI_STD_VELO
MIDI_STD_VELO: int = 100

_IS_LINUX = os.name == "posix"
_HAS_KBD = os.environ.get('HAS_KBD', "").upper() in ["Y", "YES", "TRUE", "1"]


class KbdMidiIn:
    """Using keyboard keys instead of MIDI notes"""

    def __init__(self):
        self.__kbd_notes: dict[str, int] = dict(zip(KBD_NOTES, MIDI_DICT.keys()))
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


def get_in_port(pname: str = "") -> tuple[rtmidi.MidiIn | KbdMidiIn, str]:
    midi_in: rtmidi.MidiIn = rtmidi.MidiIn()
    midi_in.close_port()
    p_count: int = midi_in.get_port_count()
    for k in range(p_count):
        port_name = midi_in.get_port_name(k)
        if pname in port_name:
            midi_in.open_port(k, name="In")
            if midi_in.is_port_open():
                return midi_in, port_name

    if _IS_LINUX and not _HAS_KBD:
        raise RuntimeError(f"Failed ot open MIDI IN port: {pname}")

    MYLOG.error(f"MIDI IN port is not open: {pname}, using computer keyboard")
    return KbdMidiIn(), "KbdMidiIn"


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


def get_out_port(pname: str = "") -> tuple[rtmidi.MidiOut | FakeMidiOut | None, str]:
    midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
    midi_out.close_port()
    for k in range(midi_out.get_port_count()):
        port_name = midi_out.get_port_name(k)
        if pname in port_name:
            midi_out.open_port(k, name="Out")
            if midi_out.is_port_open():
                return midi_out, port_name

    MYLOG.error(f"MIDI OUT port is not open: {pname}, using fake port")
    return FakeMidiOut(), "FakeMidiOut"


def show_out_ports(pname: str = "") -> str:
    midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
    port_lst = midi_out.get_ports()
    port_lst = [x.split(":")[0] for x in port_lst if "RtMidi" not in x and "Through" not in x]
    port_str = "\n".join(port_lst)
    return f"OUT: {pname} open: {midi_out.port.is_port_open()}\n{port_str}"
