#!/usr/bin/env bash
# Cross-build the Windows version on this Mac and zip it as
# dist/SuperPunchOut-Windows.zip (copied to ~/Downloads).
# Needs: brew install mingw-w64, vendor/ from setup.sh, and the ROM at
# rom/superpunchout.sfc (only to scan the zip contents for ROM bytes).
# The zip holds no ROM: the launcher asks for one. SDL3 is built from source
# by the engine's CMake and linked into the .exe (static), so the zip needs
# no SDL3.dll; this script checks that every DLL the .exe imports is either
# built into Windows or sits in the zip.
set -euo pipefail
cd "$(dirname "$0")/.."
OBJDUMP=x86_64-w64-mingw32-objdump
# SDL3 is hidden from CMake on purpose: Homebrew's SDL3 is a Mac library, and
# the engine must build its own Windows SDL3 (static) instead.
cmake -S . -B build-win -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE=cmake/mingw-w64.cmake \
    -DCMAKE_DISABLE_FIND_PACKAGE_SDL3=ON >/dev/null
cmake --build build-win --parallel 8 >/dev/null

OUT="dist/SuperPunchOut-Windows"
rm -rf "$OUT" "$OUT.zip"
mkdir -p "$OUT"
# The program must be named SuperPunchOut.exe (the CMake target keeps its name).
cp build-win/SuperPunchOutRecomp.exe "$OUT/SuperPunchOut.exe"
cp build-win/*.dll "$OUT/" 2>/dev/null || true   # none expected: SDL3 is static
cp -R build-win/assets "$OUT/assets"
[ -d build-win/mods ] && cp -R build-win/mods "$OUT/mods"
cp LICENSE THIRD_PARTY_NOTICES.md "$OUT/"

# Checks: a GUI program (no console window), icon built in, every DLL accounted for.
EXE="$OUT/SuperPunchOut.exe"
# (Output is captured first: "objdump | grep -q" can die of a broken pipe under pipefail.)
INFO=$(file "$EXE"); HDR=$($OBJDUMP -p "$EXE")
case "$INFO" in *"PE32+ executable (GUI) x86-64"*) ;; *) echo "FAIL: not a 64-bit Windows GUI program: $INFO" >&2; exit 1;; esac
case "$HDR" in *"(Windows GUI)"*) ;; *) echo "FAIL: subsystem is not Windows GUI" >&2; exit 1;; esac
# The icon is two top-level resource entries: RT_ICON (3) and RT_GROUP_ICON (14).
RES=$(sed -n '/Resource Directory section/,$p' <<<"$HDR")
for t in 3 e; do
    grep -q -E "^[0-9a-f]+   Entry: ID: 0x0*$t," <<<"$RES" || { echo "FAIL: icon resource type $t missing: the icon is not embedded" >&2; exit 1; }
done
SYSTEM_DLL='^(kernel32|user32|gdi32|shell32|advapi32|winmm|opengl32|imm32|ole32|oleaut32|setupapi|version|comdlg32|comctl32|shlwapi|ws2_32|cfgmgr32|msvcrt|ucrtbase|dbghelp|rpcrt4|combase|hid|bcrypt|crypt32|iphlpapi|d2d1|dwrite|dwmapi|uxtheme|shcore|mf|mfplat|mfreadwrite|cabinet|wininet|secur32|userenv|netapi32|powrprof|dinput8|xinput1_4|xinput9_1_0|d3d9|d3d11|dxgi|api-ms-win-.*)\.dll$'
MISSING=""
for dll in $(awk '/DLL Name:/ {print $3}' <<<"$HDR"); do
    lc=$(echo "$dll" | tr 'A-Z' 'a-z')
    if echo "$lc" | grep -q -E "$SYSTEM_DLL"; then continue; fi
    ls "$OUT" | tr 'A-Z' 'a-z' | grep -qx "$lc" || MISSING="$MISSING $dll"
done
[ -z "$MISSING" ] || { echo "FAIL: the .exe needs DLLs that are neither in Windows nor in the zip:$MISSING" >&2; exit 1; }
python3 -I tools/release_scan.py "$OUT"

( cd dist && zip -qr SuperPunchOut-Windows.zip SuperPunchOut-Windows )
# Finished games always go to Downloads (Maddie, 14 Oct 2026).
cp -f dist/SuperPunchOut-Windows.zip "$HOME/Downloads/"
echo "$HOME/Downloads/SuperPunchOut-Windows.zip"
