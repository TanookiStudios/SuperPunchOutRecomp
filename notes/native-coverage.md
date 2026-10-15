# Native coverage and tier equivalence (measured, final build)

Plain-English version: the recompiler turned **1,343 routines** (798 starting points, grown from what the game
actually ran) into real C code. About **55% of the game's real, non-idle work** now runs as that C code
(about 64-67% in an ordinary fight; lower in the long cheat-driven runs that play every boxer and the ending
credits). The rest still runs in the interpreter, which executes the original game code byte for byte. That
is how this engine is built, not a hole in the port: see "What stays interpreted and why". Where we compared
the two against each other they play the same game.

## How it was measured
* **Routes** (tests/route_*.txt, one line each in tests/README.md) were run with coverage recording
  (`tests/coverage_check.sh`), which lists every place the interpreter had to take over.
* Each such place became an entry in `recomp/symbols.toml` (`tests/promote_from_coverage.py`) and the whole
  program was regenerated (`bash tools/regen.sh`, never partial, `src/gen` never touched by hand).
  Loop: run, promote, regenerate, rebuild (`tests/coverage_iterate.sh`).
* **Idle polling is counted separately.** About 90-94% of all interpreted instructions are the game
  spinning in a two-instruction loop until the next frame starts (for example `LDA $4B / BNE`). They are
  not work. `tests/interp_regions.py` finds them and leaves them out.
* **Native share** = 1 - (real work still interpreted in the normal build) / (real work in a run where every
  recompiled function is blocked so the interpreter does everything). Both runs are the same route
  (`tests/native_share.sh`).

## Numbers (final build, 9 routes, 168,949,381 real instructions in the all-interpreter runs)
| Route | Real work, all-interpreter | Real work still interpreted | Native share |
|---|---|---|---|
| attract (6000 frames, no input) | 10,555,834 | 3,775,710 | 64.2% |
| menus | 6,023,804 | 2,076,701 | 65.5% |
| fight Gabby Jay | 13,581,238 | 4,501,790 | 66.9% |
| win, next boxer | 18,381,686 | 7,130,426 | 61.2% |
| lose until Game Over, back to menu | 38,052,355 | 13,187,600 | 65.3% |
| Minor / Major / World / Special circuit (all 16 boxers, with the cheat switches; Special ends in the credits) | 20.2-21.1M each | 10.7-11.6M each | 44.8-47.0% |
| **all routes** | **168,949,381** | **75,101,714** | **55.5%** (by guest cycles: 54.4%) |

The coverage tool's own raw view of the first attract-and-fight capture listed 765 places where the interpreter
had to take over (a call or jump with no compiled target). On the final build every route lists 2 to 20
(`tests/coverage_check.sh`), all of them the deliberate cases below. Interpreted instructions per route
are mostly idle polling: for attract, 77.4M interpreted, of which 73.6M (95%) are the wait-for-next-frame loops.

Promoted routines: 1,343 compiled variants of 1,374 analyzed; 31 variants refused (listed by
`tests/lle_report.py`; every refusal has a reason, below).

## What stays interpreted and why
1. **Interrupt handlers and the top-level frame loop (by design).** The engine's frame driver always enters
   NMI and IRQ through the interpreter (`snes_beam_frame_driver_run_frame` -> `run_interrupt` ->
   `interp_bridge_run_interrupt`) and only switches to compiled code when that code CALLS a routine.
   Proof: setting `I_NMI` to `emit = true` compiled it and changed nothing (identical interpreter step count
   before and after: 78,264,621 on the attract route). So the NMI body, the IRQ body and the `JMP`-chained
   mode loops stay interpreted; the routines they call are native.
