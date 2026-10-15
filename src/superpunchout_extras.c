/* Super Punch-Out!! cheats and extras. See superpunchout_extras.h and notes/ram-map.md. */
#include "superpunchout_extras.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "common_rtl.h"

SpoCheats g_spo_cheats;

/* ---- game RAM addresses (all proven in notes/ram-map.md) ---- */
enum {
    A_FIGHT_FLAG   = 0x0000, /* 1 = a fight is loaded and running; bit 7 = end-of-fight / restart request */
    A_REAL_FIGHT   = 0x0001, /* 1 in a real fight, 0x80 in the attract demo, 0 elsewhere */
    A_CIRCUIT_OPP  = 0x0600, /* opponent index in the roster = circuit*4 + (0..3) */
    A_CIRCUIT      = 0x0601, /* 0 Minor, 1 Major, 2 World, 3 Special */
    A_OPP_LEFT     = 0x0602, /* boxers left after this one: 3,2,1,0 (0 = champion) */
    A_LOSSES_HERE  = 0x0603,
    A_WINS         = 0x0604,
    A_LOSSES       = 0x0605,
    A_REST         = 0x0606, /* tries left (starts at 3) */
    A_MAC_HEALTH_F = 0x089E, /* Mac health, 8.8 fixed point: $089F = 0..80 */
    A_MAC_HEALTH   = 0x089F,
    A_METER        = 0x089C, /* super meter 0..27 */
    A_SOUND_CMD    = 0x0C00, /* music/sound request mailbox */
    A_FIGHT_ON     = 0x0B00, /* 1 while the fight engine runs */
    A_CLOCK_STATE  = 0x0B21, /* 0 = clock running, 0x40 = paused (intro, knockdown count), 0x41 = time up */
    A_SCRIPT_ID    = 0x0BA4, /* referee/announcer script id (x2) */
    A_SCRIPT_STEP  = 0x0BA6  /* its step (x2) */
};

enum { METER_FULL = 0x1B, HEALTH_FULL = 0x5000, SKIP_JINGLE_FRAMES = 205 };

/* Developer tool, off unless SPO_RAM_TRACE=<file> is set: append the first
 * SPO_RAM_TRACE_BYTES (default 0x2000) bytes of game RAM to <file> after every frame.
 * Used to find what changes when something happens in the game. */
static void SpoRamTrace(void)
{
    static int init;
    static FILE *f;
    static size_t bytes = 0x2000;
    if (!init) {
        init = 1;
        const char *p = getenv("SPO_RAM_TRACE");
        if (p && *p) f = fopen(p, "wb");
        const char *n = getenv("SPO_RAM_TRACE_BYTES");
        if (n && *n) bytes = (size_t)strtoul(n, NULL, 0);
        if (bytes > 0x20000) bytes = 0x20000;
    }
    if (f) fwrite(g_ram, 1, bytes, f);
}

static int s_skip_repeat;   /* test only: SPO_CHEATS=skipall re-arms skip after every use */

/* Developer / test switch, parsed once: SPO_CHEATS="hearts,stars,nohit,skip,rest,start=major:3"
 * SPO_CHEATS_FROM=<n> (test only) delays turning the cheats on until frame n, to prove they can be
 * flipped in the middle of a fight. */
static void SpoParseEnv(void)
{
    static int done;
    static unsigned frame;
    if (done) return;
    const char *from = getenv("SPO_CHEATS_FROM");
    if (from && *from && frame++ < strtoul(from, NULL, 0)) return;
    done = 1;
    const char *e = getenv("SPO_CHEATS");
    if (!e || !*e) return;
    char buf[256];
    strncpy(buf, e, sizeof buf - 1);
    buf[sizeof buf - 1] = 0;
    for (char *tok = strtok(buf, ", "); tok; tok = strtok(NULL, ", ")) {
        if (!strcmp(tok, "hearts"))      g_spo_cheats.infinite_hearts = 1;
        else if (!strcmp(tok, "stars"))  g_spo_cheats.infinite_stars = 1;
        else if (!strcmp(tok, "nohit"))  g_spo_cheats.cant_be_hit = 1;
        else if (!strcmp(tok, "skip"))   g_spo_cheats.skip_to_next = 1;
        else if (!strcmp(tok, "skipall")) { g_spo_cheats.skip_to_next = 1; s_skip_repeat = 1; }
        else if (!strcmp(tok, "rest"))   g_spo_cheats.infinite_rest = 1;
        else if (!strncmp(tok, "start=", 6)) {
            const char *c = tok + 6;
            const char *colon = strchr(c, ':');
            int circuit = 0, opp = colon ? atoi(colon + 1) : 1;
            if (!strncmp(c, "minor", 5)) circuit = 0;
            else if (!strncmp(c, "major", 5)) circuit = 1;
            else if (!strncmp(c, "world", 5)) circuit = 2;
            else if (!strncmp(c, "special", 7)) circuit = 3;
            else circuit = atoi(c);
            if (circuit < 0 || circuit > 3 || opp < 1 || opp > 4) {
                fprintf(stderr, "[spo cheats] bad start= value '%s' (want minor|major|world|special:1..4)\n", tok);
                continue;
            }
            g_spo_cheats.start_circuit = (uint8_t)circuit;
            g_spo_cheats.start_at_opponent = (uint8_t)opp;
        } else {
            fprintf(stderr, "[spo cheats] unknown SPO_CHEATS entry '%s'\n", tok);
        }
    }
}

