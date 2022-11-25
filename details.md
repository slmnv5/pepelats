## Drums configuration

Drums are configured in a text files (in [config/drums/pop](config/audiodrum/_1_pop)) using JSON format. Several popular drum
patterns are pre-configured. Looper uses randomness to make it less repetitive. Drum
breaks play when loop is switched or when a button is pushed. Drums accompaniment is created after the first loop is
recorded and BPM is defined by length of this loop. Drum volume and swing may be changed on the run. Swing settings is
same as Linn's LM-1, from 0.5 to 0.75.

## MIDI foot controller

Any MIDI controller sending notes may be configured to work with the looper. MIDI commands and looper actions are
configured in a text files (e.g. [etc/midi/playing.json](config/midicontrol/playing.json)) for Irig Blueboard foot controller.
There are 4 buttons on this pedal named A,B,C,D and 2 extra buttons attached to MIDI expression inputs named E1 and E2.

MIDI over Bluetooth needs manual pairing. You may use wired USB MIDI controller as well or even typing keyboard. Check
file [looper.sh](looper.sh) for details.

## Looper modes - "direct" and "indirect"

There are two MIDI configurations that we may call "direct" and "indirect".

Direct has each song part/loop assigned a separate button like on a hardware looper. Direct configuration is clear and
fast but number of loops is limited by number of available buttons.

Indirect may have any number of parts/loops. Some buttons scroll and select a loop, others apply various actions. This
configuration takes more button pushes and is slow.

Direct configuration is used to for song parts and indirect for loops in a part, exact details are below.

## Looper views - Playing, Song, Params

### Playing 0

- commands to play / record / clear four song parts and switching between them.

### Playing 1

- commands to scroll over loops making one part. Selected loop can be deleted, muted, moved, reversed.
  A loop may be moved to the end so when part's undo is applied this loop disapper first even thogh it was not recorded
  the
  last.

### Params 0

- chande drum volume and drum swing. All drums are regenerated

### Params 2

- Change drum type, update code from repository, restart looper

### Song 0

- current song - stop looper at different points, save song, save as new, make empty song.

### Song 1

- song selection - scroll, load, delete

MIDI commands assigned to buttons are different for these views and are listed in [commands.md](commands.md)
located alongside JSON files in [config/midi/](config/midicontrol)

## Extending MIDI foot controller commands

Buttons are scarce resource for looper and there are more commands than available buttons. To deal with it multi tapping
mode is used. If delay between taps is less than 0.6 seconds they belong to one series and produce different MIDI
command.

As an example button A sends note 60. Multiple tapping will send additional note 60 with changed velocity. Velocity =
number of taps + 5 if the last tap was long (hold after tap). For this example:

- single tap sends notes 60 with original velocity (e.g 100) and note 60 with velocity = 1
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


