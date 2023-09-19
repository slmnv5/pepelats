## iRig BlueBoard

This configuration is made for Irig Blueboard foot controller. There are 4 buttons on this pedal: A,B,C,D (MIDI notes
60, 62, 64, 65) and 2 buttons in MIDI expression pedal input: E1, E2 (MIDI notes 12, 13).
Application uses multi tap mode as shown below.

## Extending MIDI foot controller commands

Buttons are few on most foot controllers, and there are more commands than available buttons. To deal with it multi
tapping mode is used. If delay between taps is less than 0.6 seconds they belong to a series and produce different
MIDI command.

As an example button A sends note 60 on, velocity = 100. Multiple tapping will send additional note 60 with changed
velocity. Velocity = number of taps + 5 if the last tap had a hold after tap. For this example:

- tap sends note 60 with original velocity = 100 and note 60 with velocity = 1
- double tap sends ... velocity = 2
- triple tap sends ... velocity = 3
- tap with hold sends ... velocity = 1 + 5 = 6
- double tap with hold ... velocity = 2 + 5 = 7

Using this method one button may send 6-7 times more of MIDI messages.

Multi tapping uses 0.6 seconds delay to decide if there will be next tap. Because of this it should not be used for
time critical commands e.g. start playing/recording. But for other commands like changing volume it is
indispensable.

## Specific configuration for iRig BlueBoard

### Play parts (configure/menu/play.ini)

- Buttons A,B,C,D switch between 4 different song parts.
    - 1 tap: play/record if empty. New loop has same length as the 1-st loop.
    - 1 tap + hold: clear part if it is not active part.
    - 2 taps: same as 1 tap but new loop has variable length - multiple of 1st loop.
- Buttons E1 and E2 affect the whole looper or currently playing song part:
    - Button E1
        - 1 tap: randomize drum
        - 2 taps: mute drum
        - 3 taps: stop at the part's end
        - 1 tap + hold: switch to "Play loops" view
    - Button E2
        - 1 tap: undo current part/loop, if available
        - 2 taps: redo current part/loop if available
        - 3 taps: redo whole history
        - 1 tap + hold: switch to "Song stop" view

### Play loops [configure/menu/play.ini]

- Buttons A,B,C,D manipulate loops of one song part.
    - Button A - 1 tap: scroll up
    - Button B - 1 tap: scroll down
    - Button C
        - 1 tap: volume down
        - 2 taps: volume up
    - Button D
        - 1 tap: mute on/off selected loop
        - 2 taps: inverse on/off selected loop
        - 3 taps: move selected loop to the end (next undo will remove it)
        - 1 tap + hold: delete selected loop
- Buttons E1 and E2 are the same as for "all parts" view

### Song and Param views [configure/menu/song.ini]

- The screen shows hints for all buttons. For example in Songs save:
    - C2-save -- that 2 taps of button C will save song
    - CH-save new -- tap and hold button C will save song under new name (names are generated, ex: "Happy Day 28.s")
- Buttons E1 and E2 - 1 tap: scroll to previous/next screen of the same view
- Button E1 - hold : switch to "Play parts" view
- Button E2 - hold: switch between Play/Song/Param views
