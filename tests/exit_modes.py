#!/usr/bin/env python3
"""Work out the register widths a routine can return in, following its calls (a reading aid for writing
exit_mx_variant facts; the recompiler's analysis is the authority).
  tests/exit_modes.py BB:AAAA [m=1 x=0]
Prints the set of (M,X) widths at its returns, e.g. {M0X0}. PLP, a jump into RAM or an indexed jump
makes the answer 'unknown' for that path (shown as ?)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "vendor/snesrecomp/recompiler"))
import snes65816 as s
rom = open(os.path.join(ROOT, "rom/superpunchout.sfc"), "rb").read()
s.set_rom_image_size(len(rom)); s.set_rom_mapping("lorom")
memo, active = {}, set()

def exits(bank, pc0, m0, x0):
    key = (bank, pc0, m0, x0)
    if key in memo: return memo[key]
    if key in active: return set()          # recursion: contributes nothing new
    active.add(key)
    res, seen, work = set(), set(), [(pc0, m0, x0)]
    while work:
        pc, m, x = work.pop()
        while (pc, m, x) not in seen:
            seen.add((pc, m, x))
            i = s.decode_insn(rom, s.rom_offset(bank, pc), pc, bank, m, x)
            if i is None or i.mnem in ("BRK", "COP"): res.add("?"); break
            mn = i.mnem
            if mn == "REP": m = 0 if i.operand & 0x20 else m; x = 0 if i.operand & 0x10 else x
            if mn == "SEP": m = 1 if i.operand & 0x20 else m; x = 1 if i.operand & 0x10 else x
            if mn == "PLP": res.add("?"); break
            if mn in ("RTS", "RTL", "RTI"): res.add((m, x)); break
            if mn in ("JSR", "JSL"):
                if i.mode == 6 or mn == "JSL" and i.mode == 9:
                    tb = (i.operand >> 16) if mn == "JSL" else bank
                    ta = i.operand & 0xFFFF
                    if ta < 0x8000: res.add("?"); break
                    ex = exits(tb & 0x7F, ta, m, x)
                    if not ex: break
                    for e in ex:
                        if e == "?": res.add("?")
                        else: work.append((pc + i.length, e[0], e[1]))
                    break
                res.add("?"); break
            nxt = pc + i.length
            if mn in ("BCC","BCS","BEQ","BNE","BMI","BPL","BVC","BVS","BRA"):
                work.append((i.operand, m, x))
                if mn == "BRA": break
            elif mn == "BRL": work.append((i.operand, m, x)); break
            elif mn == "JMP" and i.mode == 6:
                if i.operand < 0x8000: res.add("?"); break
                work.append((i.operand, m, x)); break
            elif mn in ("JMP", "JML"):
                if mn == "JML" and i.mode == 9: 
                    work.append((i.operand & 0xFFFF, m, x)); break
                res.add("?"); break
            pc = nxt
    active.discard(key); memo[key] = res
    return res

if __name__ == "__main__":
    bank, pc = [int(v, 16) for v in sys.argv[1].split(":")]
    m = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    x = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    r = exits(bank, pc, m, x)
    print(f"{bank:02X}:{pc:04X} entered M{m}X{x} returns in: " + ", ".join(sorted(f"M{e[0]}X{e[1]}" if e != "?" else "?" for e in r)))
