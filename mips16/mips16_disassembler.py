# index look up for now
m16e_regmap = [
    #[ name, idx ]
    [ "$s0", 0 ],
    [ "$s1", 1 ],
    [ "$v0", 2 ],
    [ "$v1", 3 ],
    [ "$a0", 4 ],
    [ "$a1", 5 ],
    [ "$a2", 6 ],
    [ "$a3", 7 ]
]

m32_regmap = [
    #[ name, idx ]
    [ "$r0",  0 ],
    [ "$at",  1 ],
    
    # Return values
    [ "$v0",  2 ],
    [ "$v1",  3 ],
    
    # Arguments
    [ "$a0",  4 ], 
    [ "$a1",  5 ], 
    [ "$a2",  6 ], 
    [ "$a3",  7 ], 
    
    # Temp registers
    [ "$t0",  8 ], 
    [ "$t1",  9 ], 
    [ "$t2", 10 ], 
    [ "$t3", 11 ], 
    [ "$t4", 12 ], 
    [ "$t5", 13 ], 
    [ "$t6", 14 ], 
    [ "$t7", 15 ], 
    
    # Saved registers
    [ "$s0", 16 ], 
    [ "$s1", 17 ], 
    [ "$s2", 18 ], 
    [ "$s3", 19 ], 
    [ "$s4", 20 ], 
    [ "$s5", 21 ], 
    [ "$s6", 22 ], 
    [ "$s7", 23 ], 
    
    # Temp registers
    [ "$t8", 24 ], 
    [ "$t9", 25 ], 
    
    # Kernel registers
    [ "$k0", 26 ], 
    [ "$k1", 27 ], 
    
    # Special
    [ "$gp", 28 ], 
    [ "$sp", 29 ], 
    [ "$fp", 30 ], 
    [ "$ra", 31 ], 
]

def extract_extend_val_15_5(extend_val):
  # handles when
  # bits 26:21 = imm 10:5 
  # bits 20:16 = imm 15:11
  # Which can be OR'd with the bottom 5 bits of the immediate
  ev1 = extend_val & 0x07E0
  ev2 = extend_val & 0x001F
  evo = ev1 | ( ev2 << 11 )
  #print(f"[+] LW Extend Val: {hex(extend_val)} -- evo {hex(evo)} = ev1({hex(ev1)}) and ev2({hex(ev2)})")
  return evo

def fmt16_I(in_data):
  """
  3.14.1 I-Type
  
  │1│1│1│1│1│1│ │ │ │ │ │ │ │ │ │ │
  │5│4│3│2│1│0│9│8│7│6│5│4│3│2│1│0│
  ├─┴─┴─┴─┴─┼─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┤
  │ op      │ immediate           │

  """
  _imm = in_data & 0x3FF
  return _imm

def fmt16_RI(in_data):
  """
  3.14.2 RI-Type

  │1│1│1│1│1│1│ │ │ │ │ │ │ │ │ │ │
  │5│4│3│2│1│0│9│8│7│6│5│4│3│2│1│0│
  ├─┴─┴─┴─┴─┼─┴─┴─┼─┴─┴─┴─┴─┴─┴─┴─┤
  │ op      │ rx  │ immediate     │

  """
  _rx  = in_data >> 8
  _rx  = _rx & 7
  _imm = in_data & 0xFF
  return _rx, _imm

def fmt16_RRI(in_data):
  """
  3.14.4 RRI-type instruction forma
  
  │1│1│1│1│1│1│ │ │ │ │ │ │ │ │ │ │
  │5│4│3│2│1│0│9│8│7│6│5│4│3│2│1│0│
  ├─┴─┴─┴─┴─┼─┴─┴─┼─┴─┴─┼─┴─┴─┴─┴─┤
  │ op      │ rx  │ ry  │immediate│

  """
  _rx  = in_data >> 8
  _rx  = _rx & 7

  _ry  = in_data >> 5
  _ry  = _ry & 7

  _imm = in_data & 0x1F
  return _rx, _ry, _imm

