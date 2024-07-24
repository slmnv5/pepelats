class AppName:
    app_name: str = "pepelats"

    # menu INI config files related
    update_method: str = "update_method"
    description: str = "description"
    play_section: str = "play"

    # method names
    client_log: str = "_client_log"
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
    keyboard_keys: str = "keyboard_keys"
    keyboard_notes: str = "keyboard_notes"
    screen_type: str = "screen_type"
    euclid_break: str = "euclid_break"
    style_break: str = "style_break"

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
    documents_dir: str = "doc"
    main_ini: str = "main.ini"
    local_ini: str = "local.ini"
    save_song: str = "save_song"
