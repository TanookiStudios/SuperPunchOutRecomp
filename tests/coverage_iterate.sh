#!/usr/bin/env bash
# One full turn of the native-coverage loop (about 5 minutes):
#   promote what the last coverage run found -> regenerate -> rebuild -> run routes with coverage -> summary
#   tests/coverage_iterate.sh [route names...]       (default: all routes)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOFTWARE:-${BASH_SOURCE[0]}}")/.." && pwd)"
cd "$ROOT"
ROUTES=("$@"); [ ${#ROUTES[@]} -gt 0 ] || ROUTES=(route_attract route_fight_gabby route_win_next route_menus route_lose route_circuit_minor route_circuit_major route_circuit_world route_circuit_special)
INGEST=(); for r in "${ROUTES[@]}"; do INGEST+=("build-game/cov/$r.ingest.json"); done
python3 tests/promote_from_coverage.py --regions "${INGEST[@]}"
python3 tests/promote_from_coverage.py "${INGEST[@]}"
bash tools/regen.sh 2>&1 | grep -E 'analysis: [0-9]+ roots|AOT-eligible|error|Error|rror:' || true
tests/build_game.sh | tail -1
tests/coverage_check.sh "${ROUTES[@]}" | tail -4
python3 tests/interp_regions.py "${INGEST[@]}" | head -14
python3 tests/lle_report.py | head -3
