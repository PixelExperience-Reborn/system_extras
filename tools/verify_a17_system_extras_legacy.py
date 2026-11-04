#!/usr/bin/env python3
"""Host-only archived Android14 system/extras source inventory."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise AssertionError(message)
    print("PASS historical extras:", message)


def main():
    pt = (ROOT / "partition_tools/Android.bp").read_text(encoding="utf-8")
    bs = (ROOT / "verity/BootSignature.java").read_text(encoding="utf-8")
    fscrypt = (ROOT / "libfscrypt/Android.bp").read_text(encoding="utf-8")
    f2fs = (ROOT / "f2fs_utils/Android.bp").read_text(encoding="utf-8")
    require('name: "lpunpack"' in pt and 'name: "lpunpack_static"' in pt,
            "historical lpunpack + optional statically linked host tool")
    block = pt.split('name: "lpunpack_static"', 1)[1]
    require('static_executable: true' in block and '"liblp"' in block
            and '"libsparse"' in block, "legacy static extraction Soong dependency graph")
    require('if (headerVersion > 0 && headerVersion <= 4)' in bs
            and 'if (headerVersion > 4)' in bs,
            "legacy QCDT/boot image size interpretation — NOT approved port")
    require('BOOT_IMAGE_HEADER_V1_RECOVERY_DTBO_SIZE_OFFSET' in bs
            and 'BOOT_IMAGE_HEADER_V2_DTB_SIZE_OFFSET' in bs,
            "legacy boot header recovery DTBO parsing source")
    require('name: "libfscrypt"' in fscrypt,
            "archived fscrypt module is not equivalent to tested AOSP17 FBE")
    require('name: "mkf2fsuserimg"' in f2fs,
            "archived F2FS host image tool")
    require((ROOT / "bootctl/Android.bp").exists()
            and (ROOT / "postinst/Android.bp").exists(),
            "historical bootctl and postinstall build files")
    require((ROOT / "Android.mk").is_file(), "archived root Android.mk retained")
    require(not (ROOT / "pinner").exists() and not (ROOT / "libatrace_rust").exists(),
            "newer AOSP17 extras root modules absent from archived source")
    print("PASS source inventory only. No boot signing, AVB, FBE, Soong or mondrian device test.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        sys.exit(1)
