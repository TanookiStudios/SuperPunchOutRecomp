# Super Punch-Out!! (SNES, USA) RAM map for the cheats

All addresses are WRAM offsets (0..$1FFFF; the low bank mirror $0000-$1FFF is where everything below lives).
Every row says how it was found and what the proof is. "Route" names are the files in `tests/route_cheat_*.txt`
(written by `tests/gen_routes_cheats.py`); `python3 tests/gen_routes_cheats.py --run` re-runs every proof headless and
writes `build-game/route-out/cheat/REPORT.txt` plus picture sheets (`sheet_*.png`) next to the run folders.
Confidence: **high** = poked/traced AND confirmed in the game's own code; **medium** = one of the two; **low** = guess.

## How things were found (so the next person can repeat it)

* Poke and look: `poke`/`forcepoke` in a route, then screenshots (`dump`) and the dumped `.wram.bin`.
* Who writes this byte? The engine logs every write to an address range: run with
  `SPO_EXTRA_ENV="SNESRECOMP_WLOG_ADDR=LO:HI:/path/log SNESRECOMP_WLOG_STATE=1"` (hex, 16-bit range). Each line has the frame,
  the writing recompiled function (`fn_00_C80D...`) or, for interpreted code, `IPC=<bank><pc>` (that is the real program counter;
  the text after "interp@" is only the last entry the interpreter was started from). Lines whose bank column says `70` or `7F` are
  save-RAM / backup copies, not game RAM: ignore them. Then `python3 tests/dis.py 00:C80D 40 1 0` shows the game's code there.
* Inside several routines the direct page register is not 0. Fighter code runs with D=$0800 (Mac) or D=$0900 (opponent),
  the referee/announcer script code with D=$0B00. So a `STA $A1` there writes **$0BA1**, not $00A1.
* Trace everything: `SPO_EXTRA_ENV="SPO_RAM_TRACE=/path/file"` appends the first 8 KB of WRAM after every frame
  (`SPO_RAM_TRACE_BYTES` to change); `work/tl.py`-style scripts then read one address across time.

## The big picture

* One fight = one 3'00''00 clock. **There are no rounds** (no round counter changes at 1'00'' or 2'00'', no "ROUND" text in any of ~200
  screenshots of intros, fights, KO and results). Time running out (TIME UP banner) is a LOSS: REST goes down.
* A fight is won by knocking the opponent down 3 times (TKO) or by a KO (he does not get up); it is lost the same way, or by TIME UP.
* The game is a circuit run: Minor, Major, World, Special; 4 boxers each (3 + champion). Win = next boxer's card.
  After the champion: "MINOR CIRCUIT CLEAR" screen, then it carries straight on to the next circuit (seen in route `skipchain`).
* Resources the player has: **health**, **super meter** (the bottom-left "S" gauge), **REST** (tries left, starts at 3).
  There is **no hearts counter and no star counter in this game** (see "Things that do not exist").
* Mac is drawn as a see-through silhouette seen from behind; opponents and health bars are the things to read in screenshots.

## Table 1: the items you asked for