2. **Routines resumed after a yield.** A compiled routine that is still running when the frame ends (long
   loops such as the graphics decompressor at `0D:F8C9`, 13,000 passes) unwinds to the frame driver and is
   resumed by the interpreter from that exact instruction. The same happens at polls of hardware that
   answers later (the sound-command handshake at `01:EC00`, waiting on the sound chip's ports).
   About 80% of the remaining real work is this; it is the largest single piece (decompression alone is
   a third to a half of it).
3. **Code that lives in RAM** (copied there from the ROM at run time; `$1000`, `$00D0`, `$7E:4143`):
   2%. Its bytes are not in the ROM, and `$00D0` is patched by the game while it runs.
4. **16 routines refused on purpose** (`notes/coverage-facts.md`): the mode switch `JML [$51]` (destination is
   a pointer the game stores in RAM), routines that end by jumping into RAM code, and the `00:DEBB` family
   where the original game runs 8-bit code with a 16-bit accumulator on one path. Declaring widths there
   would change the game, so only the interpreter runs them.
Not covered by any route: Time Attack and Records View (the menu cursor wraps and kept landing on Button
Setting, see tests/gen_routes.py `route_menus`), 2-player, and the rest of the Special/credits flow beyond
what route_circuit_special shows. Code only those reach stays with the interpreter until a route reaches it.

## Hand-written facts
`notes/coverage-facts.md` lists every cfg directive written by hand (one exit width, 18 jump-table sizes) with
the reason it is true. It took the refused routines from 69 to 16 on the early routes.

## Tier equivalence: does the native code play the same game as the original code?
Strict per-frame hash equality native vs interpreter is **not** achievable here and was measured to say why:
compiled code cannot be paused in the middle of a block, so the frame is cut at a slightly different
instruction than in the interpreter. Across 3000 attract frames only 26 frames hash identically; the median
frame differs in 13 of 131,072 bytes, almost all in the stack page (leftover bytes below the stack pointer).
The rest are a free-running counter at `$0348` and in-flight work (a half-decompressed buffer) at the
moment the frame is cut.

What does hold, and is checked by `tests/tier_check.sh` (PASS on the final build):
`tests/logic_digest.py` hashes the game's RAM at every dump point of a route with only the stack page and
the two timing bytes `$0348`, `$0330` blanked.
| Route | Dump points compared | native vs interpreter |
|---|---|---|
| fight Gabby Jay | 9 | identical `4bc235b8...` |
| win, KO, results, next card, second fight | 13 | identical `fd6f2d50...` |
| lose three fights in a row (through the third loss) | 10 | identical `1f94d4a0...` |
Those dumps include health, score, clock, both boxers, scene state, the sprite lists and the sound state,
across KOs, results screens and cards.

Not identical, reported plainly: the attract demo and the four circuit routes differ by a frame or two of
animation phase (a handful of timer bytes off by 1-3 in one fighter's struct, ~5,000-19,000 pixels in the frames
where a sprite is mid-step), because the timing counter differs and feeds the random choices. In
`route_lose`, after the game restarts (Game Over, Continue) the same counter makes the next fight go
differently, so only the first three losses are compared. None of these differences touches game
rules: scores, health totals, REST and win/loss results agree where compared (`tests/compare_tiers.py`).

## Baselines (tests/baseline/)
`check_baseline.sh` re-runs every route on the current build.
* `*.logic.sha1`: the logic digest. Must stay equal after any change that is not meant to change gameplay.
* `*.frames.sha1`: one digest over EVERY frame's full-RAM hash. Equal only for the identical generated code
  and engine; a mismatch with equal logic digests means timing moved, gameplay did not.
* `route_fight_gabby.frames.csv`: the full 6000-frame list; other routes keep every 50th frame.
All nine routes reproduce (run twice on the final build). The vendor engine patches (menu, scale,
controller database, settings folder) and the cheats code (all off) do not change a single frame hash:
the 6000-frame fight digest is `7b35d2c2b0eb16ef00a3347994380ae3e5133d42` before and after.
Cheats-off inertness was also re-proven on the final build against a build whose cheats function does
nothing: identical every-frame digests on attract, menus, fight, win-next and lose.
