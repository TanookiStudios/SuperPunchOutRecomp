#!/usr/bin/env bash
# Runs INSIDE the build container (tools/make_linux.sh starts it).
# Builds the game into build-linux/. The engine's CMake downloads and builds
# SDL3 from source and links it in statically.
set -euo pipefail
cd /src
# FreeType off: it would add a system library the player may not have.
# OpenGL LEGACY: link libGL.so.1 (every desktop with graphics has it), not
# libOpenGL.so.0, which minimal desktops can lack.
cmake -S . -B build-linux -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_DISABLE_FIND_PACKAGE_Freetype=ON -DOpenGL_GL_PREFERENCE=LEGACY
cmake --build build-linux --parallel "$(nproc)"