def m16e_xlat(i):
  """
  4.1.1.1
  The Xlat function translates the MIPS16e register 
  field ind x to the correct 32-bit MIPS physical 
  register index. It is used to assure that a value 
  of 0b000 in a MIPS16e register field maps to GPR 16, 
  and a value of 0b001 maps to GPR 17. 
  All other values (0b010 through 0b111) map directly.

  PhyReg <-- Xlat(i)

  PhyReg: Physical Register index in range 0..7
  i: opcode register field index

  """
  if i < 2:
      i = i + 16
  return i

### Instruction Decoders
def m16e_addiu(unpacked_insn, extend_val):
  # TODO - finish implementing and do better matching
  out = ""
  #if (unpacked_insn & 0x4800) == 0x4800:
  #    # 2 op
  #    print("ADDIU rx, immediate")
  if (unpacked_insn & 0x4000) == 0x4000:
      #print("ADDIU ry, rx, immediate")
      _rx, _ry, _imm = fmt16_RRI(unpacked_insn)
      _rx_name = m16e_regmap[_rx][0]
      _ry_name = m16e_regmap[_ry][0]
      out = f"{_ry_name}, {_rx_name}, {_imm}"
      return out

def m16e_addu(unpacked_insn, extend_val):
  # TODO - finish implementing
  out = ""
  return out

def m16e_b(unpacked_insn, extend_val=0):
  _imm = fmt16_I(unpacked_insn)
  _imm = _imm << 1
  # todo - sign extend, pc relative
  out = f"{hex(_imm)}"
  return out

def m16e_beqz(unpacked_insn, extend_val=0):
  _rx, _imm = fmt16_RI(unpacked_insn)
  _rx_name = m16e_regmap[_rx][0]
  _imm = _imm << 1
  # TODO - add _imm to the address after this instruction
  out = f"{_rx_name}, {hex(_imm)}"
  return out

def m16e_bteqz(unpacked_insn, extend_val=0):
  # Note that the _rx is not used bc this is a special format
  _rx, _imm = fmt16_RI(unpacked_insn)
  _imm = _imm << 1
  # TODO - add _imm to the address after this instruction
  out = f"{hex(_imm)}"
  return out

def m16e_btnez(unpacked_insn, extend_val=0):
  # Note that the _rx is not used bc this is a special format
  _rx, _imm = fmt16_RI(unpacked_insn)
  _imm = _imm << 1
  # TODO - add _imm to the address after this instruction
  out = f"{hex(_imm)}"
  return out

def m16e_cmpi(unpacked_insn, extend_val=0):
  # TODO - extend version which uses a different instruction format
  # The 8-bit immediate is zero-extended and Exclusive-ORed with the contents of GPR rx. The result is placed into GPR 24.
  _rx, _imm = fmt16_RI(unpacked_insn)
  _rx_name = m16e_regmap[_rx][0]
  # spooky ???
  #   The datasheet says that it is shift left once, but the binutils objdump doesn't seem to do that
  #   I left it without this shift for now just to get parity
  #_imm = _imm << 1
  out = f"{_rx_name}, {_imm}"
  return out

def m16e_jal(unpacked_insn, extend_val=0):
  # TODO - add to PC
  out = f"{hex(unpacked_insn)}"
  return out

def m16e_lb(unpacked_insn, extend_val):
  evo = extract_extend_val_15_5(extend_val) if extend_val > 0 else 0
  _rx, _ry, _imm = fmt16_RRI(unpacked_insn)
  _rx_name = m16e_regmap[_rx][0]
  _ry_name = m16e_regmap[_ry][0]
  _imm = _imm | evo # OR with extend value extracted bits if present
  out = f"{_ry_name}, {_imm}({_rx_name})"
  return out

