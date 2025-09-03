% Copyright (c) 2025, Jesse DeGuire
% All rights reserved.
% Licensed using a BSD 3-clause license, see LICENSE at the root of this project.
% Find this project on GitHub at https://github.com/jdeguire/pic32clang_docs.

# Compiling and Linking

```{todo}
Add a few examples of compiling and linking.
```

Both compiling and linking your code are done through either the `clang` or `clang++` executables,
depending on whether or not you are using C++. These documents will use "Clang" to refer to either
of these executables.

The absolute most basic command for building a simple `hello.cpp` app is the following.

```
clang++ -o hello.elf hello.cpp
```

This should compile your C++ file, link it with the provided runtime libraries, and output an ELF file.
What it will *actually* do is exit with an error. Clang thinks you want to build your code for x86
processors because you didn't tell it otherwise. This distribution does not include libraries for x86
processors, so the link will fail. You therefore need to tell Clang about your device so it knows how
to build your code. There are plenty of options you can give to Clang to do that, but read on for a
simpler way.


## Device Config Files
Clang needs to know about your device to generate the proper code for it. That would be things like
the target architecture, if the device has an FPU, how to find startup code, and stuff like that. To
handle this, this distribution is bundled with premade configuration files for every supported device.
All you have to do is tell Clang which configuration file to use with the `--config=<devname>.cfg`
option. For example, if you wanted to build your `hello.cpp` app for a PIC32CZ8110CA80208, then you
would run the following.

```
clang++ --config=pic32cz8110ca80208.cfg -o hello.elf hello.cpp
```

Notice that the configuration file name is in lower-case. Also notice that you include the "pic" for
devices that start with "PIC32". If you have a device whose name starts with "ATSAM", then you would
drop the "AT". For example, to build for the ATSAMD10C13A, you would do the following.

```
clang++ --config=samd10c13a.cfg -o hello.elf hello.cpp
```

```{caution}
Be sure to pass the same config file every time you run Clang for your device. You'll probably get
unexpected results if you, for example, compile with one device config and link with another.
```


## A Few Useful Compile-time Options
Here are a few useful options you can use in your projects. Clang has a *lot* of options, so check
out the official documents for all of them. Options are case-senstive.

% The -\\- you see stops Sphinx from converting two hyphens into en dashes.

- **-c**  
Compile the given input files into an object file that you will link later. The default is to both
compile your files and then link them.
- **-\\-config=\<file\>**  
You already saw this option above. This lets you supply Clang with a file containing command line
options. This takes absolute or relative paths, with the path being relative to the `config` directory
in the toolchain installation location. You can supply your own configuration file to Clang if you
do not want to use one of the provided ones. Use the `--config-user-dir=<dir>` option to point Clang
to your files. That will take precedence over the default location.
- **-D\<macro\>** or **-D\<macro\>=\<value\>**  
Define a macro that is visible to all files currently being compiled. You can use the second form to
give the macro a particular value.
- **-ffunction-sections**  
Put each function into its own ELF section in the output binary. Use this with the `--gc-sections`
linker option to remove unused functions from your code.
- **-g\<level\>**  
Set the level of debug information in the output binary. The lowest level is 0, which outputs no debug
information. The highest is level 3, which outputs the most debug information, including information
for macros. This debug info is never included in an Intel HEX file, so if you distribute your firmware
with HEX files then you might as well turn this on.
- **-I\<dir\>**  
This is an upper-case `i`, not a lower-case `L`. Add the given directory to a list of include paths
to be searched when you include a file with quotes (ex: `#include "foo.h"`). Use this multiple times
to add more than one directory to the list of paths to search.
- **-mthumb**  
Compile targeting the Thumb instruction set variant appropriate for the device. Thumb is a compressed
instruction set that mixes 16- and 32-bit instructions for increased code density. MCU devices always
use Thumb and so this option is unneeded. For MPU devices, the default is the 32-bit ARM instruction
set and so you'd use this to use Thumb instead.
- **-O\<level\>**  
Set the level of optimization the compiler should apply to whatever you are compiling. The `<level>`
can be one of the following. You can omit the level to get level 1.

  - **0**: No optimization. This is the default and can be useful for debugging.
  - **1**: Basic optimization. This can provide a good balance between performance and debugability.
  - **2**: Optimize more. This provides better performance at the cost of debugability.
  - **3**: Optmize even more. This will certainly make debugging difficult and may increase the size
  of your final binary.
  - **s**: Optimize for size. This is sort of like level 2 but will also try to reduce code size.
  - **z**: Optimize more for size. This will do what it can to minimizie code size.
