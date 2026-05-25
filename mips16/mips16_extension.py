from binaryninja.architecture import Architecture, RegisterInfo, ArchitectureHook
from binaryninja.log import log_info
from binaryninja.function import InstructionInfo, InstructionTextToken, InstructionTextTokenType
from binaryninja.enums import Endianness, BranchType
import struct
from mips16_disassembler import *

class MIPSEL16E(Architecture):
  name = "MIPSEL16"
  endianness = Endianness.LittleEndian
  address_size = 4 # Addrs are 32-bit
  instr_alignment = 2 # 2 byte alignment
  max_instr_length = 4 # EXTEND and JAL opcodes are 4 bytes in length
  # MD00076-2B-MIPS1632-AFP-02.63.pdf Table 3.1
  regs = {"s0": RegisterInfo("s0", 4),
          "s1": RegisterInfo("s1", 4),
          "v0": RegisterInfo("v0", 4),
          "v1": RegisterInfo("v1", 4),
          "a0": RegisterInfo("a0", 4),
          "a1": RegisterInfo("a1", 4),
          "a2": RegisterInfo("a2", 4),
          "a3": RegisterInfo("a3", 4),
          "t8": RegisterInfo("t8", 4), # MIPS16e Condition Code register; implicitly referenced by the BTEQZ, BTNEZ, CMP, CMPI, SLT, SLTU, SLTI, and SLTIU instructions
          "sp": RegisterInfo("sp", 4),
          "ra": RegisterInfo("ra", 4),
          "hi": RegisterInfo("hi", 4), # Contains high-order word of multiply or divide result.
          "lo": RegisterInfo("lo", 4), # Contains low-order word of multiply or divide result.
          "pc": RegisterInfo("pc", 4)
	  }
  reg_lookup = ["s0", "s1", "v0", "v1", "a0", "a1", "a2", "a3", "t8", "sp", "ra", "hi", "lo", "pc"]
  stack_pointer = "sp"
  insn_disasassemblers = {"addiu": m16e_addiu,
                          "addu": m16e_addu,
                          "b": m16e_b,
                          "beqz": m16e_beqz,
                          "bteqz": m16e_bteqz,
                          "btnez": m16e_btnez,
                          "cmpi": m16e_cmpi,
                          "lb": m16e_lb,
                          "lbu": m16e_lbu,
                          "lh": m16e_lh,
                          "lhu": m16e_lhu,
                          "li": m16e_li,
                          "lw": m16e_lw,
                          "li": m16e_li,
                          "lw": m16e_lw,
                          "move": m16e_move,
                          "nop": m16e_nop, # no args, func just returns a blank string
                          "save": m16e_save,
                          "sb": m16e_sb,
                          "slt": m16e_slt,
                          "slti": m16e_slti,
                          "sw": m16e_sw
  }

  def sign_extend(self, value, from_nbits=None):
    if from_nbits is None:
      from_nbits = value.nbits
    sign_bit_mask = 1 << (from_nbits-1)
    low_bits_mask = sign_bit_mask - 1
    return (value & low_bits_mask) - (value & sign_bit_mask)

  def disassemble(self, data, extend_val=0):
    '''
    * Apply mask to bytes
    * If extended then length +=2
    '''
    insn = {"insn": "",
            "args": "",
            "length": 2
    }
    if (len(data) < 2):
      # Invalid length
      return insn
    unpacked_insn = struct.unpack("<H", data[0:2])[0]
    if (unpacked_insn & 0xfc00) == 0x1800:
      # cheap JAL patch for now
      # TODO fix this shit
      # - make it relative to the base addr
      # - fix collision with other similar functions
      # the current 0x1a00 match includes part of the target addr so it's not the best
      insn['insn'] = "jal"
      insn['length'] = 4
      jump_target_20_16 = (unpacked_insn & 0x03E0) >> 5
      jump_target_25_21 = (unpacked_insn & 0x001F) << 5
      jump_target_15_0 = struct.unpack("<H", data[2:4])[0]
      jump_target = jump_target_25_21 | jump_target_20_16 | jump_target_15_0
      jump_target = jump_target << 2
      insn['args'] = m16e_jal(jump_target)
      return insn
    for mips16_insn in mips16_opcodes:
      # index 3 == Mask, index 2 == Match
      if (mips16_insn[3] & unpacked_insn) == mips16_insn[2]:
        insn['insn'] = mips16_insn[0]
        if insn.get("insn") == 'extend':
          '''
          Extended OPCODE
          * 4 byte length in total
          * 0-11 bits used to combine with the next instruction
          * an abomination of an opcode lol
          '''
          # Disassemble the next two bytes.
          _extend_val = unpacked_insn & 0x7FF
          next_op_code = self.disassemble(data[2::], _extend_val)
          insn['insn'] = next_op_code['insn']
          insn['length'] = 4
          insn['args'] = next_op_code['args']
          return insn
        break
    # Get Operands
    get_args = self.insn_disasassemblers.get(insn.get("insn"))
    if get_args == None:
      print(f"[*] insn {insn.get('insn')} diassembly is not supported atm :<")
    else:
      insn['args'] = get_args(unpacked_insn, extend_val)
    return insn


  '''
  Binja Callbacks below
  '''
  def get_instruction_info(self, data, addr):
    result = InstructionInfo()
    insn = self.disassemble(data)
    #print(f"[get_instruction_info] addr: 0x{addr:08X}, insn: {insn}")
    result.length = insn['length']
    if insn['insn'] == 'restore':
      result.add_branch(BranchType.FunctionReturn)
    return result

  def get_instruction_text(self, data, addr):
    result = []
    insn = self.disassemble(data)
    print(f"[get_instruction_text] addr: 0x{addr:08X}, insn: {insn}")
    result.append(InstructionTextToken(InstructionTextTokenType.InstructionToken, insn['insn']))
    # Express Operands
    if len(insn.get("args")) > 0:
      result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " " * (8-len(insn.get("insn"))))) # Add spaces for operands
    # Parse operands with more than 1 thing in it
    if insn.get("args").find(",") != -1:
      operands = insn.get("args").split(",")
      for arg in operands:
        #print(arg)
        if arg.find("-") != -1:
          for arg2 in arg.split("-"): # Register range
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, arg2.strip()))
            result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, "-"))
          continue
        elif arg.strip()[0] == "$": # Register
          result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, arg.strip()))
          result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "))
          continue
        elif arg.strip().isdigit() == True: # Integer
          result.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, arg.strip()))
          result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "))
        else:
          result.append(InstructionTextToken(InstructionTextTokenType.TextToken, arg.strip()))
    else:
      if insn.get("args").strip().startswith("0x") == True: # Address?
        result.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(int(insn.get("args").strip(), 16) + addr)))
      else:
        # Fall through
        # TODO fix this
        result.append(InstructionTextToken(InstructionTextTokenType.TextToken, insn.get("args").strip()))
    # low budget cleanup
    if result[-1] == InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "):
      result.pop()
    elif result[-1] == InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, "-"):
      result.pop()
    return result, insn['length']
  
  def get_instruction_low_level_il(self, data, addr, il):
    #print(f"[get_instruction_low_level_il] addr: 0x{addr:08X}")
    return True


MIPSEL16E().register()