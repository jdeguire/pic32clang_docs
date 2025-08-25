% Copyright (c) 2025, Jesse DeGuire
% All rights reserved.
% Licensed using a BSD 3-clause license, see LICENSE at the root of this project.
% Find this project on GitHub at https://github.com/jdeguire/pic32clang_docs.
%
% LLVM for PIC32 documentation master file, created by sphinx-quickstart on Sun Aug 24 15:05:39 2025.

# LLVM for PIC32® Documentation

```{todo}
Find a better theme and see if I can increase the width.
```

Welcome! LLVM for PIC32® is a distribution of LLVM that includes all the support files you
need to build baremetal projects for Microchip's PIC32C and SAM devices. It is, essentially, an
alternative to Microchip's XC32 toolchain with a boring name.

```{note}
As of this writing (August 2025), Pic32Clang supports only the PIC32C and SAM microcontrollers. I
plan to support the MPUs in the future, but I'm not yet familiar enough with them to do so. I do not
plan to support the MIPS parts because MIPS is more or less dead. I also do not plan to support the
32-bit dsPICs like the dsPIC33A because those use a proprietary architecture not supported by LLVM.
```

These documents are not intended to make you an expert in using Clang or LLVM, but they will cover
some basics. You will want to have at least a little bit of experience running Clang or GCC (Clang is
purposefully largely compatible with GCC). These are more meant to help you with stuff that is specific
to the PIC and SAM devices, such as what you need to do to run the tools, how to access device registers,
and stuff like that.

```{todo}
Add links here or below for the LLVM and Clang docs.
```

```{toctree}
:maxdepth: 2
:caption: Contents:

compiling_and_linking.md
```

## A Note About Trademarks
This LLVM for PIC32 project and my [supporting projects](#my-projects) make references to trademarked
names from Microchip Technology Inc., such as "PIC®", "MPLAB®", and non-trademarked names such as
"PIC32", "SAM", and "XC32"[^1]. These names are all property of Microchip Technology Inc. These projects
also make reference to trademarked names from Arm Limited, such as "Arm®", "Cortex®", and "Thumb®" and
non-trademarked names such as "CMSIS"[^2]. These names are all property of Arm Limited.

These projects are all independent efforts not affiliated with, endorsed, sponsored, or otherwise
approved by Microchip Technology, Arm Limited, nor any of the contributors to any of the external
projects used by LLVM for PIC32.

[^1]: Checked August 2025. See the Microchip Trademark Standards document for a list of trademarked names:
<https://ww1.microchip.com/downloads/aemDocuments/documents/legal/Microchip-Trademark-Standards.pdf>.
[^2]: Checked August 2025. See Arm's Trademark List for the list of trademarked names:
<https://www.arm.com/company/policies/trademarks/arm-trademark-list>.


## Disclaimer
Microchip's toolchains are supported by a large company with a team of highly-experienced developers
who have been working with their GCC-based toolchains for *years*. You get integration with Microchip's
development environments and other software tools like MPLAB® Harmony. You get real support from a
real support team. Finally, you will get support for new devices as they're released and support for
more devices (LLVM for PIC32 will never support MIPS devices, for example). In other words, Microchip's
official toolchains provide you with proper integration and a seamless out-of-the-box experience.

With LLVM for PIC32, you're getting...not those things. I am just some dude on the internet who had
apparently too much time on his hands. What you *do* get are the latest and greatest that LLVM and
Clang have to offer. You get to use the `lld` linker, which is purported to offer much faster link
times than GNU `ld` and it supports [ThinLTO](http:../share/doc/LLVM/clang/html/ThinLTO.html). You get
the latest in C++ and C standards support that Clang has to offer. You get access to tools like 
`clang-tidy`, a static analyzer, `clang-format`, a code formatter, and `clangd`, a language server
to add some smarts to editors that support the Language Server Protocol.

It is up to you to decide which toolset will best meet your needs. If you need the proper integration
and support or if you need to use devices supported only by XC32, then you will want to stick with XC32.
If you want access to newer C and C++ goodies, do not mind going out on your own, and do not plan on
using Microchip's other software tools, then maybe give this a shot.

Just as a standard disclaimer, though: this software is provided "AS IS" with no warranty, implied
or otherwise. This project, its owners or contributors, or the owner or contributors of any supporting
projects shall be held liable for any damages regardless of cause as a result of using this software.


## Supporting Projects
This section shows projects used in the making of this toolchain distribution and these documents.

### External Projects
LLVM for PIC32 could not have happened without the efforts of the many people who made these projects
happen. Many thanks to all the contributors to these projects, no matter how big or small!

- LLVM Project  
Author: The LLVM Foundation  
Website: <https://www.llvm.org>  
Repository: <https://github.com/llvm/llvm-project>  
License: Apache 2.0 with LLVM Exceptions <https://github.com/llvm/llvm-project/blob/main/LICENSE.TXT>
- CMSIS 6  
Author: ARM Limited  
Website: <https://www.arm.com/technologies/cmsis>  
Repository: <https://github.com/ARM-software/CMSIS_6>  
License: Apache 2.0 <https://github.com/ARM-software/CMSIS_6/blob/main/LICENSE>
- Sphinx Doc  
Author: the Sphinx developers  
Website: <https://www.sphinx-doc.org/>  
Repository: <https://github.com/sphinx-doc/sphinx>  
License:  BSD 2-clause <https://github.com/sphinx-doc/sphinx/blob/master/LICENSE.rst>  
Note: The Sphinx Python package is used to create these docs rather than using the repo directly. It
is included here for completeness.

### My Projects

In addition, you can find my projects on GitHub at the folloing locations. If you want to build a
complete Pic32Clang distribution or modify it for your own use, you can use the Python script found
at <https://github.com/jdeguire/buildPic32Clang>. Follow the README there to get going. The Python
files are under the BSD 3-clause license and the CMake caches use the Apache 2.0 license with LLVM
Exceptions. The latter is because I used example CMake caches from LLVM to make the ones in that
project.

If you want to generate device files, such as linker scripts, header files, startup code, and device
config files for your own project, you can find the Python app to do that at <https://github.com/jdeguire/pic32-device-file-maker>.
You can find the sources for these documents at <https://github.com/jdeguire/pic32clang_docs>. The
sources for both are under the BSD 3-clause license. The files generated by the `pic32-device-file-maker`
script are under the Apache 2.0 license. This is the license used by ARM's CMSIS 6 and the files I
generate are based on the example files provided in CMSIS.

These documents are written using the MyST flavor of Markdown, which you can learn more about
[here](https://myst-parser.readthedocs.io/en/latest/index.html).
