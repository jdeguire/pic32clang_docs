% Copyright (c) 2026, Jesse DeGuire
% All rights reserved.
% Licensed using a BSD 3-clause license, see LICENSE at the root of this project.
% Find this project on GitHub at https://github.com/jdeguire/mchpclang_docs.

# Builtin Functions

This chapter describes some predefined functions and function-like macros you may find useful. This
is not a comprehensive list, so you would want to check out Clang and CMSIS documentation for more
info. You can also browse the CMSIS header files in the install location at `CMSIS/Core/Include`. If
you are using an older ARM chip, then this toolchain provides some CMSIS-like functionality in
`arm/include/arm_legacy`.


## Common Functions
CMSIS provides quite a few inline functions and function-like macros you can easily use in your code.
CMSIS (or legacy ARM support for older devices) is provided to you by simply including your processor
specific header or `<which_device.h>`.

Quite a few of these map directly to CPU instructions of the same name: `__NOP()`, `__BKPT()`, `__CLZ()`,
and the memory barrier instructions (explained more below). There are a few less-commonly used macros
for event handling, such as `__WFI()`, `__WFE()`, `__SEV()`. There are more macros for more instructions,
which you can find by browsing the compiler-specific header files in CMSIS.

Another pair of functions you will probably use often in your embedded developement are `__enable_irq()`
to enable interrupts and `__disable_irq()` to disable them. On newer ARM devices, these map directly
to the instructions for enable and disabling interrupts. On older ARM devices, these map to short
instruction sequeences to modify the CPSR register. If you want to check if interrupts are enabled
on microcontroller devices, you can check the memory-mapped PRIMASK register. If you want to check
on microprocessor devices, you need to check some bits in the CPSR register using the `__get_CPSR()`
function.

On some devices, particularly the microcontroller parts, the instruction used to disable interrupts
is "self-synchronizing", meaning that you do not need to put a memory barrier instruction after it.
Other devices, particularly older ones, might require you to do so. In that case, you would want to
use `__ISB()` (see below) right after you disable interrupts. The instruction used to enable interrupts
is never self-synchronizing, but that is presumably less important unless you really need to be sure
interrupts are enabled for the next instruction.

