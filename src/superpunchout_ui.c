/* See superpunchout_ui.h. */
#include "superpunchout_ui.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "recomp_runtime_ui.h"
#include "snes/dsp.h"          /* g_dsp_voice_mute_mask */
#include "superpunchout_extras.h"

#define VOICES 8
#define FIGHTERS 16

static const char *const kFighters[1 + FIGHTERS] = {
    "Off (start with the first fight)",
    "Gabby Jay (Minor Circuit)", "Bear Hugger (Minor Circuit)",
    "Piston Hurricane (Minor Circuit)", "Bald Bull (Minor Circuit)",
    "Bob Charlie (Major Circuit)", "Dragon Chan (Major Circuit)",
    "Masked Muscle (Major Circuit)", "Mr. Sandman (Major Circuit)",
    "Aran Ryan (World Circuit)", "Heike Kagero (World Circuit)",
    "Mad Clown (World Circuit)", "Super Macho Man (World Circuit)",
    "Narcis Prince (Special Circuit)", "Hoy Quarlow (Special Circuit)",
    "Rick Bruiser (Special Circuit)", "Nick Bruiser (Special Circuit)",
};

#define MUTE_DESC "Silences one of the SNES's eight sound voices. The game decides what each voice plays."
#define BOOL_ROW(key, label, desc) { key, "Cheats", label, desc, \
                      RECOMP_RUNTIME_UI_BOOL, 0, 1, 1, NULL, 0, NULL }

static uint8_t s_fighter;   /* 0 off, 1..16 */

const RecompRuntimeUiItem kSpoMenuItems[SPO_MENU_ITEM_COUNT] = {
    /* Voice numbers on screen are 1-8; the keys count from 0 (see mute_voice). */
    { "spo.mute.0", "Audio", "Mute voice 1", MUTE_DESC, RECOMP_RUNTIME_UI_BOOL, 0, 1, 1, NULL, 0, NULL },
    { "spo.mute.1", "Audio", "Mute voice 2", MUTE_DESC, RECOMP_RUNTIME_UI_BOOL, 0, 1, 1, NULL, 0, NULL },
    { "spo.mute.2", "Audio", "Mute voice 3", MUTE_DESC, RECOMP_RUNTIME_UI_BOOL, 0, 1, 1, NULL, 0, NULL },
    { "spo.mute.3", "Audio", "Mute voice 4", MUTE_DESC, RECOMP_RUNTIME_UI_BOOL, 0, 1, 1, NULL, 0, NULL },
    { "spo.mute.4", "Audio", "Mute voice 5", MUTE_DESC, RECOMP_RUNTIME_UI_BOOL, 0, 1, 1, NULL, 0, NULL },
    { "spo.mute.5", "Audio", "Mute voice 6", MUTE_DESC, RECOMP_RUNTIME_UI_BOOL, 0, 1, 1, NULL, 0, NULL },
    { "spo.mute.6", "Audio", "Mute voice 7", MUTE_DESC, RECOMP_RUNTIME_UI_BOOL, 0, 1, 1, NULL, 0, NULL },
    { "spo.mute.7", "Audio", "Mute voice 8", MUTE_DESC, RECOMP_RUNTIME_UI_BOOL, 0, 1, 1, NULL, 0, NULL },
    BOOL_ROW("spo.hearts", "Infinite hearts", "Mac never runs out of hearts, so he can always throw punches."),
    BOOL_ROW("spo.stars", "Infinite stars", "Keeps your stars, so you can throw a super punch whenever you like."),
    BOOL_ROW("spo.hit", "Can't be hit", "Mac takes no damage and can't be knocked down."),
    { "spo.start", "Cheats", "Start at fighter", "New games begin against this fighter.",
      RECOMP_RUNTIME_UI_CHOICE, 0, FIGHTERS, 1, kFighters, 1 + FIGHTERS, NULL },
    { "spo.skip", "Cheats", "Skip to the next fight", "Ends the fight you are in as a win.",
      RECOMP_RUNTIME_UI_ACTION, 0, 0, 0, NULL, 0, NULL },
};

static void save(void) {
    FILE *f = fopen("superpunchout.ini", "w");
    if (!f) return;
    fprintf(f, "mute_mask=%u\nhearts=%d\nstars=%d\nhit=%d\nstart=%d\n",
            (unsigned)g_dsp_voice_mute_mask, g_spo_cheats.infinite_hearts,
            g_spo_cheats.infinite_stars, g_spo_cheats.cant_be_hit, s_fighter);
    fclose(f);
}

