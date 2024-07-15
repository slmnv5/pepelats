import os
from configparser import ConfigParser

from utils.utilother import get_ip_address

IP_ADDR = get_ip_address()


class ConfigName:
    # kill_command = "killall -9 -qw python > /dev/null"
    # menu INI config files related
    update_method: str = "update_method"
    description: str = "description"
    play_section: str = "play"
    # method names
    client_redraw: str = "_client_redraw"
    client_stop: str = "_client_stop"
    menu_update: str = "_menu_update"
    section_update: str = "_section_update"

    # main INI file options
    menu_choice: str = "menu_choice"
    midi_out: str = "midi_out"
    midi_in: str = "midi_in"
    max_len_seconds: str = "max_len_seconds"
    device_name: str = "device_name"
    device_type: str = "device_type"
    sample_rate: str = "sample_rate"
    kbd_notes_linux: str = "kbd_notes_linux"
    kbd_notes_midi: str = "kbd_notes_midi"
    screen_type: str = "screen_type"
    # drum config related
    drum_type: str = "drum_type"
    drum_config_file: str = "drum_config_file"
    drum_volume: str = "drum_volume"
    drum_par: str = "drum_par"
    # drum types
    EuclidDrum: str = "EuclidDrum"
    StyleDrum: str = "StyleDrum"
    MidiDrum: str = "MidiDrum"
    LoopDrum: str = "LoopDrum"
    # directories and files
    pickled_drum_samples: str = "pickled_drum_samples.pkl"  # saved dictionary with drum samples
    drum_samples_dir: str = "config/drum/wav"
    menu_config_dir: str = "config/menu"
    drum_config_dir: str = "config/drum"
    main_ini: str = "main.ini"
    local_ini: str = "local.ini"


def load_ini_section(sect: str) -> dict[str, str]:
    main = ConfigName.main_ini
    local = ConfigName.local_ini
    assert os.path.isfile(main)
    cfg = ConfigParser()
    cfg.read([main, local])  # local file overwrites main
    if sect not in cfg.sections():
        return dict()
    return dict(cfg.items(sect))


SCREEN_TYPE = load_ini_section("SCREEN").get(ConfigName.screen_type, 'lcd')


def update_ini_section(sect: str, dic: dict[str, str]) -> None:
    local = ConfigName.local_ini
    cfg = ConfigParser()
    cfg.read(local)
    if sect not in cfg.sections():
        cfg.add_section(sect)
    for k, v in dic.items():
        cfg.set(sect, k, v)
    with open(local, 'w') as f:
        cfg.write(f)