def m16e_lbu(unpacked_insn, extend_val):
  evo = extract_extend_val_15_5(extend_val) if extend_val > 0 else 0
  _rx, _ry, _imm = fmt16_RRI(unpacked_insn)
  _rx_name = m16e_regmap[_rx][0]
  _ry_name = m16e_regmap[_ry][0]
  _imm = _imm | evo # OR with extend value extracted bits if present
  out = f"{_ry_name}, {_imm}({_rx_name})"
  return out

def m16e_lh(unpacked_insn, extend_val):
  evo = extract_extend_val_15_5(extend_val) if extend_val > 0 else 0
  _rx, _ry, _imm = fmt16_RRI(unpacked_insn)
  _rx_name = m16e_regmap[_rx][0]
  _ry_name = m16e_regmap[_ry][0]
  _imm = _imm << 1
  _imm = _imm | evo # OR with extend value extracted bits if present
  out = f"{_ry_name}, {_imm}({_rx_name})"
  return out

def m16e_lhu(unpacked_insn, extend_val):
  evo = extract_extend_val_15_5(extend_val) if extend_val > 0 else 0
  _rx, _ry, _imm = fmt16_RRI(unpacked_insn)
  _rx_name = m16e_regmap[_rx][0]
  _ry_name = m16e_regmap[_ry][0]
  _imm = _imm << 1
  _imm = _imm | evo # OR with extend value extracted bits if present
  out = f"{_ry_name}, {_imm}({_rx_name})"
  return out

def m16e_li(unpacked_insn, extend_val):
  evo = extract_extend_val_15_5(extend_val) if extend_val > 0 else 0
  _rx, _imm = fmt16_RI(unpacked_insn)
  _imm = _imm | evo # OR with extend value extracted bits if present
  _rx_name = m16e_regmap[_rx][0]
  out = f"{_rx_name}, {_imm}"
  return out

def m16e_lw(unpacked_insn, extend_val):
  evo = extract_extend_val_15_5(extend_val) if extend_val > 0 else 0
  if (unpacked_insn & 0x9800) == 0x9800:
      #print(f"Load Word - LW ry, offset(rx)")
      _rx, _ry, _imm = fmt16_RRI(unpacked_insn)
      _rx_name = m16e_regmap[_rx][0]
      _imm = _imm << 2
      _imm = _imm | evo # OR with extend value extracted bits if present
      _ry = m16e_xlat(_ry)
      _ry_name = m32_regmap[_ry][0]
      out = f"{_ry_name}, {_imm}({_rx_name})"
      return out

  if (unpacked_insn & 0xb000) == 0xb000:
      #print("Load Word - LW rx, offset($pc)")
      _rx, _imm = fmt16_RI(unpacked_insn)
      _rx_name = m16e_regmap[_rx][0]
      _imm = _imm << 2
      _imm = _imm | evo # OR with extend value extracted bits if present
      out = f"{_rx_name}, {_imm}($pc)"
      return out
  if (unpacked_insn & 0x9000) == 0x9000:
      #print("Load Word - LW rx, offset(sp)")
      _rx, _imm = fmt16_RI(unpacked_insn)
      _rx_name = m16e_regmap[_rx][0]
      _imm = _imm << 2
      _imm = _imm | evo # OR with extend value extracted bits if present
      out = f"{_rx_name}, {_imm}($sp)"
      return out

def m16e_move(unpacked_insn, extend_val=0):
  # if bit 9 is 0, it's MOVE r32, rz
  # if bit 9 is 1, it's MOVE ry, r32
  out = ""
  if unpacked_insn & 0x20:
    _ry  = ( unpacked_insn >> 5 ) & 7
    _ry_name = m16e_regmap[_ry][0]
    _r32 = unpacked_insn & 0x1F
    _r32_name = m32_regmap[_r32][0]
    out = f"{_ry_name}, {_r32_name}"

  else:
    _rz  = unpacked_insn & 7
    _rz_name = m16e_regmap[_rz][0]
    _r32 = ( ( unpacked_insn & 0xE ) >> 5 ) & ( unpacked_insn & 0x1C )
    _r32 = m16e_xlat(_r32)
    _r32_name = m32_regmap[_r32][0]
    out = f"{_r32_name}, {_rz_name}"
  return out

