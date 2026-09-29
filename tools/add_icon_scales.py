#!/usr/bin/env python3
"""Add the icon scales that cyan does not generate.

cyan -k writes <uid>60x60@2x.png (120px) and <uid>76x76@2x~ipad.png (152px) and points
Info.plist at them. Modern iPhones ask for 60x60@3x (180px), so append that file, plus the
iPad Pro 83.5x83.5@2x (167px) variant, straight into the IPA. Appending keeps every
existing entry byte-for-byte, so nothing cyan did is disturbed.

Usage: add_icon_scales.py <ipa> <icon-180.png> <icon-167.png>
"""
import plistlib
import sys
import zipfile


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    ipa, icon_180, icon_167 = sys.argv[1:]

    with zipfile.ZipFile(ipa) as archive:
        plist_path = next(
            (n for n in archive.namelist() if n.count("/") == 2 and n.endswith(".app/Info.plist")),
            None,
        )
        if plist_path is None:
            print("no app Info.plist inside the IPA")
            return 1
        app_dir = plist_path.rsplit("/", 1)[0]
        info = plistlib.loads(archive.read(plist_path))

    uid = (info.get("CFBundleIcons", {}).get("CFBundlePrimaryIcon", {}) or {}).get("CFBundleIconName")
    if not uid:
        print("Info.plist has no CFBundleIconName, so cyan was not asked to change the icon")
        return 1

    additions = [
        (f"{uid}60x60@3x.png", icon_180),
        (f"{uid}83.5x83.5@2x~ipad.png", icon_167),
    ]
    with zipfile.ZipFile(ipa, "a", zipfile.ZIP_DEFLATED) as archive:
        for name, source in additions:
            archive.write(source, f"{app_dir}/{name}")
            print(f"added {app_dir}/{name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
