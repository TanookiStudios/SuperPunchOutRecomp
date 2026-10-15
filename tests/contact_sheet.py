#!/usr/bin/env python3
"""Glue several saved screenshots into one picture so a route can be checked at a glance.

  tests/contact_sheet.py out.png dumps/a.fb.bgrx dumps/b.fb.bgrx ...   (4 per row)

Reads the raw 256-wide BGRX screenshots a route's "dump" lines save. Needs only
Python and the macOS `sips` tool (no extra packages).
"""
import os, subprocess, sys, tempfile

def load(path):
    data = open(path, "rb").read()
    w = 256
    h = len(data) // (w * 4)
    return w, h, data

def main():
    out, files = sys.argv[1], sys.argv[2:]
    cols = 4
    imgs = [load(f) for f in files]
    h = max(i[1] for i in imgs)
    rows = (len(imgs) + cols - 1) // cols
    W, H = cols * 256 + (cols - 1) * 2, rows * h + (rows - 1) * 2
    buf = bytearray(b"\x40\x40\x40" * (W * H))
    for n, (w, ih, d) in enumerate(imgs):
        ox, oy = (n % cols) * 258, (n // cols) * (h + 2)
        for y in range(ih):
            row = d[y * w * 4:(y + 1) * w * 4]
            rgb = bytearray(w * 3)
            rgb[0::3] = row[2::4]; rgb[1::3] = row[1::4]; rgb[2::3] = row[0::4]
            o = ((oy + y) * W + ox) * 3
            buf[o:o + w * 3] = rgb
    ppm = tempfile.NamedTemporaryFile(suffix=".ppm", delete=False)
    ppm.write(b"P6 %d %d 255\n" % (W, H)); ppm.write(buf); ppm.close()
    subprocess.check_call(["sips", "-s", "format", "png", ppm.name, "--out", out], stdout=subprocess.DEVNULL)
    os.unlink(ppm.name)

main()
