from __future__ import annotations

from typing import Union

import rtmidi

from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class _FakeMidiOut:

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

        my_log.info(f"~~~~~~~~~~~~Send MIDI message: {msg}")


TYPE_MIDI_OUT = Union[rtmidi.MidiOut, _FakeMidiOut]


class MidiOutWrap:
    def __init__(self):
        self._midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
        self.port: TYPE_MIDI_OUT = self._midi_out
        self.name: str = ""

    def get_port(self, pname: str) -> bool:
        self._midi_out.close_port()
        self.name = ""
        for k in range(self._midi_out.get_port_count()):
            port_name = self._midi_out.get_port_name(k)
            if pname in port_name:
                self._midi_out.open_port(k, name="Out")
                self.port, self.name = self._midi_out, port_name
                break

        if self.name and self.port.is_port_open():
            return True
        else:
            my_log.error(f"MIDI OUT port is not open: {pname}, using fake port")
            self.port, self.name = _FakeMidiOut(), "FakeMidiOut"
            return True

    def show(self) -> str:
        port_lst = self._midi_out.get_ports()
        port_lst = [x.split(":")[0] for x in port_lst if "RtMidi" not in x and "Through" not in x]
        port_str = "\n".join(port_lst)
        return f"OUT: {self.name} open: {self.port.is_port_open()}\n{port_str}"
