import os

from utils.utilconfig import load_ini_section, find_path, ConfigName
from utils.utillog import MYLOG

_keyboard = load_ini_section(find_path(ConfigName.main_ini), "KEYBOARD")
_option_name = ConfigName.kbd_notes_windows if os.name != 'posix' else ConfigName.kbd_notes_linux
tmp = _keyboard.get(_option_name, '1,2,3,4,q,w')
tmp = [x.strip() for x in tmp.split(',')]
if len(tmp) != 6:
    raise RuntimeError(f"kbd_notes_windows in main.ini must have at 6 keys, found: {tmp}")
KBD_NOTES: list[str] = tmp

# ==================================
tmp = _keyboard.get(ConfigName.kbd_midi_notes, '60,62,64,65,12,13')
tmp = [x.strip() for x in tmp.split(',')]
# noinspection PyBroadException
try:
    tmp = [int(x) for x in tmp]
except Exception:
    pass

if len(tmp) != 6:
    raise RuntimeError(f"{ConfigName.kbd_midi_notes} in main.ini must have 6 values, found: {tmp}")
if not all(isinstance(x, int) and 0 <= x <= 127 for x in tmp):
    raise RuntimeError(f"{ConfigName.kbd_midi_notes} in main.ini must have integer values from 0 to 127, found: {tmp}")

MIDI_NOTES: list[int] = tmp
# ==================================
# min note velocity to consider, counted notes have small velocity
MIDI_MIN_VELO: int = 10
_midi = load_ini_section(find_path(ConfigName.main_ini), "MIDI")
# noinspection PyBroadException
try:
    MIDI_MIN_VELO = int(_midi.get(ConfigName.midi_min_velocity, '10'))
except Exception as ex:
    MIDI_MIN_VELO = 10
    MYLOG.error(f"Failed loading from main.ini file: {ConfigName.midi_min_velocity}, error: {ex}")

# standard note velocity used in menu files, note louder than MIDI_MIN_VELO is converted to MIDI_STD_VELO
MIDI_STD_VELO: int = 100
