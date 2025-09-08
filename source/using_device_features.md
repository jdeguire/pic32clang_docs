% Copyright (c) 2025, Jesse DeGuire
% All rights reserved.
% Licensed using a BSD 3-clause license, see LICENSE at the root of this project.
% Find this project on GitHub at https://github.com/jdeguire/pic32clang_docs.

# Using Device Features

This chapter will provide examples showing how to access device-specific features like peripheral
registers or interrupts. You will want to consult the datasheet for your device for additional
information on the feature you are trying to use.

This documentation will focus mostly on accessing features from C and C++ code because that is most
likely how they will be used. Accessing features from assembly is possible, but generaly more limited
to using macros to form the addresses you need to access registers and stuff like that.


## A Word of Caution
The datasheet can help you determine how to access device features, but you might need to do a bit
of device header devling on occasion. In my experience, you will have a pretty easy time mapping things
like register and bitfield names in the datasheet into the correct names in code. Interrupt vector
names, however, do not always match what the documentation for the peripheral says. This limitation
applies to Microchip's own toolchains as well, but it is worth mentioning here.

The device-specific header files are located in the toolchain install location under the `arm/include/proc`
subdirectory. When you supply Clang with a device-specific config file, it tells Clang to look for
headers in this directory. If you have a text editor or IDE that can query the compiler for its include
directories, like Visual Studio Code, then you should provide it with the `--config` option you supply
to Clang. That way, any auto-complete features the editor has can help you fill in the register or
interrupt names you need.

```{admonition} Implementation Detail
:class: note

The build scripts that build this LLVM distribution parse special Microchip XML files that contain
all of the information about the devices to generate the device-specific code this ships with. These
XML files have the suffix `.atdf` and are included with Microchip device packs. If you have used
Microchip's MPLAB® X IDE, then you have likely had to select a pack version for your project and seen
notifications about updating your packs. These packs contain the sorts of device-specific stuff that
this distribution bundles for you, but those files contain stuff specific to Microchip's toolchains
and so cannot be used here.

Basically, the build scripts can use only what info these packs provide and that info may not 100%
agree with the datasheet. This is why Microchip's own toolchains have this same problem.
```


## The Device Header Files
Every device supported by this toolchain has a device-specific header file that provides access to the
device's perpheral registers, config registers, interrupt vector values, and so on. These are located
in the toolchain install location under the `arm/include/proc` subdirectory. However, you do not have
to explictly include the device-specific header if you do not want to. Instead, you can include the
`which_pic32.h` header and that will figure out which device-specific header you need. For this to
work, you need to supply Clang with the proper `--config` file option for your device.

If you are working on a project that you want to build both with Clang and Microchip's XC32 compiler,
then you can use this snippet to select the correct file.

```c
#ifdef __clang__
#  include <which_pic32.h>
#else
#  incluce <xc.h>
#endif
```


## CMSIS
Arm® provides a device support library called the Common Microcontroller Software Interface Standard,
or CMSIS (pronounced "Sim-sis"). CMSIS is a common base set of macros and routines that will work on
any Cortex®-M MCU and Cortex-A MPUs that use the ARMv7-A instruction set, no matter the vendor. It
includes macros and routines to do things like do cache maintenance operations, access system control
registers, and handle interrupts.

This distrubtion includes an at-the-time recent version of the core CMSIS libraries. These are included
from the device-specific header files so you do not have to do this manually. The next sections may
include some CMSIS routines where applicable, but you should check out the official Arm CMSIS website
if you want the complete documentation. You can find more info at <https://www.arm.com/technologies/cmsis>.

Arm provides additional libraries under the CMSIS umbrella, such as CMSIS-NN for neural network math
or CMSIS-DAP for using their Debug Access Protocol. This additional libraries are NOT provided with
this distribution.

CMSIS also has examples for how to create device-specific files, like headers, linker scripts, and
startup code. This distribution used those examples to create the device-specific files included
with it.