def m16e_nop(unpacked_insn, extend_val):
  # no args, it's nop lol
  return ""

def m16e_save(unpacked_insn, extend_val):
  # Example:
  # save  a0,64,ra,s0-s1
  # evo is unused atm??
  evo = extract_extend_val_15_5(extend_val) if extend_val > 0 else 0
  out = ""
  _ra = unpacked_insn & 0x40
  _ra_name = "$ra" if _ra else ""
  _s0 = unpacked_insn & 0x20
  _s0_name = "$s0" if _s0 else ""
  _s1 = unpacked_insn & 0x10
  _s1_name = "$s1" if _s1 else ""
  _framesize = unpacked_insn & 0x0F 
  if _framesize == 0:
    # NOTE: A framesize value of 0 is interpreted as a stack adjustment of 128.
    _framesize = 128
  else:
    if _ra or _s0 or _s1:
      _framesize = _framesize * 8
  # TODO - confirm if a0 is always there
  out = f"$a0,"
  out += f"{_framesize}"
  out += f",{_ra_name}"
  out += f",{_s0_name}-{_s1_name}" 
  return out


def m16e_sb(unpacked_insn, extend_val):
  evo = extract_extend_val_15_5(extend_val) if extend_val > 0 else 0
  _rx, _ry, _imm = fmt16_RRI(unpacked_insn)
  _rx_name = m16e_regmap[_rx][0]
  _ry_name = m16e_regmap[_ry][0]
  _imm = _imm | evo # OR with extend value extracted bits if present
  out = f"{_ry_name}, {_imm}({_rx_name})"
  return out

def m16e_slt(unpacked_insn, extend_val=0):
  _rx, _ry, _imm = fmt16_RRI(unpacked_insn)
  _rx_name = m16e_regmap[_rx][0]
  _ry_name = m16e_regmap[_ry][0]
  out = f"{_rx_name}, {_ry_name}"
  return out

def m16e_slti(unpacked_insn, extend_val):
  evo = extract_extend_val_15_5(extend_val) if extend_val > 0 else 0
  _rx, _imm = fmt16_RI(unpacked_insn)
  _rx_name = m16e_regmap[_rx][0]
  #_imm = _imm << 1
  # TODO - zero extend
  _imm = _imm | evo # OR with extend value extracted bits if present
  out = f"{_rx_name}, {_imm}"
  return out

def m16e_sw(unpacked_insn, extend_val):
  """
  Handler for:
    11011xxx (0xd8) sw -- SW ry, offset(rx)
    11010xxx (0xd0) sw rx (sp rel) -- SW rx, offset(sp)
    01100010 (0x62) sw ra (sp rel) -- SW ra, offset(sp) 
  """
  evo = extract_extend_val_15_5(extend_val) if extend_val > 0 else 0

  if (unpacked_insn & 0xd800) == 0xd800:
      _rx, _ry, _imm = fmt16_RRI(unpacked_insn)
      _rx_name = m16e_regmap[_rx][0]
      _ry_name = m16e_regmap[_ry][0]
      if evo:
          _imm = _imm | evo # OR with extend value extracted bits if present
      else:
          _imm = _imm << 2 # TODO - zero extend
      out = f"{_ry_name}, {_imm}({_rx_name})"
      return out
  if (unpacked_insn & 0xd000) == 0xd000:
      _rx, _imm = fmt16_RI(unpacked_insn)
      _rx_name = m16e_regmap[_rx][0]
      if evo:
          _imm = _imm | evo # OR with extend value extracted bits if present
      else:
          _imm = _imm << 2 # TODO - zero extend
      out = f"{_rx_name}, {_imm}($sp)"
      return out
  if (unpacked_insn & 0x6200) == 0x6200:
      _rx, _imm = fmt16_RI(unpacked_insn)
      if evo:
          _imm = _imm | evo # OR with extend value extracted bits if present
      else:
          _imm = _imm << 2 # TODO - zero extend
      out = f"ra, {_imm}($sp)"
      return out

