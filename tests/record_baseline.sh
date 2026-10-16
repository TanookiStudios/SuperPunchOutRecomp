#!/usr/bin/env bash
# Saves the runs in build-game/check/ (made by tests/check_baseline.sh) as the new baseline in tests/baseline/.
# Only do this on purpose: after a change that is meant to move timing or pictures, once the checks you trust
# (tests/tier_check.sh, the Snes9x comparison in tests/ref/) pass.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
for d in build-game/check/route_*/; do
  r=$(basename "$d")
  last=""; [ "$r" = route_lose ] && last=loss2
  python3 tests/logic_digest.py "build-game/check/$r" $last | cut -d' ' -f1 > "tests/baseline/$r.logic.sha1"
  cp "build-game/check/$r/digest.txt" "tests/baseline/$r.frames.sha1"
  if [ "$r" = route_fight_gabby ]; then cp "build-game/check/$r/hashes.txt" "tests/baseline/$r.frames.csv"
  else awk -F, '$1 % 50 == 0' "build-game/check/$r/hashes.txt" > "tests/baseline/$r.frames_every50.csv"; fi
  echo "recorded $r"
done