```{important}
CMSIS does not support Arm products that predate the Cortex branding. In particular, it does not have
any code to handle ARM11™ or older devices. In those cases, you are currently on your own. A future
version of this distribution may be able to provide a few useful CMSIS-like functions for you to use.
```


## ACLE
Clang provides support for the Arm C Language Extensions, or ACLE. These are extensions that are
built into the compiler to provide things like predefined macros to provide device info, more builtin
functions to access device features beyond what CMSIS provides, and even new attributes (think the
GNU `__attribute__` keyword or the C++11 `[[attr]]` syntax).

This document may highlight some ACLE macros or functions, but is not comprehensive. You can find more
information on the Arm developer site at <https://developer.arm.com/Architectures/Arm%20C%20Language%20Extensions>.
There are separate specification documents for base ACLE support, SIMD operations for MCUs and MPUs,
and security extensions.

You can see what other extensions Clang supports in the Clang documentation [here](llvm:clang/html/LanguageExtensions.html).


## Peripheral Registers
Peripheral registers are memory-mapped; that is, they are located at fixed memory addresses and you
access them as though they were global variables. The device-specific headers provide macros to let
you access the registers. Each device-specific header includes additional peripheral-specific headers
that provide many of the macros and types discussed in this section.

There is a lot going on here. As you will see, having an editor with good completion features does
come in handy.

### Peripherals vs Instances
This section will refer to both peripherals and instances. A *peripheral* is a type of functional block
on the device and one or more *instances* of that peripheral will be present on the device. For example,
the CAN peripheral provides Controller Area Network functionality to a device. A device can have, say,
two instances of the CAN peripheral and they would be referred to as CAN0 and CAN1.

In other words, if a number is present (CAN**0**) then this is an *instance*; otherwise, it is a
*peripheral*. If a device has only one instance of a peripheral, then it might omit the number and
so the instance and peripheral names will be the same.

### Base Address Macros
All peripherals have macros you can use to get its base address. Each instance of each peripheral has
its own macro. The format of these macros is `{instance}_REGS_BASE`. For example, if you
wanted the base address of SERCOM0, you would use `SERCOM0_REGS_BASE`{l=c}. For TCC4, you would use
`TCC4_REGS_BASE`{l=c}. These macros evaluate to the absolute address of the start of the peripheral's
registers as an `unsigned long`{l=c}.

To access a specific register within a peripheral, you can get its offset from the base address with
a macro of the form `{peripheral}_{register}_OFFSET`. So, if you wanted the address of the `TOCV`
register of the CAN1 instance, you would use `CAN1_REGS_BASE + CAN_TOCV_OFFSET`{l=c}. Notice that the
offset macro uses the *peripheral* name "CAN" and not the *instance* name "CAN1". This is because
the registers are the same for each instance of a peripheral and so having each perpiheral-specific
macro use the instance would just be redundant.

Macros are always in upper-case, which is a common convention in C programming. These macros can be
used in assembly along with C and C++. If your assembly file ends in a capital `.S`, then Clang will
run the preprocessor on it before the assembler.

### Other Register Macros
Each register has two additional macros associated with it. The first is formatted as `{peripheral}_{register}_RESETVAL`
and gives the value of the register upon device reset. The other is formatted as `{peripheral}_{register}_MASK`
and indicates which bits of the register are used.

These macros can be used in assembly along with C and C++.

### Peripheral Structs/Unions (C/C++ Only)
Another way to access device registers is to use macros that present the peripheral registers as a
C struct you can reference. The macros are formatted as `{instance}_REGS` and evaluate to 
`((volatile {peripheral}_registers_t *){instance_REGS_BASE)`{l=c}. The type name here is all lower-case
and is provided by the periphal-specific headers included by the device-specific headers. The structs
mimic the layout of the instance's registers in memory. You can think of these macros as "overlaying"
the struct on top of the memeory locations the instance's registers occupy.

