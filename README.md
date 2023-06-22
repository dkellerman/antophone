# Antophone
Training RL ants to play a synthesizer. Extremely WIP. Uses python, with pygame window for display.

* `antophone.py` - run instrument - use `a` key to add ants (`A` to remove)
* `train.py` - train ants
* `farm.py` - interactive ant farm for debugging RL (`>` to step, `n` for new game)

## Install (Mac)
* `brew install portaudio --HEAD`
* `brew install portmidi libsndfile liblo aubio`
* `CFLAGS="-I/opt/homebrew/include -L/opt/homebrew/lib" poetry install`
* `poetry shell`
* `./main.py`


## Keys
* `a`|`A` - add/remove ant
* `c` - clear ants
* `>`|`<` - faster/slower cycle time
* `z`|`Z` - zoom in/out
* `m` - toggle mute
* `r` - toggle record (mic input)
* `/` - hot reload config

## Build Mac App
(from poetry shell)
* `python ./setup.py py2app -A`
* `./dist/Antophone.app/Contents/MacOS/Antophone`
