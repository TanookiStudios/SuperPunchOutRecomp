/* Minimal headless libretro host: refhost <core.dylib> <rom> <outdir> <script> 
 * script lines: "wait N" | "press BTN N" (hold BTN for N frames) | "dump TAG"
 * (zero-frame, saves the last video frame as TAG.ppm). Buttons as in our routes. */
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

struct retro_game_info { const char *path; const void *data; size_t size; const char *meta; };
struct retro_system_info { const char *library_name, *library_version, *valid_extensions; bool need_fullpath, block_extract; };
struct retro_game_geometry { unsigned base_width, base_height, max_width, max_height; float aspect_ratio; };
struct retro_system_timing { double fps, sample_rate; };
struct retro_system_av_info { struct retro_game_geometry geometry; struct retro_system_timing timing; };
struct retro_variable { const char *key, *value; };

static uint16_t pad_mask;
static int pixfmt = 0;               /* 0 = 0RGB1555, 1 = XRGB8888, 2 = RGB565 */
static unsigned W, H;
static uint8_t *frame;               /* RGB24 of the last frame */
static const char *sysdir = ".";

static bool env_cb(unsigned cmd, void *data) {
    switch (cmd) {
    case 9: case 31: *(const char **)data = sysdir; return true;           /* system / save dir */
    case 10: pixfmt = *(int *)data; return true;                           /* pixel format */
    case 15: ((struct retro_variable *)data)->value = NULL; return false;  /* variables: defaults */
    case 17: *(bool *)data = false; return true;                           /* variable update */
    default: return false;
    }
}
static void video_cb(const void *d, unsigned w, unsigned h, size_t pitch) {
    if (!d) return;
    W = w; H = h;
    frame = realloc(frame, (size_t)w * h * 3);
    for (unsigned y = 0; y < h; y++) {
        const uint8_t *row = (const uint8_t *)d + y * pitch;
        for (unsigned x = 0; x < w; x++) {
            uint8_t r, g, b;
            if (pixfmt == 1) { uint32_t p = ((const uint32_t *)row)[x]; r = p >> 16; g = p >> 8; b = p; }
            else if (pixfmt == 2) { uint16_t p = ((const uint16_t *)row)[x]; r = ((p >> 11) & 31) * 255 / 31; g = ((p >> 5) & 63) * 255 / 63; b = (p & 31) * 255 / 31; }
            else { uint16_t p = ((const uint16_t *)row)[x]; r = ((p >> 10) & 31) * 255 / 31; g = ((p >> 5) & 31) * 255 / 31; b = (p & 31) * 255 / 31; }
            uint8_t *o = frame + ((size_t)y * w + x) * 3; o[0] = r; o[1] = g; o[2] = b;
        }
    }
}
static void audio_cb(int16_t l, int16_t r) { (void)l; (void)r; }
static size_t audio_batch_cb(const int16_t *d, size_t n) { (void)d; return n; }
static void poll_cb(void) {}
static int16_t input_cb(unsigned port, unsigned dev, unsigned idx, unsigned id) {
    (void)idx;
    if (port != 0 || dev != 1) return 0;
    return (pad_mask >> id) & 1;
}
static int button(const char *n) {
    static const char *names[] = {"b","y","select","start","up","down","left","right","a","x","l","r"};
    for (int i = 0; i < 12; i++) if (!strcmp(n, names[i])) return i;
    fprintf(stderr, "unknown button %s\n", n); exit(2);
}
int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage\n"); return 2; }
    void *h = dlopen(argv[1], RTLD_NOW);
    if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
#define SYM(n) void *n##_p = dlsym(h, "retro_" #n)
    void (*set_env)(void *) = dlsym(h, "retro_set_environment");
    void (*set_video)(void *) = dlsym(h, "retro_set_video_refresh");
    void (*set_audio)(void *) = dlsym(h, "retro_set_audio_sample");
    void (*set_batch)(void *) = dlsym(h, "retro_set_audio_sample_batch");
    void (*set_poll)(void *) = dlsym(h, "retro_set_input_poll");
    void (*set_input)(void *) = dlsym(h, "retro_set_input_state");
    void (*init)(void) = dlsym(h, "retro_init");
    bool (*load)(const struct retro_game_info *) = dlsym(h, "retro_load_game");
    void (*run)(void) = dlsym(h, "retro_run");
    void (*ctrl)(unsigned, unsigned) = dlsym(h, "retro_set_controller_port_device");
    void *(*getmem)(unsigned) = dlsym(h, "retro_get_memory_data");
    size_t (*memsize)(unsigned) = dlsym(h, "retro_get_memory_size");
    set_env(env_cb); init();
    set_video(video_cb); set_audio(audio_cb); set_batch(audio_batch_cb); set_poll(poll_cb); set_input(input_cb);
    if (ctrl) ctrl(0, 1);
    FILE *f = fopen(argv[2], "rb"); fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    uint8_t *rom = malloc(n); fread(rom, 1, n, f); fclose(f);
    struct retro_game_info gi = { argv[2], rom, (size_t)n, NULL };
    if (!load(&gi)) { fprintf(stderr, "load failed\n"); return 1; }
    FILE *s = fopen(argv[4], "r"); char line[256]; unsigned frames = 0;
    while (fgets(line, sizeof line, s)) {
        char a[64] = "", b[64] = ""; int cnt = 0;
        int k = sscanf(line, "%63s %63s %d", a, b, &cnt);
        if (k < 1 || a[0] == '#') continue;
        if (!strcmp(a, "wait")) { int c = atoi(b); for (int i = 0; i < c; i++) { pad_mask = 0; run(); frames++; } }
        else if (!strcmp(a, "press")) { int bit = button(b); for (int i = 0; i < cnt; i++) { pad_mask = 1u << bit; run(); frames++; } pad_mask = 0; }
        else if (!strcmp(a, "dump")) {
            char p[512]; snprintf(p, sizeof p, "%s/%s.ppm", argv[3], b);
            FILE *o = fopen(p, "wb"); fprintf(o, "P6\n%u %u\n255\n", W, H); fwrite(frame, 3, (size_t)W * H, o); fclose(o);
            static const unsigned ids[] = {2, 3}; static const char *nm[] = {"wram", "vram"};
            for (int q = 0; q < 2; q++) {
                void *m = getmem(ids[q]); size_t z = memsize(ids[q]);
                if (m && z) { snprintf(p, sizeof p, "%s/%s.%s.bin", argv[3], b, nm[q]); o = fopen(p, "wb"); fwrite(m, 1, z, o); fclose(o); }
            }
        }
    }
    fprintf(stderr, "ran %u frames, last frame %ux%u fmt %d\n", frames, W, H, pixfmt);
    return 0;
}
