#!/usr/bin/env python3
"""Show which stretches of game code the interpreter still ran, biggest first.
  python3 tests/interp_regions.py build-game/cov/*.ingest.json
Runs of neighbouring instructions are merged (gap under 12 bytes). The first address of a
region is where to look for a missing function start."""
import json, sys, collections, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vendor/snesrecomp/recompiler"))
import snes65816 as sn
ROM = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rom/superpunchout.sfc"), "rb").read()
sn.set_rom_image_size(len(ROM)); sn.set_rom_mapping("lorom")
BRANCH = {"BNE", "BEQ", "BMI", "BPL", "BCC", "BCS", "BVC", "BVS", "BRA"}
READONLY = {"LDA", "CMP", "AND", "BIT", "LDX", "LDY", "CPX", "CPY", "ORA", "EOR", "NOP"}

def wait_loop_pcs(hits):
    """PCs that belong to a tiny polling loop (a backward branch over read-only instructions):
    the game waiting for the next frame / a flag the interrupt sets. The engine runs these in the
    interpreter on purpose (it hands control back to the frame driver there), so they are counted
    separately from real work."""
    out = set()
    for pc in hits:
        bank, a = pc >> 16, pc & 0xFFFF
        try:
            i = sn.decode_insn(ROM, sn.rom_offset(bank, a), a, bank, 1, 0)
        except Exception:
            continue
        if i is None or i.mnem not in BRANCH or not (a - 8 <= i.operand <= a): continue
        pcs, cur, ok = [], i.operand, True
        while cur <= a:
            j = sn.decode_insn(ROM, sn.rom_offset(bank, cur), cur, bank, 1, 0)
            if j is None or (j.mnem not in READONLY and j.mnem not in BRANCH and cur != a) : ok = False; break
            pcs.append((bank << 16) | cur); cur += j.length
        if ok and len(pcs) <= 4: out.update(pcs)
    return out

def compute(paths):
    hits = collections.Counter(); mx = {}
    for p in paths:
        for h in json.load(open(p))["hot_instructions"]:
            pc = int(h["target_pc24"], 16)
            hits[pc] += h["interpreted_instructions"]
            mx.setdefault(pc, h["entry_mx"])
    waits = wait_loop_pcs(hits)
    regions = []
    for pc in sorted(hits):
        if regions and pc - regions[-1][1] < 12 and (pc >> 16) == (regions[-1][1] >> 16):
            regions[-1][1] = pc; regions[-1][2] += hits[pc] if pc not in waits else 0; regions[-1][3] += 1
        else:
            regions.append([pc, pc, hits[pc] if pc not in waits else 0, 1])
    return hits, mx, waits, regions

def main():
    hits, mx, waits, regions = compute(sys.argv[1:])
    tot = sum(hits.values()); wait_n = sum(hits[p] for p in waits)
    print(f"total interpreted instruction executions: {tot:,}; {len(hits)} distinct instruction addresses in {len(regions)} regions")
    print(f"  of which waiting-for-the-next-frame polling loops: {wait_n:,} ({100*wait_n/tot:.1f}%); real work: {tot-wait_n:,} ({100*(tot-wait_n)/tot:.1f}%); distinct poll-loop addresses: {len(waits)}")
    print("regions ranked by real work (polling loops excluded):")
    for lo, hi, n, k in sorted(regions, key=lambda r: -r[2])[:40]:
        print(f"{lo:06X}-{hi:06X}  {n:>12,} ({100*n/max(1,tot-wait_n):5.1f}% of real work)  {k} instrs")

if __name__ == "__main__":
    main()
