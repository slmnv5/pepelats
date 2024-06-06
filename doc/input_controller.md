## MIDI foot controller

### Multi tapping

There are only few buttons on foot controllers and number of looper commands is much bigger. To deal with it multi
tapping is
used.
If delay between taps is less than 0.6 seconds they belong to one series and produce MIDI note as explained below.

Assume button A sends note 60, velocity = 100. Multiple tapping will send one additional note 60 with changed
velocity. Changed velocity = number of taps + 5 if the last tap was a long hold. For this example:

- one tap sends note 60 with original velocity = 100 and note 60 with velocity = 1
- double tap sends note 60 with original velocity = 100 and note 60 with velocity = 2
- triple tap sends ..... velocity = 3
- one tap and hold sends ..... velocity = 1 + 5 = 6
- double tap and hold sends ..... velocity = 2 + 5 = 7

Using multiple taps one button may send 6-7 different MIDI messages.

Multiple taps use 0.6 seconds delay to decide if there will be next tap. Because of this it should not be used for
time critical commands e.g. start playing or recording. But for other commands like changing volume it is
indispensable.

### MIDI input controller restrictions

Midi input controller must send notes ON/OFF with velocity >10 because lower velocity values are used in multi
tapping. All notes with velocity >10 are converted to velocity of 100 and this value is used in the menu configuration
files.

## MIDI input controller configurations

Foot controller is coupled with menu configuration files e.g. [play.ini](./../config/menu/6x4/play.ini) which
translate notes to looper commands (see also [menu_config.md](menu_config.md))
Each line looks like:

```
Note-Velocity : _command1 [p1, p2, ...] [:_command2 [p1, p2, ...]] ....
```

Notes are: A, B, C, D, E, F and they correspond to integer values in kbd_notes_midi option in the main.ini
Velocity=100 : is the standard velocity assigned to all original MIDI notes from controller
Velocity=1, 2, 3, ... 10: is velocity of counted note as explained above
_command1, _command2 : are commands of the looper. Multiple commands are separated by colon
p1, p2, ... : optional parameters of commands. Each one may be a number or text

```
C-100 : _play_song_part 2
D-100 : _play_song_part 3
A-2 : _overdub_song_part
B-2 : _overdub_song_part
```

## Changing configurations

There are few configurations some using 4 buttons and some 6 buttons. Two rightmost buttons are
made by plugging in two ON/OFF momentarily switches into expression pedal input of **iRig BlueBoard MIDI foot controller
**. The looper converts control changes to note ON/OFF message



