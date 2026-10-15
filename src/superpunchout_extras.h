/*
 * Super Punch-Out!! cheats and extras.
 *
 * Everything here is OFF by default and does nothing until a switch is turned on.
 * The menu (wired up later) just flips the fields of g_spo_cheats; the game loop calls
 * SpoCheatsApplyAfterFrame() once at the end of every frame.
 *
 * Every address and rule used here is proven in notes/ram-map.md.
 *
 * Developer / test switch: the environment variable SPO_CHEATS turns cheats on from the
 * command line (read once, on the first frame):
 *     SPO_CHEATS="hearts,stars,nohit,skip,rest,start=<circuit>:<opponent>"
 * any subset, comma separated.  <circuit> is minor|major|world|special (or 0..3),
 * <opponent> is 1..4 (4 = the circuit champion).  Example: SPO_CHEATS=nohit,start=major:3
 *
 * Which switches are safe to flip while a fight is running:
 *   infinite_hearts  harmless (does nothing, SPO has no hearts)
 *   infinite_stars   safe any time (refills the super meter whenever a fight is loaded)
 *   cant_be_hit      safe any time (tops Mac up to full health the frame it is on)
 *   infinite_rest    safe any time
 *   skip_to_next     press it only while a fight is in play (clock running); one-shot. If it is set
 *                    outside a fight it stays armed and fires at the first moment the clock runs
 *   start_*          only read at the moment a new circuit run starts (after the circuit
 *                    pick); flipping it mid-game has no effect until the next new game
 */
#ifndef SUPERPUNCHOUT_EXTRAS_H
#define SUPERPUNCHOUT_EXTRAS_H

#include <stdint.h>

typedef struct SpoCheats {
    /* In-fight cheats: only act while a fight is actually being played. */
    uint8_t infinite_hearts;   /* does NOTHING: Super Punch-Out has no hearts counter (kept so the menu list stays the same) */
    uint8_t infinite_stars;    /* super meter ($089C) is always full while a fight is loaded */
    uint8_t cant_be_hit;       /* Mac stays at full health while he is standing: no damage, no knockdowns (TIME UP can still lose) */
    uint8_t skip_to_next;      /* one-shot: ends the current fight as a win (about 4 s); clears itself */
    uint8_t infinite_rest;     /* REST ($0606, tries left) never goes down, so no Game Over */

    /* New-game cheat: applies once, when a circuit run starts (right after the circuit pick). */
    uint8_t start_at_opponent; /* 0 = off; 1..4 = begin the circuit at the 1st..4th boxer (4 = champion) */
    uint8_t start_circuit;     /* 0 Minor, 1 Major, 2 World, 3 Special (used with the above) */
} SpoCheats;

extern SpoCheats g_spo_cheats;

/* Call once at the end of every simulated frame. */
void SpoCheatsApplyAfterFrame(void);

#endif /* SUPERPUNCHOUT_EXTRAS_H */
