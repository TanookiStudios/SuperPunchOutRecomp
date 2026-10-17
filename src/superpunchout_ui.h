/* Super Punch-Out!! options shown on the launcher's Game page and in the
 * in-game menu, and the About page text. */
#ifndef SUPERPUNCHOUT_UI_H
#define SUPERPUNCHOUT_UI_H

#include <stddef.h>

#include "recomp_runtime_ui.h"

#define SPO_MENU_ITEM_COUNT 22
#define SPO_LAUNCHER_ITEM_COUNT 13   /* the rows before the About section */
extern const RecompRuntimeUiItem kSpoMenuItems[SPO_MENU_ITEM_COUNT];
extern const RecompRuntimeUiCallbacks kSpoMenuCallbacks;
extern const char kSpoAboutText[];

/* Reads superpunchout.ini from the settings folder and applies it. Call once
 * the settings folder is the working directory (the host's after_config). */
void SpoUiLoad(void);

#endif
