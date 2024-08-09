import random


class AppName:
    app_name: str = "pepelats"
    # command line options
    dash_no_progress: str = "--no_progress"  # do not update loop position
    dash_info: str = "--info"
    dash_debug: str = "--debug"

    # menu INI config files related
    header: str = "header"  # header line on screen whre progress is shown
    content: str = "content"  # method name to calculate content
    description: str = "description"  # static description text
    play_section: str = "play"  # INI file section to select at start

    # method names
    client_log: str = "_client_log"
    client_redraw: str = "_client_redraw"
    full_stop: str = "_full_stop"
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
    drum_param: str = "drum_param"
    drum_len: str = "drum_len"
    song_part: str = "song_part"

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


def song_name_generate() -> str:
    words1 = ["brave", "slim", "wise", "smart", "good", "new", "first", "last", "long", "great", "little", "my",
              "another", "old", "right", "big", "high", "his", "small", "large", "next", "early", "young", "fast",
              "her", "fit", "same", "able", "happy", "nice", "deep", "black", "blue", "green"]

    words2 = ["year", "people", "way", "day", "man", "thing", "woman", "life", "child", "world", "school",
              "state", "family", "student", "group", "country", "chair", "hand", "part", "place", "case",
              "week", "company", "system", "program", "question", "work", "wife", "number", "night",
              "point", "home", "water", "room", "mother", "area", "money", "story", "fact", "month", "lot",
              "right", "study", "book", "eye", "job", "word", "line", "issue", "side", "kind", "head",
              "house", "service", "friend", "father", "power", "hour", "game", "line", "end", "member", "law",
              "car", "city", "link", "name", "president", "team", "minute", "idea", "kid", "body",
              "case", "back", "parent", "face", "others", "level", "office", "door", "health", "person",
              "art", "war", "history", "party", "result", "change", "morning", "reason", "smile", "girl",
              "guy", "moment", "air", "teacher", "force", "run", "smile", "moon", "pen", "ring", "square"]

    return f"{random.choice(words1)}_{random.choice(words2)}"
