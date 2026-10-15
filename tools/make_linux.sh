#!/usr/bin/env bash
# Build the Linux release on this Mac inside an Ubuntu 20.04 container (Colima)
# and pack dist/SuperPunchOut-Linux.tar.gz, copied to ~/Downloads. No ROM inside.
# Needs: brew install colima docker; colima start --vm-type vz --vz-rosetta --arch aarch64
# (colima stop afterwards), vendor/ from setup.sh, and the ROM at
# rom/superpunchout.sfc (only to scan the package for ROM bytes).
# SDL3 is built from source inside the container and linked in statically.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p work/docker-config; [ -f work/docker-config/config.json ] || echo '{}' > work/docker-config/config.json
export DOCKER_CONFIG="$PWD/work/docker-config" DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"
docker image inspect superpunchout-linux-build >/dev/null 2>&1 || docker build --platform linux/amd64 -t superpunchout-linux-build tools/linux
docker run --rm --platform linux/amd64 -v "$PWD":/src superpunchout-linux-build /src/tools/linux/build.sh >/dev/null
OUT=dist/SuperPunchOut-Linux
rm -rf "$OUT" "$OUT.tar.gz"; mkdir -p "$OUT"
# The program must be named SuperPunchOut (the CMake target keeps its name).
cp build-linux/SuperPunchOutRecomp "$OUT/SuperPunchOut"
cp -R build-linux/assets "$OUT/assets"
[ -d build-linux/mods ] && cp -R build-linux/mods "$OUT/mods"
cp LICENSE THIRD_PARTY_NOTICES.md "$OUT/"
cp assets/icon/superpunchout-256.png "$OUT/superpunchout.png"
cp tools/linux/superpunchout.desktop tools/linux/README-Linux.txt tools/linux/install-shortcut.sh "$OUT/"

# Checks: 64-bit Intel/AMD, and no libraries beyond what any 2020+ desktop has.
# (SDL3 is inside the program; it opens the sound and window libraries itself at run time.)
file "$OUT/SuperPunchOut" | grep -q "ELF 64-bit.*x86-64" || { echo "FAIL: not a 64-bit Intel/AMD program" >&2; exit 1; }
NEEDED=$(docker run --rm --platform linux/amd64 -v "$PWD/$OUT":/pkg superpunchout-linux-build sh -c 'ldd /pkg/SuperPunchOut' | awk '{print $1}')
echo "Libraries the program needs:"; echo "$NEEDED" | sed 's/^/  /'
BAD=$(echo "$NEEDED" | grep -v -E '^(linux-vdso\.so\.1|/lib64/ld-linux-x86-64\.so\.2|libc\.so\.6|libm\.so\.6|libdl\.so\.2|libpthread\.so\.0|librt\.so\.1|libGL\.so\.1|libGLdispatch\.so\.0|libGLX\.so\.0|libstdc\+\+\.so\.6|libgcc_s\.so\.1|libX11\.so\.6|libxcb\.so\.1|libXau\.so\.6|libXdmcp\.so\.6|libbsd\.so\.0|libmd\.so\.0)$' || true)
[ -z "$BAD" ] || { echo "FAIL: unusual libraries needed:" >&2; echo "$BAD" >&2; exit 1; }
python3 -I tools/release_scan.py "$OUT"

tar -C dist -czf "$OUT.tar.gz" SuperPunchOut-Linux
# Finished games always go to Downloads (Maddie, 14 Oct 2026).
cp -f "$OUT.tar.gz" "$HOME/Downloads/"
echo "$HOME/Downloads/SuperPunchOut-Linux.tar.gz"
