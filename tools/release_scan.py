#!/usr/bin/env python3
"""Fail loudly if a staged release folder holds the ROM, or anything made from it.

    tools/release_scan.py <staged-folder>     scan one package folder
    tools/release_scan.py --self-test         prove the scan can fail

The three make_* scripts run this on the folder BEFORE it is zipped. It checks:
  - no .sfc/.smc/.srm/.state files, no rom.cfg (names a path on this machine),
    no generated .c/.h source, no src/gen or recomp folder;
  - no file is byte-for-byte the ROM;
  - no file contains any of several 32-byte samples cut from the ROM.
"""
import hashlib
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROM = os.path.join(ROOT, "rom", "superpunchout.sfc")
IDENTITY = os.path.join(ROOT, "rom_identity.txt")

BAD_EXT = {".sfc", ".smc", ".srm", ".state", ".cycstate", ".c", ".cpp", ".h"}
BAD_NAMES = {"rom.cfg"}
BAD_DIRS = {"gen", "recomp", "src", "rom"}
SAMPLE_LEN = 32


def expected_sha():
    with open(IDENTITY, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\s*expected_sha256\s*=\s*(\S+)", line)
            if m:
                return m.group(1).strip('"').lower()
    sys.exit("release_scan: no expected_sha256 in rom_identity.txt")


def pick_samples(rom):
    """Several 32-byte windows with plenty of distinct bytes (not blank runs)."""
    out = []
    for i in range(1, 8):
        base = len(rom) * i // 8
        for off in range(base, base + 4096):
            w = rom[off:off + SAMPLE_LEN]
            if len(set(w)) >= 20:
                out.append(w)
                break
    if len(out) < 5:
        sys.exit("release_scan: could not pick ROM samples")
    return out


def scan(folder, rom):
    rom_sha = hashlib.sha256(rom).hexdigest()
    samples = pick_samples(rom)
    problems, nfiles, nbytes = [], 0, 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for d in dirnames:
            if d in BAD_DIRS:
                problems.append(f"forbidden folder: {os.path.join(dirpath, d)}")
        for name in filenames:
            p = os.path.join(dirpath, name)
            nfiles += 1
            if name.lower() in BAD_NAMES or os.path.splitext(name)[1].lower() in BAD_EXT:
                problems.append(f"forbidden file type: {p}")
            if os.path.islink(p):
                problems.append(f"symlink (not scanned): {p}")
                continue
            with open(p, "rb") as f:
                data = f.read()
            nbytes += len(data)
            if hashlib.sha256(data).hexdigest() == rom_sha:
                problems.append(f"IS THE ROM: {p}")
            for i, s in enumerate(samples):
                if s in data:
                    problems.append(f"contains ROM bytes (sample {i}): {p}")
                    break
    return problems, nfiles, nbytes, len(samples)


def load_rom():
    if not os.path.isfile(ROM):
        sys.exit(f"release_scan: ROM not found at {ROM}; cannot prove the package is clean")
    with open(ROM, "rb") as f:
        rom = f.read()
    if hashlib.sha256(rom).hexdigest() != expected_sha():
        sys.exit("release_scan: rom/superpunchout.sfc is not the expected ROM (SHA-256 mismatch)")
    return rom


def self_test(rom):
    """Each bad package must be caught; a clean one must pass."""
    samples = pick_samples(rom)
    cases = {
        "ROM bytes inside a binary": lambda d: open(os.path.join(d, "prog"), "wb").write(b"x" * 99 + samples[2] + b"y" * 99),
        "a .sfc file": lambda d: open(os.path.join(d, "game.sfc"), "wb").write(b"x"),
        "rom.cfg": lambda d: open(os.path.join(d, "rom.cfg"), "w").write("rom/x.sfc"),
        "a generated .c file": lambda d: open(os.path.join(d, "bank00.c"), "w").write("int x;"),
        "the whole ROM renamed": lambda d: open(os.path.join(d, "data.bin"), "wb").write(rom),
    }
    for label, make in cases.items():
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
            make(d)
            problems = scan(d, rom)[0]
            if not problems:
                sys.exit(f"SELF-TEST FAILED: scan did not catch {label}")
            print(f"  caught {label}: {problems[0].split(':')[0]}")
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
        open(os.path.join(d, "prog"), "wb").write(os.urandom(4096))
        if scan(d, rom)[0]:
            sys.exit("SELF-TEST FAILED: clean folder was flagged")
    print("  clean folder passes")
    print("release_scan self-test OK")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test(load_rom())
        return
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        sys.exit(__doc__)
    problems, nfiles, nbytes, ns = scan(sys.argv[1], load_rom())
    if problems:
        print("ROM SAFETY SCAN FAILED, do not ship this package:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        sys.exit(1)
    print(f"ROM safety scan passed: {nfiles} files, {nbytes} bytes, {ns} ROM samples, SHA-256 compared, no ROM-type files")


if __name__ == "__main__":
    main()
