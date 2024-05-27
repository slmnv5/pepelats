import os

from utils.utilconfig import load_ini_section, find_path, ConfigName

_keyboard = load_ini_section(find_path(ConfigName.main_ini), "KEYBOARD")
_option_name = "kbd_notes_windows" if os.name != 'posix' else 'kbd_notes_linux'
tmp = _keyboard.get(_option_name, '1,2,3,4,q,w')
tmp = [x.strip() for x in tmp.split(',')]
if len(tmp) != 6:
    raise RuntimeError(f"kbd_notes_windows in main.ini must have at 6 keys, found: {tmp}")
KBD_NOTES: list[str] = tmp

# ==================================
tmp = _keyboard.get('midi_notes', '60,62,64,65,12,13')
tmp = [x.strip() for x in tmp.split(',')]
# noinspection PyBroadException
try:
    tmp = [int(x) for x in tmp]
except Exception:
    pass

if len(tmp) != 6:
    raise RuntimeError(f"midi_notes in main.ini must have 6 values, found: {tmp}")
if not all(isinstance(x, int) and 0 <= x <= 127 for x in tmp):
    raise RuntimeError(f"midi_notes in main.ini must have integer values from 0 to 127, found: {tmp}")

MIDI_NOTES: list[int] = tmp
# ==================================
# min note velocity to consider, conted notes have velocity equal to count
MIN_VELO: int = 10
# standard note velocity, note loder than MIN_VELO is converted to STD_VELO
STD_VELO: int = 100
