#!/usr/bin/env python3
"""Summarize one routine by following its branches (not its calls): where it returns, what widths it
returns in, where it saves/restores flags (PHP/PLP), calls, and anything dynamic.
  tests/fn_info.py BB:AAAA [m=1 x=0]
Only a reading aid for writing cfg facts (like exit widths); the recompiler's own analysis is the authority."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "vendor/snesrecomp/recompiler"))
import snes65816 as s
rom = open(os.path.join(ROOT, "rom/superpunchout.sfc"), "rb").read()
s.set_rom_image_size(len(rom)); s.set_rom_mapping("lorom")
bank, pc0 = [int(x, 16) for x in sys.argv[1].split(":")]
m0 = int(sys.argv[2]) if len(sys.argv) > 2 else 1
x0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
seen, work = {}, [(pc0, m0, x0)]
rets, calls, dyn, plps, php, rams, brks = [], [], [], [], [], [], []
n = 0
while work and n < 5000:
    pc, m, x = work.pop()
    while True:
        if (pc, m, x) in seen: break
        seen[(pc, m, x)] = 1; n += 1
        i = s.decode_insn(rom, s.rom_offset(bank, pc), pc, bank, m, x)
        if i is None: brks.append(("undecodable", pc)); break
        mn = i.mnem
        if mn in ("BRK", "COP"): brks.append((mn, pc)); break
        if mn == "REP": m = 0 if i.operand & 0x20 else m; x = 0 if i.operand & 0x10 else x
        if mn == "SEP": m = 1 if i.operand & 0x20 else m; x = 1 if i.operand & 0x10 else x
        if mn == "PHP": php.append(pc)
        if mn == "PLP": plps.append(pc); 
        if mn in ("RTS", "RTL", "RTI"): rets.append((pc, mn, m, x)); break
        if mn in ("JSR", "JSL"):
            calls.append((pc, mn, i.mode, i.operand, m, x))
        nxt = pc + i.length
        if mn in ("BCC","BCS","BEQ","BNE","BMI","BPL","BVC","BVS","BRA"):
            work.append((i.operand, m, x))
            if mn == "BRA": break
        elif mn == "BRL": work.append((i.operand, m, x)); break
        elif mn == "JMP" and i.mode == 6:
            if i.operand < 0x8000: rams.append((pc, i.operand)); break
            work.append((i.operand, m, x)); break
        elif mn in ("JMP", "JML"):
            dyn.append((pc, mn, i.mode, i.operand)); break
        pc = nxt
print(f"{bank:02X}:{pc0:04X} entry M{m0}X{x0}: {n} instruction-states")
print("returns :", [f"{p:04X} {mn} exit M{m}X{x}" for p, mn, m, x in rets])
print("PHP at  :", [f"{p:04X}" for p in php], " PLP at:", [f"{p:04X}" for p in plps])
print("calls   :", [f"{p:04X} {mn} ${o:X} (M{m}X{x})" for p, mn, md, o, m, x in calls])
print("dynamic :", [f"{p:04X} {mn} mode{md} ${o:X}" for p, mn, md, o in dyn], " jump-to-RAM:", [f"{p:04X}->${o:04X}" for p, o in rams])
print("decode problems:", [f"{k}@{p:04X}" for k, p in brks])
