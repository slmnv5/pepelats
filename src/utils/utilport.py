import json
import logging
import os
import time
from multiprocessing import Queue
from typing import Tuple, Dict, List

import keyboard
import rtmidi.midiutil


class MyRtmidi:
    def __init__(self, midi_input: rtmidi.MidiIn):
        self._input = midi_input
        self._input.set_callback(self)
        self._queue = Queue()

    def __call__(self, event, *args):
        event, _ = event
        self._queue.put_nowait(event)

    def put(self, event):
        self._queue.put_nowait(event)

    def receive(self):
        return self._queue.get()

    def close_port(self):
        self._input.close_port()

    def __del__(self):
        self._input.close_port()


class FakePort:
    """ When there is no MIDI OUT ports """

    def __init__(self):
        self.__count: int = 0

    def send_message(self, msg: List[int]) -> None:
        if self.__count % 100 == 0:
            msg = f"MockMidiPort: sent MIDI: {msg}"
            logging.debug(msg)
        self.__count += 1

    def __str__(self):
        return f"{self.__class__.__name__}"


class ChargedMidiPort:
    """ For testing when there is no MIDI ports """

    def __init__(self):
        self.__notes: Dict[float, List[int]] = dict()
        self.__count: int = 0

    def charge(self, notes: Dict[float, Tuple[int, int]]):
        """set dictionary of {time: (note,vel), ...} to send e.g. {0.1: (60,100), 0.2: (-60,0), 1.2:(62, 1)}
        negative values are note off messages"""
        self.__notes.clear()
        for k, v in notes.items():
            if v[0] >= 0 and v[1] > 0:
                self.__notes[k] = [0x90, v[0], v[1]]
            else:
                self.__notes[k] = [0x80, -v[0], 0]

    # noinspection PyUnusedLocal
    def receive(self) -> List[int]:
        if len(self.__notes) == 0:
            raise EOFError

        k = list(self.__notes)[0]
        time.sleep(k)
        return self.__notes.pop(k)

    def __str__(self):
        return f"{self.__class__.__name__}"


# noinspection PyUnresolvedReferences
class KbdMidiPort:
    """Using keyboard keys instead of MIDI notes"""

    def __init__(self):
        kbd_map_str: str = os.getenv("KBD_NOTES", '"q": 12, "w": 13, "1":60, "2": 62, "3": 64, "4": 65')
        try:
            self.__kbd_notes: Dict[str, int] = json.loads("{" + kbd_map_str + "}")
        except Exception as err:
            msg = f"Failed to parse env. variable KBD_NOTES, error: {err}"
            raise RuntimeError(msg)

        self.__queue = Queue()
        self.pressed_key = False
        keyboard.on_press(callback=self.on_press, suppress=True)
        keyboard.on_release(callback=self.on_release, suppress=True)

    def put(self, event) -> None:
        self.__queue.put_nowait(event)

    def on_press(self, kbd_event):
        # print(type(kbd_event), str(kbd_event.__dict__))
        if kbd_event.name == "esc":
            keyboard.unhook_all()
            print("Done unhook_all and exit !")
            # noinspection PyProtectedMember
            os._exit(1)
            return

        val = self.__kbd_notes.get(kbd_event.name, None)
        if val is not None and not self.pressed_key:
            msg = [0x90, val, 100]
            self.__queue.put(msg)
            self.pressed_key = True

    def on_release(self, kbd_event):
        val = self.__kbd_notes.get(kbd_event.name, None)
        if val is not None and self.pressed_key:
            msg = [0x80, val, 0]
            self.__queue.put(msg)
            self.pressed_key = False

    def receive(self) -> List[int]:
        tmp = self.__queue.get()
        return tmp


if __name__ == "__main__":
    def test():
        inp = rtmidi.midiutil.open_midioutput()
        print(str(inp))


    test()
