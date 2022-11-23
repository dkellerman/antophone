# Antophone

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
