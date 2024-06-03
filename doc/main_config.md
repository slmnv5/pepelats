## Main configuration

This INI file [**main.ini**](./../main.ini) has few sections that define configuration of the looper.

Some of the options used in this INI file are:

* max_len_seconds = 60 -- how long a loop may be
* device_name = USB Audio -- name (or part of name) of the device to use, case-insensitive
* device_type = int16 -- data type to process and store audio information, int16 or float32
* drum_volume = 0.7 -- adjust all WAV samples volume
* kbd_notes_linux = `, 4, 8, =, page up, - -- 6 computer keyboard keys to use for MIDI control
* kbd_notes_midi = 60, 62, 64, 65, 12, 13 -- 6 notes sent by MIDI controller
* midi_in = -- input name (or part of name) for MIDI control port, optional. If MIDI port is not found and computer
  keyboard is attached it is used instead. Also on Windows keyboard is always used with fixed keys: 1, 2, 3, 4, q, w
* midi_out = -- name of MIDI out for MIDI drum output, optional
* midi_min_velo = 10 -- min note velocity to consider, small velocities used by counted notes (e.g. 1, 2,…8,…)
* menu_dir = 6x4xN -- menu layout directory located in [6x4xN](./../config/menu/6x4xN) (6 buttons x 4 parts x N loops in
  part). There are other configurations switchable inside service menu -- 4x2xN and 4xNxN (N means any number)