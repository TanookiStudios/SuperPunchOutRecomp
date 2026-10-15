#!/usr/bin/env bash
# Run one input route headless and save screenshots, state dumps and a per-frame
# game-state hash. No window opens, no sound plays, nothing touches your real saves.
#
#   tests/run_route.sh tests/route_attract.txt [native|interp] [out-dir]
#
# A route is a plain input script the game host reads (press / wait / until /
# poke / dump ...). Extra header lines start with "#@":
#   #@ frames=6000      how many game frames to run (required)
#   #@ netenv=NAME=VAL  extra environment for this route (optional, repeatable)
#
# Modes:
#   native  the normal build: recompiled code where we have it, interpreter for the rest
#   interp  same build, but every recompiled function is blocked so the ORIGINAL game code
#           runs in the interpreter only (the "answer key" to compare against)
#
# Output (default build-game/route-out/<route>-<mode>/):
#   trace.csv    one line per frame: frame, hash of all 128 KB of game RAM, CPU registers
#   hashes.txt   frame,hash only (the CPU registers can differ at a frame edge legally)
#   digest.txt   one SHA-1 over hashes.txt, the single number to compare between runs
#   dumps/       <tag>.fb.bmp (screenshot), <tag>.wram.bin etc. from the route's "dump" lines
#   shots/       the same screenshots as PNG
#   run.log      what the host printed
# Environment: BIN (executable), ROM, SPO_EXTRA_ENV (extra VAR=VALUE words), TIMEOUT (seconds),
#   COVERAGE=1 also records which game code was run by the interpreter (coverage.json + .jsonl)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROUTE="${1:?usage: run_route.sh <route.txt> [native|interp] [out-dir]}"
MODE="${2:-native}"
NAME="$(basename "$ROUTE" .txt)"
OUT="${3:-$ROOT/build-game/route-out/$NAME-$MODE}"
BIN="${BIN:-$ROOT/build-game/SuperPunchOutRecomp}"
ROM="${ROM:-$ROOT/rom/superpunchout.sfc}"
TIMEOUT="${TIMEOUT:-900}"
case "$ROUTE" in /*) ;; *) ROUTE="$PWD/$ROUTE" ;; esac
case "$OUT" in /*) ;; *) OUT="$PWD/$OUT" ;; esac

FRAMES=$(sed -n 's/^#@ *frames=\([0-9]*\).*/\1/p' "$ROUTE" | head -1)
[ -n "$FRAMES" ] || { echo "run_route: $ROUTE has no '#@ frames=N' line" >&2; exit 2; }
[ -x "$BIN" ] || { echo "run_route: build first: cmake --build build-game ($BIN missing)" >&2; exit 2; }

rm -rf "$OUT"; mkdir -p "$OUT/dumps" "$OUT/shots" "$OUT/cwd"
# A throwaway working folder: fresh config and an EMPTY save, so every run starts the same
# and your real saves are never touched. (--config stops the game from anchoring to the
# executable's folder; saves/ then lands in this folder.)
cat > "$OUT/cwd/config.ini" <<CFG
[General]
Autosave = 0
DisableFrameDelay = 1
[Sound]
EnableAudio = 0
CFG

EXTRA=()
if [ "$MODE" = "interp" ]; then
  # Every compiled entry point (and its $80 mirror) goes on the "run it in the interpreter" list.
  grep -ho '{ 0x[0-9A-Fa-f]\{6\}u' "$ROOT/src/gen/dispatch_v2.c" | sed 's/{ 0x//; s/u//' | \
    while read -r a; do echo "$a"; printf '%06X\n' $((0x$a + 0x800000)); done > "$OUT/aot_roots.txt"
  EXTRA+=("SNESRECOMP_LLE_INTERP_TARGET_FILE=$OUT/aot_roots.txt")
fi
while IFS= read -r l; do EXTRA+=("$l"); done < <(sed -n 's/^#@ *netenv=\(.*\)/\1/p' "$ROUTE")
if [ "${COVERAGE:-0}" = "1" ]; then
  EXTRA+=("SNESRECOMP_TIER2_CAPTURE=1" "SNESRECOMP_TIER2_MANIFEST=$OUT/coverage.json" "SNESRECOMP_TIER2_JOURNAL=$OUT/coverage.jsonl")
fi
# shellcheck disable=SC2206
[ -n "${SPO_EXTRA_ENV:-}" ] && EXTRA+=($SPO_EXTRA_ENV)

cd "$OUT/cwd"
set +e
env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy SNESRECOMP_NO_LAUNCHER=1 \
    SNESRECOMP_RUN_FRAMES="$FRAMES" SNESRECOMP_STATE_TRACE="$OUT/trace.csv" \
    SNESRECOMP_DUMP_DIR="$OUT/dumps" ${EXTRA[@]+"${EXTRA[@]}"} \
    perl -e 'alarm shift; exec @ARGV' "$TIMEOUT" \
    "$BIN" --config config.ini --rom "$ROM" --script "$ROUTE" > "$OUT/run.log" 2>&1
RC=$?
set -e
cut -d, -f1,2 "$OUT/trace.csv" > "$OUT/hashes.txt"
shasum "$OUT/hashes.txt" | cut -d' ' -f1 > "$OUT/digest.txt"
for f in "$OUT"/dumps/*.fb.bmp; do
  [ -e "$f" ] || continue
  sips -s format png "$f" --out "$OUT/shots/$(basename "$f" .fb.bmp).png" >/dev/null 2>&1 || true
done
echo "route=$NAME mode=$MODE exit=$RC frames=$(wc -l < "$OUT/trace.csv" | tr -d ' ') digest=$(cat "$OUT/digest.txt") out=$OUT"
grep -E 'script f=|timed out|Error|FATAL' "$OUT/run.log" | tail -n "${SPO_LOG_LINES:-5}" || true
exit $RC
