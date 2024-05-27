from __future__ import annotations

import os
from multiprocessing import Queue
from typing import Union, Callable

import keyboard
import rtmidi

from mvc.countmidicontrol import CountMidiControl
from mvc.menuhost import MenuHost
from utils.utilconfig import find_path, load_ini_section, ConfigName
from utils.utillog import MYLOG
from utils.utilmidi import KBD_NOTES, MIDI_NOTES

_IS_LINUX = os.name == "posix"
_HAS_KBD = os.environ.get('HAS_KBD', "").upper() in ["Y", "YES", "TRUE", "1"]


def get_pedal_control(q: Queue) -> MenuHost:
    dic = load_ini_section(find_path(ConfigName.main_ini), "MIDI")
    pname = dic.get(ConfigName.midi_in, "")
    miw = MidiInWrap()
    if not miw.get_port(pname):
        raise RuntimeError(f"MIDI IN port is not open: {pname}")
    return CountMidiControl(miw.port, q)


class _KbdMidiIn:
    """Using keyboard keys instead of MIDI notes"""

    def __init__(self):
        self.__kbd_notes: dict[str, int] = dict(zip(KBD_NOTES, MIDI_NOTES))
        self._func: Callable[[tuple[list, any]], None] = self._fake_callback
        self._data: any = None
        self._pressed_key = False
        keyboard.on_press(callback=self.on_press, suppress=True)
        keyboard.on_release(callback=self.on_release, suppress=True)

    @staticmethod
    def is_port_open() -> bool:
        return True

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


TYPE_MIDI_IN = Union[rtmidi.MidiIn, _KbdMidiIn]


class MidiInWrap:
    def __init__(self):
        self._midi_in: rtmidi.MidiIn = rtmidi.MidiIn()
        self.port: TYPE_MIDI_IN = self._midi_in
        self.name: str = ""

    def get_port(self, pname: str) -> bool:
        self._midi_in.close_port()
        if _HAS_KBD or not _IS_LINUX:
            self.port, self.name = _KbdMidiIn(), "KbdMidiIn"
            return True

        self.name = ""
        for k in range(self._midi_in.get_port_count()):
            port_name = self._midi_in.get_port_name(k)
            if pname in port_name:
                self._midi_in.open_port(k, name="In")
                self.port, self.name = self._midi_in, port_name
                break

        if self.name and self.port.is_port_open():
            return True
        else:
            return False

    def show(self) -> str:
        return f"IN: {self.name} open: {self.port.is_port_open()}\n{self._midi_in.get_ports()}"
