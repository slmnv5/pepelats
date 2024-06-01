import os

from utils.utilconfig import load_ini_section, ConfigName
from utils.utillog import MYLOG

_keyboard = load_ini_section("KEYBOARD")
_option_name = ConfigName.kbd_notes_windows if os.name != 'posix' else ConfigName.kbd_notes_linux
tmp = _keyboard.get(_option_name, '')
tmp = [x.strip() for x in tmp.split(',')]
if len(tmp) != 6:
    raise RuntimeError(f"kbd_notes_windows and kbd_notes_linux in main.ini must have 6 values, found: {tmp}")
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
