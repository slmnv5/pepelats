import logging
import os
import sys

from rtmidi import MidiIn, MidiOut
from rtmidi.midiutil import open_midiinput, open_midioutput

from midi._utilport import KbdMidiPort
from midi._utilport import MyRtmidi, BlackHolePort


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
        else:
            port_name = os.getenv('PEDAL_PORT_NAME', "PedalCommands_out")
            midi_in, _ = open_midiinput(port_name, interactive=False)  # may throw
            self._midi_input = MyRtmidi(midi_in)  # adapter classs
        logging.info(f"Opened port for MIDI input: {self._midi_input.__class__.__name__}")

    def _init_output(self):
        port_name = os.getenv('CLOCK_PORT_NAME', "DrumClock_in")
        # noinspection PyBroadException
        try:
            self._midi_output, _ = open_midioutput(port_name, interactive=False)
        except Exception:
            logging.error(f"Cannot open port for MIDI output: {port_name}")
            self._midi_output = BlackHolePort()
        logging.info(f"Opened port for MIDI output: {self._midi_output.__class__.__name__}")


if __name__ == "__main__":
    pass
