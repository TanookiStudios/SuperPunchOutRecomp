/*
 * Super Punch-Out!! — per-game runtime glue.
 *
 * THIS FILE IS THE PORT. Everything else the scaffold produced is layout,
 * build wiring, and packaging; this is where the actual work happens.
 *
 * The framework does not, and cannot, drive an arbitrary SNES game on its
 * own. Two responsibilities always land on the game host:
 *
 *   1. Deciding what "one frame" means for THIS title, and returning from
 *      run_frame() at that boundary. A real ROM's reset vector never
 *      returns — it enters a main loop that waits on vblank — so somebody
 *      has to choose the yield point.
 *   2. Delivering NMI/IRQ at the hardware edge (see
 *      snesrecomp/docs/FRAME_MODEL_HOSTS.md).
 *
 * A new port starts on the framework's beam-aligned driver
 * (runner/src/beam_frame_driver.h): one frame is one PPU field, cut at the
 * beam's vblank edge; interrupts -- raster splits and a coprocessor's IRQ
 * line -- are taken where the beam latches them; parked time still runs the
 * beam, APU and coprocessors; and the field is rasterized from the raster
 * journal with real HDMA. It is the framework's, so a fix to it reaches this
 * port on a submodule pull.
 *
 * This file used to hold its own copy of a simpler driver: frames measured
 * from wherever the CPU last stopped, NMI delivered at an arbitrary beam
 * position, the field drawn with end-of-frame register state. A game that
 * uploads in vblank between INIDISP=$80 and $0F flickered black, and one
 * that chains raster splits fell apart. Replace these calls only for what
 * the driver does not do; MetalWarriorsSNESRecomp's src/mw_rtl.c and
 * GundamWingEndlessDuelSNESRecomp's src/game_rtl.c are developed examples of
 * title-specific drivers.
 */

#include "game_rtl.h"

#include "beam_frame_driver.h"
#include "snes/dma.h"
#include "cpu_state.h"
#include "superpunchout_extras.h"

void GameRunOneFrame(void)
{
    /* This game switches its screen effects on partway down the picture and
     * relies on them staying idle until the next field. */
    g_dma_hdma_midframe_inert = 2;
    static int excluded;
    if (!excluded && !getenv("SPO_NO_EXCLUSIONS")) {
        /* Four routines left to the original code: played as translated code, the title and the
         * "How to win" demo stop matching Snes9x frame for frame (see tests/ref/README.md). Raster
         * interrupts no longer wait for translated code (patches/0010), so nothing else needs this. */
        static const uint32 kInterpTargets[] = { 0x00F440, 0x00FFA3, 0x018006, 0x088035 };
        const char *only = getenv("SPO_EXCLUDE");   /* dev switch: "00F440,00FFA3" replaces the list below */
        if (only && *only) {
            uint32 list[64]; size_t n = 0;
            for (const char *q = only; *q && n < 64; ) {
                list[n++] = (uint32)strtoul(q, (char **)&q, 16);
                while (*q == ',') ++q;
            }
            interp_bridge_set_lle_bounce_exclusions(list, n);
        } else
        interp_bridge_set_lle_bounce_exclusions(kInterpTargets, sizeof kInterpTargets / sizeof kInterpTargets[0]);
        excluded = 1;
    }
    snes_beam_frame_driver_run_frame();
    SpoCheatsApplyAfterFrame();
}

void GameDrawPpuFrame(void)
{
    snes_beam_frame_driver_draw_ppu_frame();
}

void GameSessionReset(void)
{
    /* Rematch / soft-return: clear anything that must not survive a new
     * session. recomp-ai-rules/NETPLAY.md §3 — sticky state that "has always
     * been fine" is the usual desync culprit, because single-player never
     * re-enters the boot path twice in one process. */
    snes_beam_frame_driver_reset();
}

const RtlGameInfo kGameInfo = {
    .title = "superpunchout",
    .initialize = NULL,
    .run_frame = &GameRunOneFrame,
    .draw_ppu_frame = &GameDrawPpuFrame,
    .save_name_prefix = "save",
    .session_reset = &GameSessionReset,
};