void SpoCheatsApplyAfterFrame(void)
{
    static uint8_t prev_rest;
    static int skip_phase, skip_timer;
    uint8_t *m = g_ram;

    SpoRamTrace();
    SpoParseEnv();

    /* "A fight is loaded and the player is in it": not title/menu/card/results ($0000 is 0 or has
     * bit 7 set there), not the attract demo ($0001 is 0x80 there). Includes the boxer intro and
     * knockdown counts; the individual cheats below are written so that is harmless. */
    uint8_t fight = (m[A_FIGHT_FLAG] == 1 && m[A_REAL_FIGHT] == 1 && m[A_FIGHT_ON] == 1);
    uint8_t play = fight && m[A_CLOCK_STATE] == 0;   /* clock running */
    uint16_t health = (uint16_t)(m[A_MAC_HEALTH_F] | (m[A_MAC_HEALTH] << 8));

    /* New game: right after the new-game setup wrote REST=3 and a fresh circuit block, move the
     * run to the chosen circuit and boxer. Fires once per circuit run; touches only these 3 bytes. */
    if (g_spo_cheats.start_at_opponent && m[A_REST] == 3 && prev_rest != 3 && m[A_LOSSES_HERE] == 0 &&
        m[A_WINS] == 0 && m[A_LOSSES] == 0 && m[A_OPP_LEFT] == 3 && m[A_CIRCUIT] < 4 &&
        m[A_CIRCUIT_OPP] == m[A_CIRCUIT] * 4) {
        uint8_t c = g_spo_cheats.start_circuit & 3, n = (uint8_t)((g_spo_cheats.start_at_opponent - 1) & 3);
        m[A_CIRCUIT] = c;
        m[A_CIRCUIT_OPP] = (uint8_t)(c * 4 + n);
        m[A_OPP_LEFT] = (uint8_t)(3 - n);
    }

    /* REST (tries left): undo a drop of exactly one, only while a fight is loaded. */
    if (g_spo_cheats.infinite_rest && m[A_FIGHT_FLAG] != 0 && prev_rest >= 1 && prev_rest <= 3 &&
        m[A_REST] == prev_rest - 1)
        m[A_REST] = prev_rest;

    /* Mac's health: keep it full while he is standing. The game decides "knocked down" inside the same
     * frame the punch lands (the damage routine reports "health is 0" straight to the caller), so undoing a
     * drop at the end of the frame is too late for a punch that would empty the bar. Topping him up first
     * means no single punch can. A boxer who is already on the floor (health 0) is left alone. */
    if (g_spo_cheats.cant_be_hit && fight && health != 0 && health < HEALTH_FULL) {
        m[A_MAC_HEALTH_F] = 0;
        m[A_MAC_HEALTH] = HEALTH_FULL >> 8;
        health = HEALTH_FULL;
    }

    /* Super meter: always full while a fight is loaded. */
    if (g_spo_cheats.infinite_stars && fight && m[A_METER] < METER_FULL)
        m[A_METER] = METER_FULL;

    /* Skip to next opponent: play the KO jingle for ~3.4 s, then jump the fight's referee script to its
     * "fade out and report a Mac win" step. Starting only while the clock runs. */
    if (skip_phase == 0 && g_spo_cheats.skip_to_next && play) {
        m[A_SOUND_CMD] = 0x82;
        skip_phase = 1;
        skip_timer = SKIP_JINGLE_FRAMES;
    } else if (skip_phase == 1) {
        if (!fight) {                       /* the fight ended by itself: nothing to do */
            skip_phase = 0;
            g_spo_cheats.skip_to_next = s_skip_repeat;
        } else if (--skip_timer <= 0) {
            m[A_SOUND_CMD] = 0;
            m[A_SCRIPT_ID] = 0x0E;
            m[A_SCRIPT_STEP] = 0x08;
            skip_phase = 0;
            g_spo_cheats.skip_to_next = s_skip_repeat;
        }
    }

    prev_rest = m[A_REST];
}
