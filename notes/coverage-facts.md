# Hand-written facts given to the recompiler

Everything here is in `recomp/bank*.cfg`, below the line `# --- hand-written facts`. The generated block above
that line is rewritten from `recomp/symbols.toml` by `tools/regen.sh`; the facts below it are kept.
Each one was read out of the ROM and checked, not guessed. A fact the recompiler cannot use (or that turns out
wrong) falls back to the interpreter, which runs the original bytes, so a too-small table is safe.

## Exit widths
| Fact | Why it is true |
|---|---|
| `exit_mx_variant 01EC00 1 0 1 0` | `$01:EC00` (the sound-command sender) does PHP on entry; every path ends at `$EC25..$EC28` (PLB, PLD, PLP, RTL). The flags come back as they went in, so entered 8-bit-A / 16-bit-X it leaves the same way. (`tests/fn_info.py 01:EC00 1 0` shows the single return.) Cleared 18 functions that had been refused only because this exit was "unproven". |

## Indexed jump tables (`indirect_dispatch <site> <entries> idx:X`)
Each site is a `JMP ($table,X)`. The table was read with `tests/jmptable.py` and sized to the entries that are real code
in the same bank; entries after the last valid one are the next routine's code or art data.

| Site | Table | Entries | Note |
|---|---|---|---|
| `00:DA47` | `DAD3` | 5 | sprite-animation script commands. Entry 5 is $0000 (unused), entries 6+ decode as data (COP/BRK), so they are left out |
| `00:E1C2` | `E1C5` | 16 | |
| `00:B270` | `B275` | 4 | fight-loop handlers |
| `00:E2A1` | `E2A4` | 3 | entry 0 is $0000 (unused) |
| `00:B713` | `B716` | 4 | the fifth word is the next routine's code |
| `00:A2AD` | `A2B0` | 5 | the NMI handler's sub-handlers (the NMI body itself stays interpreted, see native-coverage.md) |
| `01:BC73` | `BC76` | 6 | |
| `01:9D75`, `01:9D85` | `9D78`, `9D88` | 4 each | two small tables back to back |
| `08:C734`, `08:C738` | `C73B`, `C741` | 6, 3 | the second table is the tail of the first |
| `08:D06D`, `08:D071` | `D074`, `D080` | 12, 6 | same layout |
| `0D:F36D`, `0D:F372` | `F4A1`, `F4AB` | 10, 5 | sound driver |
| `0D:A177` | `A17A` | 2 | two handlers, then code |
| `0E:F3F1`, `0E:F3F5` | `F3FE`, `F3F8` | 3, 6 | |

Effect: functions the analysis refused went from 69 to 16 on the first routes (31 after the circuit routes brought in more code; see native-coverage.md for what is left and why).

Tried and dropped: `exit_mx_set 088026 M1X0 M0X0,M1X0` (the stub at `08:8026` really returns in either width, per `tests/exit_modes.py`) changed nothing, so it was removed rather than left as an unused claim.

## Left on purpose (not a gap, not guessed)
* `00:9EC2` `JML [$51]`: the mode switch. The destination is a pointer the game stores in RAM, so it is
  dynamic by nature; every destination seen in the routes is promoted as its own function instead.
* `00:8E87 JMP $1000`, `00:CA1A JSR $00D0`, `7E:4143`: the game copies small routines into RAM and runs them there. The bytes
  are not in the ROM, so they stay with the interpreter.
* `00:DEBB`, `00:DEF5` (and what calls them): `JMP $E088` is reached with a 16-bit accumulator although
  its code was written for 8-bit. The original game runs that path with the wrong width; only the interpreter reproduces it
  faithfully, so declaring a width would change the game.
