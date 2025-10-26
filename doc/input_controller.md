## MIDI foot controller

### Multi tapping

There are only few buttons on foot controllers and number of looper commands is much bigger. To deal with it multi
tapping is used. If delay between taps is less than 0.5 seconds they belong to one series and produce MIDI note as
explained below.

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

Foot controller is coupled with menu configuration files e.g. [play.ini](../config/menu/play.ini) which
translate notes to looper commands (see also [menu_config.md](menu_layout))
Each line looks like:

```
Note-Velocity : _command1 [p1, p2, ...] [:_command2 [p1, p2, ...]] ....
```

Notes are: A, B, C, D, E, F and they correspond to integer values in **keyboard_notes** option in the user.ini  
Velocity=100 : is the standard velocity assigned to all original MIDI notes from controller  
Velocity=1, 2, 3, ... 10: is velocity of counted note as explained above  
_command1, _command2 : are commands of the looper. Multiple commands are separated by colon  
p1, p2, ... : optional parameters of commands. Each one may be a number or text

```
A-100 : _menu_part_play 0
B-100 : _menu_part_play 1
...
A-2 : _menu_part overdub
B-2 : _menu_part overdub
```

## Control change messages

If foot controller sends control change (CC) messages from expression pedal the looper can convert them into notes. E.g.
CC 12 will be converted to Note 12 ON/OFF.  
As an example in **iRig BlueBoard MIDI foot controller** there are two expression pedal inputs. Plugging ON/OFF
momentarily switches into these inputs will send CC messages converted into note messages.

## Changing menu configurations

To change this edit **user.ini**



