import logging
import os
import sys

from rtmidi import MidiIn, MidiOut
from rtmidi.midiutil import open_midiinput, open_midioutput

from midi._utilport import KbdMidiPort
from midi._utilport import MyRtmidi, MockMidiPort


class MidiPortFactory:
    def __init__(self):
        self._midi_output: MidiIn
        self._midi_input: MidiOut
        self._init_input()
        # noinspection PyBroadException
        try:
            self._init_output()
        except Exception as e:
            logging.error(f"Cannot open MIDI output: {e}")

    def get_input(self):
        return self._midi_input

    def get_output(self):
        return self._midi_output

    def _init_input(self):
        if "--kbd" in sys.argv:
            self._midi_input = KbdMidiPort()
            port_name = "KbdMidiPort"
        else:
            port_name = os.getenv('PEDAL_PORT_NAME', "PedalCommands_out")
            midi_in, _ = open_midiinput(port_name, interactive=False)  # may throw
            self._midi_input = MyRtmidi(midi_in)  # adapter classs
        logging.info(f"Opened port for MIDI input: {port_name}")

    def _init_output(self):
        # noinspection PyBroadException
        try:
            port_name = os.getenv('CLOCK_PORT_NAME', "DrumClock_in")
            self._midi_output, _ = open_midioutput(port_name, interactive=False)
        except Exception:
            logging.error(f"Cannot open port for MIDI output: {port_name}")
            port_name = "MockMidiPort"
            self._midi_output = MockMidiPort()
            logging.info(f"Opened port for MIDI output: {port_name}")


if __name__ == "__main__":
    pass
