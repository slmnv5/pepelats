## Main configuration

This INI file [main.ini](../main.ini) has few sections that define configuration of the looper. This file is not
supposed to change, instead edit **local.ini** file that will override any configuration in main.ini. File main.ini
may be updated when pulling latest version from git while local.ini will be preserved.

Some of the options in this INI file:

**[Do not change this file, it is restored by update. Edit local.ini]**
; audio options
max_len_seconds -- how long a loop may be.
device_name -- name (or part of name) of the device to use, case insensitive
device_type -- data type to process and store audio information, int16 or float32
drum_volume -- multiplier for WAV samples volume if Style or Euclid drums volume need to change
sample_rate -- sample rate, 48000 or 44100, depends on audio device used
; midi options
midi_in  -- name (or part of name) for MIDI input control, optional
midi_out --  name (or part of name) for MIDI drum output, optional
; menu options
menu_choice -- menu layout directory located in /config/menu/ (6 buttons x 4 parts)
; screen options
screen_type -- where to show looper's info, 0-terminal, 1-web page. For web WiFi connection is required
; drum options
style_break -- if name contains it, it is a break, if empty, break is defined by pattern's energy, not by name
euclid_break -- same as above for Euclid drum type

