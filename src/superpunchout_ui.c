/* See superpunchout_ui.h. */
#include "superpunchout_ui.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "recomp_runtime_ui.h"
#include "desktop/sdl_compat.h"
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

/* The letter, shared by the launcher's About page and the Esc menu's About section. */
#define ABOUT_P1 "Hi, I'm Maddie. I make apps and games on my own at Tanooki Studios."
#define ABOUT_P2 "Super Punch-Out!! is one of my favorite SNES games, and I wanted it to run on a modern " \
                 "computer with crisp pixels, controllers that just work, and a few cheats for when a " \
                 "fighter is being mean."
#define ABOUT_P3 "It's free, and it'll stay free. You bring your own copy of the game; nothing from the " \
                 "original cartridge ships with this. It isn't made by or affiliated with Nintendo."
#define ABOUT_P4 "Making apps (including some decomps) is how I pay my bills. If this game brought you " \
                 "some nostalgia and you got knocked out by Mr. Sandman more times than you'd like to " \
                 "admit, feel free to drop me a tiny tip. It really helps!"

static const char *const kBlank[] = { " " };
#define INFO(key, label, desc) { key, "About", label, desc, RECOMP_RUNTIME_UI_CHOICE, 0, 0, 1, kBlank, 1, NULL }

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
    BOOL_ROW("spo.meter", "Full super meter", "Keeps the super meter full during a fight."),
    BOOL_ROW("spo.hit", "Can't be hit", "Mac stays at full health, so no damage and no knockdowns. Time running out can still lose the fight."),
    BOOL_ROW("spo.rest", "Infinite tries", "REST never goes down, so losing a fight never ends the game."),
    { "spo.start", "Cheats", "Start at fighter", "New games begin against this fighter.",
      RECOMP_RUNTIME_UI_CHOICE, 0, FIGHTERS, 1, kFighters, 1 + FIGHTERS, NULL },
    { "spo.skip", "Cheats", "Skip to the next fight", "Ends the fight you are in as a win.",
      RECOMP_RUNTIME_UI_ACTION, 0, 0, 0, NULL, 0, NULL },
    /* The About section of the Esc menu. The menu shows one line per label and per description, so the
     * letter is broken into short lines. The rows stay selectable so the keys can scroll through it. */
    INFO("spo.about.1", "Hi, I'm Maddie. I make apps and games on my own at Tanooki Studios.", ""),
    INFO("spo.about.2", "Super Punch-Out!! is one of my favorite SNES games, and I",
                        "wanted it to run on a modern computer with crisp pixels,"),
    INFO("spo.about.3", "controllers that just work, and a few cheats for when a", "fighter is being mean."),
    INFO("spo.about.4", "It's free, and it'll stay free. You bring your own copy of the",
                        "game; nothing from the original cartridge ships with this."),
    INFO("spo.about.5", "It isn't made by or affiliated with Nintendo.", ""),
    INFO("spo.about.6", "Making apps (including some decomps) is how I pay my bills.",
                        "If this game brought you some nostalgia and you got knocked out"),
    INFO("spo.about.7", "by Mr. Sandman more times than you'd like to admit, feel free",
                        "to drop me a tiny tip. It really helps!"),
    { "spo.about.tip", "About", "Leave a Tip", "Opens tanookistudios.com/SupportMe in your browser.",
      RECOMP_RUNTIME_UI_ACTION, 0, 0, 0, NULL, 0, NULL },
    INFO("spo.about.sig", "- Maddie", "Tanooki Studios"),
};

static void save(void) {
    FILE *f = fopen("superpunchout.ini", "w");
    if (!f) return;
    fprintf(f, "mute_mask=%u\nmeter=%d\nhit=%d\nrest=%d\nstart=%d\n",
            (unsigned)g_dsp_voice_mute_mask, g_spo_cheats.infinite_stars,
            g_spo_cheats.cant_be_hit, g_spo_cheats.infinite_rest, s_fighter);
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
        else if (sscanf(line, "meter=%u", &v) == 1) g_spo_cheats.infinite_stars = v != 0;
        else if (sscanf(line, "hit=%u", &v) == 1) g_spo_cheats.cant_be_hit = v != 0;
        else if (sscanf(line, "rest=%u", &v) == 1) g_spo_cheats.infinite_rest = v != 0;
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
    if (it->key && !strncmp(it->key, "spo.about.", 10)) *out = 0;   /* reading rows */
    else if (v >= 0) *out = (g_dsp_voice_mute_mask >> v) & 1;
    else if (!strcmp(it->key, "spo.meter")) *out = g_spo_cheats.infinite_stars;
    else if (!strcmp(it->key, "spo.hit")) *out = g_spo_cheats.cant_be_hit;
    else if (!strcmp(it->key, "spo.rest")) *out = g_spo_cheats.infinite_rest;
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
    } else if (!strcmp(it->key, "spo.meter")) g_spo_cheats.infinite_stars = value != 0;
    else if (!strcmp(it->key, "spo.hit")) g_spo_cheats.cant_be_hit = value != 0;
    else if (!strcmp(it->key, "spo.rest")) g_spo_cheats.infinite_rest = value != 0;
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
    if (!strcmp(it->key, "spo.about.tip")) { SDL_OpenURL("https://tanookistudios.com/SupportMe"); return 1; }
    return 0;
}

static void save_cb(void *ctx) { (void)ctx; }

const RecompRuntimeUiCallbacks kSpoMenuCallbacks = {
    .context = NULL, .get_value = get_value, .set_value = set_value,
    .run_action = run_action, .is_enabled = NULL, .save = save_cb,
};

const char kSpoAboutText[] = ABOUT_P1 "\n\n" ABOUT_P2 "\n\n" ABOUT_P3 "\n\n" ABOUT_P4;