For most peripherals, the members of the struct correspond to the registers in the device. The format
is `{peripheral}_{register}`. For example, if you wanted to access the `SYNCBUSY` register in the
TCC5 instance, then you would use `TCC5_REGS->TCC_SYNCBUSY`{l=c}. It does seem redundant to have the
peripheral name present in the register name, but this was done to maintain some compatibility with
Microchip's XC32 toolchain.

These struct macros can be used only in C and C++.

(peripheral-modes)=
#### Peripheral Modes
Some peripherals can operate in different "modes". The main examples are the SERCOM and FLEXCOM
peripherals. These can act as a I2C Master or Slave, a SPI Master or Slave, or a USART. FLEXCOM uses
the term "TWI" instead of "I2C" for some reason.

In periphreals with modes, the peripheral type is a union rather than a struct. Its members refer to
the possible modes the peripheral can be in. Those members are themselves structs that contain the
registers. All registers here are accessed through a mode even if the register is not specific to a
particular mode. For example, to access the `STATUS` register in SERCOM8, you need to decide the mode
you intend to use the instance in first. If you want to use it in SPI Master mode, then you could access
the register with `SERCOM8_REGS->SPIM.SERCOM_STATUS`{l=c}.

#### Register Groups
Some peripherals will groups sets of registers together because the peripheral is used to handle a
set of subperipherals. For example, a DMA peripheral might have some registers to control the DMA
module as a whole, but then have register groups to control DMA channels independently.

Cases like these are sort of a cross of the normal case and the above "modes" case. Registers that
control the peripheral as a whole are accessed like normal. For example, the `CTRLA` register is a
member of the overall DMA peripheral rather than existing per-channel, so you would access it with
`DMA_REGS->DMA_CTRLA`{l=c}. On the other hand, each DMA channel has its own register to store a DMA
start address, `CHSSA`. If you wanted to access the start address for channel 2, then you would use
`DMA_REGS->CHANNEL[2].DMA_CHSSA`{l=c}.

As a special case for this special case, some devices have a single PORT peripheral with no registers
at the top level and all of under groups. Each group corresponds to a port letter. So group 0 is for
the `PAx` pins, group 1 for the `PBx` pins, and so on. To toggle a `PDx` pin with the `OUTTGL` register,
you would use `PORT_REGS->GROUP[3].PORT_OUTTGL`{l=c}.

#### DMA Descriptor Structs
Peripherals that can access memory, such as the DMA or SQI peripherals, provide additional structs
for the descriptors the peripheral looks for in memory. You do not have to use these if you are using
the in-memory descriptors, but are there for convenience. Unfortunately, not all peripherals that
use descriptor structures provide these for some reason. In particular, the ETH peripheral for Ethernet
uses descriptors to read and write packet data, but no structures are provided for this.

### Array Access to Peripheral Instances
The instance macros above work if you want to hardcode the peripheral to access at compile time.
However, it may be useful to be able to access peripheral instances from an array. This is handy for
writing reusable code such as for a C++ class. In such a case, you could supply the instance number
through the class's constructor.

The device-specific files provide a set of static variables to access peripheral instances through
arrays. The names of the arrays are formatted as `{peripheral}n_REGS`. Each array will have at least
one element in it. Here is an example of accessing the TCC peripheral through one of these arrays.

```c
void EnableTcc(uint32_t which)
{
    if(which < (sizeof(TCCn_REGS) / sizeof(TCCn_REGS[0])))
    {
        TCCn_REGS[which]->TCC_CTRLA |= TCC_CTRLA_ENABLE_Msk;
    }
}
```

### Register Field Macros
Now that you can access device registers, you can use additional macros to access the fields within
the registers. You do not have to use these and can simply write literal values to registers if you
like.

