# Pyfilesync_GUI
#### A graphic user interface for pyfilesync written in python and using [Flet] framework.

<p align="middle">
	<img src="assets/images/icon-default.png"/>
</p>

This is a desktop GUI application that includes pyfilesync code in a stand alone binary.

> Note: Only French is available in the app for now


## TODO
- Multi-languages support
- Files history management
- Theming
- Testing on Linux

## Target platforms
Flet allows an app to run on the following targets :
- Mobile (Android, iOS),
- Desktop (Windows, MacOS, Linux)
- Web

Nevertheless, this App is intended to run only on desktop, and is not designed to run on mobile targets.

## Some Screenshots
TBD

## Tech and dependencies
This app uses [Flet] and [python] v3.12 or later

## Installation
### 1) Flet installation
go to https://flet.dev/docs/getting-started/installation and follow given instructions.
On Windows, the sequence is as follow :
```sh
cd pyfilesync_gui
python -m venv .venv
.venv/scripts/activate
pip install flet
```

### 2) code configuration
TBD

### 3) Running the app
from the base folder of the repo, type :
```flet run```

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
  [Flet]: <https://flet.dev/>
  [python]: <https://www.python.org/>