#!/usr/bin/env python3
"""Writes the route_*.txt input scripts from small named pieces, so a change to the
menu walk-through is made once. Run:  python3 tests/gen_routes.py   (rewrites tests/route_*.txt)

Every piece is plain host-script text (press / wait / until / poke / dump ...).
Timings were measured on the real game and are repeatable: the emulation is
deterministic and the harness always starts from an empty save.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def press(btn, n=4):  return [f"press {btn} {n}"]
def wait(n):          return [f"wait {n}"]

def boot_to_title():            # intro + "How to win" attract run, then the title screen
    return wait(1200)

def title_to_name_screen():     # PUSH START -> NEW GAME -> Name Registration
    return press("start") + wait(200) + press("start") + wait(100)

def name_to_card():             # name "A", OK, Championship mode, Minor circuit, first boxer card
    return (press("a") + wait(30) + press("start") + wait(30) + press("start") + wait(60)
            + press("a") + wait(76) + press("a") + wait(76) + press("a") + wait(76))

def card_to_fight():            # skip the boxer's speech and wait through the intro
    return press("a") + wait(76) + press("a") + wait(76) + press("a") + wait(76) + press("a") + wait(76)

def to_fight():
    return boot_to_title() + title_to_name_screen() + name_to_card() + card_to_fight()

def write(name, frames, lines, header=""):
    with open(os.path.join(HERE, name), "w") as f:
        if header: f.write("".join("# " + l + "\n" for l in header.strip().splitlines()))
        f.write(f"#@ frames={frames}\n")
        f.write("\n".join(lines) + "\n")

PAT = ["b", "y", "a", "x", "b", "y", "b", "a"]

def mash(reps, dump_every=0, tag="m", each=()):
    """Punch pattern with a dodge each round of it (128+56 frames per repeat)."""
    out = []
    for r in range(reps):
        out += list(each)
        for b in PAT: out += press(b, 3) + wait(13)
        out += press("left", 8) + wait(20) + press("right", 8) + wait(20) + press("down", 8) + wait(0)
        if dump_every and r % dump_every == dump_every - 1: out.append(f"dump {tag}{r // dump_every:02d}")
    return out

ROUTES = {}

ROUTES["route_attract.txt"] = (6000, "Hands off the controller for 6000 frames: intro, title, then the attract demos.",
    sum([wait(500) + [f"dump a{i:02d}"] for i in range(11)], []) + wait(400))

ROUTES["route_fight_gabby.txt"] = (6000, "Title -> Name 'A' -> Championship -> Minor circuit -> first fight (Gabby Jay), then punch/dodge for the rest of 6000 frames (Mac gets hurt and knocked down, so both fighters go down).",
    to_fight() + wait(300) + ["dump fight_start"] + mash(18, 2, "play") + ["dump end"])

ROUTES["route_win_next.txt"] = (9000, "First fight, but the boxer's health is set to 1 before every punch round so a landed punch knocks him out: the game's own knockout, results, next-boxer card (Bear Hugger) and second fight run. Evidence dumps along the way.",
    to_fight() + wait(300) + mash(14, 2, "ko", each=["poke 099F 01", "poke 098F 01"]) + wait(900) + ["dump after_ko"]
    + press("start") + wait(300) + ["dump next_a"] + press("a") + wait(200) + press("a") + wait(300) + ["dump next_b"] + mash(4, 2, "f2") + ["dump end"])

def lose_loop(n):
    out = []
    for i in range(n):
        out += press("start") + wait(300) + [f"dump l{i}a"] + press("start") + wait(300) + [f"dump l{i}b"] + press("a") + wait(150) + press("a") + wait(150)
        out += wait(2400) + [f"dump loss{i}"]
    return out

ROUTES["route_lose.txt"] = (22500, "First fight with Mac's health held at 1 and no input: Gabby knocks him out, the results screen shows, Start brings the boxer's card and the fight again; repeated until the tries (REST) run out and the game over / menu path plays.",
    to_fight() + wait(300) + ["forcepoke 089F 01", "forcepoke 088F 01"] + wait(2300) + ["dump results"]
    + lose_loop(5) + press("start") + wait(600) + ["dump end"])

def mode_select():              # name "A", OK -> the Mode select screen
    return boot_to_title() + title_to_name_screen() + press("a") + wait(30) + press("start") + wait(120)

def menu_visit(downs, tag):
    """From Mode select: move down `downs` times, open that screen, poke around, back out twice."""
    out = []
    for _ in range(downs): out += press("down") + wait(30)
    out += press("a") + wait(250) + [f"dump {tag}a"] + press("down") + wait(30) + press("a") + wait(250) + [f"dump {tag}b"]
    out += press("start") + wait(250) + [f"dump {tag}c"] + press("b") + wait(150) + press("b") + wait(150) + press("b") + wait(150) + [f"dump {tag}d"]
    return out

ROUTES["route_menus.txt"] = (6500, "Name entry, then the Mode select screen: opens the Button Setting screen (the cursor wraps there), presses a few keys, changes and resets buttons.",
    mode_select() + sum([menu_visit(k, f"v{k}") for k in (1, 2, 3)], []))

def spam(btn, n, gap):
    return sum([press(btn) + wait(gap) for _ in range(n)], [])

def circuit_chain(circuit):
    """Plays all four boxers of one circuit using the cheats' switches (skip every fight, start at boxer 1)
    so every boxer's own fight code runs. Waits on the game's own 'boxers left' counter ($0602)."""
    out = [f"#@ netenv=SPO_CHEATS=skipall,start={circuit}:1"] + to_fight()
    out += ["until 0602 == 02 4000"] + spam("a", 12, 60) + ["until 0000 == 01 3000", "until 0602 == 01 4000"]
    out += spam("a", 12, 60) + ["until 0000 == 01 3000", "until 0602 == 00 4000"] + spam("a", 12, 60)
    out += ["until 0000 == 01 3000", "wait 1200", "dump champion"] + spam("a", 14, 60)
    out += ["dump end0", "wait 400", "dump end1", "wait 400", "dump end2"]
    return out

for _c in ("minor", "major", "world", "special"):
    ROUTES[f"route_circuit_{_c}.txt"] = (9000, f"Cheat switches on (skip every fight, start at boxer 1 of the {_c.title()} circuit): plays all four boxers' cards and fights, then the circuit-clear screens.",
        circuit_chain(_c))

def main():
    for name, (frames, desc, lines) in ROUTES.items():
        write(name, frames, lines, header=desc)
        print("wrote", name, frames, "frames")

if __name__ == "__main__":
    main()
