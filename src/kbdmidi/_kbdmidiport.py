import json
import os
from queue import Queue
from typing import Dict

import keyboard
import mido

KBD_NOTES = "KBD_NOTES"


# noinspection PyUnresolvedReferences
class KbdMidiPort:
    """Using keyboard keys instead of MIDI notes"""

    def __init__(self):
        self.name: str = "Typing keyboard"
        kbd_map_str: str = os.getenv(KBD_NOTES)
        try:
            self.__kbd_notes: Dict[str, int] = json.loads("{" + kbd_map_str + "}")
        except Exception as err:
            msg = f"Failed to parse env. variable KBD_NOTES, error: {err}"
            raise RuntimeError(msg)

        self.__queue = Queue()
        self.pressed_key = False
        keyboard.on_press(callback=self.on_press, suppress=True)
        keyboard.on_release(callback=self.on_release, suppress=True)

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
            msg = mido.Message.from_bytes([0x90, val, 100])
            self.__queue.put(msg)
            self.pressed_key = True

    def on_release(self, kbd_event):
        val = self.__kbd_notes.get(kbd_event.name, None)
        if val is not None and self.pressed_key:
            msg = mido.Message.from_bytes([0x80, val, 0])
            self.__queue.put(msg)
            self.pressed_key = False

    def receive(self, block=True) -> mido.Message:
        tmp = self.__queue.get(block)
        return tmp


if __name__ == "__main__":
    pass