The other set of functions you will need are ones to handle interrupts. This is covered in more detail
[here](./using_device_features.md#interrupts-for-arm-microcontrollers) for microcontrollers and
[here](./using_device_features.md#interrupts-for-arm-microprocessors) for microprocessors. CMSIS
does provide a function for the microcontrollers to perform a system reset called `__NVIC_SystemReset()`.
You will need to consult your device's datasheet to learn how to perform a reset if you are using a
microprocessor device.


## Memory Barriers
Most ARM processors support three types of "memory barrier" instructions. These are instructions or
sequences that forces the CPU to apply some ordering to memory operations that occur before and after
the instruction. You use these instructions when you need to ensure that a memory access happens in
the order you expect it to. This is generally most important when you are accessing things that
affect the system as a whole, such as disabling interrupts, modifying certain system registers,
or doing cache operations. In those cases, functions provided by CMSIS (or mchpClang's legacy ARM
supoprt) will use the correct barriers for you.

Also provided is the `__COMPILER_BARRIER()` macro to tell the compiler to not reorder memory
access instructions past it. This macro evaluates to `asm volatile("":::"memory")`,
which is an expression supported in GCC and Clang.

- `__DMB()`: Data Memory Barrier  
This tells the processor to wait for all outstanding memory accesses to complete before allowing any
memory access instructions after this to run. This is sort of like the compiler barrier described above
in that the intent is to ensure the desired ordering of memory accesses. On newer ARM cores, this is
an explicit `dmb` instruction. On ARMv6, this writes to CP15 register 7. ARMv5 and older have no
equivalent and so this is the same as using the compiler barrier described above.
- `__DSB()`: Data Synchronization Barrier  
This is a more restrictive form of DMB in that this waits for all outstanding memory accesses to
complete before allowing *any* instruction after this to execute. Use this when your memory access
might have important side effects that need to propogate, particularly when modifying certain system
control registers. On newer ARM cores, this is an explicit `dsb` instruction. On ARMv6 and older, this
is called a "Drain Write Buffer" operation and writes to CP15 register 7.
- `__ISB()`: Instruction Synchroniztion Barrier  
This flushes the CPU pipeline and any instruction prefetch buffers in the CPU, causing instructions
following this to be re-fetched after this completes. This is useful for ensuring that upcoming
instructions "see" a new system state, such as changes in system control registers or cache state.
On newer ARM cores, this is an explicit `isb` instruction. On ARMv6, this is called a "Prefetch
Buffer Flush" and writes to CP15 register 7.  
On ARMv5 and older, this was called an "Instruction Memory Barrier" and is implementation-specific.
The implementation provided by mchpClang follows Section 2.7.4 in Part A of the ARMv5TE Reference
Manual, which says that a restricted form of IMB can simply be any instruction other than `b`, `bl`,
or `blx` that updates PC. This implementation therefore uses a dummy `ldr pc, ...` to update the PC
to one instruction ahead. You may need to do additional operations for a "full" IMB; see the Technical
Reference Manual for your CPU for more info.

These barrier function-like macros are implemented to also perform the equivalent of the compiler
barrier described above. If you need to perform both a data and instruction synchroniziation barrier,
then do the DSB first followed immediately by the ISB. This ensures that re-fetched instructions do
not "see" a stale device state.

You may want to do some extra reading to better understand when and how to use these. It's okay, *I*
also need to do some extra reading because it can be confusing at times. Searching for "arm memory
barrier" online yields some useful results from ARM's developer site, including a document titled
"ARM Cortex®-M Programming Guide to Memory Barrier Instructions". That document provides good info on
when and how to use these instructions.


## Cache Maintenance
CMSIS provides functions for handling caches on both the microcontroller and microprocessor devices,
though the function names differ for the two device sets.

Cache operations affect a whole line of cache. On the microcontrollers, this is fixed at 32 bytes.
On microprocessors, this varies and there is a register you can read to give you info about the cache.
Cache lines are always aligned to their width. For example, the lines on the microcontrollers will
always be aligned to 32-byte address boundaries.

While you can specify the cache line to operate on directly, you pretty much never need to do that.
Instead, you can provide the address you want to operate on and the cache logic will figure out the
line for you. The entire line of cache containing that address is affected. If that address is not
in the cache, then the operation does nothing.

Besides enabling or disabling the caches, there are two operations you will do with them: *clean*
and *invalidate*. A *clean* operation writes the contents of the cache line back to memory. If you
have a DMA peripheral that you wanted to read from a buffer in memory, then you would want to clean
all of the addresses that make up that buffer before starting the DMA operation. The DMA cannot see
into the cache and so you need to do this to prevent the peripheral from seeing stale data. Note that
if your buffer is really huge, then you might be better off just cleaning the whole cache. An
*invalidate* operation tells the cache that the line is no longer valid and thus should be re-read
from memory. Continuing our DMA example, you would want to do this before reading data from a buffer
that DMA has just written to. Otherwise, you will see stale cached data instead of what the DMA has
written.

Instruction caches are used only to hold previously-fetched instructions and so they are never written
to. Therefore, clean operations do not apply to them because there is not really anything to clean.

### Cache Functions for Microcontrollers
The startup code that runs before `main()` enables the caches for you on microcontroller parts.
These functions include the proper memory barrier instructions, so you do not need to handle that.
Microcontrollers have separate data and instruction caches, indicated here by "DCache" and "ICache",
respectively.

- `void SCB_EnableICache(void)`  
`void SCB_EnableDCache(void)`  
Enable the given cache.
- `void SCB_DisableICache(void)`  
`void SCB_DisableDCache(void)`  
Disable the given cache. The data cache is both cleaned and invalidated after it is disabled.
- `void SCB_InvalidateICache(void)`  
`void SCB_InvalidateDCache(void)`  
Invalidate the given cache.
- `void SCB_CleanDCache(void)`  
Clean the entire data cache.
- `void SCB_CleanInvalidateDCache(void)`  
Clean and invalidate the entire data cache.
- `void SCB_InvalidateICache_by_Addr(volatile void *addr, int32_t size)`  
`void SCB_InvalidateDCache_by_Addr(volatile void *addr, int32_t size)`  
`void SCB_CleanDCache_by_Addr(volatile void *addr, int32_t size)`  
`void SCB_CleanInvalidateDCache_by_Addr(volatile void *addr, int32_t size)`  
Perform the stated operation on a chunk of cache starting at the line containing `addr`. This function
will operate on a number of cache lines to cover the number of bytes given by `size`. If `addr` is
not 32-byte aligned or `size` is not a multiple of 32 bytes, then this will include more memory than
indicated since operations work on whole 32-byte cache lines.

### Cache Functions for Microprocessors
Most devices with caches use separate data and instruction caches. If your device has unified caches,
then use the data cache functions for it. The startup code does NOT enable caches for you, so you
will want to do that yourself, probably after you set up the MMU. These functions include the proper
memory barrier instructions, so you do not need to handle that.

The cache line size is depedent on your CPU type (Cortex-A7 vs ARM926, for exmaple) and might even
differ for the instruction and data caches. There are CP15 registers you can read to get more info
about your cache if you want something you can use at runtime. Use `__get_CACHETYPE()` on ARMv6 and
older devices or `__get_CCSIDR()` on newer devices. You will need to consult the Reference Manual
for you CPU to figure out how to use those registers. You might also be able to look up the info you
need online for your device.

- `void L1C_EnableCaches(void)`  
Enable all L1 caches.
- `void L1C_DisableCaches(void)`  
Disable all L1 caches.
- `void L1C_EnableBTAC(void)`  
Enable branch prediction if your CPU has it.
- `void L1C_DisableBTAC(void)`  
Disable branch prediction.
- `void L1C_InvalidateBTAC(void)`  
Invalidate the branch predictor cache.
- `void L1C_InvalidateICacheMVA(void *va)`  
Invalidate the instruction cache line containing the given virtual address.
- `void L1C_InvalidateICacheAll(void)`  
Invalidate the entire instruction cache.
- `void L1C_CleanDCacheMVA(void *va)`  
`void L1C_InvalidateDCacheMVA(void *va)`  
`void L1C_CleanInvalidateDCacheMVA(void *va)`  
Perform the given operation on the data cache line containing the given virtual address.
- `void L1C_CleanDCacheAll(void)`  
`void L1C_InvalidateDCacheAll(void)`  
`void L1C_CleanInvalidateDCacheAll(void)`  
Perform the given operation on the entire data cache.

If your device also has an L2 cache, then there are additional functions you can use to manipulate
that. They differ a bit from the above functions in the that L2 cache is unified--instructions and
data use the same cache. Here are the functions CMSIS makes available.

- `void L2C_Sync(void)`
- `int L2C_GetID(void)`
- `int L2C_GetType(void)`
- `void L2C_InvAllByWay(void)`
- `void L2C_CleanInvAllByWay(void)`
- `void L2C_Enable(void)`
- `void L2C_Disable(void)`
- `void L2C_InvPa(void *pa)`
- `void L2C_CleanPa(void *pa)`
- `void L2C_CleanInvPa(void *pa)`

Oddly enough, CMSIS as of this writing does not appear to provide a `L2C_CleanAllByWay()` function.
You might need to implement that yourself using one of the similar functions as a guide.


## System Control
CMSIS (and the legacy ARM support provided by mchpClang) provide functions for accessing system
control registers. These are implemented as static inline functions that usually map directly to
assembly instructions.

### Micorcontroller System Registers
Most system control functions are accessed through memory-mapped registers in the Private Peripheral
Bus space. This starts at memory address 0xE000_0000 and ends at 0xE00F_FFFF. CMSIS provides pointers
you can access register sets through, such as `SCB` for accessing registers in the System Control Block,
`SysTick` for accessing the SysTick timer, `FPU` for accessing FPU control registers, and `MPU` for
accessing the Memory Protection Unit. You access these like you would any other pointer-to-struct.

```c
SysTick->LOAD = 10000;
MPU->RNR = 0;
uint32_t cpuid = SCB->CPUID;
```

You should have a look at the Technical Reference Manual for your CPU to see what is available because
there are plenty of registers that vary by CPU type. You can also have a look at the CPU-specific
header (`core_cmN.h`) that is included through your device-specific header. If your device supports
the Cortex-M Security Extensions, then there will also be pointers ending in `_NS` such as `SCB_NS`
and `SysTick_NS` for non-secure access.

There are some registers that are accessed through instructions rather than the Private Peripheral
Bus. CMSIS provides static inline functions to access these. All of the "get" functions will return
`uint32_t` and all of the "set" functions take a `uint32_t` as its only argument. Here is a list of
some of those functions. They are formatted as `__get_REGNAME()` and `__set_REGNAME(val)`. This list
will not go explain what these registers do. Again, you should check the docs for your CPU or the
CPU-specific CMSIS header file to see what else is available for you.

- `__get_CONTROL()` / `__set_CONTROL(val)`
- `__get_IPSR()`
- `__get_APSR()`
- `__get_xPSR()` (yes, this has a lower-case `x`)
- `__get_PSP()` / `__set_PSP(val)`
- `__get_MSP()` / `__set_MSP(val)`
- `__get_PRIMASK()` / `__set_PRIMASK(val)`
- `__get_BASEPRI()` / `__set_BASEPRI(val)`
- `__get_FAULTMASK()` / `__set_FAULTMASK(val)`
- `__get_PSPLIM()` / `__set_PSPLIM(val)` (only for devices with CMSE)
- `__get_MSPLIM()` / `__set_MSPLIM(val)` (only for devices with CMSE)
- `__get_FPSCR()` / `__set_FPSCR(val)`  (only if an FPU is present)

If your CPU supports the Cortex-M Security Extensions, then some of these will have variants to
access non-secure versions of these registers. These are of the forms `__TZ_get_REGNAME_NS()` and
`__TZ_set_REGNAME_NS(val)`. This applies to registers that can be both written and read.

### Microprocessor System Registers
Most system control functions are accessed through coprocessor 15 on the microprocessor devices.
That is covered in the next section, but there are a few system registers that are available outside
it.

All of the "set" functions you will see here take a `uint32_t` as its only argument and all "get"
functions return a `uint32_t`.

The main one is the *Current Program Status Register* or CPSR. You can read this using `__get_CPSR()`
and write it using `__set_CPSR(val)`. If you want to read just the processor mode bits, whch are the
low 5 bits of CPSR, then you can use `__get_mode()`. You can also use `__set_mode(val)` to set the
processor mode, but be careful because this actually sets the low **8** bits of the CPSR register.
These are the `I`, `F`, and `T` flags and the 5 bits that make up the processor mode. This is because
`__set_mode()` outputs the `MSR cpsr_c` instruction, which updates the low byte of CPSR.

There is no set of functions to access SPSR, so you would need to make your own for that. You can
use the CPSR functions as a starting point.

If your device has an FPU, there are a few extra control registers you can access. The read-only
FPSID register is accessed with `__get_FPSID()`. You can access FPSCR with `__get_FPSCR()` and
`__set_FPSCR(val)` and FPEXC with `__get_FPEXC()` and `__set_FPEXC(val)`. The C startup code for the
microprocessors enables and initializes the FPU, if present, with `__FPU_Enable(void)`.

While not a system control register, you can use `__get_SP()` and `__set_SP(val)` to access the
current stack pointer register (R13). Each processor mode has its own banked stack pointer (the
"system" and "user" modes share the same register set), so these functions access the one for the
current mode. The C startup code for the microprocessors uses `__set_SP(val)` and `__set_mode(val)`
together to initialize the stacks for the different processors modes.

### CP15 Access
ARM microprocessors use coprocessor 15 (CP15) to act as the System Control coprocessor. This gives
you a way to control things like the caches, MMU, and TLB. It also provides information about the
CPU core. CP15 registers are read using the `MRC` instruction and written using the `MCR` instruction.
The instructions look like this.

```
MRC p15, Op1, Rt, CRn, CRm, Op2
MCR p15, Op1, Rs, CRn, CRm, Op2
```

Here, `Rt` is the target general-purpose register for reads and `Rs` is the source register for writes.
The other fields are used to select the CP15 register to access. `CRn` selects the category of CP15
registers. For example, `c0` is for CPU info and `c7` is for cache maintenance registers. The other
operands select the specific register variant within the category. In practice, `Op1` is almost always
zero.

Of course, not all CPUs will have all of these registers. You will need to consult the Technical
Reference Manual for your CPU to see what is actually avaialble. You also might notice some of the
registers overlap. This is because some registers have different meanings depending on what features
are available on your specific device. For example, some registers change meaning if your device has
a memory management unit (MMU) versus a memory protection unit (MPU).

This list has most, but not all, registers. Have a look at `arm/include/arm_legacy/arm_cp15.h` (older
devices) and `CMSIS/Core/include/a-profile/cmsis_cp15.h` (Cortex and newer devices) in the toolchain
install location to see the full set of functions you can use. Also, unless otherwise noted, "get"
functions return a `uint32_t` and take no arguments while "set" functions return nothing and take a
`uint32_t` argument.

```{list-table} CP15 Functions
:header-rows: 1
:widths: "auto"
*   - Read
    - Write
    - Op1, CRn, CRm, Op2
    - Description
*   - `__get_MAINID()`
    - N/A
    - 0, c0, c0, 0
    - Main ID Register
*   - `__get_CACHETYPE()`
    - N/A
    - 0, c0, c0, 1
    - Cache Type Register
*   - `__get_TCMSTATUS()`
    - N/A
    - 0, c0, c0, 2
    - TCM Status Register
*   - `__get_TLBTYPE()`
    - N/A
    - 0, c0, c0, 3
    - TLB Type Register
*   - `__get_MPUTYPE()`
    - N/A
    - 0, c0, c0, 4
    - Main ID Register
*   - `__get_MPIDR()`
    - N/A
    - 0, c0, c0, 5
    - Multiprocessor Affinity Register

*   - `__get_SCTLR()`
    - `__set_SCTLR(val)`
    - 0, c1, c0, 0
    - System Control Register
*   - `__get_ACTLR()`
    - `__set_ACTLR(val)`
    - 0, c1, c0, 1
    - Auxiliary Control Register
*   - `__get_CPACR()`
    - `__set_CPACR(val)`
    - 0, c1, c0, 2
    - Coprocess Access Control Register

*   - `__get_TTBR0()`
    - `__set_TTBR0(val)`
    - 0, c2, c0, 0
    - Translation Table Base Register 0
*   - `__get_TTBR1()`
    - `__set_TTBR1(val)`
    - 0, c2, c0, 1
    - Translation Table Base Register 1
*   - `__get_TTBCTRL()`
    - `__set_TTBCTRL(val)`
    - 0, c2, c0, 2
    - Translation Table Base Control Register
*   - `__get_MPUDCC()`
    - `__set_MPUDCC(val)`
    - 0, c2, c0, 0
    - MPU Data Cache Control Register
*   - `__get_MPUICC()`
    - `__set_MPUICC(val)`
    - 0, c2, c0, 1
    - MPU Instruction Cache Control Register

*   - `__get_DACR()`
    - `__set_DACR(val)`
    - 0, c3, c0, 0
    - Domain Access Control Register
*   - `__get_MPUWBC()`
    - `__set_MPUWBC(val)`
    - 0, c3, c0, 0
    - MPU Write Buffer Control Register

*   - `__get_DFSR()`
    - `__set_DFSR(val)`
    - 0, c5, c0, 0
    - Data Fault Status Register
*   - `__get_IFSR()`
    - `__set_IFSR(val)`
    - 0, c5, c0, 1
    - Instruction Fault Status Register

*   - `__get_DFAR()`
    - `__set_DFAR(val)`
    - 0, c6, c0, 0
    - Data Fault Address Register
*   - `__get_WFAR()`
    - `__set_WFAR(val)`
    - 0, c6, c0, 1
    - Watchpoint Fault Address Register
*   - `__get_IFAR()`
    - `__set_IFAR(val)`
    - 0, c6, c0, 2
    - Instruction Fault Address Register

*   - N/A
    - `__set_WFI(val)`
    - 0, c7, c0, 4
    - Drain write buffers, put CPU to sleep, and wait for interrupt
*   - N/A
    - `__set_ICIALLU(val)`
    - 0, c7, c5, 0
    - Instruction cache invalidate all
*   - N/A
    - `__set_ICIMVAC(val)`
    - 0, c7, c5, 1
    - Instruction cache invalidate by virtual address
*   - N/A
    - `__set_ICISW(val)`
    - 0, c7, c5, 2
    - Instruction cache invalidate by set/way
*   - N/A
    - `__set_PFBF(val)`
    - 0, c7, c5, 4
    - Prefetch buffer flush (older name for ISB)
*   - N/A
    - `__set_ISB(val)`
    - 0, c7, c5, 4
    - Another name for `__set_PFBF()`
*   - N/A
    - `__set_BPIALL(val)`
    - 0, c7, c5, 6
    - Branch predictor invalidate all
*   - N/A
    - `__set_DCIALLU(val)`
    - 0, c7, c6, 0
    - Data cache invalidate all
*   - N/A
    - `__set_DCIMVAC(val)`
    - 0, c7, c6, 1
    - Data cache invalidate by virtual address
*   - N/A
    - `__set_DCISW(val)`
    - 0, c7, c6, 2
    - Data cache invalidate by set/way
*   - N/A
    - `__set_IDCIALLU(val)`
    - 0, c7, c7, 0
    - Instruction and data cache invalidate all
*   - N/A
    - `__set_DCCMVAC(val)`
    - 0, c7, c10, 1
    - Data cache clean by virtual address
*   - N/A
    - `__set_DCCSW(val)`
    - 0, c7, c10, 2
    - Data cache clean by set/way
*   - N/A
    - `__set_DWB(val)`
    - 0, c7, c10, 4
    - Drain write buffer (older name for DSB)
*   - N/A
    - `__set_DSB(val)`
    - 0, c7, c10, 4
    - Another name for `__set_DWB()`
*   - N/A
    - `__set_DMB(val)`
    - 0, c7, c10, 5
    - Data memory barrier (ARMv6 only)
*   - N/A
    - `__set_ICPFMVAC(val)`
    - 0, c7, c13, 1
    - Instruction cache prefetch by virtual address
*   - N/A
    - `__set_DCCIMVAC(val)`
    - 0, c7, c14, 1
    - Data cache clean and invalidate by virtual address
*   - N/A
    - `__set_DCCISW(val)`
    - 0, c7, c14, 2
    - Data cache clean and invalidate by set/way

*   - N/A
    - `__set_TLBIALL(val)`
    - 0, c8, c7, 0
    - TLB invalidate all
*   - N/A
    - `__set_TLBIMVA(val)`
    - 0, c8, c7, 1
    - TLB invalidate by virtual address
*   - N/A
    - `__set_TLBIASID(val)`
    - 0, c8, c7, 2
    - TLB invalidate by ASID

*   - `__get_DCLDR()`
    - `__set_DCLDR(val)`
    - 0, c9, c0, 0
    - DCache Lockdown Register
*   - `__get_ICLDR()`
    - `__set_ICLDR(val)`
    - 0, c9, c0, 1
    - ICache Lockdown Register
*   - `__get_DTCMRR()`
    - `__set_DTCMRR(val)`
    - 0, c9, c1, 0
    - Data TCM Region Register
*   - `__get_ITCMRR()`
    - `__set_ITCMRR(val)`
    - 0, c9, c1, 1
    - Instruction TCM Region Register

*   - `__get_TLBLDR()`
    - `__set_TLBLDR(val)`
    - 0, c10, c0, 0
    - TLB Lockdown Register

*   - `__get_VBAR()`
    - `__set_VBAR(val)`
    - 0, c12, c0, 0
    - Vector Base Address Register
*   - `__get_MVBAR()`
    - `__set_MVBAR(val)`
    - 0, c12, c0, 1
    - Monitor Vector Base Address Register
*   - `__get_ISR()`
    - N/A
    - 0, c12, c1, 0
    - Interrupt Status Register

*   - `__get_FCSEPID()`
    - `__set_FCSEPID(val)`
    - 0, c13, c0, 0
    - Fast Context Switch Extension Process ID Register
*   - `__get_FCSECTX()`
    - `__set_FCSECTX(val)`
    - 0, c13, c0, 1
    - Fast Context Switch Extension Context ID Register

*   - `__get_CSSIDR()`
    - N/A
    - 1, c0, c0, 0
    - Current Cache Size ID Register
*   - `__get_CLIDR()`
    - N/A
    - 1, c0, c0, 1
    - Cache Level ID Register
*   - `__get_CSSELR()`
    - `__set_CSSELR(val)`
    - 2, c0, c0, 0
    - Cache Size Selection Register
*   - `__get_CBAR()`
    - N/A
    - 4, c15, c0, 0
    - Configuration Base Address Register
```

## Compiler Built-ins
Clang has lots of built-in functions. Rather than trying to duplicate them in this document, here
are links to the relevant sections of Clang documentation.

Online: <https://clang.llvm.org/docs/LanguageExtensions.html#builtin-functions>  
Local: [Built-in Functions](llvm:clang/html/LanguageExtensions.html#builtin-functions)

