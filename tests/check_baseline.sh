#!/usr/bin/env bash
# Re-runs the routes on the current build and checks them against the saved first recording in tests/baseline/.
#   <route>.logic.sha1   the game's state at every dump point (stack residue and the timing counter blanked);
#                        must stay equal after ANY change that is not meant to change gameplay
#   <route>.frames.sha1  the one-number digest of EVERY frame's full-memory hash; equal only for the exact same
#                        generated code + engine (any recompile that changes timing changes it) - a mismatch
#                        here with equal logic digests means "timing moved, gameplay did not"
#   route_fight_gabby.frames.csv  the full 6000-frame list, to find the first frame that differs
#   tests/check_baseline.sh [route names...]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
ROUTES=("$@"); [ ${#ROUTES[@]} -gt 0 ] || ROUTES=(route_attract route_menus route_fight_gabby route_win_next route_lose route_circuit_minor route_circuit_major route_circuit_world route_circuit_special)
mkdir -p build-game/check
for r in "${ROUTES[@]}"; do tests/run_route.sh "tests/$r.txt" native "$ROOT/build-game/check/$r" > "build-game/check/$r.log" 2>&1 & done
wait
rc=0
for r in "${ROUTES[@]}"; do
  last=""; [ "$r" = route_lose ] && last=loss2
  l=$(python3 tests/logic_digest.py "build-game/check/$r" $last | cut -d' ' -f1); f=$(cat "build-game/check/$r/digest.txt")
  [ "$l" = "$(cat tests/baseline/$r.logic.sha1)" ] && ls_="logic OK" || { ls_="logic CHANGED"; rc=1; }
  [ "$f" = "$(cat tests/baseline/$r.frames.sha1)" ] && fs_="every-frame hashes identical" || fs_="every-frame hashes differ (expected after any recompile)"
  echo "$r: $ls_; $fs_"
done
exit $rc
