import os
from typing import Any

import keyboard
import rtmidi

from utils.util_config import load_ini_section
from utils.util_log import MY_LOG, NoMidiInputFound
from utils.util_menu import KEY_NOTE
from utils.util_name import AppName

_IS_LINUX = os.name == "posix"
_HAS_KBD = not _IS_LINUX or os.environ.get('HAS_KBD', "").upper() in ["Y", "YES", "TRUE", "1"]


class KbdMidiIn:
    """Using keyboard keys instead of MIDI notes"""

    def __init__(self):
        self._func = None
        self._data: Any = None
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

    # noinspection PyU2nresolvedReferences
    def on_press(self, kbd_event):
        if kbd_event.name == "esc":
            keyboard.unhook_all()
            MY_LOG.debug("Done unhook_all")
            self._port_count = 0

        val = KEY_NOTE.get(kbd_event.name, None)
        if val is not None and not self._pressed_key:
            msg = [0x90, val, 100]
            self._pressed_key = True
            self._func((msg, 0))

    def on_release(self, kbd_event):
        val = KEY_NOTE.get(kbd_event.name, None)
        if val is not None and self._pressed_key:
            msg = [0x80, val, 0]
            self._pressed_key = False
            self._func((msg, 0))


class FakeMidiOut:
    @staticmethod
    def is_port_open() -> bool:
        return True

    def close_port(self):
        pass

    @staticmethod
    def send_message(msg):
        if not msg or msg[0] == 0xF8 or msg[0] == 0xFE:
            return  # do not log too much

        MY_LOG.info(f"~~~~~~~~~~~~Send MIDI message: {msg}")


def get_in_port() -> rtmidi.MidiIn | KbdMidiIn:
    dic: dict[str, str] = load_ini_section("MIDI")
    pname = dic.get(AppName.midi_in, "")
    midi_in: rtmidi.MidiIn = rtmidi.MidiIn()
    midi_in.close_port()
    p_count: int = midi_in.get_port_count()
    for k in range(p_count):
        port_name = midi_in.get_port_name(k)
        if pname in port_name:
            midi_in.open_port(k, name="In")
            if midi_in.is_port_open():
                MY_LOG.info(f"Found requested MIDI IN port: {port_name}")
                return midi_in

    if not _HAS_KBD:
        raise NoMidiInputFound(f"Failed to open MIDI IN port: {pname}")

    MY_LOG.warning(f"MIDI IN port is not open: {pname}, using computer keyboard")
    return KbdMidiIn()


def get_out_port() -> rtmidi.MidiOut | FakeMidiOut:
    dic: dict[str, str] = load_ini_section("MIDI")
    pname = dic.get(AppName.midi_out, "")

    midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
    midi_out.close_port()
    for k in range(midi_out.get_port_count()):
        port_name = midi_out.get_port_name(k)
        if pname in port_name:
            midi_out.open_port(k, name="Out")
            if midi_out.is_port_open():
                MY_LOG.info(f"Found requested MIDI OUT port: {port_name}")
                return midi_out

    MY_LOG.error(f"MIDI OUT port is not open: {pname}, using fake port")
    return FakeMidiOut()
