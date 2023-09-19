## Command line parameters

- --info - verbose logging
- --debug - more verbose logging
- --count - count notes (see Extending MIDI foot controller commands) (commands.md)

## Configuration file and default values:

looper.ini content:
MAX_LEN_SECONDS='60' # loop's max length is 60 seconds
SD_RATE='44100' # sample rate to use
IN_PORT='BlueBoard'  
KBD_NOTES=' "q": 12, "w": 13, "1":60, "2": 62, "3": 64, "4": 65 '

## MIDI foot controller

MIDI controller sending notes may be configured to work with this looper. MIDI commands and looper actions are
configured in INI files (e.g. [config/menu/play.ini](config/menu/play.ini)).

MIDI over Bluetooth or USB or computer keyboard will work.
Starting script is: [looper.sh](looper.sh).

## Looper views - Play, Song, Param

There are 3 looper views:

### Play parts [configure/menu/play.ini]

- commands to play / record / overdub / clear four song parts and switching between them.

### Play loops [configure/menu/play.ini]

- commands to scroll over current part's loops. Selected loop can be deleted, muted, reversed.

### Param drum_param [configure/menu/param.ini]

- select one of four drum types, adjust volume and other param-s.

### Param service [configure/menu/param.ini]

- restart looper, reboot device, check for updates

### Param midi_in [configure/menu/param.ini]

- select MIDI IN port for controller

### Param midi_out  [configure/menu/param.ini]

- select MIDI OUT port for drum output

### Song save [configure/menu/song.ini]

- stop looper at different points, save song, save as new, empty song.

### Song load  [configure/menu/song.ini]

- scroll over saved song, load, delete

MIDI commands assigned to buttons are listed in [commands.md](commands.md)


