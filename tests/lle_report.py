#!/usr/bin/env python3
"""List the functions the analysis refused to turn into native code and why (from src/gen/program_manifest.json).
Root causes (no dependency on another refused function) are printed first."""
import json, re, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = json.load(open(os.path.join(ROOT, "src/gen/program_manifest.json")))
nodes = m["nodes"]
lle = {k: n for k, n in nodes.items() if n["disposition"] == "lle_only"}
def callee(reason):
    mm = re.match(r"unproven_call_at_([0-9A-F]+)_to_([0-9A-F]+)_m(\d)x(\d)", reason)
    return f"{mm.group(2)}:M{mm.group(3)}X{mm.group(4)}" if mm else None
roots, deps = [], []
for k, n in sorted(lle.items()):
    callees = [callee(r) for r in n["reasons"] if callee(r)]
    (deps if any(c in lle for c in callees) else roots).append((k, n))
print(f"{len(lle)} refused of {len(nodes)} analysed; {len(roots)} root causes, {len(deps)} only because they call a refused one")
for title, lst in (("ROOT CAUSES", roots), ("DEPENDENT", deps)):
    print("==", title)
    for k, n in lst:
        print(f"{k} insns={n.get('instruction_count')} {','.join(n['reasons'][:4])}")