static void apply_fighter(void) {
    if (s_fighter == 0) {
        g_spo_cheats.start_at_opponent = 0;
        g_spo_cheats.start_circuit = 0;
    } else {
        g_spo_cheats.start_circuit = (uint8_t)((s_fighter - 1) / 4);
        g_spo_cheats.start_at_opponent = (uint8_t)((s_fighter - 1) % 4 + 1);
    }
}

void SpoUiLoad(void) {
    FILE *f = fopen("superpunchout.ini", "r");
    if (!f) return;
    char line[64];
    while (fgets(line, sizeof(line), f)) {
        unsigned v;
        if (sscanf(line, "mute_mask=%u", &v) == 1) g_dsp_voice_mute_mask = (uint8_t)v;
        else if (sscanf(line, "hearts=%u", &v) == 1) g_spo_cheats.infinite_hearts = v != 0;
        else if (sscanf(line, "stars=%u", &v) == 1) g_spo_cheats.infinite_stars = v != 0;
        else if (sscanf(line, "hit=%u", &v) == 1) g_spo_cheats.cant_be_hit = v != 0;
        else if (sscanf(line, "start=%u", &v) == 1) s_fighter = v > FIGHTERS ? 0 : (uint8_t)v;
    }
    fclose(f);
    apply_fighter();
}

static int mute_voice(const RecompRuntimeUiItem *it) {
    if (!it->key || strncmp(it->key, "spo.mute.", 9)) return -1;
    int v = atoi(it->key + 9);
    return v >= 0 && v < VOICES ? v : -1;
}

static int get_value(void *ctx, const RecompRuntimeUiItem *it, int *out) {
    (void)ctx;
    int v = mute_voice(it);
    if (v >= 0) *out = (g_dsp_voice_mute_mask >> v) & 1;
    else if (!strcmp(it->key, "spo.hearts")) *out = g_spo_cheats.infinite_hearts;
    else if (!strcmp(it->key, "spo.stars")) *out = g_spo_cheats.infinite_stars;
    else if (!strcmp(it->key, "spo.hit")) *out = g_spo_cheats.cant_be_hit;
    else if (!strcmp(it->key, "spo.start")) *out = s_fighter;
    else return 0;
    return 1;
}

static int set_value(void *ctx, const RecompRuntimeUiItem *it, int value) {
    (void)ctx;
    int v = mute_voice(it);
    if (v >= 0) {
        if (value) g_dsp_voice_mute_mask |= (uint8_t)(1u << v);
        else g_dsp_voice_mute_mask &= (uint8_t)~(1u << v);
    } else if (!strcmp(it->key, "spo.hearts")) g_spo_cheats.infinite_hearts = value != 0;
    else if (!strcmp(it->key, "spo.stars")) g_spo_cheats.infinite_stars = value != 0;
    else if (!strcmp(it->key, "spo.hit")) g_spo_cheats.cant_be_hit = value != 0;
    else if (!strcmp(it->key, "spo.start")) {
        s_fighter = value < 0 || value > FIGHTERS ? 0 : (uint8_t)value;
        apply_fighter();
    } else return 0;
    save();
    return 1;
}

static int run_action(void *ctx, const RecompRuntimeUiItem *it) {
    (void)ctx;
    if (!strcmp(it->key, "spo.skip")) { g_spo_cheats.skip_to_next = 1; return 1; }
    return 0;
}

static void save_cb(void *ctx) { (void)ctx; }

const RecompRuntimeUiCallbacks kSpoMenuCallbacks = {
    .context = NULL, .get_value = get_value, .set_value = set_value,
    .run_action = run_action, .is_enabled = NULL, .save = save_cb,
};

const char kSpoAboutText[] =
    "Hi, I'm Maddie. I make apps and games on my own at Tanooki Studios.\n\n"
    "Super Punch-Out!! is one of my favorite SNES games, and I wanted it to run on a modern "
    "computer with crisp pixels, controllers that just work, and a few cheats for when a "
    "fighter is being mean.\n\n"
    "It's free, and it'll stay free. You bring your own copy of the game; nothing from the "
    "original cartridge ships with this. It isn't made by or affiliated with Nintendo.\n\n"
    "Making apps (including some decomps) is how I pay my bills. If this game brought you "
    "some nostalgia and you got knocked out by Mr. Sandman more times than you'd like to "
    "admit, feel free to drop me a tiny tip. It really helps!";
