#!/usr/bin/env python3
"""Look at the jump table behind an indexed jump (JMP ($xxxx,X)) so a cfg entry can state its size.
  tests/jmptable.py BB:SITE [max=40]     e.g. tests/jmptable.py 00:DA47
Prints each 16-bit entry; marks entries that do not look like code in the same bank (below $8000)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "vendor/snesrecomp/recompiler"))
import snes65816 as s
rom = open(os.path.join(ROOT, "rom/superpunchout.sfc"), "rb").read()
s.set_rom_image_size(len(rom)); s.set_rom_mapping("lorom")
bank, site = [int(x, 16) for x in sys.argv[1].split(":")]
mx = int(sys.argv[2]) if len(sys.argv) > 2 else 40
i = s.decode_insn(rom, s.rom_offset(bank, site), site, bank, 1, 0)
print(f"{bank:02X}:{site:04X} {i.mnem} mode={i.mode} operand=${i.operand:04X}")
base = i.operand
ents = []
for k in range(mx):
    o = s.rom_offset(bank, base + 2 * k)
    v = rom[o] | rom[o + 1] << 8
    ents.append(v)
line = []
for k, v in enumerate(ents):
    flag = "" if v >= 0x8000 else "?"
    line.append(f"{k}:{v:04X}{flag}")
print("  ".join(line))