Each field will have at least three macros associated with it. The first is a mask that indicates the
width of the field and is formatted as `{peripheral}_{mode}_{register}_{field}_Msk`. The second
indicates the bit position of the field starting from the least-significant bit and is formatted as
`{peripheral}_{mode}_{register}_{field}_Pos`. Finally, you can set a value for the field with a
function-like macro of the form `{peripheral}_{mode}_{register}_{field}(value)`. The `{mode}` portion
applies only to peripherals with [operating modes](#peripheral-modes); otherwise, you omit that portion
and one of the underscores.

These field macros can be used in assembly along with C and C++.

This is a lot to take in, so here are a couple examples take directly from some peripheral headers.
First, here are the macros available for the `TXSPACE` field in the `FIFOSPACE` SERCOM register.
Since SERCOM has different operating modes, these macros will reflect that. Here the mode is `I2CM`
for I2C Master.

```c
#define SERCOM_I2CM_FIFOSPACE_TXSPACE_Msk (0x0000001Ful)   /* Tx FIFO Empty Space */
#define SERCOM_I2CM_FIFOSPACE_TXSPACE_Pos (0ul)
#define SERCOM_I2CM_FIFOSPACE_TXSPACE(v)  (SERCOM_I2CM_FIFOSPACE_TXSPACE_Msk & ((uint32_t)(v) << SERCOM_I2CM_FIFOSPACE_TXSPACE_Pos))
```

Here is another exmaple from the ETH peripheral that does not have a `{mode}` value.

```c
#define ETH_CTRLB_GMIIEN_Msk              (0x00000001ul)   /* Select GMII/MII mode */
#define ETH_CTRLB_GMIIEN_Pos              (0ul)
#define ETH_CTRLB_GMIIEN(v)               (ETH_CTRLB_GMIIEN_Msk & ((uint32_t)(v) << ETH_CTRLB_GMIIEN_Pos))
```

You can see that the last function-like macro uses the other two to shift and mask your value. This
`GMIIEN` field is used to enable GMII mode for the Ethernet MAC. If you wanted to enable this, you
can write to the `CTRLB` register like so.

```c
ETH_REGS->ETH_CTRLB |= ETH_CTRLB_GMIIEN(1);
```

Notice that you can use bitwise OR (`|`) and bitwise AND (`&`) to perform read-modify-write operations
on registers. Also notice here that the `GMIIEN` field is only a single bit. Because of this, we can
also use the mask to set the field.

```c
ETH_REGS->ETH_CTRLB |= ETH_CTRLB_GMIIEN_Msk;
```

Some fields have extra macros that indicate the meanings of the field values. These are useful for
making your code more readable versus simply providing a number. There is no explicit rule for when
these sorts of macros are available, but if the description of the field in the datasheet has a table
to explain its values then there is a good chance these extra macros will be present.

Here is what those macros look like for setting the oversampling mode of an ADC peripheral. There are
two sets of them: one that you can use with the function-like value macro and the other you can use
on its own.

```c
#define ADC_FLTCTRL_OVRSAM_Msk                  (0x00000007ul)   /* Oversampling Ratio */
#define ADC_FLTCTRL_OVRSAM_Pos                  (0ul)
#define ADC_FLTCTRL_OVRSAM(v)                   (ADC_FLTCTRL_OVRSAM_Msk & ((uint32_t)(v) << ADC_FLTCTRL_OVRSAM_Pos))
#define     ADC_FLTCTRL_OVRSAM_4_SAMPLES_Val    (0x0ul)
#define     ADC_FLTCTRL_OVRSAM_16_SAMPLES_Val   (0x1ul)
#define     ADC_FLTCTRL_OVRSAM_64_SAMPLES_Val   (0x2ul)
#define     ADC_FLTCTRL_OVRSAM_256_SAMPLES_Val  (0x3ul)
#define     ADC_FLTCTRL_OVRSAM_2_SAMPLES_Val    (0x4ul)
#define     ADC_FLTCTRL_OVRSAM_8_SAMPLES_Val    (0x5ul)
#define     ADC_FLTCTRL_OVRSAM_32_SAMPLES_Val   (0x6ul)
#define     ADC_FLTCTRL_OVRSAM_128_SAMPLES_Val  (0x7ul)
#define ADC_FLTCTRL_OVRSAM_4_SAMPLES            (ADC_FLTCTRL_OVRSAM_4_SAMPLES_Val << ADC_FLTCTRL_OVRSAM_Pos)
#define ADC_FLTCTRL_OVRSAM_16_SAMPLES           (ADC_FLTCTRL_OVRSAM_16_SAMPLES_Val << ADC_FLTCTRL_OVRSAM_Pos)
#define ADC_FLTCTRL_OVRSAM_64_SAMPLES           (ADC_FLTCTRL_OVRSAM_64_SAMPLES_Val << ADC_FLTCTRL_OVRSAM_Pos)
#define ADC_FLTCTRL_OVRSAM_256_SAMPLES          (ADC_FLTCTRL_OVRSAM_256_SAMPLES_Val << ADC_FLTCTRL_OVRSAM_Pos)
#define ADC_FLTCTRL_OVRSAM_2_SAMPLES            (ADC_FLTCTRL_OVRSAM_2_SAMPLES_Val << ADC_FLTCTRL_OVRSAM_Pos)
#define ADC_FLTCTRL_OVRSAM_8_SAMPLES            (ADC_FLTCTRL_OVRSAM_8_SAMPLES_Val << ADC_FLTCTRL_OVRSAM_Pos)
#define ADC_FLTCTRL_OVRSAM_32_SAMPLES           (ADC_FLTCTRL_OVRSAM_32_SAMPLES_Val << ADC_FLTCTRL_OVRSAM_Pos)
#define ADC_FLTCTRL_OVRSAM_128_SAMPLES          (ADC_FLTCTRL_OVRSAM_128_SAMPLES_Val << ADC_FLTCTRL_OVRSAM_Pos)
```

In most cases, it is probably easier to use the second set. Here are a couple of examples to show how
you could use these.

```c
// First clear CTRLA.MODE to remove the old value.
ADC0_REGS->ADC_FLTCTRL &= ~(ADC_FLTCTRL_OVRSAM_Msk);

// Set the new value like this
ADC0_REGS->ADC_FLTCTRL |= ADC_FLTCTRL_OVERSAM(ADC_FLTCTRL_OVRSAM_128_SAMPLES_Val);
// OR like this
ADC0_REGS->ADC_FLTCTRL |= DC_FLTCTRL_OVRSAM_128_SAMPLES;
```

### Additional Helpful Macros
CMSIS provides a couple of useful macros for setting and getting fields from registers. These are the
`_FLD2VAL(field, value)` and `_VAL2FLD(field, value)` function-like macros. Both macros take a field
name and a value. `_FLD2VAL()` is used to extract a field from a register and `_VAL2FLD()` is used
to set a field.

`_FLD2VAL()` is probably the more useful one. To use it, give it the name of the field you want and
the name of the register or variable to extract it from. For example, if you want to get the oversample
mode of the ADC we set above, you can do this.

```c
uint32_t ovrsmp = _FLD2VAL(ADC_FLTCTRL_OVRSAM, ADC0_REGS->ADC_FLTCTRL);
```

This macro applies the given field's `_Msk` and `_Pos` macros to mask and shift down the field for you.

`_VAL2FLD()` is a lot like the function-like macros each field has that you saw above. This is useful
when working with system register definitions provided by CMSIS because those provide only the `_Msk`
and `_Pos` macros. For example, if you wanted to access memory region 7 in the Memory Protection Unit,
you could do the following.

```c
// Clear the REGION field.
MPU->RNR &= MPU_RNR_REGION_Msk;
// Set the new REGION value.
MPU->RNR |= _VAL2_FLD(MPU_RNR_REGION, 7);
```


## Configuration Registers (Fuses)
Many devices have configuration registers that are programmed into a special area of flash when the
device is programmed with a programming tool. These registers contain things like default values for
flash operation registers, security options for devices that have security features, and stuff to
force the watchdog to stay on and set the watchdog time. These are also called "fuses" since they are
a reprogrammable version of old device configurations that were set permanently by actually blowing
fuses built into the device. Accessing these registers is similar to accessing peripheral registers,
but not quite the same.

```{note}
If you have used Microchip's XC32 toolchain, you may have seen that it defines configuration fuses
using #pragmas. This syntax is unique to Microchip and is not supported on Clang or normal GCC.
```

### Fuses in C and C++ Files
For C and C++ files, you set the values of these registers by defining specially-named variables once
somewhere in your project sources. The device-specific header files contain C `extern` declarations
for these registers. These, with the help of the device-specific linker scripts, will put your variables
into the correct memory locations for you. In your C or C++ source file of choice, include the
device-specific file (or `which_pic32.h`) and define your config fuses as a `const uint32_t` with 
names following the format `CFG_FUSES_{group}_{register}`.

Group names will be things like `BOOTCFG` or `USERCFG`. Some devices have two of each programmable
group because their config flash is remappable. In those cases, you would have `BOOTCFG1`, `BOOTCFG2`,
`USERCFG1`, and `USERCFG2`. The datasheet for your device will help you figure out the names of the
groups, the registers within those sections, and the allowed values you can put in those registers.
Clang does not know anything about fuses and so cannot stop you from putting invalid values in them.

Setting the values for your fuses can be done just like with normal peripheral registers, except that
you can set them only once. You can set them to literal numeric values or you can use value, `_Pos`,
and `_Msk` field macros like you use with peripheral register [fields](#register-field-macros). Here,
the `{perpiheral}` is `FUSES` and there is no `{mode}`. The fuse group names, like `BOOTCFG`, are 
not included in the field macro names. This is because doing so would be redundant, especially for
devices that have two remappable fuse regions.

Here is an example that sets the `FUCFG0` register in the `USERCFG1` section. This is a register used
on the PIC32CZ CA devices that is used to configure the Watchdog timer.

```c
const uint32_t CFG_FUSES_USERCFG1_FUCFG0 = (FUSES_FUCFG0_WDT_ENABLE(0) |
                                            FUSES_FUCFG0_WDT_WEN(0) |
                                            FUSES_FUCFG0_WDT_RUNSTDBY(0) |
                                            FUSES_FUCFG0_WDT_ALWAYSON(0) |
                                            FUSES_FUCFG0_WDT_PER(0) |
                                            FUSES_FUCFG0_WDT_WINDOW(0) |
                                            FUSES_FUCFG0_WDT_EWOFFSET(0));
```

Notice that the group `USERCFG1` is present in the variable name on the left but not in the field
macros used on the right. Some of these are single-bit fields and so you could also use the `_Msk`
version of the field macro to set that.

Some registers are pre-programmed with info and cannot be modified. You do not need to define variables
for these ones, though doing so can be useful for accessing the data in them. The group names for
these will be probably be something like `CALOTP` to indicate they are programmed only once ever.

### Fuses in Assembly Files
```{caution}
This is not yet tested! The instructions here should help, but may not fully work.
```

If you want to put your fuses in an assembly file, you need to use the `.section` directive to tell
the assembler where they go. The section name to use is `.fuses_{group}_{register}`, all in lower-case.
Inside the section, all you need is a single `.word` directive to provide the 32-bit value to use for
the register.

Here is the same example as the above C version, but in assembler.

```
.section .fuses_usercfg1_fucfg0
    .word 0x00
```

That example is not particularly interesting because we just set it to zero. There is not enough
room on this page to use the above macros, so here is another example that sets the PIC32CZ CA
`FSEQ` register instead.

```
.section .fuses_usercfg1_fseq
    .word FUSES_FSEQ_SEQNUM(0x01) | FUSES_FSEQ_SEQBAR(0xFFFE)
```


## Special and Control Registers
TODO
Things you would access using CMSIS function or macros.


## Interrupts (ARM MCUs)
TODO


## Interrupts (ARM MPUs)
TODO


## Peripheral IDs
TODO


## Device Information Macros
The PIC32 macros in the config files and maybe some of the ACLE macros for architecture.

## Other Useful Macros
Things like the _BASE and _ADDR macros in the header files.