| Item | Address (size) | Meaning | How found | PROOF | Conf. |
|---|---|---|---|---|---|
| Mac health | `$089E` (low byte, fraction) + `$089F` (0..80) | 8.8 fixed point, `$5000` = 80.0 = full. `$089F` is what the game tests and what damage subtracts from | lead's poke + writer log + code | Code: `00:C80D` loads `$089F`, subtracts the hit value from a table via pointer `($D0)`, and on underflow zeroes `$089E` and stores 0. Writer log: only `fn_00_C80D` (hits: 80,73,66,59,52,42...), `fn_00_C14B` (copy), start-of-fight init (`$50`). Poke `$089F=0,$089E=0` in a fight (`work` run `kd_mac`, same as route `rest`): HUD bar empties and Mac goes down next frame. cheat `cant_be_hit` route `nohit`: with it ON health is 80 at all 9 checkpoints over 9000 frames, OFF it falls to 35, 42, 0, 9, 0... | high |
| Mac health copy | `$088E`/`$088F` | copy of `$089E/F` made every frame by `fn_00_C14B` (`LDX $89E; STX $88E`) | lead: one-frame poke into `$088F` did not stick; writer log | `00:C171..C174` in the disassembly; poking `$088F` is overwritten | high |
| Mac health on the HUD | `$0B14` | the bar's drawn value; it drains 1 per 2 frames toward `$089F` (so the bar slides) | trace after poking `$089F=0` | `tr_kd_mac`: `$0B14` 80,79,78,... one step every 2 frames from the poke frame; poking `$0B14` itself does nothing lasting | high |
| Opponent health | `$099E`/`$099F` (0..80), copy `$098E/F`, HUD copy `$0B1A` | same layout as Mac | same | `00:C828` is the twin of `C80D` for `$099F`. Poking `$099F=0` empties his HUD bar (`$0B1A` drains 1/2 frames) but **he does not fall by himself**: he only goes down when a punch lands on him (`kd_opp` run: 40 screenshots, he keeps boxing with an empty bar) | high |
| Mac knockdown count | `$089D` (1 byte) | knockdowns Mac has suffered **in this fight** (not per round, no rounds). 3rd = TKO loss | written by `bank_00_C68F` (D=$0800) each time Mac goes down; trace | Route `rest`/`gameover`: three health-empty pokes => `$089D` = 1,2,3 at frames 2712, 3607, 4358, then the "NORMAL PUNCH..." results screen with REST=2. Code: `00:A66A LDA $089D; CMP #3` picks the TKO script. Natural play: idle run (`nohit` OFF) `$089D` = 1,2,3 at frames 4065, 5559, 6801 | high |
| Opponent knockdown count | `$099D` | knockdowns the opponent has suffered; 3rd = TKO win | `fn_00_C26D..C390` increments `$099D` (D=$0900); trace of a won fight | Preset `$099D=2` then play: first knockdown makes it 3 and the fight ends **1100 frames earlier** (`$0BA1`=80 at 3658 instead of 4761; runs `kdo_two` vs `kdo_ctl`, same mash route). Code `00:A6F0 LDA $099D; CMP #3`. Note: a plain KO (cannot get up) can end a fight with `$099D` still 2 | high (TKO rule) / medium (KO case) |
| Super meter | `$089C` (0..27, `$1B` max) | the bottom-left gauge; also decides the yellow/blue "S" icon | lead (rises to 27) + code + pokes | Poke 0,7,14,21,28 into `$089C`: gauge fills 0..full, 28+ looks the same as 27 (screens `out_meter`, route `stars`). Only writer is `fn_00_EEDA` (`00:EF21..EF34`, caps at `$1B`): landed punches add 2, 4, 5 or 7, being hit adds -10 (`$F6`), a knockdown -27 (`$E5`) and floors at 0 (full list from a 7750-frame mash: deltas 4,4,...,7,2,2,5,2,-10,-27). Cheat `infinite_stars`: meter 27 at every checkpoint ON, 0 OFF, and the HUD shows the full coloured gauge + yellow S (picture `sheet_stars_on.png`) | high |
| "Super punch ready" flag | `$0878` bit 0 | set when the *drawn* gauge reaches the top, cleared when it drops below 26. Used by Mac's input code (`01:86DB`) | `00:EF55..EF75` + trace | `$0878` goes 0 -> 1 about 200 frames after forcing `$089C=27` and back to 0 at the next hit | medium |
| How the super meter is spent | not found | | 15 button combinations (L, R, Select, A, B, X, Y, up/down+punch, L+R...) pressed with the ready flag set (`work/exp_super.txt` run): **no write to `$089C` other than hit/KO/landed-punch deltas** | The only things that touch the meter are listed above | dead end |
| Stars | does not exist | no counter in RAM; the "S" icon is the only thing. (`$089D` is knockdowns, not stars) | HUD in every screenshot; `$089D` proof above | | high |
| Hearts | does not exist | no hearts HUD; no byte drops when punching: in 3100 frames of button mashing the only byte in `$0000-$1FFF` that only ever goes down is `$0B48` (a digit of the BONUS) | trace `ram_mash` | `infinite_hearts` is kept in the struct but does nothing (route `inert_fight`: digest identical to the reference with it on) | high |
| REST (tries left) | `$0606` | starts at 3 (`fn_00_993C` new-game init), -1 after every lost fight, 0 + loss = Game Over (menu with CONTINUE) | lead (REST on the results screen) + trace + code | Results screen after one loss shows REST=2 and `$0606`=2 (route `rest`); after 3 timeouts/losses 2,1,0 (`ram_win` trace: 15880, 26896, 37912) then Game Over; code `00:B1F7 LDA $0606; BEQ game-over`. Cheat `infinite_rest`: stays 3 after 1 loss and after 3 losses in a row, OFF it is 2 / 0 and the game is back on the menu (route `gameover`) | high |
| Other run counters | `$0603` losses against the current boxer, `$0604` wins this run, `$0605` total losses | zeroed by new-game init, `$0603` zeroed on a win | writer log + code `00:B231/B1E7/B1F5` | after 1 skip `$0604` = 1 (`skip`); after 4 skips `$0604` = 4 (`skipchain`) | medium |
| Circuit | `$0601` | 0 Minor, 1 Major, 2 World, 3 Special | `01:B9CD LDA $07E5; STA $0601` (copies the circuit chosen in the menu, cursor in `$07E5`) | Writing `$0601` = 1/2/3 right after the new-game init gives Major/World/Special cards and fights although the menu only offers Minor on a fresh save (`start` proof, picture `sheet_start_cards.png`) | high |
| Opponent index | `$0600` | position in the whole 16-boxer roster = circuit*4 + 0..3 (Minor 0-3 Gabby Jay, Bear Hugger, Piston Hurricane, Bald Bull; Major 4.. Bob Charlie, Dragon Chan, ?, Mr. Sandman(7); World 8.. Aran Ryan, ?, Mad Clown(10), ?; Special 12.. Narcis Prince, Hoy Quarlow(13), ?, ?) | `01:B9D5 ASL;ASL;STA $0600`; `00:B24D INC $0600` after a win | Cards and in-fight sprites follow it exactly (`start` proof: index 0,1,3,4,7,10,13 -> Gabby Jay, Bear Hugger, Bald Bull, Bob Charlie, Mr. Sandman, Mad Clown, Hoy Quarlow) | high |
| Boxers left after this one | `$0602` | 3,2,1,0 (0 = champion). The card's "#3/#2/#1/CHAMP" label is this | `01:B9D8 LDA #3; STA $0602`; `00:B250 DEC $0602` | same `start` proof | high |
| Start a new game at a chosen circuit + boxer | the three bytes above | write `$0601=c`, `$0600=4c+n`, `$0602=3-n` (n=0..3) in the window after the new-game init (`$0606` becomes 3, `$0602`=3, wins/losses 0) and before the card (about 80 frames) | experiments `start` + code | `start=minor:2`, `minor:4`, `major:1`, `major:4`, `world:3`, `special:2` all land on the right card and the fight loads and plays; `start=major:3` then skip goes on to index 7 | high |
| Fight clock | `$0B26..$0B2A` one decimal digit per byte: hundredths-ones, hundredths-tens, seconds-ones, seconds-tens, minutes (`$0B28` = seconds like the lead guessed, runs 1.13x real time: 53 frames per game second) | the fight ends with TIME UP at 3'00''00 | trace vs screenshots; writer `fn_00_F254` | `$0B2A` goes 1, 2, 3 at frames 9099, 12279, 15459 in the idle Bear Hugger fight (`ram_win`), TIME UP at 3: poking minutes=2, tens=5 made TIME UP arrive ~8 s later (`timeup` run). The on-screen digits are not redrawn from the poked bytes, so treat the digits as the game's counter, not the HUD source. B26 does not always match the drawn last digit | medium |
| Clock state | `$0B21` | `$00` clock running, `$40` paused (intro, any knockdown count), `$41` time up, `$80` toggles in the attract demo | writes at `fn_00_A569` (start bell) and in knockdown code; trace | Timeline of the first fight: `$40` at 2031 (intro), `$00` at 2486 (bell), `$40` at 2790 (opponent down)... (`ram_win` trace, 8 transitions listed in the log) | high |
| BONUS | `$0B45..$0B49` one digit per byte, ones first | starts at 20000 (Minor first fight; higher in later circuits), loses about 10 every 3.4 frames, reaches 0 around 1'55'' | search of dumps for the screenshot number | BONUS 18460 on screen = `00 06 04 08 01` at `$0B45` (route `out_sp_l` dumps p0..p6, four values matched) | high |
| SCORE | `$0B33..$0B3A` one digit per byte, ones first (8 digits) | points: NORMAL PUNCH 30, COUNTER PUNCH 100, UPPERCUT/HOOK 150, RAPID PUNCH 80, KNOCKDOWN 500, SUPER KNOCKDOWN 1500 (text on the results screen), plus a STAMINA REMAINING BONUS (health left) and the time BONUS on a win | search of 8 mash dumps: all matched at `$0B33`; results screens | e.g. screen SCORE 120, 240, 490, 640, 2320, 2540, 2600, 2690 matched `$0B33` in 8/8 dumps. The drawn number can lag the byte by a moment | high (address) / medium (rules) |
| Round number | does not exist | a single clock; no per-round counters reset at 1'00'' / 2'00''; knockdown counts run for the whole fight | clock log above; HUD | `ram_win` trace: `$089D/$099D` never reset inside a fight | high |
| Real fight (in the ring, player's fight) | `$0000==1 && $0001==1` (also `$0B00==1`, `$0B12==2`) | see Table 2 | traces over title/menu/demo/fight/results | Table 2 | high |
| Fight in play (clock running) | the above and `$0B21==0` | | | Table 2 | high |
| Screen / scene mode | **no single variable** | the main flow is code (outer loop at `00:8895/88B1`), not a mode byte | scanning, code | Table 2 gives the combination that tells screens apart | medium |
| Instant win / skip to next boxer | write `$0C00=$82` (KO jingle), 205 frames later write `$0C00=0`, `$0BA4=$0E`, `$0BA6=$08` | makes the referee script jump to its "fade out and report a win" step; the game does the whole win path (win results screen, wins +1, next boxer card) | code `00:A50A` script runner, table `00:A8DE`, steps `A8EA A8F7 A905 A910 A92D A941`; many failed attempts (below) | route `skip`: ON: boxer index 0->1 and 3->2 at frame 2752, results screen with STAMINA BONUS and a Bear Hugger card; OFF: still fighting at all 24 checkpoints. Route `skipchain` (`skipall`): all four Minor boxers skipped, "MINOR CIRCUIT CLEAR - 4 Wins 0 Loss", Major circuit starts | high |

## Table 2: how to tell the screens apart (values read from dumps at the stated frames)

| Screen | `$0000` | `$0001` | `$0B00` | `$0B12` | `$0B21` | `$0C00` (sound mailbox) | notes |
|---|---|---|---|---|---|---|---|
| Boot, title, attract "How to win" fight is NOT a mode of its own; title itself (frame 1200) | 00 | 00 | 00 | 00 | 00 | 44 (title music) | |
| NEW GAME menu, name entry, mode select, circuit select (1405..1645) | 00 | 00 | 00 | 00 | 00 | 02 | `$07E5` = circuit cursor |
| black fade after the circuit pick (1726) and boxer card (1807, 1888) | 00 | 00 | 00 | 00 | 00 | 00 | `$0602`=3 `$0606`=3 already set |
| **Attract demo fight** (appears about 300 frames after the title idles; frame 1528 in the 3000-frame idle run) | **01** | **80** | 01 | **00** | toggles 80/00 | 06 | Mac and opponent health `$50`; `$0B14/$0B1A` stay 0; no REST (`$0606`=0). This is why the cheats test `$0001==1` |
| Real fight, intro (boxer walks in, health bars drawn) (2056..2486) | 01 | 01 | 01 | 02 | 40 | 06 | `$0B12` becomes 2 at 2031, 25 frames before `$0000` |
| **In play** (2486 on) | 01 | 01 | 01 | 02 | **00** | 06 | |
| Knockdown count (either boxer on the floor, number on screen) | 01 | 01 | 01 | 02 | 40 | 06 | clock stopped; referee script `$0BA4/$0BA6` runs |
| TIME UP banner, then results overlay of a loss | 01 | 01 | 01 | 02 | 41 | 06 then 04 | results are drawn INSIDE the fight scene: `$0000` stays 1 until START is pressed |
| End of fight (KO/TKO win and START on results) | **80** for a few frames, then 00 | 00 | 01 -> 00 | | | | `$0BA1` bit 7 = Mac won (set by `00:A941` together with `$0000=$80`) |
| After a skip win | 80 and stays 80 through results and card until the next fight loads | | | | | | harmless: the next fight sets `$0000` itself (`00:B13F` writes $81) |

So the cheats use: **fight scene** = `$0000==1 && $0001==1 && $0B00==1` (true from the first intro frame to the end of the results of a loss, false on title/menus/cards/demo/ end-of-win), and **play** = fight scene and `$0B21==0`.
Not safe as a flag: `$0000` alone (the demo also has 1), `$004B` (changes every frame, it is the raster IRQ phase), `$0C00` (sound request, not a mode).

## Fight engine landmarks (for whoever goes on)

| Where | What |
|---|---|
| `00:B0xx-B1xx` | the fight scene's main loop: per frame `JSR C14B` (fighters), `A493` (referee script), wait for NMI/IRQ (`$004B`). Loop ends when `$0000` has bit 7 set; then `B1DD`: if `$0BA1` bit 7 -> win path `B231` (zero `$0603`, `$0604`++, if `$0602`==0 circuit cleared else `INC $0600; DEC $0602`, next boxer via `88B1`); else loss path (`$0605`++, `$0603`++, if `$0606`==0 Game Over else retry `88B1`) |
| `00:C14B` | per-frame fighter update: copies health `$089E`->`$088E`, `$099E`->`$098E`; handles the hit mailboxes `$0860` (Mac's punch landed -> `C828` damages the opponent) and `$0960` (opponent's punch landed -> `C80D` damages Mac) |
| `00:C80D / C828` | damage routines; both return at once if `$0B01` is non-zero (`$0B01`=$80 for 66 frames at TIME UP and toggling in the demo, so nobody is hurt then) |
| `00:C26D-C390` | opponent knockdown start; `C390 INC $099D` |
| `00:EEDA` | super meter (deltas in `$0B53`), HUD gauge animation, sets `$0878` |
| `00:F254` | fight clock/HUD timers (`$0B24..$0B2D`, per-fighter seconds counters `$08DC/$09DC`: +1 every 53 frames, reset at a knockdown; meaning unknown) |
| `00:A493 -> A50A` | referee/announcer script runner: script id (x2) in `$0BA4`, step (x2) in `$0BA6`, countdown in `$0BA3`, result flag `$0BA1`. Table `00:A511` (script 7 = `A8DA`, the end-of-fight script) |
| `00:A8DE` table | end-of-fight script steps: `A8EA A8F7 A905 A910` (3: plays the KO jingle `$0C00=$82`), `A92D` (4: waits until `$0C00==0`, then fade out `$0049=$82`, stop music `$0320=$80`), `A941` (5: when `$0049==0`: `$0BA1=$80`, `$0000=$80` = "Mac won") |
| `00:993C` | new-game init: REST=3, clears `$0603-$0616`, sets flags `$0620..$0638`=$80 |
| `01:B9CD-B9DA` | circuit pick: `$0601`=`$07E5`, `$0600`=`$0601*4`, `$0602`=3 |

## Dead ends and things that did not work (kept on purpose)

* Poking `$0000=$80` (+`$0BA1=$80`) in a fight: `00:A493` sees bit 7 *before* the loop test and treats it as "restart the referee script" (sets `$0C00=$86`, clears `$0BA0`, `$0000`), so nothing ends. Writing it at a frame boundary cannot hit the narrow window after `A493` and before the loop test.
* Jumping straight to the last referee step (`$0BA4=$0E, $0BA6=$0A`) **ends the fight and starts the next one, but then the whole game freezes**: the next scene's music upload to the sound chip waits forever (`01:EF78 CMP $2140` loop) because the fight music was never stopped. Seen with `SNESRECOMP_INTERP_PCTRACE=200`. Fix = play the KO jingle first and let `A92D` do the stop-music + fade (what `skip_to_next` does).
* Jumping to step 4 (`$0BA6=$08`) while the fight music (`$0C00=06`) is still playing does nothing: step 4 waits for `$0C00==0`, which only the jingle script clears.
* Poking `$0BA3=1` to make step 3 run does nothing visible: `$0BA3` is reloaded each cycle by `00:AABF` while `$0771 & $1F` is non-zero.
* Poking the opponent's health to 0 does not end the fight (see Table 1). Poking `$089C` (meter) does not make Mac throw anything.
* `$0000=$80/$0BA1=$80` and the `$0B01` flag are not usable as "win" triggers (above).
* `$0C00` is the sound-request mailbox, not a scene id (values 44/02/06/04/82/86 are track ids; bit 7 = new request). It looked like a scene number at first because it follows the scenes.
* Super punch: how it is triggered/spent was not found (see Table 1).
* Circuit locks: Major/World are greyed on a fresh save and the cursor does not move onto them. The lock is in the save (SRAM), not in `$0601`; writing `$0601` in a running new game bypasses it. The Special circuit cannot be reached from the menu on a fresh save either.
* Per-fighter counters `$08DC/$09DC`: +1 every 53 frames, reset at a knockdown; I could not tie them to anything on screen (low confidence: stamina/regen timer).

## Things that do not exist (with evidence)

* Hearts: no HUD element, no counter that drops with punches thrown (monotone-decrease scan of a 3100-frame mash found only a BONUS digit).
* Stars: no counter; the "S" icon only reflects the meter. Do not map "star" to `$089D` (that is knockdowns).
* Rounds: one clock, one set of knockdown counters per fight, TIME UP at 3'00''00 ends the fight as a loss.

## Cheat behaviour notes (src/superpunchout_extras.c)

* `cant_be_hit`: while the fight scene is loaded and Mac is standing (health not 0), tops `$089E/F` up to full (`$5000`) at the end of every frame. **Why not just undo the drop** (the first version did): the game decides "knocked down" in the same frame the punch lands (`00:C49A JSR C80D; BEQ` reacts to the routine reporting health 0), so undoing a drop at the end of the frame was too late for a punch that would empty the bar. Test: Mac poked to 3 health, cheat on from the next frame: first version = knocked down at the first hit (`nohit_edge` run, knockdowns=1, health 3 -> get-up 30); current version = health 80 and 0 knockdowns at all checkpoints. Every hit seen in the tests takes 7 or 10 points, so topping up first is enough (a single hit of 80 or more, not seen, would still go through). It does not stop TIME UP: an idle fight still ends in a loss at 3'00''00.
* `infinite_stars`: sets `$089C=27` whenever it is lower, only while the fight scene is loaded (also during the intro, so the gauge shows full from the start).
* `infinite_rest`: undoes a drop of exactly 1 in `$0606` while `$0000 != 0`.
* `skip_to_next`: starts only while the clock runs; about 4 seconds to the win results; one-shot.
* `start_at_opponent/start_circuit`: fires when `$0606` changes to 3 with `$0603/4/5`=0, `$0602`=3 and `$0600==4*$0601`, i.e. right after the new-game init; also fires at the start of every later circuit run (after a circuit is cleared).
* Inert when off: digest of the attract route and of title -> fight -> 3000 punch frames equal the pre-cheat binary's (proof `inert`).

## Proof log (last full run: `python3 tests/gen_routes_cheats.py --run`, ALL PASSED, about 11 minutes)

Key numbers from `build-game/route-out/cheat/REPORT.txt`:

* Inert when off: attract route digest `66ebe681...9fe9b` identical for the pre-cheat binary, the new binary, and the new binary with every cheat on; title -> fight -> 3000 punch frames digest `ebebc8fe...2f948` identical pre-cheat vs new vs "hearts" on.
* First frame each cheat changes anything (frame numbers of the 3732-frame route; fight loads at 2056, clock starts 2486, first hit on Mac 2712, circuit pick about 1646): hearts never, rest never (no loss in the window), stars 2057, nohit 2713, skip 2487, start 1674. Nothing before the fight scene exists is touched, except `start`, which writes its three bytes right after the new-game init (that is its whole job).
* nohit: 9000 idle frames, ON health 80 and 0 knockdowns at all nine checkpoints; OFF health 35, 42, 0, 9, 0, ... knockdowns 0,1,2,2,3 and REST 3 -> 2 (TKO at about frame 7595); switched on at frame ~3000 with Mac at 52: back to 80 and no knockdowns; started at health 3: topped up before the first hit, no knockdown (the earlier "undo the drop" version failed this test, see the cheat notes).
* stars: meter 27 at all 5 checkpoints ON, 0 OFF; switched on at ~3500: 0 before, 27 after.
* rest: one loss (3 knockdowns -> TKO): REST 2 OFF, 3 ON; three losses in a row: OFF REST 0 and back on the menu, ON REST 3 and a fourth fight is loaded.
* skip: OFF still in fight 1 at all 24 checkpoints; ON boxer index 0 -> 1 at frame 2752 (win results screen, wins=1, Bear Hugger card); four skips in a row clear the Minor circuit (wins=4, CLEAR screen, Major circuit starts). `start=major:3` + skip: index 6 -> 7.
* start: card/fight check for none, minor:2, minor:4, major:1, major:4, world:3, special:2 (circuit, index, left) = (0,0,3) (0,1,2) (0,3,0) (1,4,3) (1,7,0) (2,10,1) (3,13,2).

Developer switches added for the proofs only: `SPO_CHEATS=...` (see the header of `src/superpunchout_extras.h`), `SPO_CHEATS=skipall` (re-arms skip after every use) and `SPO_CHEATS_FROM=<frame>` (turn the cheats on in the middle of a run).
