## Audio drum

Audio drum is using text patterns and sample WAV files to produce drum accompaniment.
These sound samples are written into audio buffer along with recorded loops. This provides ideal synchronization between
drums and recorded loops.

There are about 200 patterns in a dozen of styles in directory: [config/drum/audio](./../config/drum/audio)
Example: [Pop.ini](./../config/drum/audio/Pop.ini)

Sound samples are saved in [config/drum/samples](./../config/drum/wav)

### Drum patterns

Drum patterns look like below. One pattern is inside INI section. Number of steps is equal to the longest drum length:

\[Pop1MeasureA 4/4\]
#...1234567890123456
ac: ....!.......!...
ch: !.!.!.!.!.!.!.!.
sd: ....!.!.....8...
bd: !.......8.....!.

* ac -- shows accents
* bd, sd -- are drum names
* "." -- silence on a step
* "!" -- drum hit on a step
* "8" -- 80% probability of drum hit, patterns may change from on bar to another

Drum names used in INI file and sample file names are the same (ex. sd.wav):

* ac: Accent - increases drum hit volume on specific step
* bd: Bass drum
* sd: Snare Drum
* lt: Low tom
* mt: Medium tom
* ht: High tom
* ch: Closed hi-hat
* oh: Open hi-hat
* cy: Cymbal
* rs: Rim shot
* cp: Clap
* cb: Cowbell

### Drum levels

There are three drum levels for Audio drum. At the start all patterns are sorted by intensity of drum accompaniment.
Intensity depends on number of drum hits, their probability, accents and specific samples volume.

After sorting samples are split into 3 equal groups - quiet, medium and intense. Thus, it is possible to switch drum
levels and select random drum in each group. Given that patterns have embedded hit probability the accompaniment is
quite
dynamic and non-repeating.

