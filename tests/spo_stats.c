/* Test-only (not part of the shipped game): prints, when the game exits, how much work the
 * interpreter did versus how many recompiled functions were entered from it.
 * Added to the build only by tests/extras_build.cmake. */
#include <stdio.h>
#include <stdlib.h>

extern unsigned long long g_interp_bridge_bounces; /* recompiled functions entered from the interpreter */
extern unsigned long long g_interp_bridge_steps;   /* instructions the interpreter ran */

static void spo_stats_report(void)
{
    fprintf(stderr, "[spo-stats] interpreter_instructions=%llu native_function_entries_from_interpreter=%llu\n",
            g_interp_bridge_steps, g_interp_bridge_bounces);
}

__attribute__((constructor)) static void spo_stats_register(void)
{
    atexit(spo_stats_report);
}
