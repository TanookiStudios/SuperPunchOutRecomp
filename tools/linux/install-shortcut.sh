#!/bin/sh
# Adds Super Punch-Out to the application menu for this user only.
here="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.local/share/applications" "$HOME/.local/share/icons/hicolor/256x256/apps"
cp "$here/superpunchout.png" "$HOME/.local/share/icons/hicolor/256x256/apps/superpunchout.png"
sed "s|^Exec=.*|Exec=\"$here/SuperPunchOut\"|" "$here/superpunchout.desktop" > "$HOME/.local/share/applications/superpunchout.desktop"
echo "Added Super Punch-Out to your application menu."
