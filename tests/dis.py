#!/usr/bin/env python3
"""Tiny disassembler for looking at the game's code while mapping things.
  tests/dis.py BB:AAAA [count] [m=1] [x=1]   e.g.  tests/dis.py 00:A299 40
Follows nothing, guesses nothing: it prints bytes as the 65816 would read them with the
given register widths (m=1 means 8-bit accumulator). REP/SEP in the listing update the widths.
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "vendor/snesrecomp/recompiler"))
import snes65816 as s

def main():
    bank, addr = [int(x, 16) for x in sys.argv[1].split(":")]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    m = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    x = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rom = open(os.path.join(ROOT, "rom/superpunchout.sfc"), "rb").read()
    s.set_rom_image_size(len(rom)); s.set_rom_mapping("lorom")
    pc = addr
    for _ in range(count):
        off = s.rom_offset(bank, pc)
        i = s.decode_insn(rom, off, pc, bank, m, x)
        if i is None:
            print(f"{bank:02X}:{pc:04X}  ?? {rom[off]:02X}"); pc += 1; continue
        raw = " ".join(f"{b:02X}" for b in rom[off:off + i.length])
        print(f"{bank:02X}:{pc:04X}  {raw:<12} {i.mnem} {i.mode} ${i.operand:X}")
        if i.mnem == "REP": m = 0 if i.operand & 0x20 else m; x = 0 if i.operand & 0x10 else x
        if i.mnem == "SEP": m = 1 if i.operand & 0x20 else m; x = 1 if i.operand & 0x10 else x
        pc += i.length
main()
