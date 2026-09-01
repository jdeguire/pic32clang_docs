% Copyright (c) 2026, Jesse DeGuire
% All rights reserved.
% Licensed using a BSD 3-clause license, see LICENSE at the root of this project.
% Find this project on GitHub at https://github.com/jdeguire/mchpclang_docs.

# Using Device Features

This chapter will provide examples showing how to access device-specific features like peripheral
registers or interrupts. You will want to consult the datasheet for your device for additional
information on the feature you are trying to use.

This documentation will focus mostly on accessing features from C and C++ code because that is most
likely how they will be used. Accessing features from assembly is possible, but generaly more limited
to using macros to form the addresses you need to access registers and stuff like that.


## A Word of Caution
The datasheet can help you determine how to access device features, but you might need to do a bit
of device header delving on occasion. In my experience, you will have a pretty easy time mapping things
like register and bitfield names in the datasheet into the correct names in code. Interrupt vector
names, however, do not always match what the documentation for the peripheral says. This limitation
applies to Microchip's own toolchains as well, but it is worth mentioning here.

The device-specific header files are located in the toolchain install location under the `arm/include/proc`
subdirectory. When you supply Clang with a device-specific config file, it tells Clang to look for
headers in this directory. If you have a text editor or IDE that can query the compiler for its include
directories, like Visual Studio Code, then you should provide it with the `--config` option you supply
to Clang (see [here](compiling_and_linking.md#device-config-files)). That way, any auto-complete features
the editor has can help you fill in the register or interrupt names you need.

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
`which_device.h` header and that will figure out which device-specific header you need. For this to
work, you need to supply Clang with the proper `--config` file option for your device.

If you are working on a project that you want to build both with Clang and Microchip's XC32 compiler,
then you can use this snippet to select the correct file.

```c
#ifdef __clang__
#  include <which_device.h>
#else
#  include <xc.h>
#endif
```


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
All instances have macros you can use to get their base addresses. The format of these macros is
`{instance}_REGS_BASE`. Here are a couple of examples. 

```c
// The base address of the SERCOM0 registers.
SERCOM0_REGS_BASE
// The base address of the TCC4 registers.
TCC4_REGS_BASE
```
These macros evaluate to the absolute address of the start of the peripheral's registers as an
`unsigned long`.

To access a specific register within a peripheral, you can get its offset from the base address with
a macro of the form `{peripheral}_{register}_OFFSET`. If you wanted the address of the `TOCV`
register of the CAN1 instance, you would use 

```c
CAN1_REGS_BASE + CAN_TOCV_OFFSET
```

Notice that the offset macro uses the *peripheral* name "CAN" and not the *instance* name "CAN1".
This is because the registers are the same for each instance of a peripheral and so having each
perpiheral-specific macro use the instance would just be redundant.

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
C struct or union you can reference. The name of the type is `{peripheral}_registers_t` in all
lower-case. The type definitions are provided by peripheral-specific header files. The macros are 
formatted as `{instance}_REGS` and evaluate to a `volatile` pointer to the peripheral type located
at the instance's base address. The data types mimic the layout of the instance's registers in memory.
You can think of these macros as "overlaying" the struct on top of the memeory locations the instance's
registers occupy.

For most peripherals, the type is a struct whose members correspond to the registers in the device.
The format is `{peripheral}_{register}`. For example, if you wanted to wait for the `SYNCBUSY` register
in the TCC5 instance to clear, then you would use 

```c
while(TCC5_REGS->TCC_SYNCBUSY)
{ 
    /* Wait for sync to complete */
}
```

It does seem redundant to have the peripheral name present in the register name, but this was done
to maintain some compatibility with Microchip's XC32 toolchain.

These struct macros can be used only in C and C++.

(peripheral-modes)=
#### Peripheral Modes
Some peripherals can operate in different "modes". A common example is the SERCOM peripheral, which
can act as a I2C Master or Slave, a SPI Master or Slave, or a USART.

In periphreals with modes, the peripheral type is a union rather than a struct. Its members refer to
the possible modes the peripheral can be in. Those members are themselves structs that contain the
registers. Usually, all registers are accessed through a mode even if the register is not specific to a
particular mode. For example, to access the `STATUS` register in SERCOM8, you need to decide the mode
you intend to use the instance in first. If you want to use it in SPI Master mode, then you could
access the register with 

```c
uint32_t status = SERCOM8_REGS->SPIM.SERCOM_STATUS;
```

#### Register Groups
Some peripherals will groups sets of registers together because the peripheral is used to handle a
set of subperipherals. For example, a DMA peripheral might have some registers to control the DMA
module as a whole, but then have register groups to control DMA channels independently.

Cases like these are sort of a cross of the normal case and the above "modes" case. Registers that
control the peripheral as a whole are accessed like normal. Registers that control peripheral channels
or subperipherals are accessed through a group. Here are a couple of examples using the DMA
peripheral. The `CTRLA` register is a member of the overall DMA peripheral rather than existing
per-channel. Each channel, however, has its own transfer start address set by its `CHSSA` register.


```c
// CTRLA applies to the DMA peripheral as a whole.
DMA_REGS->DMA_CTRLA |= 0x01;
// Set the transfer start address for channel 2. Each channel has its own CHSSA.
DMA_REGS->CHANNEL[2].DMA_CHSSA = start_addr;
```

As a special case for this special case, some devices have a single PORT peripheral with no registers
at the top level and all of under groups. Each group corresponds to a port letter. So group 0 is for
the `PAx` pins, group 1 for the `PBx` pins, and so on. To toggle `PDx` pins with the `OUTTGL` register,
you would use 

```c
PORT_REGS->GROUP[3].PORT_OUTTGL = 0xA5;
```

#### DMA Descriptor Structs
Peripherals that can access memory, such as the DMA or SQI peripherals, provide additional structs
for the descriptors the peripheral looks for in memory. You do not have to use these if you are using
the in-memory descriptors, but are there for convenience. Unfortunately, not all peripherals that
use descriptor structures provide these for some reason. In particular, the ETH peripheral for Ethernet
uses descriptors to read and write packet data, but no structures are provided for this.

### Array Access to Peripheral Instances
The instance macros above work if you want to hardcode the peripheral to access at compile time.
However, it may be useful to be able to access peripheral instances from an array. This is handy for
writing reusable code such as for a C++ class. In such a case, you might want to supply the instance
number through the class's constructor.

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

This feature is NOT present in Microchip's XC32 and so you should not use it if you want to maintain
some compatibility with their toolchain.


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

This is a lot to take in, so here are a couple of examples taken directly from some peripheral headers.
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

In most cases, it is probably easier to use the second set. Here is an example to show how you could
use these.

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
name and a value. `_FLD2VAL()` is used to extract a field from a register and `_VAL2FLD()` is used to
set a field.

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
device-specific file (or `which_device.h`) and define your config fuses as a `const uint32_t` with 
names following the format `FUSES_{group}_{register}`.

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
const uint32_t FUSES_USERCFG1_FUCFG0 = (FUSES_FUCFG0_WDT_ENABLE(0) |
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

Your assembly source file needs to use the C preprocessor. Clang will do that for you if you give
your file a capital "S" extension (`.S`).


## Special and Control Registers
CMSIS provides its own set of types and macros for accessing core peripherals on M-profile devices.
These peripherals include the SysTick interval timer, the Memory Protection Unit, and FPU control
registers. These core peripherals are accessed similarly to device peripherals as described above.
To learn more about the core peripherals your device has, you should look through the ARM Technical
Reference Manual for the CPU in your device. For example, a PIC32CZ CA80 has a Cortex-M7 CPU and so
you would want the Cortex-M7 Technical Reference Manual. That in turn may point you to other documentation,
such as an Architecture Reference Manual based on the CPUs architecture (such as ARMv7-M).

If you want to dig around, you can look inside the `CMSIS/Core/Include` found in the toolchain install
location. There you will find header files for supported CPUs that contain the types and macros for
the different peripherals. The appropriate header is already included in the device-specific header
file, so you do not have to do that.

You can also consult the online CMSIS documentation for more info. This link will go to a page that
describes how to access core peripheral registers in code: <https://arm-software.github.io/CMSIS_6/latest/Core/regMap_pg.html>.

```{important}
Remember that CMSIS supports only Cortex-M devices and Cortex-A devices that use ARMv7-A. This
toolchain provides some CMSIS-like functionality for ARMv4 through ARMv6 devices. You can find those
files in `arm/include/arm_legacy`.
```


## Interrupts for ARM Microcontrollers
The ARM microcontroller (Cortex-M) devices provide special handling of interrupts and faults that
require less work from us as developers.

```{note}
Interrupts and faults are both classes of hardware exceptions, so you may see "exception" used to
refer to either of those. To avoid confusion with the C++ error handling mechanism of the same names,
this document will mainly use "interrupts" to refer to these events.
```

Whenever an interrupt or fault handler is entered, the CPU automatically puts registers R0-R3, R12,
and R14 (LR) on the stack and updates the stack pointer. It also stacks the address to which the
interrupt will return (ie. the value of the program counter when the interrupt occurred) and the
program status register `xPSR`. LR will then contain a special sentinel value that tells the CPU to
unstack those value to return from an interrupt. The CPU can even handle FPU registers by allocating
stack space for them and lazily stacking the FPU registers only if the FPU is used in the interrupt.
This means that an interrupt or fault handler can look just like a normal C function without extra
compiler-specific attributes. The M-Profile devices do not have a "return from interrupt" instruction
because the special LR value handles that.

You can read more about how this works in the Technical Reference Manual for your CPU, but this section
will focus on how to add handlers to your code.

If you want to globally enable or disable interrupts, you can use the `__enable_irq()` and `__disable_irq()`
CMSIS functions to do this. These do not affect fault interrupts.

### Interrupt Vectors
Each device-specific header file contains an enum typedef called `IRQn_Type`. Each member's name is
formatted as `{irq_name}_IRQn`. Each member's value is its interrupt request number. Numbers less than
0 are reserved for CPU interrupts: the reset interrupt, fault handlers, the SysTick handler, and so on.
Zero and positive numbers are for device-specific peripherals or instances.

You will need to figure out the name of the interrupt you want to configure. The peripheral documentation
in your device's datasheet can be helpful--look for a section titled "Interrupts" or "Nested Vectored
Interrupt Controller"--though sometimes you just have to take a look at the enum yourself. This is
particularly true for peripherals or instances that have multiple interrupt vectors. The CPU vector
names can be found in the Architecture Reference Manual for your device.

Once you have your name, you can configure the interrupt using some function provided by CMSIS. The
CMSIS functions you want to use are prefixed with `NVIC_`. This will describe only a few of them;
the CMSIS code and docs can show you more. You can control whether or not your interrupt is enabled
with `NVIC_EnableIRQ(IRQn_Type irq)` and `NVIC_DisableIRQ(IRQn_Type irq)`. To clear the "pending" flag
for an interrupt, use `NVIC_ClearPendingIRQ(IRQn_Type irq)`. You normally do NOT need to do this in
your handler, but it is good practice to clear the pending flag when you are first setting up an
interrupt so that you do not unexpectedly enter your handler. Finally, to set the priority level for
your interrupt, use `NVIC_SetPriority(IRQn_Type irq, uint32_t prio)`. For Cortex-M devices, *lower*
numbers mean *higher* priority, so 0 is the highest priority you can use. The lowest priority is
configurable by whoever made your device. The device-specific headers have the `__NVIC_PRIO_BITS`
macro to tell you how many bits the priority can use. For example, if `__NVIC_PRIO_BITS` is 3 then
the lowest priority level is 7.

Here is an example of setting up the NVIC for your interrupt. Suppose you want to configure an interrupt
for receiving UART data on SERCOM4. After some digging in the datasheet for your device and the device
header file, suppose that the IRQ you want to configure is called `SERCOM4_2` (names like these are
unfortunately real and why you have to do some digging). You can configure the interrupt controller
using the following.

```c
// Clear and enable the global SERCOM4_2 interrupt. We found in the datasheet that SERCOMx_2
// is the "Rx Complete" interrupt. This is used on the PIC32CZ CA80.
NVIC_ClearPendingIRQ(SERCOM4_2_IRQn);
NVIC_SetPriority(SERCOM4_2_IRQn, 5);        // Remember that higher numbers are lower priority.
NVIC_EnableIRQ(SERCOM4_2_IRQn);
```

Chances are that you will also need to access the peripheral instance registers to perform additional
setup to make the interrupt you want work. Refer to the peripheral documentation in the device datasheet
for more info on that.

### Interrupt Handlers
We need to provide a handler function that is referenced by the interrupt controller's interrupt
vector table, or IVT. The vector table is defined in the device's startup code that gets linked in
when you build an app. If you want to see what that is like, you can find the startup code (and linker
script) for your device in the toolchain install location under  `arm/proc/{procname}`.

By default, most interrupts will jump to a dummy handler that spins in a while loop forever. To
provide your own handler, simply define a function in your application with the signature
`void {irq_name}_Handler(void)`. This uses the same name that is used in the `IRQn_Type` enum described
above. If you define the function in a C++ file, you **must** declare your interrupt handler as `extern "C"`.
You do not need to call `NVIC_ClearPendingIRQ()` in your handler, but you may need to clear interrupt
flags set in the peripheral registers for whichever instance you are providing a handler for.

We can continue our SERCOM4 example from above by providing a handler for our Rx Complete interrupt.

```c++
// Remember to include this extern "C" if this is in a C++ file!
extern "C" void SERCOM4_2_Handler(void)
{
    // We do not need to clear the flag in the NVIC, but this SERCOM peripheral does have its own
    // flags to clear. The PIC32CZ this example is based on has a quirk that requires us to clear
    // the flags then read them back. Check the datasheet for your device to see what you need to do.
    SERCOM4_REGS->USART_INT.SERCOM_INTFLAG = SERCOM_USART_INT_INTFLAG_RXC_Msk;
    SERCOM4_REGS->USART_INT.SERCOM_INTFLAG;

    ReceiveTheData();
}
```

The startup code is set up so that any handler you provide will override any handler it provides,
so defining the function is all you have to do.

One handler you will certainly want in your application is the HardFault handler. This is the last
stop for catching faults before the CPU locks up and has to be reset. You can use it as a "catch-all"
handler or you can provide handlers for the other faults as well. Those are `MemoryManagement`, 
`UsageFault`, and `BusFault` handlers.

```c++
// Remember to include this extern "C" if this is in a C++ file!
extern "C" void HardFault_Handler(void)
{
    // Here are some system registers you can use to get more info about the fault that brought you
    // here. See the Architecture Reference Manual for your device for more info on these.
    uint32_t cfsr  = SCB->CFSR;         // Configurable Fault Status Register
    uint32_t hfsr  = SCB->HFSR;         // Hard Fault Status Register 
    uint32_t mmfar = SCB->MMFAR;        // MemoryMagagement Fault Address Register
    uint32_t bfar  = SCB->BFAR;         // BusFault Address Register

#ifdef __DEBUG
    __BKPT();                           // breakpoint instruction
#endif

    while(1)
    {}
}
```

If you provide implementations for the other fault handlers, then you need to enable them using the
`SHCSR` system register. This snippet will enable all three handlers.

```c++
    SCB->SHCSR |= (SCB_SHCSR_BUSFAULTENA_Msk 
                    | SCB_SHCSR_USGFAULTENA_Msk
                    | SCB_SHCSR_MEMFAULTENA_Msk);
```

There are two additional handlers you might want to override in your code: the `Default_Handler()`
and the `Reserved_Handler()`. The default implementations for both simply spin in a loop forver.
The Default Handler is the handler used when you have not provided your own, so you can define your
own if you appear to have an interrupt that is entering the Default Handler. The Reserved Handler
fills in spots in the IVT that are not used at all. It would be very strange for you app to enter a
reserved space, but you can provide your own handler to handle this case if you want.

```{admonition} Implementation Detail
:class: note
If you look at the startup code, you will see each interrupt handler is by default an alias to a stub
function that jumps to the Default Handler. Testing indicated that this indirection was needed to let
you override the Default Handler like any other handler. This presumably is related to how the
`alias` attribute works.
```


## Interrupts for ARM Microprocessors
ARM microprocessor devices have an interrupt mechanism that is very differnt from the microcontrollers.
They have a fixed vector table with only eight entries, one of which is unused. This vector table is
located at address 0x00 by default but may be movable depending on the ARM CPU in your device.

If you are wondering how all possible interrupt sources in a device can be handled by only 7 handlers,
the [Peripheral Interrupts](#peripheral-interrupts) section below will explain that. This introduction
will be a brief overview of how the ARM MPU interrupt handling system works.

```
Offset | Description                    | C Function Name
-------------------------------------------------------------------
0x00   | Reset Handler                  | void Reset_Handler(void)
0x04   | Undefined Instruction Handler  | void Undef_Handler(void)
0x08   | SVC/SWI Handler                | void SVC_Handler(void)
0x0C   | Prefetch Abort Handler         | void PAbt_Handler(void)
0x10   | Data Abort Handler             | void DAbt_Handler(void)
0x14   | Unused (see note below)        | 
0x18   | IRQ Handler                    | void IRQ_Handler(void)
0x1C   | FIQ Handler                    | void FIQ_Handler(void)
```

The startup code puts the program size at 0x14 since it is otherwise unused by the CPU. This can be
useful for bootloaders that read the vector table to determine how much data needs to be loaded.
Newer Arm devices with Virtualization Extensions use this for certain hypervisor operations, but no
Microchip devices support this extension.

Some of the CPU registers are banked depending on the processor's current "mode". The base set of
registers is used in both "User" and "System" modes. The System mode allows more access to system
control registers and so is considered a "privileged" mode. This is the mode the startup code will
use upon entering `main()`. When one of the interrupt handlers is entered, the processor switches
R13 (stack pointer) and R14 (link register) to the banked version for that mode. The stack pointer
in all modes is initialized by the startup code and the link register contains the address to which
to return when the interrupt finishes. In addition, these interrupt modes can access a new register
called SPSR. This is the Saved Program Status Register and is the value of CPSR when the interrupt
was entered. The FIQ ("Fast Interrupt Request") mode additionally banks R8-12.

If you want to globally enable or disable interrupts, you can use the `__enable_irq()` and `__disable_irq()`
CMSIS functions to do this. These do not affect FIQ or fault interrupts. These are included in the
CMSIS-like functions provided by mchpClang for older ARM devices.

### System Interrupts
This section will refer to the first five handlers in the vector table as the "system interrupts".
The startup code provides a `Reset_Handler` that should be useful to most applications. If you want
to see what that is like, you can find the startup code (and linker script) for your device in the
toolchain install location under  `arm/proc/{procname}`.

The startup code also provides dummy functions for the others. The dummy functions will simply spin
in a loop forever, so you will want to provide your own. To do that, implement functions with the
names shown in the above table in your project and they will override the handlers provided in the
startup code. If you are building in C++ mode, then you will need to declare your functions with
`extern "C"`.

ARM MPUs have a system control coprocessor called CP15 that, among many other things, provides
information that may help you in troubleshooting a fault. Here is an example of a handler that reads
a few of those CP15 registers. You will want to look in the reference manual for you CPU to see
what these registers contain on your device.

```c++
// Remember to include this extern "C" if this is in a C++ file!
extern "C" void __attribute__((noreturn)) DAbt_Handler(void)
{
    uint32_t dfsr = __get_DFSR();       // Data Fault Status Register
    uint32_t ifsr = __get_IFSR();       // Instruction Fault Status Register
    uint32_t dfar = __get_DFAR();       // Data Fault Address Register

#ifdef __DEBUG
    __BKPT();
#endif

    printf("DAbt_Handler: DFSR=0x%08X, IFSR=0x%08X, DFAR=0x%08X\n", dfsr, ifsr, dfar);

    while(1)
    {}
}
```

If you plan on returning from any of these interrupt handlers, then you should apply the `interrupt`
attribute to them so that the compiler knows to save and restore register state and use the correct
return sequence. The attribute takes an optional argument telling it was kind of interrupt is being
handled: “IRQ”, “FIQ”, “SWI”, “ABORT”, or “UNDEF”.

If you want to read additional registers, such as the link register to determine where the fault
occurred, then you will need a bit of assembly code to do it. Something like this should work.

```c
#define read_link_reg(lr)   __asm__ volatile("mov %0, lr" : "=r" (lr))
```

Note that this will read the current bank of registers. This is useful for the link register, but
you will need to go through extra work to read the registers from the previous mode. You can either
explicitly check and set the mode using the `__get_mode()` and `__set_mode()` macros or use an assembly
snippet with one of the `STM` instruction variants. If the last character in the instruction is `^`,
then the instruction will store User mode registers regardless of the current mode (remember that
User and System modes use the same base set of registers).  The `__set_mode()` macro sets the
low 8 bits of the CPSR register, which covers the 5-bit Mode field and the `I`, `F`, and `T` flags,
so be sure to configure those, too.

### Peripheral Interrupts
Peripheral interrupts from things like UARTs are handled by a separate interrupt controller outside
of the CPU. When an interrupt request comes from a peripheral, the external interrupt controller
will assert either the IRQ or FIQ interrupt line depending on how you have configured it. It is
then up to your `IRQ_Handler()` or `FIQ_Handler()` to determine which interrupt needs handling and
jump to the correct handler.

As of this writing, Microchip devices one of two possible external interrupt controllers: the Advanced
Interrupt Controller (AIC) that was developed by Atmel (Microchip bought Atmel in 2016) or the
Generic Interrupt Controller (GIC) that was developed by Arm.

#### Advaned Interrupt Controller
You will want to consult the datasheet for your device for more information, but here is a quick
overview of how you would configure a single interrupt on a device with the AIC. This will use the
Periodic Interval Timer (PIT) on the SAM9X75 as an example. This is basically a free running timer
peripheral and is very simple.

First, we need to create a handler for our PIT interrupt. This can have any name and can look like a
normal function. It does not take any arguments nor return any parameters.

```c++
static void IntervalTimerInterruptHandler(void)
{
    // Update our timer in here.
}
```

It does not matter if we declare this `extern "C"` in a C++ file. We also do not have to access the
AIC from within here. You would of course need to clear any peripheral-specific flags if needed, but
the PIT does not have any.

Next, let's configure the AIC to tell it about our handler. Rather than having a set of configuration
registers for each interrupt source, you instead set the `AIC_SSR` register to tell it what interrupt
you need to configure and any accesses to the configuration registers will apply to that interrupt.
Like with the microcontrollers, the device-specific header files each contain an enum typedef called
`IRQn_Type`. Each member's name is formatted as `{irq_name}_IRQn` and the value is the interrupt
number for that request. You can supply this value to the `AIC_SSR` register for convenience.

```c++
static void ConfigurePITInterrupt(void)
{
    // Tell the AIC which interrupt we are configuring.
    AIC_REGS->AIC_SSR = PIT_IRQn;

    // Use level sensitive mode (which may be the only option for "internal" interrupts) and a
    // middle priority. This controller uses higher numbers for higher priority, with 7 as the max.
    // Notice that is the opposite of the micrcontrollers, which use lower numbers for higher priority.
    AIC_REGS->AIC_SMR = (AIC_SMR_SRCTYPE_INT_LEVEL_SENSITIVE |
                         AIC_SMR_PRIOR(3));

    // Provide the AIC our handler function. The AIC presents this as the vector to use in its IVR
    // register when an interrupt occurs. Later in this example, we will create our IRQ_Handler()
    // function to jump to this handler when the interrupt triggers.
    AIC_REGS->AIC_SVR = uint32_t(IntervalTimerInterruptHandler);

    // Clear the interrupt flag before enabling it. This normally does NOT need to be done in the
    // interrupt handler because reading or writing AIC_IVR does this. Your device datasheet might
    // have info regarding a "Protected Mode" for the AIC. Have a look at that; this example assumes
    // that is disabled.
    AIC_REGS->AIC_ICCR = AIC_ICCR_INTCLR_Msk;

    // Enable this interrupt source.
    AIC_REGS->AIC_IECR = AIC_IECR_INTEN_Msk;
}
```

To add more interrupt handlers, just repeat these first two steps for each perpiheral interrupt source.

Now we can supply our `IRQ_Handler()` that will run whenever the AIC says we have a new interrupt
request to handle. The AIC does allow you to specify some interrupts as FIQ interrupts instead, but
this example will not do that to keep things simple. Clang provides the `interrupt` and `interrupt_save_fp`
attributes to tell it that a function is an interrupt handler. The compiler will take care of setting
up the stack, using the correct return sequence, and saving the proper registers. The former does not
save FPU registers and the latter does. The attribute takes an optional argument telling it what kind
of interrupt is being handled; we will use "IRQ" here but we could use "FIQ" for an FIQ handler.

```c++
// This 'extern "C"` is needed if this is in a C++ file!
extern "C" void __attribute__((interrupt("IRQ"))) IRQ_Handler(void)
{
    // The AIC is configured to give us the pointer to the handler in the AIC_IVR register, which
    // is the default.
    void (*handler_func)(void) = (void (*)(void))AIC_REGS->AIC_IVR;

    // If we had the AIC "Protected Mode" enabled, we'd want to write a dummy value back to AIC_IVR
    // here.

    // Call our handler.
    handler_func();

    // We have to tell the AIC when our interrupt is done. Do that with a dummy write to AIC_EOICR.
    AIC_REGS->AIC_EOICR = 0;
}
```

The last thing we need to do is provide the AIC with what is called a "Spurious Interrupt Handler".
If an interrupt source is asserted then de-asserted before we read the `AIC_IVR` register, then the
AIC will have the Spurious Interrupt Handler in that register instead.

```c++
static void SpuriousInterruptHandler(void)
{
    puts("Hit our spurious interrupt handler");
}

// Tell the AIC about our handler sometime during application initialization.
AIC_REGS->AIC_SPU = uint32_t(SpuriousInterruptHandler);
```

One thing you might realize is that this example is NOT the most optimal way to handle interrupts.
First, interrupt nesting will not work. You would need to add extra code to your `IRQ_Handler()` to
revert the processor mode back to User or System as well as save extra context. A lack of nesting
just means that even higher priority interrupts will wait until your current interrupt is done before
being executed. Whether you need this will depend on your application. Second, you may be able to get
extra performance by having your `IRQ_Handler()` branch to the handler function and leave each individual
handler to use the `interrupt` attribute. You would also need each handler to write to `AIC_EOICR` when
they are done. This does require more work on your part to remember to add those on every handler,
but you might also be able to use `interrupt_save_fp` only in handlers that need it.

#### Generic Interrupt Controller
You will want to consult the datasheet for your device for more info. The GIC is more complex than
the AIC because it supports things like virtualization, multiple cores, and security extensions.

Unfortunately, as of this writing I do not have a device with a GIC and so I cannot yet offer much
guidance in this document. Luckily, CMSIS has an implementation that you could copy into your project
and use. You can find the source under the toolchain install location at `CMSIS/Core/Source/irq_ctrl_gic.c`
and the header at `CMSIS/Core/include/a-profile/irq_ctrl.h`.

The GIC appears to supply only vector numbers, not handlers. The CMSIS code contains a table of
handlers that its `IRQ_Handler()` will use to index into its table. The last index in the table is
for the Spurious Interrupt Handler. Like with the AIC, this is supplied when an interrupt source
asserts and de-asserts before it can be read and handled.

If you do use the CMSIS code, you might need to modify its `IRQ_Handler()` to use the `interrupt`
attribute so that the compiler can properly set up a stack and save and restore registers. See the
`IRQ_Handler()` example above for the AIC for more info.
