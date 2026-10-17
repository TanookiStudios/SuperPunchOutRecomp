#!/usr/bin/env bash
# Build "Super Punch-Out.app" for every Mac (Apple chips and Intel, macOS 11+),
# signed with the Developer ID, and zip it as SuperPunchOut-Mac.zip.
# Copies the zip (and the app) to ~/Downloads.
#
#   tools/make_app.sh            build + sign + zip
#   tools/make_app.sh --notarize also notarize with Apple and staple, then zip
#                                (dist/SuperPunchOut-Mac.zip, copied to ~/Downloads)
#
# Needs: vendor/ from setup.sh, the ROM at rom/superpunchout.sfc (only to scan
# the finished app for ROM bytes), a "Developer ID Application" certificate
# (without one the app is signed ad-hoc and says so), and for --notarize the
# notarytool keychain profile "notarytool". The app contains no ROM: the
# launcher asks for one. SDL3 is built from source by the engine's CMake and
# linked into the program, so nothing else has to be installed.
#
# The program inside is named SuperPunchOut (not the CMake target name),
# because on a Mac the settings folder is
# ~/Library/Application Support/<program name>/.
set -euo pipefail
cd "$(dirname "$0")/.."
NOTARIZE=0; [ "${1:-}" = "--notarize" ] && NOTARIZE=1
ID="Developer ID Application"

# Homebrew's SDL3/freetype/harfbuzz must never leak into the Mac build: they
# are Apple-chip-only dylibs that other Macs do not have. Hide them from CMake;
# the engine then builds SDL3 itself, static and universal.
cmake -S . -B build-mac -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" -DCMAKE_OSX_DEPLOYMENT_TARGET=11.0 \
    -DCMAKE_DISABLE_FIND_PACKAGE_SDL3=ON \
    -DCMAKE_DISABLE_FIND_PACKAGE_Freetype=ON -DCMAKE_DISABLE_FIND_PACKAGE_PkgConfig=ON \
    -DCMAKE_IGNORE_PREFIX_PATH=/opt/homebrew:/usr/local >/dev/null
cmake --build build-mac --parallel 8 >/dev/null

APP="dist/Super Punch-Out.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp build-mac/SuperPunchOutRecomp "$APP/Contents/MacOS/SuperPunchOut"
# Inside an .app, SDL looks for the launcher's fonts, pictures (icon, signature) and the controller database
# in Contents/Resources, NOT beside the program: put them there or the launcher shows a plain font and no
# icon or signature.
cp -R build-mac/assets "$APP/Contents/Resources/assets"
for need in img/maddie-signature.png img/brand_mark.tga fonts/LatoLatin-Regular.ttf gamecontrollerdb.txt; do
  [ -e "$APP/Contents/Resources/assets/$need" ] || { echo "make_app: $need is missing from the app's Resources/assets" >&2; exit 1; }
done
[ -d build-mac/mods ] && cp -R build-mac/mods "$APP/Contents/MacOS/mods"
cp assets/icon/AppIcon.icns "$APP/Contents/Resources/AppIcon.icns"
cp LICENSE THIRD_PARTY_NOTICES.md "$APP/Contents/Resources/"
VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || true)
VERSION=${VERSION:-$(tr -d '[:space:]' < VERSION)}
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Super Punch-Out</string>
  <key>CFBundleDisplayName</key><string>Super Punch-Out</string>
  <key>CFBundleIdentifier</key><string>com.tanookistudios.superpunchoutrecomp</string>
  <key>CFBundleExecutable</key><string>SuperPunchOut</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundleShortVersionString</key><string>$VERSION</string>
  <key>CFBundleVersion</key><string>$VERSION</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>LSApplicationCategoryType</key><string>public.app-category.arcade-games</string>
</dict></plist>
PLIST

# Checks before signing: both chips, nothing but system libraries, no ROM.
BIN="$APP/Contents/MacOS/SuperPunchOut"
ARCHS=$(lipo -archs "$BIN")
case "$ARCHS" in *arm64*x86_64*|*x86_64*arm64*) ;; *) echo "FAIL: app is not universal (got: $ARCHS)" >&2; exit 1;; esac
BAD=$(otool -L "$BIN" | grep '^[[:space:]]' | awk '{print $1}' | grep -v -E '^(/usr/lib/|/System/Library/)' || true)
if [ -n "$BAD" ]; then echo "FAIL: app needs libraries other Macs do not have:" >&2; echo "$BAD" >&2; exit 1; fi
python3 -I tools/release_scan.py "$APP"

if [ -n "$(security find-identity -v -p codesigning | grep "$ID")" ]; then
    codesign --force --deep --options runtime --timestamp --sign "$ID" "$APP" >/dev/null
    echo "Signed with: $ID"
else
    # Not notarizable, and other Macs will warn; fine for a local test.
    codesign --force --deep --sign - "$APP" >/dev/null
    echo "WARNING: no Developer ID certificate in the keychain; signed AD-HOC." >&2
    [ "$NOTARIZE" = 1 ] && { echo "FAIL: --notarize needs the Developer ID certificate" >&2; exit 1; }
fi
codesign --verify --deep --strict "$APP"

ZIP=dist/SuperPunchOut-Mac.zip
rm -f "$ZIP"
if [ "$NOTARIZE" = 1 ]; then
    ditto -c -k --keepParent "$APP" "$ZIP"
    xcrun notarytool submit "$ZIP" --keychain-profile notarytool --wait
    xcrun stapler staple "$APP"
    rm -f "$ZIP"
    ditto -c -k --keepParent "$APP" "$ZIP"
    spctl --assess --type execute --verbose "$APP"
else
    ditto -c -k --keepParent "$APP" "$ZIP"
    echo "NOT notarized: other Macs will show a Gatekeeper warning. Run with --notarize for release."
fi

# Finished games always go to Downloads (Maddie, 14 Oct 2026).
cp -f "$ZIP" "$HOME/Downloads/"
rm -rf "$HOME/Downloads/Super Punch-Out.app"
cp -R "$APP" "$HOME/Downloads/"
echo "$HOME/Downloads/SuperPunchOut-Mac.zip"
echo "$HOME/Downloads/Super Punch-Out.app"
