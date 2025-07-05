# Pepelats - Audio looper and drum machine on Raspberry Pi

## New Features

- Binary distribution. Installation and configuration simplified.
- Default looper monitor is web: http://loop.local:8000. May be changed in menu. 
- Improved memory use as big Python libraries (numpy et al.) replaced by C code.
- Tested on Pi-3B and Pi-Zero2W with/without attached 3.5" LCD.
- Eucleadean drum type removed
- Non-registered version limits play time.

### Looper

- Multiple song parts (intro/verse/chorus/bridge). Each part consists of any number of parallel loops
- Parallel loops of variable length: 1, 2, 3 ... of the 1-st loop in a part
- Quantization - time of changing parts, recording, stopping is adjusted
- Delay allowance - being late in switching loops by 0.1s or less is acceptable
- Full history of "undo/redo" for each part, not only the latest change
- Parts and their loops may be deleted/cleared on the run
- Silencing and re-arranging of loops in song parts
- Songs may be saved and loaded

### Looper control and display

- Display looper state in attached terminal (ex. 3.5" LCD screen) or in a web browser
- Control of looper via MIDI or computer keyboard
- User configurable menu files. Default pre-made configuration is 6x4 -- 6 buttons x 4 parts
- Scrollable lists to select options using MIDI control

### Drum machine

- Drum machine with tree drum types: MIDI, Style and Loop
- Drums patterns and midi commands are plain text files easy to edit
- Drums have volume control, random variations and can play breaks/fills
- MIDI drum may sync and control external MIDI device, good for IOS drums.
- Style drum is pattern based, have adjustable swing parameter
- Loop drum uses the first song part as drums, good for beatboxing

### [Read more ... ](./doc/contents.md)
