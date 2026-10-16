# Checking the picture against Snes9x

The surest way to know our picture is right is to play the same inputs in a trusted emulator and put
the pictures side by side. This folder is that check. The emulator is **not** in this repo (and neither
is any game data): you download Snes9x's libretro core yourself.

## One-time setup
1. Download `snes9x_libretro.dylib.zip` (Mac, Apple chip) from
   https://buildbot.libretro.com/nightly/apple/osx/arm64/latest/ and unzip it somewhere outside the repo.
2. Build the little runner: `clang -O2 -o refhost tests/ref/refhost.c`

## Use
```sh
# Snes9x plays a route (only press / wait / dump lines; `until` and `poke` need our own host)
./refhost snes9x_libretro.dylib rom/superpunchout.sfc OUT_REF tests/route_fight_gabby.txt
# our game plays the same route and saves its pictures
tests/run_route.sh tests/route_fight_gabby.txt native OUT_OURS
# percent of pixels that differ at each `dump` (0.0 = identical)
python3 tests/ref/compare.py OUT_REF OUT_OURS/dumps
# ours on the left, Snes9x on the right, for the tags you name
python3 tests/ref/pair.py OUT_REF OUT_OURS/dumps pair.ppm fight_start play02
```
Rules of thumb: with no button presses the two should match to within a few frames (the title and the
"How to win" demo match pixel for pixel). With button presses the fights drift apart a little because
the two programs read the controller on slightly different frames, so judge those by eye.

## What this found (October 2026)
- Six long routines, when run as translated code, held back the game's raster interrupts and turned the
  picture on late, hiding the top bar. They now run in the original code (`kInterpTargets` in
  `src/game_rtl.c`).
- The game switches its screen effects on part-way down the picture and expects them to carry on from
  where they last stopped. The engine used to restart them, which garbled the top bar and the big
  knockdown numbers (`patches/0008`).
