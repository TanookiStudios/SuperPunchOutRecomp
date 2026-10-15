# Observations for the engine author (nothing here blocked the port)

1. **Native frame cut vs interpreter frame cut.** The same route, all-native vs interpreter, differs in
   ~13 bytes per frame (stack residue, a wait-loop counter, in-flight buffers). Not a codegen bug; the
   engine cannot pause compiled blocks mid-way. Details and a masked comparison that does hold: notes/native-coverage.md.
   Command: `tests/tier_check.sh`. Expected by a strict reader of the NES method: identical per-frame hashes. Observed: 26 of 3000 equal.
2. **A direct `JMP` from compiled code into a routine that has no compiled entry leaves no coverage record.**
   Example: the stub `0D:8049` (`JMP $F8C9`). Only indirect jumps are recorded as `goto_gap`; the interpreted
   instructions do show up in `hot_instructions`, so we recover the entry from there
   (`tests/promote_from_coverage.py --regions`). Expected: a gap record for the direct jump too.
3. **Compiled routines that run past the frame end are finished by the interpreter.** After a yield at a
   loop header, the whole remainder of the routine is interpreted (graphics decompression at `0D:F8C9`
   is about a third of the remaining interpreted work). Expected by a reader of `docs/MULTI_TIER.md`:
   resume native at the next loop header. Observed: `interp_bridge_lle_yield_unwind` resumes in LLE until the routine returns.
4. **`I_NMI`/`I_IRQ` with `emit = true` compile but are never entered.** The beam frame driver always runs
   interrupt vectors through `interp_bridge_run_interrupt`. The scaffold's `emit = false` for `I_NMI` is therefore the honest setting.
5. The scaffold CMakeLists in git commit `64e37be` does not link once the engine patches are applied; the current CMakeLists does.
