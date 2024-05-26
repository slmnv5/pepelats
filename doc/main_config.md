## Main configuration

This INI file [main.ini](./../main.ini) has few sections that define main configuration of the looper.

Some of the options used in this INI file are:

* max_len_seconds -- loop's max. length is in seconds (default is 60 seconds)
* device_name -- name (or part of name) for USB audio devices to use.
* midi_in -- name (or part of name) of MIDI IN port to get looper control messages (default is BlueBoard)
* midi_out -- name (or part of name) of MIDI OUT port to use with MIDI drum
* kbd_notes_linux -- 6 keys on computer keyboard connected to linux (to use keyboard as foot controller)
* kbd_notes_windows -- 6 keys on computer keyboard connected to windows (to use keyboard for debugging)
* midi_notes -- 6 MIDI notes sent by computer keyboard keys.
* menu_dir -- where menu configuration files are stored. (default is [button6](./../config/menu/button6), optional
  is [button4](./../config/menu/button4))
