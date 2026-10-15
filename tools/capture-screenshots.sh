#!/usr/bin/env bash
# Release screenshots, unattended, into docs/screenshots/ (12 pictures):
#   gameplay-1..7   headless runs of the test routes (no window), enlarged 3x
#   launcher-*      the launcher's LNG_SCRIPT mode: its window shows for ~10 seconds
#   ingame-menu     the Esc menu: a game window shows for ~5 seconds
# Fails if any expected picture is missing. Needs rom/superpunchout.sfc, a built
# build/ (cmake -S . -B build; cmake --build build) and tests/ (the ROM never
# leaves this machine; only pictures are written). If ../SuperPunchOut-Site exists
# the same pictures are copied into its dist/assets/shots/.
# Every run uses a throwaway HOME, so your own settings and saves are never touched.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
BIN="${BIN:-$ROOT/build/SuperPunchOutRecomp}"
ROM="$ROOT/rom/superpunchout.sfc"
OUT=docs/screenshots; TMP="$ROOT/work/shots-release"
[ -x "$BIN" ] || { echo "build first: cmake -S . -B build && cmake --build build" >&2; exit 2; }
[ -f "$ROM" ] || { echo "missing $ROM" >&2; exit 2; }
rm -rf "$TMP"; mkdir -p "$OUT" "$TMP"

# --- gameplay: the pictures the test routes save at known moments ------------------
export BIN
tests/run_route.sh tests/route_fight_gabby.txt native "$TMP/gabby" >/dev/null
tests/run_route.sh tests/route_win_next.txt native "$TMP/winnext" >/dev/null
pick() {  # pick <out name> <route dir> <picture>
    python3 -I tools/png_scale.py "$TMP/$2/shots/$3.png" "$OUT/$1.png" 3
}
pick gameplay-1 gabby   fight_start
pick gameplay-2 gabby   play01
pick gameplay-3 winnext ko03
pick gameplay-4 winnext next_a
pick gameplay-5 winnext f200
pick gameplay-6 gabby   play02
pick gameplay-7 winnext after_ko

# --- demo settings: a few cheats ticked, so the Game page shows them on -------------
HOME_DIR="$TMP/home"
SETTINGS="$HOME_DIR/Library/Application Support/SuperPunchOutRecomp"
mkdir -p "$SETTINGS"
printf 'mute_mask=0\nmeter=1\nhit=1\nrest=0\nstart=0\n' > "$SETTINGS/superpunchout.ini"

# --- launcher pages (a window shows for about ten seconds) -------------------------
echo "A launcher window will show on screen for about 10 seconds; please don't click it."
HOME="$HOME_DIR" SDL_AUDIODRIVER=dummy \
LNG_SCRIPT="wait:40;shot:$TMP/launcher-main.png;view:game;wait:15;shot:$TMP/launcher-game.png;view:settings;wait:15;shot:$TMP/launcher-settings.png;view:about;wait:15;shot:$TMP/launcher-about.png;quit" \
    perl -e 'alarm 90; exec @ARGV' "$BIN" --launcher --rom "$ROM" >/dev/null 2>&1 || true
for n in launcher-main launcher-game launcher-settings launcher-about; do cp "$TMP/$n.png" "$OUT/$n.png"; done

# --- the Esc menu over a live scene (a window shows for about five seconds) ---------
echo "A game window will show on screen for about 5 seconds; please don't click it."
HOME="$HOME_DIR" SDL_AUDIODRIVER=dummy SNESRECOMP_NO_LAUNCHER=1 SNESRECOMP_RUN_FRAMES=1000 \
SNESRECOMP_RUNTIME_MENU_SELFTEST=900 SNESRECOMP_RUNTIME_MENU_DUMP="$TMP/ingame-menu.ppm" \
    perl -e 'alarm 90; exec @ARGV' "$BIN" --rom "$ROM" >/dev/null 2>&1 || true
sips -s format png "$TMP/ingame-menu.ppm" --out "$OUT/ingame-menu.png" >/dev/null

missing=0
for n in gameplay-1 gameplay-2 gameplay-3 gameplay-4 gameplay-5 gameplay-6 gameplay-7 ingame-menu launcher-main launcher-game launcher-settings launcher-about; do
    [ -s "$OUT/$n.png" ] || { echo "MISSING: $n" >&2; missing=1; }
done
[ "$missing" = 0 ] || exit 1

SITE="$ROOT/../SuperPunchOut-Site/dist/assets/shots"
if [ -d "$ROOT/../SuperPunchOut-Site/dist" ]; then
    mkdir -p "$SITE"; cp "$OUT"/*.png "$SITE"/
    echo "copied into the website folder"
fi
ls "$OUT"
