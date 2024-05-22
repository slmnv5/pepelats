## Main configuration

This INI file [main.ini](./../main.ini) has few sections that define main configuration of the looper.

Some of the options used in this INI file are:

* max_len_seconds -- loop's max. length is in seconds (default is 60 seconds)
* midi_in -- name (or part of name) of MIDI IN port to get looper control messages (default is BlueBoard)
* kbd_notes -- mapping of computer keyboard keys to MIDI notes. May be used instead of **midi_in** port if program
  started as:

```
looper.sh
```

* menu_dir -- where menu configuration files are stored. (default is [button6](./../config/menu/button6))
