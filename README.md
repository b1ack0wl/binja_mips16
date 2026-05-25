# MIPS16e/e2 Architecture Plugin for Binary Ninja

## Challenges

* Convert bytes to MIPS16e/e2 instructions
  * Once complete then Operand extraction logic needs to be implemented for each insn (Found in the PDFs in the `resources` folder)
* Express branches and function ends to Binja
  * The callback function `get_instruction_info()` is where this is done. The object `InstructionInfo` carries this information back to Binary Binja (e.g. `InstructionInfo.add_branch(BranchType.FunctionReturn)` when the disassembler finds a `restore` insn)
* Express the IL to Binary Ninja
  * This is for decompliation! (Very last step after the above tasks are complete)


## Resources

* The `resources` folder within `mips16` has all of the relevant PDFs and C code from MIPS binutils (https://github.com/MIPS/binutils-gdb)

* Binja Issue to implement MIPS16e/e2 - https://github.com/Vector35/binaryninja-api/issues/4013

* Intro to Architecture Plugin development - https://binary.ninja/2020/01/09/guide-to-architecture-plugins-part1.html


## Contributors

* [b1ack0wl](https://github.com/b1ack0wl/)
* [netspooky](https://github.com/netspooky/)
