#!/usr/bin/env bash
# How much of the game's real work now runs as recompiled (native) code?
# For each route: run it once with every recompiled function blocked (the interpreter does everything,
# "interp") and once normally ("native"), both with coverage recording, then compare how many NON-WAITING
# instructions the interpreter still had to run. (Waiting = tiny polling loops that spin until the next
# frame; the engine runs those in the interpreter on purpose and they would swamp the numbers.)
#   native share = 1 - (real work still interpreted in the normal build) / (real work in the all-interpreter run)
#   tests/native_share.sh [route names...]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
ROUTES=("$@"); [ ${#ROUTES[@]} -gt 0 ] || ROUTES=(route_attract route_menus route_fight_gabby route_win_next route_lose route_circuit_minor route_circuit_major route_circuit_world route_circuit_special)
mkdir -p build-game/share
for r in "${ROUTES[@]}"; do for mode in native interp; do
  ( COVERAGE=1 tests/run_route.sh "tests/$r.txt" $mode "$ROOT/build-game/share/$r-$mode" > "build-game/share/$r-$mode.log" 2>&1
    python3 vendor/snesrecomp/tools/tier2_ingest.py "build-game/share/$r-$mode/coverage.json" "build-game/share/$r-$mode/coverage.jsonl" \
      --cfg-dir recomp --program-manifest src/gen/program_manifest.json --json > "build-game/share/$r-$mode.ingest.json" ) &
done; done
wait
python3 - "${ROUTES[@]}" <<'PY'
import sys, json
sys.path.insert(0, "tests")
import interp_regions as ir
print(f"{'route':18s} {'all-interp real work':>22s} {'normal build real work':>23s} {'native share':>13s} | {'all instrs (interp run)':>24s} {'all instrs (normal)':>20s}")
T_i = T_n = 0
for r in sys.argv[1:]:
    res = {}
    for mode in ("interp", "native"):
        hits, mx, waits, regions = ir.compute([f"build-game/share/{r}-{mode}.ingest.json"])
        tot = sum(hits.values()); wn = sum(hits[p] for p in waits)
        res[mode] = (tot - wn, tot)
    ri, rn = res["interp"][0], res["native"][0]
    T_i += ri; T_n += rn
    print(f"{r:18s} {ri:>22,} {rn:>23,} {100*(1-rn/ri):>12.1f}% | {res['interp'][1]:>24,} {res['native'][1]:>20,}")
print(f"{'ALL ROUTES':18s} {T_i:>22,} {T_n:>23,} {100*(1-T_n/T_i):>12.1f}%")
PY
