#!/usr/bin/env bash
# One round of the coverage loop. Runs every route with coverage recording, then prints per route:
#   how many game instructions the interpreter still had to run (the NOT-yet-native work),
#   and how many places it had to take over (the gaps to promote next).
# Gap lists are saved as build-game/cov/<route>.ingest.json; feed them to tests/promote_from_coverage.py.
#   tests/coverage_check.sh [route names...]      (default: all route_*.txt except cheat routes)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
ROUTES=("$@"); [ ${#ROUTES[@]} -gt 0 ] || ROUTES=(route_attract route_fight_gabby route_win_next route_lose)
mkdir -p build-game/cov
for r in "${ROUTES[@]}"; do
  ( COVERAGE=1 tests/run_route.sh "tests/$r.txt" native "$ROOT/build-game/cov/$r" > "build-game/cov/$r.log" 2>&1
    python3 vendor/snesrecomp/tools/tier2_ingest.py "build-game/cov/$r/coverage.json" "build-game/cov/$r/coverage.jsonl" \
      --cfg-dir recomp --program-manifest src/gen/program_manifest.json --json > "build-game/cov/$r.ingest.json" ) &
done
wait
python3 - "${ROUTES[@]}" <<'PY'
import json, sys, collections
tot_i = tot_c = 0
for r in sys.argv[1:]:
    d = json.load(open(f"build-game/cov/{r}.ingest.json"))
    kinds = collections.Counter(x["site_kind"] for x in d["discoveries"])
    nodes = len({x["target_pc24"] for x in d["discoveries"]})
    print(f"{r:20s} interpreted_instructions={d['interpreted_instructions']:>12,} guest_cycles={d['interpreted_guest_cycles']:>13,} gaps={dict(kinds)} distinct_targets={nodes}")
    tot_i += d["interpreted_instructions"]; tot_c += d["interpreted_guest_cycles"]
print(f"{'TOTAL':20s} interpreted_instructions={tot_i:>12,} guest_cycles={tot_c:>13,}")
PY
