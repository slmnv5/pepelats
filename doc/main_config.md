## Main configuration

This INI file [main.ini](../main.ini) has few sections that define configuration of the looper. This file is not
supposed to change, instead edit **local.ini** file that will override any configuration in main.ini. File main.ini
may be updated when pulling latest version from git while local.ini will be preserved.

Some of the options in this INI file:

**[Do not change this file, it is reverted by update. Put your changes in local.ini]**  
max_len_seconds = 60 -- how long a loop may be  
device_name = USB Audio -- name (or part of name) of the device to use, case insensitive  
device_type = int16 -- data type to process and store audio information, int16 or float32  
drum_volume = 0.7 -- adjust all WAV samples volume if Style or Euclid drums volume need to change  
sample_rate = 44100 -- sample rate, mostly 48000 and 44100  
keyboard_keys = `, 4, 8, =, page up, -  -- 6 computer keys on linux keyboard if MIDI controller is missing  
keyboard_notes = 60, 62, 64, 65, 12, 13 -- 6 notes of MIDI foot controller pedal. Note velocity must be > 10  
midi_in = BlueBoard -- name (or part of name) for MIDI input control, optional  
midi_out = Ssh -- name (or part of name) for MIDI drum output, optional  
menu_choice = 6x4 -- menu layout directory located in /config/menu/ (6 buttons x 4 parts)  
screen_type = -- where to show looper's info (0 - LCD screen, 1 - web page)  
