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
- Display looper state in attached terminal or in a web browser on another device
- Control of looper via MIDI or computer keyboard
- Configurable menu files. Pre-made configurations are 6x4 and 4x2. (default is 6 buttons x 4 parts)
- Scrollable lists to select saved songs and drum patterns

### Drum machine
- Drum machine with four drum types: MIDI, Pattern, Euclidean and Loop
- Drums have volume control, automatic random variations and can play breaks/fills
- MIDI drum can sync and control external MIDI device via SysEx messages, good for IOS drums.
- Pattern drum and Euclidean drum have adjustable swing parameter
- Loop drum uses recorded audio loop, good for beat boxing

### [Read more ... ](./doc/contents.md)
