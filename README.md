# Pepelats - Audio looper and drum machine on Raspberry Pi

## New Features

Binary distribution, installation, configuration is simple now.      
Display loops on attached monitor or in a web browser (iPad, SmartPhone, ...)  
Memory use reduced, speed increased after Python libraries (numpy, ...) replaced by C code.
Well tesetd on Pi-3B and Pi-Zero2W.
Non-registered version limits play time to 10 minutes and disable saving songs.

### Looper

- Multiple song parts (intro/verse/chorus/bridge). Each part consists of any number of parallel loops
- Parallel loops of variable length: 1, 2, 3 ... of the 1-st loop in a part
- Quantization - time of changing parts, recording, stopping is adjusted
- Delay allowance - being late in switching loops by 0.1s or less is acceptable
- Full history of "undo/redo" for each part, not only the latest change
- Parts and their loops may be deleted/cleared on the run
- Silencing and re-arranging of loops in song parts
- Songs saved to / loaded from SD card

### Looper control and display

- Display looper state in attached terminal or in a web browser
- Control of looper via MIDI or computer keyboard emulating MIDI
- User configurable menu files. Default pre-made configuration is 6x4 -- 6 buttons x 4 parts
- Scrollable lists to select options using MIDI control

### Drum machine

- Drum machine with four drum types: MIDI, Style, Euclidean and Loop
- Drums patterns and midi commands are plain text files easy to edit
- Drums have volume control, random variations and can play breaks/fills
- MIDI drum may sync and control external MIDI device, good for IOS drums.
- Pattern based Style and Euclidean drums have adjustable swing parameter
- Loop drum uses the first song part as drums, good for beatboxing

### Installation and configuration

- The looper is installed by cloning from web repository, LCD touch screen driver installed separately

### [Read more ... ](./doc/contents.md)
