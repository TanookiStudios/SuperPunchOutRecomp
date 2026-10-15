#!/usr/bin/env bash
# Builds the game into build-game/ with the working-tree CMakeLists.txt (which now lists the cheats and the
# UI files) on the patched engine in vendor/, plus tests/spo_stats.c (a test-only counter printed at exit).
# The CMakeLists.txt is copied into a small stand-in folder so the test build never touches your own build/.
#   tests/build_game.sh            configure (first time) and build
# Set CMAKELISTS_FROM=rev (and CMAKELISTS_REV=<commit>) to use a committed CMakeLists.txt instead.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
SHIM="$ROOT/build-game/_src"
mkdir -p "$SHIM"
if [ "${CMAKELISTS_FROM:-working}" = "working" ]; then cp CMakeLists.txt "$SHIM/CMakeLists.txt"
else git show "${CMAKELISTS_REV:-HEAD}:CMakeLists.txt" > "$SHIM/CMakeLists.txt"; fi
for f in *; do
  case "$f" in CMakeLists.txt|build*|tests|dist|work) continue ;; esac
  [ -e "$SHIM/$f" ] || ln -s "$ROOT/$f" "$SHIM/$f"
done
cmake -S "$SHIM" -B "$ROOT/build-game" -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PROJECT_SuperPunchOutRecomp_INCLUDE="$ROOT/tests/extras_build.cmake" > "$ROOT/build-game/configure.log" 2>&1 \
  || { tail -20 "$ROOT/build-game/configure.log"; exit 1; }
cmake --build "$ROOT/build-game" 2>&1 | grep -E 'error|Error|FAILED|Linking' || true
ls -la "$ROOT/build-game/SuperPunchOutRecomp"
