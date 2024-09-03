# Pepelats - Audio looper with drums on Raspberry Pi

## Features

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
- Configurable menu files. Pre-made configurations are 6x4 and 4x2. (default is 6 buttons x 4 parts)
- Scrollable lists to select options using MIDI control

### Drum machine

- Drum machine with four drum types: MIDI, Style, Euclidean and Loop
- Drums have volume control, random variations and can play breaks/fills
- MIDI drum may sync and control external MIDI device via SysEx messages, good for IOS drums.
- Pattern based Style and Euclidean drums have adjustable swing parameter
- Loop drum uses recorded audio loop, good for beat boxing

### Simple install and configuration

- Pepelats looper is an executable file, making it easy to install.
- There is web server and page to edit configurations in a browser

### [Read more ... ](./doc/contents.md)
