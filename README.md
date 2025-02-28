# Pepelats - Audio looper and drum machine on Raspberry Pi

## Features

Binary distribution, installation, configuration are simplified compared to previous Python disrtribution.  
Display loops on Raspbery Pi tiny LCD screen, attached monitor or in the web browser on any device (e.g. iPad)  
Memory use reduced a lot copared to previous python version, no use of numpy library.
Non-registered version limits play time to 10 minutes and disable saving songs

### Looper

- Multiple song parts (intro/verse/chorus/bridge). Each part consists of any number of parallel loops
- Parallel loops of variable length: ... 0.25, 0.5, 1, 2, 3 ... of the 1-st loop in a part
- Quantization - time of changing parts, recording, stopping is adjusted
- Full history of "undo/redo" for each part, not only the latest change
- Loops/parts may be deleted/cleared on the run
- Silencing, reversing and re-arranging of loops in song parts
- Songs saved to and loaded from SD card

### Looper control and display

- Display looper state in attached terminal or via web server
- Control of looper via MIDI or computer keyboard emulating MIDI
- User configurable menu files. Default pre-made configuration is 6x4 -- 6 buttons x 4 parts
- Scrollable lists to select options using MIDI control

### Drum machine

- Drum machine with four drum types: MIDI, Style, Euclidean and Loop
- Drums patterns and midi commands are plain text files easy to edit
- Drums have volume control, random variations and can play breaks/fills
- MIDI drum may sync and control external MIDI device via SysEx messages, good for IOS drums.
- Pattern based Style and Euclidean drums have adjustable swing parameter
- Loop drum uses one the first loop for drums, good for beatboxing

### Installation and configuration

- The looper is installed by cloning from web repository, and running install command

### [Read more ... ](./doc/contents.md)
