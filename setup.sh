#!/usr/bin/env bash
# Fetch snesrecomp and recomp-ui into vendor/ at the versions this port was
# tested with, then apply our local changes to them (patches/).
# vendor/ is not committed: anything changed there must live in patches/.
set -euo pipefail
cd "$(dirname "$0")"
SNESRECOMP_COMMIT=a6be9756285f26ccc74539c811d4d23d57d8c33d
RECOMP_UI_COMMIT=af7a6d95ead6ad785fbfbc2889b8648f589d4eeb
fetch() {  # fetch <url> <dir> <commit>
    if [ ! -d "vendor/$2/.git" ]; then
        git clone -q "$1" "vendor/$2"
        git -C "vendor/$2" checkout -q "$3"
        git -C "vendor/$2" submodule update -q --init --recursive
    fi
}
fetch https://github.com/mstan/snesrecomp.git snesrecomp "$SNESRECOMP_COMMIT"
fetch https://github.com/mstan/recomp-ui.git recomp-ui "$RECOMP_UI_COMMIT"
apply() {  # apply <dir> <patch>
    if git -C "vendor/$1" apply --check "../../$2" 2>/dev/null; then
        git -C "vendor/$1" apply "../../$2" && echo "applied $(basename "$2")"
    else
        echo "$(basename "$2") already applied (or does not fit: check vendor/$1)"
    fi
}
for p in patches/recomp-ui-*.patch; do [ -f "$p" ] && apply recomp-ui "$p"; done
for p in patches/0*.patch; do [ -f "$p" ] && apply snesrecomp "$p"; done
[ -f rom/superpunchout.sfc ] || echo "Put your Super Punch-Out!! (USA) .sfc file at rom/superpunchout.sfc"
true
