% Copyright (c) 2025, Jesse DeGuire
% All rights reserved.
% Licensed using a BSD 3-clause license, see LICENSE at the root of this project.
% Find this project on GitHub at https://github.com/jdeguire/mchpclang_docs.

# Other Tools

LLVM comes with lots of useful utilties beyond those used for compiling and linking code. This chapter
will describe a few of them you might find useful for your normal baremetal development. If you have
used GCC and some of the GNU Binutils utilities, then these will be familiar to you. If you want more
information on any of these tools or to see what other tools LLVM provides, you can check out the
[LLVM Command Guide](llvm:llvm/html/CommandGuide/index.html).


## Convert an ELF File to a Programmable Format
The linker outputs an ELF file, which is the standard Unix executable file format. However, programming
tools may not support ELF files and instead want some other format. Common formats are straight binary
files (particularly for MPUs), Intel Hex files, or Motorola S-record files. You can use the `llvm-objcopy`
tool to convert from an ELF file to one of those formats. In particular, you want to use the **-O**
option to tell `llvm-objcopy` the output format you want. It can figure out the input format automatically
if it is an ELF file.

```
# To create a binary file
llvm-objcopy -O binary file_name.elf file_name.bin
# To create an Intel Hex file
llvm-objcopy -O ihex file_name.elf file_name.hex
# To create a Motorola SREC file
llvm-objcopy -O srec file_name.elf file_name.srec
```

The input file must of course be an existing file. The output file does not have to have the same
name as the input file nor does the file extension matter as long as you provide the **-O** option.

For binary files, the output will contain the raw memory image as given in the input file. It will
start at the address of the first loadable section in the ELF file and end at the last address. If
you are using a binary file, then chances are you are using an MPU that has a bootloader application
on it that expects the binary to be within a particular address range.


## Get the Size of Your Binary
LLVM provides the `llvm-size` tool to print size information for binary files. You would provide it
with your output ELF file to see the size of its .text, .data, and .bss sections. There are a few
command line options to control how the output looks. Use the **-B** option to give output in "Berkeley"
format, which is the default, or **-A** to give output in "SysV" format. You can also use **-d** to
have the size value be in decimal, the default, **-o** for octal, or **-x** for hex. Here are a few
examples of what the outputs look like.

Notice that you give `llvm-size` your ELF file rather than an, say, an Intel Hex file.

```
llvm-size -B my_app.elf 
   text    data     bss     dec     hex filename
 971774    1324  782504 1755602  1ac9d2 my_app.elf
```

```
llvm-size -B -x my_app.elf 
   text    data     bss     dec     hex filename
0xed3fe   0x52c 0xbf0a8 1755602  1ac9d2 my_app.elf
```

```
llvm-size -A my_app.elf 
my_app.elf  :
section                   size        addr
.vectors                  1414   134217728
.text                   970168   201326592
.gnu.sgstubs                 0   202296768
.ARM.exidx                 192   202296768
.itcm                        0           0
.dtcm                        0   536870912
.data                     1324   537001984
.tdata                       0   537003308
.tbss                        0   537003308
.bss                    778408   537003328
.heap                     3072   537781736
.stack                    1024   538049536
.comment                   251           0
.ARM.attributes             71           0
.debug_abbrev           145596           0
.debug_info            1800725           0
.debug_str_offsets      247096           0
.debug_str              119368           0
.debug_line             960783           0
.debug_line_str          76728           0
.debug_loclists         983857           0
.debug_rnglists         169059           0
.debug_addr              36332           0
.debug_frame             36160           0
Total                  6331628
```

```
llvm-size -Ax my_app.elf 
my_app.elf  :
section                    size         addr
.vectors                  0x586    0x8000000
.text                   0xecdb8    0xc000000
.gnu.sgstubs                  0    0xc0ecdc0
.ARM.exidx                 0xc0    0xc0ecdc0
.itcm                         0            0
.dtcm                         0   0x20000000
.data                     0x52c   0x20020000
.tdata                        0   0x2002052c
.tbss                         0   0x2002052c
.bss                    0xbe0a8   0x20020540
.heap                     0xc00   0x200de5e8
.stack                    0x400   0x2011fc00
.comment                   0xfb            0
.ARM.attributes            0x47            0
.debug_abbrev           0x238bc            0
.debug_info            0x1b7a15            0
.debug_str_offsets      0x3c538            0
.debug_str              0x1d248            0
.debug_line             0xea90f            0
.debug_line_str         0x12bb8            0
.debug_loclists         0xf0331            0
.debug_rnglists         0x29463            0
.debug_addr              0x8dec            0
.debug_frame             0x8d40            0
Total                  0x609cec
```

The output provided by `llvm-size` is pretty basic. It can show only output sections and so does not
show how much space individual object files or functions take up. If you want that, then you should
use the **-Map** option to your linker to generate a Map file.


## Disassemble Your Binary
Use `llvm-objdump` to disassemble your ELF file into a readable disassembly listing file. This is
useful if you want to see how the compiler compiled your code or if you are investigating a crash.
This utility has a lot of options, but chances are there is a particular set of them you will want
to use the majority of the time. Here is an example of that set of options.

```
# Use this in Unix or Linux or old Windows consoles
llvm-objdump -dSrC my_app.elf > my_app.asm

# Use this in Windows PowerShell terminals
llvm-objcump -dSrC my_app.elf | out-file -encoding utf8 my_app.asm
```

These options are case-sensitive. Most Linux or Unix utilities, not just Clang or LLVM, let you combine
multiple single-letter options into a single option. Here, the string `-dSrC` is actually four different
options combined together. This is equivalent to `-d -S -r -C`, but is generally easier to type.

The **-d** option tells `llvm-objdump` that you want to disassemble the ELF file. The **-S** option
tell it to mix in lines of source code with the disassembly so you can associate lines of disassembly
with the source code that generated them. The **-r** option tells it to include relocation information
in the file. This is info that the linker will use to locate external symbols at link time. This option
is not always necessary, but there is no harm in using it. Finally, **-C** tells `llvm-objdump` to
demangle C++ symbol names.