mips16_opcodes =[
#/* name,    args,	match,	mask,	 */
["nop",	    "",		0x6500, 0xffff], #/* move $0,$Z */
["la",	    "x,A",	0x0800, 0xf800],
["addiu",   "y,x,F",	0x4000, 0xf810],
["addiu",   "x,k",	0x4800, 0xf800],
["addiu",   "S,K",	0x6300, 0xff00],
["addiu",   "S,S,K",	0x6300, 0xff00],
["addiu",   "x,P,V",	0x0800, 0xf800],
["addiu",   "x,S,V",	0x0000, 0xf800],
["addiu",   "x,S,V",	0x0000, 0xf800],
["addiu",   "x,S,V",	0xf0000000, 0xf800f8e0],
["addiu",   "x,G,V",	0xf0000020, 0xf800f8e0],
["addu",    "z,v,y",	0xe001, 0xf803],
["addu",    "y,x,F",	0x4000, 0xf810],
["addu",    "x,k",	0x4800, 0xf800],
["addu",    "S,K",	0x6300, 0xff00],
["addu",    "S,S,K",	0x6300, 0xff00],
["addu",    "x,P,V",	0x0800, 0xf800],
["addu",    "x,S,V",	0x0000, 0xf800],
["addu",    "x,S,V",	0x0000, 0xf800],
["addu",    "x,S,V",	0xf0000000, 0xf800f8e0],
["addu",    "x,G,V",	0xf0000020, 0xf800f8e0],
["and",	    "x,y",	0xe80c, 0xf81f],
["andi",    "x,u",	0xf0006860, 0xf800f8e0],
["b",	    "q",	0x1000, 0xf800],
["beqz",    "x,p",	0x2000, 0xf800],
["bnez",    "x,p",	0x2800, 0xf800],
["break",   "",		0xe805, 0xffff],
["break",   "6",	0xe805, 0xf81f],
["bteqz",   "p",	0x6000, 0xff00],
["btnez",   "p",	0x6100, 0xff00],
["cache",   "T,9(x)",	0xf000d0a0, 0xfe00f8e0],
["cmpi",    "x,U",	0x7000, 0xf800],
["cmp",	    "x,y",	0xe80a, 0xf81f],
["cmp",     "x,U",	0x7000, 0xf800],
["dla",	    "y,E",	0xfe00, 0xff00],
["daddiu",  "y,x,F",	0x4010, 0xf810],
["daddiu",  "y,j",	0xfd00, 0xff00],
["daddiu",  "S,K",	0xfb00, 0xff00],
["daddiu",  "S,S,K",	0xfb00, 0xff00],
["daddiu",  "y,P,W",	0xfe00, 0xff00],
["daddiu",  "y,S,W",	0xff00, 0xff00],
["daddu",   "z,v,y",	0xe000, 0xf803],
["daddu",   "y,x,F",	0x4010, 0xf810],
["daddu",   "y,j",	0xfd00, 0xff00],
["daddu",   "S,K",	0xfb00, 0xff00],
["daddu",   "S,S,K",	0xfb00, 0xff00],
["daddu",   "y,P,W",	0xfe00, 0xff00],
["daddu",   "y,S,W",	0xff00, 0xff00],
["ddiv",    ".,x,y",	0xe81e, 0xf81f],
["ddivu",   ".,x,y",	0xe81f, 0xf81f],
["di",	    "",		0xf006670c, 0xffffffff],
["di",	    ".",	0xf006670c, 0xffffffff],
["di",	    "y",	0xf002670c, 0xffffff1f],
["div",	    ".,x,y",	0xe81a, 0xf81f],
["divu",    ".,x,y",	0xe81b, 0xf81f],
["dmult",   "x,y",	0xe81c, 0xf81f],
["dmultu",  "x,y",	0xe81d, 0xf81f],
["drem",    ".,x,y",	0xe81e, 0xf81f],
["dremu",   ".,x,y",	0xe81f, 0xf81f],
["dsllv",   "y,x",	0xe814, 0xf81f],
["dsll",    "x,w,[",	0x3001, 0xf803],
["dsll",    "y,x",	0xe814, 0xf81f],
["dsrav",   "y,x",	0xe817, 0xf81f],
["dsra",    "y,]",	0xe813, 0xf81f],
["dsra",    "y,x",	0xe817, 0xf81f],
["dsrlv",   "y,x",	0xe816, 0xf81f],
["dsrl",    "y,]",	0xe808, 0xf81f],
["dsrl",    "y,x",	0xe816, 0xf81f],
["dsubu",   "z,v,y",	0xe002, 0xf803],
["ehb",	    "",		0xf0c03010, 0xffffffff],
["ei",	    "",		0xf007670c, 0xffffffff],
["ei",	    ".",	0xf007670c, 0xffffffff],
["ei",	    "y",	0xf003670c, 0xffffff1f],
["exit",    "L",	0xed09, 0xff1f],
["exit",    "L",	0xee09, 0xff1f],
["exit",    "",		0xef09, 0xffff],
["exit",    "L",	0xef09, 0xff1f],
["entry",   "",		0xe809, 0xffff],
["entry",   "l",	0xe809, 0xf81f],
["ext",	    "y,x,b,d",	0xf0203008, 0xf820f81f],
["ins",	    "y,.,b,c",	0xf0003004, 0xf820ff1f],
["ins",	    "y,x,b,c",	0xf0203004, 0xf820f81f],
["jalr",    "x",	0xe840, 0xf8ff],
["jalr",    "R,x",	0xe840, 0xf8ff],
["jal",	    "x",	0xe840, 0xf8ff],
["jal",	    "R,x",	0xe840, 0xf8ff],
["jal",	    "a",	0x18000000, 0xfc000000],
["jalx",    "i",	0x1c000000, 0xfc000000],
["jr",	    "x",	0xe800, 0xf8ff],
["jr",	    "R",	0xe820, 0xffff],
["j",	    "x",	0xe800, 0xf8ff],
["j",	    "R",	0xe820, 0xffff],
["jalrc",   "x",	0xe8c0, 0xf8ff],
["jalrc",   "R,x",	0xe8c0, 0xf8ff],
["jrc",	    "x",	0xe880, 0xf8ff],
["jrc",	    "R",	0xe8a0, 0xffff],
["lb",	    "y,5(x)",	0x8000, 0xf800],
["lb",	    "x,V(G)",	0xf0009060, 0xf800f8e0],
["lbu",	    "y,5(x)",	0xa000, 0xf800],
["lbu",	    "x,V(G)",	0xf00090a0, 0xf800f8e0],
["ld",	    "y,D(x)",	0x3800, 0xf800],
["ld",	    "y,B",	0xfc00, 0xff00],
["ld",	    "y,D(P)",	0xfc00, 0xff00],
["ld",	    "y,D(S)",	0xf800, 0xff00],
["lh",	    "y,H(x)",	0x8800, 0xf800],
["lh",	    "x,V(G)",	0xf0009040, 0xf800f8e0],
["lhu",	    "y,H(x)",	0xa800, 0xf800],
["lhu",	    "x,V(G)",	0xf0009080, 0xf800f8e0],
["li",	    "x,U",	0x6800, 0xf800],
["li",	    "x,U",	0x6800, 0xf800],
["li",	    "x,U",	0xf0006800, 0xf800f8e0],
["ll",	    "x,9(r)",	0xf00090c0, 0xfe18f8e0],
["lui",	    "x,u",	0xf0006820, 0xf800f8e0],
["lw",	    "y,W(x)",	0x9800, 0xf800],
["lw",	    "x,A",	0xb000, 0xf800],
["lw",	    "x,V(P)",	0xb000, 0xf800,],
["lw",	    "x,V(S)",	0x9000, 0xf800],
["lw",	    "x,V(S)",	0x9000, 0xf800],
["lw",	    "x,V(S)",	0xf0009000, 0xf800f8e0],
["lw",	    "x,V(G)",	0xf0009020, 0xf800f8e0],
["lwl",	    "x,9(r)",	0xf00090e0, 0xfe18f8e0],
["lwr",	    "x,9(r)",	0xf01090e0, 0xfe18f8e0],
["lwu",     "y,W(x)",	0xb800, 0xf800],
["mfc0",    "y,N",	0xf0006700, 0xffffff00],
["mfc0",    "y,N,O",	0xf0006700, 0xff1fff00],
["mfhi",    "x",	0xe810, 0xf8ff],
["mflo",    "x",	0xe812, 0xf8ff],
["move",    "y,X",	0x6700, 0xff00],
["move",    "Y,Z",	0x6500, 0xff00],
["movn",    "x,.,w",	0xf000300a, 0xfffff81f],
["movn",    "x,r,w",	0xf020300a, 0xfff8f81f],
["movtn",   "x,.",	0xf000301a, 0xfffff8ff],
["movtn",   "x,r",	0xf020301a, 0xfff8f8ff],
["movtz",   "x,.",	0xf0003016, 0xfffff8ff],
["movtz",   "x,r",	0xf0203016, 0xfff8f8ff],
["movz",    "x,.,w",	0xf0003006, 0xfffff81f],
["movz",    "x,r,w",	0xf0203006, 0xfff8f81f],
["mtc0",    "y,N",	0xf0016700, 0xffffff00],
["mtc0",    "y,N,O",	0xf0016700, 0xff1fff00],
["mult",    "x,y",	0xe818, 0xf81f],
["multu",   "x,y",	0xe819, 0xf81f],
["neg",	    "x,w",	0xe80b, 0xf81f],
["not",	    "x,w",	0xe80f, 0xf81f],
["or",	    "x,y",	0xe80d, 0xf81f],
["ori",	    "x,u",	0xf0006840, 0xf800f8e0],
["pause",   "",		0xf1403018, 0xffffffff],
["pref",    "T,9(x)",	0xf000d080, 0xfe00f8e0],
["rdhwr",   "y,Q",	0xf000300c, 0xffe0ff1f],
["rem",	    ".,x,y",	0xe81a, 0xf81f],
["remu",    ".,x,y",	0xe81b, 0xf81f],
["sb",	    "y,5(x)",	0xc000, 0xf800],
["sb",	    "x,V(G)",	0xf000d060, 0xf800f8e0],
["sc",	    "x,9(r)",	0xf000d0c0, 0xfe18f8e0],
["sd",	    "y,D(x)",	0x7800, 0xf800],
["sd",	    "y,D(S)",	0xf900, 0xff00],
["sd",	    "R,C(S)",	0xfa00, 0xff00],
["sh",	    "y,H(x)",	0xc800, 0xf800],
["sh",	    "x,V(G)",	0xf000d040, 0xf800f8e0],
["sllv",    "y,x",	0xe804, 0xf81f],
["sll",	    "x,w,<",	0x3000, 0xf803],
["sll",	    "x,w,<",	0x3000, 0xf803],
["sll",	    "x,w,<",	0xf0003000, 0xf83ff81f],
["sll",	    "y,x",	0xe804, 0xf81f],
["slti",    "x,8",	0x5000, 0xf800],
["slt",	    "x,y",	0xe802, 0xf81f],
["slt",     "x,8",	0x5000, 0xf800],
["sltiu",   "x,8",	0x5800, 0xf800],
["sltu",    "x,y",	0xe803, 0xf81f],
["sltu",    "x,8",	0x5800, 0xf800],
["srav",    "y,x",	0xe807, 0xf81f],
["sra",	    "x,w,<",	0x3003, 0xf803],
["sra",	    "y,x",	0xe807, 0xf81f],
["srlv",    "y,x",	0xe806, 0xf81f],
["srl",	    "x,w,<",	0x3002, 0xf803],
["srl",	    "x,w,<",	0x3002, 0xf803],
["srl",	    "x,w,<",	0xf0003002, 0xf83ff81f],
["srl",	    "y,x",	0xe806, 0xf81f],
["subu",    "z,v,y",	0xe003, 0xf803],
["sw",	    "y,W(x)",	0xd800, 0xf800],
["sw",	    "x,V(S)",	0xd000, 0xf800],
["sw",	    "x,V(S)",	0xd000, 0xf800],
["sw",	    "x,V(S)",	0xf000d000, 0xf800f8e0 ],
["sw",	    "R,V(S)",	0x6200, 0xff00],
["sw",	    "x,V(G)",	0xf000d020, 0xf800f8e0],
["swl",	    "x,9(r)",	0xf000d0e0, 0xfe18f8e0],
["swr",	    "x,9(r)",	0xf010d0e0, 0xfe18f8e0],
["sync_acquire", "",	0xf4403014, 0xffffffff],
["sync_mb", "",		0xf4003014, 0xffffffff],
["sync_release", "",	0xf4803014, 0xffffffff],
["sync_rmb", "",	0xf4c03014, 0xffffffff],
["sync_wmb", "",	0xf1003014, 0xffffffff],
["sync",    "",		0xf0003014, 0xffffffff],
["sync",    ">",	0xf0003014, 0xf83fffff],
["xor",	    "x,y",	0xe80e, 0xf81f],
["xori",    "x,u",	0xf0006880, 0xf800f8e0],
#  /* MIPS16e additions; see above for compact jumps.  */
["restore", "m",	0x6400, 0xff80],
["save",    "m",	0x6480, 0xff80],
["sdbbp",   "",		0xe801, 0xffff],
["sdbbp",   "6",	0xe801, 0xf81f],
["seb",	    "x",	0xe891, 0xf8ff],
["seh",	    "x",	0xe8b1, 0xf8ff],
["sew",	    "x",	0xe8d1, 0xf8ff],
["zeb",	    "x",	0xe811, 0xf8ff],
["zeh",	    "x",	0xe831, 0xf8ff],
["zew",	    "x",	0xe851, 0xf8ff],
#  /* MIPS16e2 MT ASE instructions.  */
["dmt",	    "",		0xf0266701, 0xffffffff],
["dmt",	    ".",	0xf0266701, 0xffffffff],
["dmt",	    "y",	0xf0226701, 0xffffff1f],
["dvpe",    "",		0xf0266700, 0xffffffff],
["dvpe",    ".",	0xf0266700, 0xffffffff],
["dvpe",    "y",	0xf0226700, 0xffffff1f],
["emt",	    "",		0xf0276701, 0xffffffff],
["emt",	    ".",	0xf0276701, 0xffffffff],
["emt",	    "y",	0xf0236701, 0xffffff1f],
["evpe",    "",		0xf0276700, 0xffffffff],
["evpe",    ".",	0xf0276700, 0xffffffff],
["evpe",    "y",	0xf0236700, 0xffffff1f],
#  /* interAptiv MR2 instruction extensions.  */
["copyw",   "x,y,o,n",	0xf020e000, 0xffe0f81c],
["ucopyw",  "x,y,o,n",	0xf000e000, 0xffe0f81c],
#     Place asmacro at the bottom so that it catches any implementation
#     specific macros that didn't match anything.  */
["asmacro", "s,0,1,2,3,4", 0xf000e000, 0xf800f800],
#  /* Place EXTEND last so that it catches any prefix that didn't match
#     anything.  */
["extend",  "e",	0xf000, 0xf800]
]