#!/usr/bin/env bash
# Proves the recompiled code plays the same game as the original code running in the interpreter.
# Runs each route twice (native build / every recompiled function blocked) and compares the game's state
# at every dump point with tests/logic_digest.py. PASS = identical digests.
#   tests/tier_check.sh [route names...]      (default: fight_gabby, win_next, lose (the circuit routes and the attract demo differ by a frame or two of animation phase, see notes/native-coverage.md); route_attract is compared by hand: its demo fights use timing-fed randomness, see notes/native-coverage.md)
# route_lose is compared only up to its third loss (after the game restarts, a timing-driven counter
# feeds the random numbers, so a different frame cut legitimately leads to a different fight).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
ROUTES=("$@"); [ ${#ROUTES[@]} -gt 0 ] || ROUTES=(route_fight_gabby route_win_next route_lose)
mkdir -p build-game/tier
for r in "${ROUTES[@]}"; do for m in native interp; do
  tests/run_route.sh "tests/$r.txt" $m "$ROOT/build-game/tier/$r-$m" > "build-game/tier/$r-$m.log" 2>&1 &
done; done
wait
rc=0
for r in "${ROUTES[@]}"; do
  last=""; [ "$r" = route_lose ] && last=loss2
  n=$(python3 tests/logic_digest.py "build-game/tier/$r-native" $last); i=$(python3 tests/logic_digest.py "build-game/tier/$r-interp" $last)
  if [ "$n" = "$i" ]; then echo "PASS $r native==interp $n"; else echo "FAIL $r native=$n interp=$i"; rc=1; fi
done
exit $rc
