#!/usr/bin/env python3
"""Turn coverage findings into recomp/symbols.toml entries (the "promote functions" step).

  1. run routes with COVERAGE=1 (tests/run_route.sh)
  2. python3 vendor/snesrecomp/tools/tier2_ingest.py <run>/coverage.json <run>/coverage.jsonl \
        --cfg-dir recomp --program-manifest src/gen/program_manifest.json --json > ingest.json
  3. python3 tests/promote_from_coverage.py ingest.json [more.json ...]
  4. bash tools/regen.sh && cmake --build build-game

Every place the interpreter had to take over for lack of a recompiled function (a call whose target
had none, or a jump that landed somewhere with no declared start) becomes an `emit = true` entry in the
block marked below. Entries already there are kept (so coverage only ever grows). Nothing outside the
block is touched, and src/gen is never edited.
"""
import json, re, sys, os
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOML = os.path.join(ROOT, "recomp", "symbols.toml")
BEGIN = "# >>> BEGIN coverage-promoted (written by tests/promote_from_coverage.py; do not hand-edit)"
END = "# <<< END coverage-promoted"

def norm(pc24):
    """LoROM: banks $80-$FF mirror $00-$7F. Only ROM addresses ($8000+) are promotable."""
    bank, addr = pc24 >> 16, pc24 & 0xFFFF
    if bank >= 0x80: bank -= 0x80
    if addr < 0x8000 or bank >= 0x70: return None
    return bank, addr

def main():
    text = open(TOML).read()
    a, b = text.find(BEGIN), text.find(END)
    head = text if a < 0 else text[:a].rstrip("\n") + "\n"
    tail = "" if b < 0 else text[b + len(END):].lstrip("\n")
    have = {}
    if a >= 0:
        data = tomllib.loads(text[a:b])
        for f in data.get("func", []):
            have[(f["bank"], int(f["addr"], 16))] = (f.get("entry_m", 1), f.get("entry_x", 1), f.get("note", ""))
    manual = set()
    for f in tomllib.loads(head).get("func", []):
        manual.add((f["bank"], int(f["addr"], 16)))
    new = 0
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    min_work = 200
    for a in sys.argv[1:]:
        if a.startswith("--min-work="): min_work = int(a.split("=")[1])
    if "--regions" in sys.argv:
        # Stretches of ROM code the interpreter ran with real work (not frame-wait polling): the first
        # address of each is where control left the recompiled code, i.e. a missing function start.
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import interp_regions
        hits, mx, waits, regions = interp_regions.compute(args)
        for lo, hi, n, k in regions:
            if n < min_work: continue
            kk = norm(lo)
            if kk is None or kk in have or kk in manual: continue
            have[kk] = (int(mx[lo][1]), int(mx[lo][3]), "interpreted region start")
            new += 1
        args = []
    for path in args:
        for d in json.load(open(path))["discoveries"]:
            if d["site_kind"] not in ("call_gap", "goto_gap"): continue
            k = norm(int(d["target_pc24"], 16))
            if k is None or k in have or k in manual: continue
            mx = d["entry_mx"]  # like "M1X0"
            have[k] = (int(mx[1]), int(mx[3]), "call target" if d["site_kind"] == "call_gap" else "jump landing")
            new += 1
    out = [head.rstrip("\n"), "", BEGIN]
    for (bank, addr), (m, x, note) in sorted(have.items()):
        out += ["[[func]]", f'name = "fn_{bank:02X}_{addr:04X}"', f'addr = "{addr:04x}"', f"bank = {bank}",
                "emit = true"] + ([f"entry_m = {m}"] if m != 1 else []) + ([f"entry_x = {x}"] if x != 1 else []) + \
               [f'note = "{note}"', ""]
    out += [END, tail]
    open(TOML, "w").write("\n".join(out).rstrip("\n") + "\n")
    print(f"promoted {new} new, {len(have)} total coverage-promoted functions")
main()
