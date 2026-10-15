#!/usr/bin/env python3
"""One number for "what state did the game end up in at every dump point of this route".
  python3 tests/logic_digest.py <run-dir> [last-tag]
SHA-1 over the game's RAM at each dump (in the order the route made them), with the bytes that
legitimately depend on sub-frame timing blanked out:
  $0600-$06FF   the stack page (leftover bytes below the stack pointer; where a frame is cut changes them)
  $0348, $0330  a free-running timer/flicker byte that counts wait-loop passes
Everything else (health, score, clock, sprites' logic, RNG-driven AI, scene state, VRAM-feeding buffers) is in.
The same route run all-native and all-interpreter gives the same number; so does a rebuild that
did not change gameplay. Not valid for the part of route_lose after the game restarts (the timer feeds the RNG)."""
import glob, hashlib, os, sys
run = sys.argv[1]; last = sys.argv[2] if len(sys.argv) > 2 else None
h = hashlib.sha1(); n = 0
for f in sorted(glob.glob(os.path.join(run, "dumps", "*.wram.bin")), key=os.path.getmtime):
    tag = os.path.basename(f)[:-9]
    d = bytearray(open(f, "rb").read())
    d[0x600:0x700] = bytes(0x100); d[0x348] = 0; d[0x330] = 0
    h.update(tag.encode()); h.update(bytes(d)); n += 1
    if tag == last: break
print(f"{h.hexdigest()} ({n} dumps)")
