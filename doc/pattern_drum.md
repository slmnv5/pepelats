## Pattern drum

**Pattern drum** is using text patterns and sample WAV files to produce drum accompaniment.
These sound samples are written into sound buffer along with recorded loops.

There are about 200 patterns in a dozen of styles in directory: [config/drum/pattern](./../config/drum/style)
Example: [Pop.ini](../config/drum/style/Pop.ini)

Sound samples are saved in [config/drum/samples](./../config/drum/wav)

### Drum patterns

Drum patterns look like below. One pattern is inside INI section. Number of steps is equal to the longest drum length

~~~
[Pop1A 4/4]  
#...1234567890123456  
ac: ....!.......!...  
ch: !.!.!.!.!.!.!.!.  
sd: ....!.!.....!...  
bd: !.......!.....!.  
~~~

* ac -- shows accents
* bd, sd -- are drum names
* "." -- silence on a step
* "!" -- drum hit on a step
* Drum names used in pattern INI file and WAV file names are the same (ex. sd.wav):

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


