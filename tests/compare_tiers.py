#!/usr/bin/env python3
"""Compare the same route run all-native vs all-interpreter, at every screenshot/state dump the route makes.
  python3 tests/compare_tiers.py build-game/share/route_X-native build-game/share/route_X-interp
The two tiers cut each frame at slightly different instructions (compiled code cannot be paused mid-block),
so whole-memory hashes are NOT expected to match frame by frame. What must match is the game's state:
this prints, per dump, how many of the 131072 RAM bytes differ and where, plus screen pixels that differ."""
import glob, os, sys, collections
a, b = sys.argv[1], sys.argv[2]
def region(ad):
    if ad < 0x100: return "direct-page scratch"
    if ad < 0x300: return "sprite list copy"
    if 0x600 <= ad < 0x700: return "stack page"
    if ad >= 0x10000: return "bank 7F buffers"
    return "other low RAM"
tot = collections.Counter()
print(f"{'dump':14s} {'RAM bytes differ':>16s} {'pixels differ':>14s}  where")
for f in sorted(glob.glob(os.path.join(a, "dumps", "*.wram.bin")), key=os.path.getmtime):
    tag = os.path.basename(f)[:-9]
    g = os.path.join(b, "dumps", tag + ".wram.bin")
    if not os.path.exists(g): continue
    x, y = open(f, "rb").read(), open(g, "rb").read()
    d = [i for i in range(len(x)) if x[i] != y[i]]
    rc = collections.Counter(region(i) for i in d)
    fa, fb = open(f[:-9] + ".fb.bgrx", "rb").read(), open(g[:-9] + ".fb.bgrx", "rb").read()
    px = sum(1 for i in range(0, min(len(fa), len(fb)), 4) if fa[i:i+3] != fb[i:i+3])
    print(f"{tag:14s} {len(d):>16d} {px:>14d}  {dict(rc)}")
    tot["dumps"] += 1; tot["identical_ram"] += (len(d) == 0); tot["identical_px"] += (px == 0)
print(dict(tot))