- **-o \<file\>**  
Set the name of the output file. If the `-c` option is present, this will be the name of the resulting
object file and so you would normally end it with `.o`. Otherwise, this will be the name of the resulting
ELF file and so you would normally end it with `.elf`.
- **-std=\<stdlevel\>**  
Set the C or C++ standard to follow, depending on if you are building a C or C++ file. The `<stdlevel>`
is either `c` or `c++` followed by the two-digit year of the standard. For example, `c++17` will give
you C++17 support. If you use `gnu` or `gnu++` instead of `c` or `c++`, you will get additional GNU
extensions to that standard. As of this writing in August 2025, Clang uses `gnu++17` for C++ and
`gnu11` for C.
- **-x \<lang\>**  
By default, Clang will use the extension of your input files to determine the language to use. Use
this option to override that. The value of `<lang>` can be `c` for C, `c++` for C++, `assembler` for
assembly language, or `assembler-with-cpp` for assembly language files that need the C preprocessor.

All options start with either `-` or `--`. Clang will assume that command line arguments that do not
are files to be built.


## A Few Useful Link-time Options
Here are some useful options you can use when linking your project. Like with the compile-time options,
this is only a very small subset of the many options Clang provides.

Some options need to be passed directly to the linker. To do this, prefix the option with `-Wl,`, such
as `-Wl,--some-linker-option`. You can use `-Wl` multiple times or you can supply multiple options by
separating them with commas. If an option takes an argument that is separated by a space, then you need
to replace that space with a comma. For example, to pass `--option-with-arg the_arg`, you would use
`-Wl,--option-with-arg,the_arg`. You do not need to do this if the option and its argument are separated
by an `=`. An option `--foo=bar` would be provided to the linker as `-Wl,--foo=bar`.

Not all options need the above syntax. The below list of options will indicate which ones do with
*-Wl* after the option name.

% The -\\- you see stops Sphinx from converting two hyphens into en dashes.

- **-\\-config=\<file\>**  
This is the same option you pass to the compiler above. This contains a few options that get passed
to the linker.
- **-\\-defsym=\<symbol\>=\<value\>** (*-Wl*)  
Use this to define symbols the linker uses when laying out the binary. In particular, you can use 
`-Wl,--defsym=__HEAP_SIZE=0x4000` to allocate a heap. Notice there are no spaces surrouning the two 
`=` in the option. There is a similar symbol `__STACK_SIZE` to ensure a minimum stack size, but it
is optional. The stack is always allowed to use whatever main memory is not used by the heap and
statically-allocated symbols. 
- **-\\-gc-sections** (*-Wl*)  
Remove any unused ELF file sections from the final binary. You generally use this with the compiler
option `-ffunction-sections` to remove any functions that are not used from your output file to reduce
code size.
- **-L\<dir\>**  
Tell the linker where to look for libraries when you use the `-l` (lower-case `L`). You can provide
this option mulitple times to have the linker look in multiple directories for libraries.
- **-l\<lib\>** or **-l:\<lib\>**  
This is a lower-case `L`, not an upper-case `i`. Link the given library into the final executable.
The first form is used when a library name is of the form `libfoo.a`. In that case, you would use
`-lfoo`. If you have a library that does not start with "lib", then you can use the second form. For
example, use `-l:my_cool_lib.lib` to link against a library called `my_cool_lib.lib`.
- **-Map=\<file\>** (*-Wl*)  
Tell the linker to create a map file, which is a text file describing the contents of your output
binary. The file is a listof symbols (variables and functions), their location in the device memory,
and what object files they came from. This can be useful for seeing why your binary is larger than
you expect or for determing in which function a crash occurred.
- **-o \<file\>**  
Like with the compiler, this tells the linker what you want the output file to be named. Usually, you'd
probably end it in `.elf`, but you don't have to.

```{tip}
If you plan on using floating-point math functions, you will want to link against the `libm` math
library. As you can see from the options above, you would simply add `-lm` to your link command.
```

All options start with either `-` or `--`. Clang will assume that command line arguments that do not
are files to be linked. The linker can take object files, which usually end in `.o`, or static libraries,
which usually end in `.a`.
