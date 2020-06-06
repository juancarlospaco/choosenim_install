# Choosenim integration for Python PIP

- Install [Nim](http://nim-lang.org) directly from [Python PIP](https://pypi.org/project/nimble-install). https://pypi.org/project/nimble-install

# Use

Uses PIP to install [Nim](http://nim-lang.org) via ChooseNim.

```console
$ nim --version
nim: command not found

$ pip install choosenim_install
    choosenim-init: Downloading choosenim-0.6.0_linux_amd64
          Info: Version 1.2.0 already selected
    choosenim-init: ChooseNim installed in /home/juan/.nimble/bin
    Downloading Official package list
        Success Package list downloaded.

Successfully built choosenim-install
Successfully installed choosenim-install-0.0.1

$ nim --version
Nim Compiler Version 1.2.0 [Linux: amd64]
Compiled at 2020-04-03
Copyright (c) 2006-2020 by Andreas Rumpf
active boot switches: -d:release

$
```

- You can re-run it several times if you want.


# Requisites

- Linux OR Apple Mac OS X *(NOT Windows)*


# More Info

- [**For Python Developers.**](https://github.com/nim-lang/Nim/wiki/Nim-for-Python-Programmers#table-of-contents)
