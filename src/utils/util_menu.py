import os
from configparser import ConfigParser

from utils.util_config import load_ini_section
from utils.util_log import ConfigError
from utils.util_name import AppName


def _check_menu_dir() -> tuple[str, int, int]:
    dname = load_ini_section("MENU").get(AppName.menu_choice, '')
    dname = f"{AppName.menu_config_dir}/{dname}"
    if not os.path.isdir(dname):
        raise ConfigError(f"Menu directory not found: {dname}")
    lst = dname.split("/")[-1].split("-")
    if not (lst[0] in "123456789" and lst[1] in "123456789"):
        raise ConfigError(f"Menu dirctory name must start with 'M-N-', M-number of buttons, N-number of parts")
    return dname, int(lst[0]), int(lst[1])


def _load_midi_lists(dname: str, buttons: int) -> tuple[list[int], list[str], list[str]]:
    cfg = ConfigParser()
    f_config = f"{dname}/config.ini"
    if not cfg.read(f_config):
        raise ConfigError(f"INI menu file not loaded: {f_config}")

    dic = dict(cfg.items("MIDI"))
    notes_str = dic.get(AppName.keyboard_notes, "")
    notes_lst = [x.strip() for x in notes_str.split(',')]
    if len(notes_lst) != buttons:
        raise ConfigError(f"Option {AppName.keyboard_notes} in {f_config} must have {buttons} integers")

    if not all([x.isdigit() for x in notes_lst]):
        raise ConfigError(f"Option {AppName.keyboard_notes} in {f_config} must have integers: {notes_lst}")

    notes_lst = [int(x) for x in notes_lst]
    if not all([0 <= x < 128 for x in notes_lst]):
        raise ConfigError(f"Option {AppName.keyboard_notes} in {f_config}, integers must be 0<=x<128: {notes_lst}")

    nine_letters: str = "abcdefghi"
    letterst_lst = list(nine_letters)[:buttons]

    keys_str = dic.get(AppName.keyboard_keys, "")
    keys_lst = [x.strip() for x in keys_str.split(',')]
    if len(keys_lst) != buttons:
        raise ConfigError(f"Option {AppName.keyboard_keys} in {f_config} must have {buttons} characters")

    return notes_lst, letterst_lst, keys_lst


# min note velocity to consider, counted notes have small velocity
MIDI_MIN_VELO: int = 10
# standard note velocity used in menu files, note louder than MIDI_MIN_VELO is converted to MIDI_STD_VELO
MIDI_STD_VELO: int = 100

MENU_DIR, BUTTONS, PARTS = _check_menu_dir()
NOTES, LETTERS, KEYS = _load_midi_lists(MENU_DIR, BUTTONS)
NOTE_LETTER: dict[int, str] = dict(zip(NOTES, LETTERS))
KEY_NOTE: dict[str, int] = dict(zip(KEYS, NOTES))
