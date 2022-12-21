import logging
import os
import sys

from rtmidi.midiutil import open_midiinput, open_midioutput

from midi._utilport import KbdMidiPort
from midi._utilport import MyRtmidi, MockMidiPort


class MidiPortFactory:
    def __init__(self):
        self._midi_output = None
        self._midi_input = None
        self._init_input()
        self._init_output()

    def get_input(self):
        return self._midi_input

    def get_output(self):
        return self._midi_output

    def _init_input(self):
        if "--kbd" in sys.argv or os.name != "posix":
            self._midi_input = KbdMidiPort()
        else:
            port_name = os.getenv('PEDAL_PORT_NAME', "PedalCommands_out")
            midi_in, _ = open_midiinput(port_name, interactive=False)  # may throw
            self._midi_input = MyRtmidi(midi_in)  # adapter classs
        logging.info(f"Opened port for MIDI input {str(self._midi_input)}")

    def _init_output(self):
        if os.name != "posix":
            self._midi_output = MockMidiPort()
        else:
            port_name = os.getenv('CLOCK_PORT_NAME', "DrumClock_in")
            self._midi_output, _ = open_midioutput(port_name, interactive=False)
        logging.info(f"Opened port for MIDI output {str(self._midi_output)}")


if __name__ == "__main__":
    pass
