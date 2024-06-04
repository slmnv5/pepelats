## Main configuration

This INI file [**main.ini**](./../main.ini) has few sections that define configuration of the looper. This file is not
supposed to change, instead edit **local.ini** file that will override any configuration in main.ini. File main.ini
may be updated when pulling latest version from git while local.ini will be preserved.

Some of the options used in this INI file are:

* max_len_seconds = 60 -- how long a loop may be
* device_name = USB Audio -- name (or part of name) of the device to use, case-insensitive
* device_type = int16 -- data type to process and store audio information, int16 or float32
* drum_volume = 0.7 -- adjust all WAV samples volume by this factor
* kbd_notes_linux = `, 4, 8, =, page up, - -- 6 computer keyboard keys to use for MIDI control, may be extended
* kbd_notes_midi = 60, 62, 64, 65, 12, 13 -- 6 notes sent by MIDI controller, may be extended
* midi_in = -- input name (or part of name) for MIDI IN control port, optional. If MIDI port is not found and computer
  keyboard is attached it is used instead.
  Also on Windows only computer keyboard is used with fixed keys: 1, 2, 3, 4, q, w
* midi_out = -- name of MIDI OUT port for MIDI drum, optional
* midi_min_velo = 10 -- min note velocity to consider, small velocities used by counted notes (e.g. 1, 2,…8,…)
* menu_dir = 6x4 -- menu layout directory located in [6x4](./../config/menu/6x4) (6 buttons x 4 parts). New directories
  with configurations may be added and switched from service menu.