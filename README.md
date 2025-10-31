# mchpclang_docs
_This project used to be called "pic32clang_docs", but I changed it to avoid any trademark concerns
with using "PIC" in the name._

This repository contains documentation specific to mchpClang, which is a distribution of LLVM set
up for use with Microchip PIC32C and SAM processors. This is meant to be run with the `buildMchpClang`
script found [here](https://github.com/jdeguire/buildMchpClang), but you can also run this on its own.

## Prerequisites
If you are planning on running the `buildMchpClang` script referenced above, then you can follow the
README in that project to get everything you need. Otherwise, these instructions should help you get
going.

This project uses the [Sphinx](www.sphinx-doc.org) documentation generator. Sphinx is a Python program,
so you'll need to install a recent vesion of Python on your system. The latest version at the time of
this writing is Python 3.13, but later Python 3.xx versions should work fine as should versions that
are a few point releases back. If you are using Windows, then you can install Python either from the
Windows Store or from the [Python website](https://www.python.org/downloads/). If you are on Linux,
then Python will likely be available in your distribution's package manager.

Install Sphinx using the directions on the [Sphinx website](https://www.sphinx-doc.org/en/master/usage/installation.html).
If you are on Windows, then follow the instructions for getting the PyPI package with `pip`. Otherwise,
follow the OS-specific instructions there. Some Linux distributions, like ones basd on Ubuntu, want
you to get packages from the system package manager rather than using `pip`.

You also need the `myst-parser` package. Install that from `pip` or your system's package manager.

## Building the Docs
To build the docs into a series of HTML files, simply run `make html` from this directory. On Windows,
the `make.bat` file should run. On other systems, GNU Make will be run and will use the `Makefile`
in this directory.

## Editing the Docs
These documents are written using the MyST flavor of Markdown. Learn more at the official 
[MyST website](https://myst-parser.readthedocs.io). If you use Visual Studio Code, the `MyST-Markdown`
plugin is very handy.

I still have a lot to learn about Markdown and MyST, so feel free to improve these documents!

## License
See the LICENSE file for the full thing, but basically this is licensed using the BSD 3-clause
license because I don't know anything about licenses and that one seemed good.

## Trademarks
This project and the similarly-named ones make references to "PIC32", "SAM", "XC32", and "MPLAB"
products from Microchip Technology. Those names are trademarks or registered trademarks of Microchip
Technology.

These project also refer to "Arm", "ARM", "Cortex", and "CMSIS", which are all trademarks of Arm
Limited.

These projects are all independent efforts not affiliated with, endorsed, sponsored, or otherwise
approved by Microchip Technology nor Arm Limited.
