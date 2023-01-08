## Command line parameters

- --info - set verbose logging
- --debug - set more verbose logging
- --kbd - use keyboard for MIDI input (see KBD_NOTES env. variable below)
- --count - count notes (see Extending MIDI foot controller commands below)

## Environment variables and default values:

### Use typing keyboard to sent note ON/OFF when press/release

export ENV_KBD_NOTES=' "q": 12, "w": 13, "1":60, "2": 62, "3": 64, "4": 65 '

### Loop audio properties

export ENV_MAX_LEN_SECONDS='60'

export ENV_SD_RATE='44100'

### Use this MIDI port (part of the name) as control input

export ENV_MIDI_IN_PORT='BlueBoard'

### Use this MIDI port (part of the name) as drum's output

export ENV_MIDI_OUT_PORT='Play mk3'

### Use this frame buffer if there are few, only Linux and only if graphics mode is used

export ENV_FRAME_BUFFER_ID='1'

### Use ALSA devices (found first is used)

export ENV_USB_AUDIO_NAMES='VALETON GP,USB Audio'

## Drums configuration

Drums are configured in a text files (in [config/drum](config/drum)) using JSON format. Several popular drum
patterns are pre-configured. Looper uses randomness to make it less repetitive. Drums accompaniment is created after the
first loop is recorded and BPM is defined by length of this loop. Drum volume and swing may be changed on the run. Swing
settings is same as Linn's LM-1, from 0.5 to 0.75.

## MIDI foot controller

MIDI controller sending notes may be configured to work with this looper. MIDI commands and looper actions are
configured in a text files (e.g. [config/menu/play.json](config/menu/play.json)). This is for Irig Blueboard foot
controller. There are 4 buttons on this pedal named A,B,C,D and 2 extra buttons attached to MIDI expression inputs named
E1 and E2.

MIDI over Bluetooth needs manual pairing. You may use wired USB MIDI controller as well or even typing keyboard. Check
file [looper.sh](looper.sh) for details.

## Control modes - "direct" and "indirect"

There are two MIDI control configurations that we may call "direct" and "indirect".

Direct has each song part/loop assigned a separate button like on a hardware looper. Direct configuration is clear and
fast but number of loops is limited by number of available buttons.

Indirect may have any number of parts/loops. Some buttons scroll, select a loop, others apply various actions. This
configuration is hard to remember and use.

Direct configuration is used to only for song parts and indirect for everything else: loops in a part, selection of
saved song, drum style, etc.

## Looper views - Playing, Song, Params

### Playing 0

- commands to play / record / clear four song parts and switching between them.

### Playing 1

- commands to scroll over loops making one part. Selected loop can be deleted, muted, moved, reversed.
  A loop may be moved to the end so when part's undo is applied this loop disapper first even thogh it was not recorded
  the last.

### Params 0

- drum style selection - scroll, load

### Params 1

- change drum volume, swing, etc

### Params 2

- update code version, restart looper, change Drum type - MIDI or WAV samples, change text or graphics mode.
  Graphics mode adds touchscreen buttons but needs special shared library. If missing text mode is used.

### Song 0

- current song - stop looper at different points, save song, save as new, make an empty song.

### Song 1

- song selection - scroll, load, delete

MIDI commands assigned to buttons are listed in [commands.md](commands.md)
Configuration JSON files are in [config/menu/](config/menu)

## Extending MIDI foot controller commands

Buttons are few on most foot controllers, and there are more commands than available buttons. To deal with it multi
tapping mode is used. If delay between taps is less than 0.6 seconds they belong to one series and produce different
MIDI command.

As an example button A sends note 60 on, velocity = 100. Multiple tapping will send additional note 60 with changed
velocity. Velocity = number of taps + 5 if the last tap was long (hold after tap). For this example:

- single tap sends notes 60 with original velocity = 100 and note 60 with velocity = 1
- double tap sends ... velocity = 2
- single tap with hold ... velocity = 1 + 5 = 6
- double tap with hold ... velocity = 2 + 5 = 7

Using this method one button may send 6-7 times more MIDI notes.

Multi tapping mode needs 0.6 sec. delay to decide if there will be next tap. Because of this it should not be used for
time critical commands e.g. start recording/playing. But for other commands like changing looper settings it is
indispensable.

### Installation of LCD:

As additinal reference check files I use [config.txt](etc/txt/config.txt)
and [cmdline.txt](etc/txt/cmdline.txt) - working for my version of LCD screen.


