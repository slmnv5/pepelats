from queue import Queue

import rtmidi.midiutil


class MyRtmidi:
    def __init__(self, midi_input):
        self._input = midi_input
        self._input.set_callback(self)
        self._queue = Queue()

    def __call__(self, event, *args):
        event, _ = event
        self._queue.put_nowait(event)

    def receive(self):
        return self._queue.get()


if __name__ == "__main__":
    def test():
        inp = rtmidi.midiutil.open_midioutput()
        print(str(inp))


    test()
