#!/usr/bin/env python3
"""Proof routes and proof runner for the Super Punch-Out!! cheats (src/superpunchout_extras.c).

  python3 tests/gen_routes_cheats.py            write tests/route_cheat_*.txt only
  python3 tests/gen_routes_cheats.py --run      write them, run every proof headless (about 6 minutes),
                                                print PASS/FAIL per claim, save evidence under
                                                build-game/route-out/cheat/ (REPORT.txt, sheet_*.png)
  python3 tests/gen_routes_cheats.py --run nohit stars   run only the named proofs

Needs build-game/SuperPunchOutRecomp (tests/build_game.sh) and, for the inertness proofs, a copy of
the binary built BEFORE the cheats existed in ref/SuperPunchOutRecomp (override with REF_BIN=...).
Nothing opens a window; every run uses a throwaway working folder with an empty save.
The proofs read the dumped game RAM ($addr below are WRAM addresses, see notes/ram-map.md).
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import gen_routes as g

NEW_BIN = os.path.join(ROOT, "build-game/SuperPunchOutRecomp")
REF_BIN = os.environ.get("REF_BIN", os.path.join(ROOT, "ref/SuperPunchOutRecomp"))
OUT = os.path.join(ROOT, "build-game/route-out/cheat")

# ---------------------------------------------------------------- route pieces
def frames_of(lines):
    n = 0
    for l in lines:
        t = l.split()
        if t and t[0] == "wait": n += int(t[1])
        elif t and t[0] == "press": n += int(t[2]) + 1
    return n

def dumps(prefix, count, step, first=None):
    out = []
    for i in range(count):
        out += [f"wait {first if (i == 0 and first is not None) else step}", f"dump {prefix}{i}"]
    return out

MASH_CYCLE = ["b", "y", "a", "x", "b", "y", "b", "a"]
def mash(frames):                       # same punch pattern as the earlier mash experiment
    out, i = [], 0
    while frames > 0:
        out += [f"press {MASH_CYCLE[i % 8]} 3", "wait 13"]; frames -= 16; i += 1
    return out

def spam(btn, n, gap=60):               # press a button n times (cards, results screens)
    out = []
    for _ in range(n): out += [f"press {btn} 4", f"wait {gap}"]
    return out

KD = ["poke 089F 00", "poke 089E 00"]  # empty Mac's health: he goes down (the 3rd time = TKO)

def lose_fight():                       # wait for the clock to run, then knock Mac down three times
    return ["until 0000 == 01 6000", "until 0B21 == 00 3000"] + KD + ["wait 800"] + KD + ["wait 800"] + KD + ["wait 1000"]

ROUTES = {}                             # name -> (lines, extra frames after the lines, comment)
def add(name, lines, comment, frames=None):
    ROUTES[name] = (lines, frames if frames is not None else frames_of(lines), comment)

add("inert_attract", ["wait 3000"], "title attract demo, nothing pressed, 3000 frames")
add("inert_fight", g.to_fight() + ["wait 420"] + mash(3000), "title -> menu -> first fight (Gabby Jay), then 3000 frames of the punch pattern")
add("prefight", g.to_fight() + ["wait 420", "wait 1100"], "title -> first fight, then 1100 frames idle in play; used to find where each cheat first changes anything")
add("nohit", g.to_fight() + ["wait 420"] + dumps("d", 9, 1000) + ["wait 50"], "idle in the first fight for 9000 frames (Mac is hit, knocked down 3 times, TKO'd unless the cheat is on)")
add("nohit_edge", g.to_fight() + ["wait 420", "poke 089F 03", "poke 089E 00"] + dumps("e", 6, 300) + ["wait 50"],
    "Mac starts with only 3 health in the first fight: the next hit would empty his bar (knockdown) unless cant_be_hit is on. (Undoing the drop at the end of the frame is NOT enough: an earlier build did that and Mac still went down, because the game reacts to health 0 inside the same frame.)")
add("stars", g.to_fight() + ["wait 420"] + dumps("d", 5, 600) + ["wait 50"], "idle in the first fight; read the super meter")
add("rest", g.to_fight() + ["wait 420"] + KD + ["wait 800"] + KD + ["wait 800"] + KD + ["wait 800"]
    + dumps("r", 8, 150) + spam("start", 2, 60) + ["wait 200", "dump r_card"] + spam("a", 4, 80) + ["wait 600", "dump r_fight", "wait 50"],
    "lose the first fight by 3 knockdowns, read REST on the results screen, then continue")
add("gameover", g.to_fight() + lose_fight() + spam("start", 10, 80) + lose_fight() + spam("start", 10, 80) + lose_fight()
    + spam("start", 10, 80) + ["dump g_after"] + ["wait 600", "dump g_after2", "wait 600", "dump g_after3", "quit"],
    "lose three fights in a row: Game Over without the rest cheat, no Game Over with it", frames=30000)
add("skip", g.to_fight() + ["wait 420"] + dumps("s", 24, 60) + ["wait 50"], "idle in the first fight and read how the fight ends (skip cheat)")
add("skipchain", g.to_fight() + ["until 0602 == 02 4000"] + spam("a", 12, 60) + ["until 0000 == 01 3000", "until 0602 == 01 4000"]
    + spam("a", 12, 60) + ["until 0000 == 01 3000", "until 0602 == 00 4000"] + spam("a", 12, 60)
    + ["until 0000 == 01 3000", "wait 1200", "dump c_champ"] + spam("a", 14, 60)
    + ["dump c_end0", "wait 400", "dump c_end1", "wait 400", "dump c_end2", "wait 400", "dump c_end3", "quit"],
    "skip every fight of the Minor circuit (Gabby Jay, Bear Hugger, Piston Hurricane, Bald Bull); the game then shows MINOR CIRCUIT CLEAR and goes on to the Major circuit", frames=30000)
add("start", ["wait 1200"] + g.title_to_name_screen() + g.name_to_card() + ["dump card"] + g.card_to_fight() + ["wait 300", "dump fight", "wait 300", "dump fight2", "wait 50"],
    "new game up to the first boxer card, then into the fight: which boxer do we get?")
add("startskip", g.to_fight() + dumps("s", 14, 60) + ["wait 50"], "like skip, but from a chosen starting boxer")

def write_routes():
    for name, (lines, frames, comment) in ROUTES.items():
        g.write(f"route_cheat_{name}.txt", frames, lines, header=comment)
    print(f"wrote {len(ROUTES)} routes: tests/route_cheat_*.txt")

# ---------------------------------------------------------------- running
def launch(runname, route, env="", binary=NEW_BIN):
    out = os.path.join(OUT, runname)
    e = dict(os.environ, SPO_EXTRA_ENV=env, BIN=binary)
    p = subprocess.Popen([os.path.join(HERE, "run_route.sh"), os.path.join(HERE, f"route_cheat_{route}.txt"), "native", out],
                         env=e, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p, out

def run_many(specs, parallel=8):
    """specs: list of (runname, route, env, binary). Returns {runname: outdir}."""
    done, pending, running = {}, list(specs), []
    while pending or running:
        while pending and len(running) < parallel:
            s = pending.pop(0)
            p, out = launch(*s)
            running.append((s[0], p, out))
        for r in list(running):
            if r[1].poll() is not None:
                txt = r[1].communicate()[0].strip().splitlines()
                print("  ran", r[0], "->", txt[0].split(" out=")[0] if txt else "?")
                done[r[0]] = r[2]; running.remove(r)
        if running: running[0][1].wait()
    return done

def wram(out, tag):
    return open(os.path.join(out, "dumps", tag + ".wram.bin"), "rb").read()

def frame_of(out, tag):
    return json.load(open(os.path.join(out, "dumps", tag + ".info.json")))["frame"]

def hashes(out):
    return [l.strip().split(",")[1] for l in open(os.path.join(out, "hashes.txt")) if "," in l]

def digest(out):
    return open(os.path.join(out, "digest.txt")).read().strip()

def sheet(out, tags, name):
    files = [os.path.join(out, "dumps", t + ".fb.bgrx") for t in tags]
    dest = os.path.join(OUT, f"sheet_{name}.png")
    subprocess.check_call([sys.executable, os.path.join(HERE, "contact_sheet.py"), dest] + files)
    return dest

REPORT = []
FAILS = []
def say(msg):
    print(msg); REPORT.append(msg)

def check(ok, msg):
    say(("PASS  " if ok else "FAIL  ") + msg)
    if not ok: FAILS.append(msg)

def first_diff(a, b):
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]: return i + 1   # frame numbers start at 1
    return None if len(a) == len(b) else n + 1

# ---------------------------------------------------------------- the proofs
def proof_inert():
    say("== INERTNESS: all cheats off, new binary vs the binary built before the cheats existed ==")
    specs = [("attract_ref", "inert_attract", "", REF_BIN), ("attract_new", "inert_attract", "", NEW_BIN),
             ("attract_allon", "inert_attract", "SPO_CHEATS=hearts,stars,nohit,skip,rest,start=major:3", NEW_BIN),
             ("fight_ref", "inert_fight", "", REF_BIN), ("fight_new", "inert_fight", "", NEW_BIN),
             ("fight_hearts", "inert_fight", "SPO_CHEATS=hearts", NEW_BIN)]
    r = run_many(specs)
    check(digest(r["attract_ref"]) == digest(r["attract_new"]), f"attract 3000 frames, cheats off: digest {digest(r['attract_new'])} == reference {digest(r['attract_ref'])}")
    check(digest(r["attract_ref"]) == digest(r["attract_allon"]), "attract demo with EVERY cheat switched on: digest identical to reference (cheats never act in the demo)")
    check(digest(r["fight_ref"]) == digest(r["fight_new"]), f"title -> fight -> 3000 frames of punches, cheats off: digest {digest(r['fight_new'])} == reference {digest(r['fight_ref'])}")
    check(digest(r["fight_ref"]) == digest(r["fight_hearts"]), "'infinite hearts' on: digest identical to reference (it really does nothing)")

def proof_prefight():
    say("== NO CHEAT TOUCHES TITLE / MENU / CARD / DEMO FRAMES: first frame where each cheat changes the game state ==")
    cases = [("ref", ""), ("hearts", "hearts"), ("rest", "rest"), ("stars", "stars"), ("nohit", "nohit"), ("skip", "skip"), ("start", "start=major:3")]
    specs = [(f"pre_{n}", "prefight", ("SPO_CHEATS=" + c) if c else "", REF_BIN if n == "ref" else NEW_BIN) for n, c in cases]
    r = run_many(specs)
    ref = hashes(r["pre_ref"])
    exp = {"hearts": (None, None), "rest": (None, None), "stars": (2056, 2200), "nohit": (2056, 2900), "skip": (2486, 2700), "start": (1640, 1700)}
    # fight 1 is loaded at frame 2056, the clock starts at 2486, Mac is first hit at 2712, the circuit pick is at ~1646
    for n, c in cases[1:]:
        fd = first_diff(ref, hashes(r[f"pre_{n}"]))
        lo, hi = exp[n]
        if lo is None:
            check(fd is None, f"{c}: no difference in {len(ref)} frames (title, menus, card, intro, 1100 frames of play)")
        else:
            check(fd is not None and lo <= fd <= hi, f"{c}: first difference at frame {fd} (allowed {lo}..{hi}; fight 1 loads at 2056, clock starts 2486, first hit on Mac 2712, circuit pick ~1646)")

def proof_nohit():
    say("== CANT_BE_HIT: idle in the first fight, 9000 frames ==")
    r = run_many([("nh_off", "nohit", "", NEW_BIN), ("nh_on", "nohit", "SPO_CHEATS=nohit", NEW_BIN),
                  ("nh_mid", "nohit", "SPO_CHEATS=nohit SPO_CHEATS_FROM=3000", NEW_BIN)])
    tags = [f"d{i}" for i in range(9)]
    for n in ("nh_off", "nh_on", "nh_mid"):
        row = [(frame_of(r[n], t), wram(r[n], t)[0x89F], wram(r[n], t)[0x89D], wram(r[n], t)[0x606]) for t in tags]
        say(f"  {n}: (frame, Mac health, Mac knockdowns, REST) = {row}")
    on = [wram(r["nh_on"], t) for t in tags]
    off = [wram(r["nh_off"], t) for t in tags]
    mid = [wram(r["nh_mid"], t) for t in tags]
    check(all(w[0x89F] == 80 and w[0x89D] == 0 and w[0x606] == 3 for w in on), "cheat ON: Mac health stays 80, knockdowns 0, REST 3 at all 9 checkpoints")
    check(off[1][0x89F] < 80 and off[8][0x89D] >= 1 and off[8][0x606] < 3, "cheat OFF: Mac loses health, is knocked down and loses the fight (REST goes down)")
    check(all(w[0x89F] == 80 and w[0x89D] == 0 and w[0x606] == 3 for w in mid),
          "switched on in the middle of the fight (frame ~3000, Mac already down to 52): health is back at 80 from the next checkpoint on, no knockdowns, REST 3")
    say("  pictures: " + sheet(r["nh_off"], tags, "nohit_off") + "  " + sheet(r["nh_on"], tags, "nohit_on"))

def proof_nohit_edge():
    say("== CANT_BE_HIT when a hit would empty the bar ==")
    r = run_many([("ne_off", "nohit_edge", "", NEW_BIN), ("ne_on", "nohit_edge", "SPO_CHEATS=nohit SPO_CHEATS_FROM=2650", NEW_BIN)])
    tags = [f"e{i}" for i in range(6)]
    for n in ("ne_off", "ne_on"):
        say(f"  {n}: (frame, Mac health, knockdowns) = {[(frame_of(r[n], t), wram(r[n], t)[0x89F], wram(r[n], t)[0x89D]) for t in tags]}")
    check(all(wram(r['ne_on'], t)[0x89F] == 80 and wram(r['ne_on'], t)[0x89D] == 0 for t in tags), "cheat ON, started with health 3: topped up to 80 before the first hit, never knocked down")
    check(wram(r['ne_off'], 'e1')[0x89D] >= 1, "cheat OFF, health 3: the first hit knocks Mac down")
    say("  pictures: " + sheet(r["ne_off"], tags, "nohit_edge_off") + "  " + sheet(r["ne_on"], tags, "nohit_edge_on"))

def proof_stars():
    say("== INFINITE_STARS (super meter): idle in the first fight ==")
    r = run_many([("st_off", "stars", "", NEW_BIN), ("st_on", "stars", "SPO_CHEATS=stars", NEW_BIN), ("st_mid", "stars", "SPO_CHEATS=stars SPO_CHEATS_FROM=3500", NEW_BIN)])
    tags = [f"d{i}" for i in range(5)]
    for n in ("st_off", "st_on", "st_mid"):
        say(f"  {n}: (frame, meter $089C) = {[(frame_of(r[n], t), wram(r[n], t)[0x89C]) for t in tags]}")
    check(all(wram(r['st_on'], t)[0x89C] == 27 for t in tags), "cheat ON: meter is 27 (full) at every checkpoint, even though Mac is being hit (every hit takes 10 off)")
    check(all(wram(r['st_off'], t)[0x89C] < 27 for t in tags), "cheat OFF: meter is below full at every checkpoint")
    check(wram(r['st_mid'], 'd0')[0x89C] < 27 and all(wram(r['st_mid'], t)[0x89C] == 27 for t in tags[1:]), "switched on in the middle (frame ~3500): meter 0 at frame ~3232, full from ~3832 on")
    say("  pictures (bottom-left meter): " + sheet(r["st_off"], tags, "stars_off") + "  " + sheet(r["st_on"], tags, "stars_on"))

def proof_rest():
    say("== INFINITE_REST: lose a fight (3 knockdowns -> TKO), read REST ==")
    r = run_many([("re_off", "rest", "", NEW_BIN), ("re_on", "rest", "SPO_CHEATS=rest", NEW_BIN)])
    tags = [f"r{i}" for i in range(8)]
    for n in ("re_off", "re_on"):
        say(f"  {n}: REST at checkpoints = {[wram(r[n], t)[0x606] for t in tags + ['r_card', 'r_fight']]}  boxer index/left at r_fight = {wram(r[n], 'r_fight')[0x600]}/{wram(r[n], 'r_fight')[0x602]}  fight loaded={wram(r[n], 'r_fight')[0]}")
    check(wram(r['re_off'], 'r7')[0x606] == 2, "cheat OFF: REST drops from 3 to 2 after the loss (results screen shows REST=2)")
    check(all(wram(r['re_on'], t)[0x606] == 3 for t in tags), "cheat ON: REST stays 3 on the results screen")
    for n in ("re_off", "re_on"):
        w = wram(r[n], "r_fight")
        check(w[0] == 1 and w[0x600] == 0 and w[0x602] == 3, f"{n}: after the loss the game continues with the same boxer (Gabby Jay) in a new fight")
    say("  pictures (results screens, REST at bottom left): " + sheet(r["re_off"], ["r2", "r_card", "r_fight"], "rest_off") + "  " + sheet(r["re_on"], ["r2", "r_card", "r_fight"], "rest_on"))

def proof_gameover():
    say("== INFINITE_REST: three losses in a row ==")
    r = run_many([("go_off", "gameover", "", NEW_BIN), ("go_on", "gameover", "SPO_CHEATS=rest", NEW_BIN)])
    for n in ("go_off", "go_on"):
        for t in ("g_after", "g_after3"):
            w = wram(r[n], t)
            say(f"  {n} {t} (frame {frame_of(r[n], t)}): REST={w[0x606]} fight-loaded={w[0]} boxer index={w[0x600]} left={w[0x602]} losses={w[0x605]}")
    wo, wn = wram(r["go_off"], "g_after3"), wram(r["go_on"], "g_after3")
    check(wo[0x606] == 0 and wo[0] != 1, "cheat OFF: after the 3rd loss REST is 0 and no fight is running (Game Over, back to the title)")
    check(wn[0x606] == 3 and wram(r["go_on"], "g_after")[0x606] == 3, "cheat ON: after 3 losses REST is still 3")
    say("  pictures: " + sheet(r["go_off"], ["g_after", "g_after2", "g_after3"], "gameover_off") + "  " + sheet(r["go_on"], ["g_after", "g_after2", "g_after3"], "gameover_on"))

def proof_skip():
    say("== SKIP_TO_NEXT ==")
    r = run_many([("sk_off", "skip", "", NEW_BIN), ("sk_on", "skip", "SPO_CHEATS=skip", NEW_BIN), ("sk_chain", "skipchain", "SPO_CHEATS=skipall", NEW_BIN)])
    tags = [f"s{i}" for i in range(24)]
    on = [(frame_of(r["sk_on"], t), wram(r["sk_on"], t)[0x600], wram(r["sk_on"], t)[0x602], wram(r["sk_on"], t)[0]) for t in tags]
    say(f"  sk_on (frame, boxer index, boxers left, fight-flag) = {on}")
    check(all(wram(r['sk_off'], t)[0x600] == 0 and wram(r['sk_off'], t)[0] == 1 for t in tags), "cheat OFF: still fighting the first boxer at all 24 checkpoints")
    won = [x for x in on if x[1] == 1 and x[2] == 2]
    check(bool(won), f"cheat ON: the game moved on to boxer #2 (index 1, 2 left) at frame {won[0][0] if won else None}; the fight was never won by hand")
    check(wram(r['sk_on'], 's23')[0x604] == 1, "cheat ON: the win counter ($0604) went up to 1 (counted as a real win)")
    say("  pictures: " + sheet(r["sk_on"], tags[:16], "skip_on"))
    w = wram(r["sk_chain"], "c_champ")
    say(f"  chain at champion fight: boxer index={w[0x600]} left={w[0x602]} wins={w[0x604]} fight-flag={w[0]}")
    check(w[0x600] == 3 and w[0x602] == 0 and w[0x604] == 4, "skip x4 chain: Gabby Jay, Bear Hugger, Piston Hurricane and the champion Bald Bull all skipped: roster index 3, 0 boxers left, 4 wins counted")
    say("  pictures (first = the MINOR CIRCUIT CLEAR screen with 4 wins, then the game carries on into the Major circuit): " + sheet(r["sk_chain"], ["c_champ", "c_end0", "c_end1", "c_end2", "c_end3"], "skip_chain"))

def proof_start():
    say("== START_AT_OPPONENT / START_CIRCUIT ==")
    cases = [("none", "", (0, 0, 3)), ("minor2", "start=minor:2", (0, 1, 2)), ("minor4", "start=minor:4", (0, 3, 0)), ("major1", "start=major:1", (1, 4, 3)),
             ("major4", "start=major:4", (1, 7, 0)), ("world3", "start=world:3", (2, 10, 1)), ("special2", "start=special:2", (3, 13, 2))]
    r = run_many([(f"start_{n}", "start", ("SPO_CHEATS=" + c) if c else "", NEW_BIN) for n, c, _ in cases])
    for n, c, want in cases:
        w = wram(r[f"start_{n}"], "card"); f = wram(r[f"start_{n}"], "fight2")
        got = (w[0x601], w[0x600], w[0x602])
        say(f"  {n}: circuit/index/left at the card = {got}; fight loaded={f[0]}/{f[1]}, opponent health={f[0x99F]}, Mac health={f[0x89F]}")
        check(got == want and f[0] == 1 and f[1] == 1, f"{c or 'no cheat'}: card shows circuit {want[0]}, roster index {want[1]}, {want[2]} boxers left, and the fight starts")
    files = [os.path.join(r[f"start_{n}"], "dumps", "card.fb.bgrx") for n, _, _ in cases]
    dest = os.path.join(OUT, "sheet_start_cards.png")
    subprocess.check_call([sys.executable, os.path.join(HERE, "contact_sheet.py"), dest] + files)
    files = [os.path.join(r[f"start_{n}"], "dumps", "fight2.fb.bgrx") for n, _, _ in cases]
    dest2 = os.path.join(OUT, "sheet_start_fights.png")
    subprocess.check_call([sys.executable, os.path.join(HERE, "contact_sheet.py"), dest2] + files)
    say(f"  pictures: {dest} (cards, order: none, minor2, minor4, major1, major4, world3, special2) and {dest2} (in the fight)")
    r2 = run_many([("startskip", "startskip", "SPO_CHEATS=start=major:3,skipall", NEW_BIN)])
    tags = [f"s{i}" for i in range(14)]
    rows = [(frame_of(r2["startskip"], t), wram(r2["startskip"], t)[0x601], wram(r2["startskip"], t)[0x600], wram(r2["startskip"], t)[0x602]) for t in tags]
    say(f"  start=major:3 + skip: (frame, circuit, index, left) = {rows}")
    check(rows[0][1:] == (1, 6, 1) and rows[-1][1:] == (1, 7, 0), "start at Major #3, skip it: the run moves on to the Major champion (index 7, 0 left)")

PROOFS = {"inert": proof_inert, "prefight": proof_prefight, "nohit": proof_nohit, "nohit_edge": proof_nohit_edge, "stars": proof_stars, "rest": proof_rest,
          "gameover": proof_gameover, "skip": proof_skip, "start": proof_start}

if __name__ == "__main__":
    write_routes()
    if "--run" in sys.argv:
        names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(PROOFS)
        os.makedirs(OUT, exist_ok=True)
        for n in names:
            PROOFS[n]()
        open(os.path.join(OUT, "REPORT.txt"), "w").write("\n".join(REPORT) + "\n")
        say(f"\n{len(FAILS)} FAILED" if FAILS else "\nALL PROOFS PASSED")
        sys.exit(1 if FAILS else 0)
