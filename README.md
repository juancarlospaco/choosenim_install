# Nim integration for Python PIP

- AutoInstall [Nim](http://nim-lang.org) directly from [Python PIP](https://pypi.org/project/choosenim-install).
- AutoInstall of `nim`, `nimble`, `nimpy`, `fusion`, `nodejs`, `cpython`.


# Use

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
Nim Compiler Version 1.2.6 [Linux: amd64]
Compiled at 2020-04-03
Copyright (c) 2006-2020 by Andreas Rumpf
active boot switches: -d:release

$
```


![](https://raw.githubusercontent.com/juancarlospaco/choosenim_install/master/choosenim_install_windows.png)


- You can re-run it several times if you want.

![](https://raw.githubusercontent.com/juancarlospaco/choosenim_install/master/choosenim2.png)

- Update an old version of Nim to the latest just by reinstalling the package using PIP.


# Requisites

#### Stable

- Python >=`3.5`, CPython implementation, Linux or Windows, x86 and ARM, 64Bit.

#### Experimental

- Mac, PYPY2, PYPY3, Python2, 32Bit are all Experimental.


# History

Originally this used multiple bundled `choosenim` to install Nim,
now it re-implements `choosenim` functionalities in pure Python.


# More Info

- [**For Python Developers.**](https://github.com/nim-lang/Nim/wiki/Nim-for-Python-Programmers#table-of-contents)

# Stars

![](https://starchart.cc/juancarlospaco/choosenim_install.svg)
