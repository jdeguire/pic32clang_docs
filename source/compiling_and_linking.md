% Copyright (c) 2025, Jesse DeGuire
% All rights reserved.
% Licensed using a BSD 3-clause license, see LICENSE at the root of this project.
% Find this project on GitHub at https://github.com/jdeguire/mchpclang_docs.

# Compiling and Linking

Both compiling and linking your code are done through either the `clang` or `clang++` executables,
depending on whether or not you are using C++. The main differences are whether sources are assumed
to be C or C++ files by default and if the C++ standard library gets linked in. These executables are
sometimes called "drivers" because they aren't the compiler themselves. Rather, they figure out what
other tools to call--assembler, compiler, or linker--based on the options you give it. These documents
will use "Clang" to refer to either of these executables.


## Some Simple Examples
This section will provide a few simple examples of how you can run Clang. These will not show you
every option--there are a LOT of them--but this is enough to get you to understand the basic workflow.
For any "real" project, you'd probably use a build system like [CMake](https://cmake.org),
[Meson](https://mesonbuild.com/), or [SCons](https://scons.org/) to generate the right Clang calls
for you.

The absolute most basic command for building a simple `hello.cpp` app is the following.

```
clang++ hello.cpp
```

This will compile your file assuming it is C++, link it, and output an executable called `a.out`. You
probably want to call it something else, so you can add the **-o** option to make that happen. Note
that options ARE case-sensitive. In fact, **-O** is used to specify an optimization level. You can
have a look at the list of compiler options below to see more info about this option. This next
example will use both of these options together.

```
clang++ -O2 -o hello.elf hello.cpp
```

Most options do not care where on the command line they go. Options always start with either `-` or
`--`. Anything that does not is assumed to be either an argument to the previous option or a source
file. Source files are usually specified last, though. You can specify multiple files on the command
line to have them all built together. This is useful for small projects with only a few files that you
want to compile and link together in one go.

```
clang++ -O1 -o hello.elf hello.cpp foo.cpp bar.cpp
```

In most projects, you'll want to separate the compile and link steps. You'll have multiple files that
you will want to compile into object files and then you'll want to link the object files into your
final executable. You tell Clang to just compile by using the **-c** option. When you do that, you
will want to use the **-o** option to provide a useful name for your object file. By convention, this
will be the name of your source file, but with `.o` or `.obj` as the extension. You then will
call Clang like normal with your object files to link them together.

```
# Build three sources files into object files.
clang++ -O1 -o hello.o hello.cpp
clang++ -O1 -o foo.o foo.cpp
clang++ -O1 -o bar.o bar.cpp
# Now link them.
clang++ -o hello.elf hello.o foo.o bar.o
```

You can also tell the linker to link in external libraries. By convention, static libraries on Unix
and baremetal systems always start with `lib` and end in `.a`. You can use the **-l** option to
the linker to link in a static library that follows those conventions. For example, C math functions
are often in their own library called `libm.a`. To be sure you link those in, then you would do the
following. Notice that you need only the base name of the library without the `lib` or `.a`. 

```
clang++ -o hello.elf -lm hello.o foo.o bar.o
```

The **-l** option is one in which its placement does matter. The order in which items are linked and
thus will appear in your final executable depend on the order of the **-l** options and object files.
You can put the **-l** option after your object files if you like. You can use this option multiple
times to link multiple libraries.

Sometimes you need to define a macro that applies to whatever source files you are compiling. Use
the **-D** option to do that. This next example will show two forms of this option: one without a
macro value and one that defines a macro with a value. In the latter, you should not include spaces
around the `=`. You can use this option multiple times to define multiple macros.

```
clang++ -DBLEH -DBLOO=42 -o hello.o hello.cpp
```

Likewise, you can provide the linker with symbols it might need while linking. The main reason you
would do this is to tell the linker to allocate space for a heap. To do that you need to give the
linker the `__HEAP_SIZE` symbol with the value being the size of the heap you want. Linker options
are a little weird in that sometimes you need bundle them with the **-Wl** option to tell Clang that
the option is meant for the linker. Have a look at the linker options below for more info about this.
You can use this option multiple times to define multiple linker symbols.

```
clang++ -Wl,--defsym=__HEAP_SIZE=0x4000 -o hello.elf hello.o foo.o bar.o -lm
```


## Device Config Files
Clang needs to know about your device to generate the proper code for it. That would be things like
the target architecture, if the device has an FPU, how to find startup code, and stuff like that. To
handle this, this distribution is bundled with premade configuration files for every supported device.
All you have to do is tell Clang which configuration file to use with the `--config <devname>.cfg`
option. For example, if you wanted to build your `hello.cpp` app for a PIC32CZ8110CA80208, then you
would run the following.

```
clang++ --config pic32cz8110ca80208.cfg -o hello.elf hello.cpp
```

Notice that the configuration file name is in lower-case. Also notice that you include the "pic" for
devices that start with "PIC32". If you have a device whose name starts with "ATSAM", then you would
drop the "AT". For example, to build for the ATSAMD10C13A, you would do the following.

```
clang++ --config samd10c13a.cfg -o hello.elf hello.cpp
```

```{caution}
Be sure to pass the same config file every time you run Clang for your device. You'll probably get
unexpected results if you, for example, compile with one device config and link with another.
```

These config files use options that are not discussed here. If you want to see what those are, you
can find the configuration files in the `config/` subdirectory of the toolchain location. This version
of Clang is built to look in there by default for the config files. If you want to use your own
configuration files, see the Clang docs on configuration files [here](llvm:clang/html/UsersManual.html#configuration-files).


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
  - **g**: This is equivalent to level 1, but is here for compatibility with GCC.
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
are files to be built or arguments to previous options.


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
is optional. The stack will always use whatever memory is left over after everything else has been
allocted. 
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
are files to be linked or arguments to previous options.
