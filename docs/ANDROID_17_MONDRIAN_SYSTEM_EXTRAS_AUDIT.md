# P1 — system/extras Android 17 and independent mondrian bring-up audit

Date: 2026-11-04. **Historical source review only; old Android14 system/extras is NOT activated in AOSP17.**

## Provenance and scope

- Archived PixelExperience-Reborn `system_extras` branch `seventeen` revision `d3afeddfb4ca47278468b6b0d928f96eae1b2a0b`; merges Android14 r21 on 2024-01-30. This original branch is unchanged.
- Official Android17 r1 `platform/system/extras` Git tree `8b4f977da051354a762f01176fa0ab5e44a9d01e` from https://android.googlesource.com/platform/system/extras/+/refs/tags/android-17.0.0_r1/ .
- The staged PE-Reborn AOSP17 manifest already selects `platform/system/extras`. No full fork or product override is justified by the identified old deltas.
- Android17 contains bootctl, boot_control_copy, partition_tools, libfscrypt, ext4_utils, f2fs_utils, verity, checkpoint_gc, postinst, simpleperf, profcollectd, and newer Rust and module utilities. It has new `pinner`, `kcmdlinectrl`, `kcmdlinemodprobe`, `libatrace_rust` and `torq` that are absent from the archived Android14 root. These are platform tools/libraries; do not convert a repository-wide replacement into a device-only optional feature.

## Historical PE-specific deltas reviewed

| Historical commit | Actual change | Android17 decision |
| --- | --- | --- |
| `12e7c99e098068930f62e5421b045ba95373b1c2` | `partition_tools/Android.bp` adds **host-only** `lpunpack_static` with `static_executable: true`, static `liblp`, `libsparse`, `libcrypto`, `libext4_utils` and others; comment: useful for extract-utils | **OPTIONAL DEVELOPMENT TOOL ONLY**. Official AOSP17 already builds `lpunpack` (host), `lpmake`, `lpdump`, `lpdumpd`. No justification to replace platform `system/extras`. If genuinely needed, implement a narrow stand-alone Android17 host tool with audited Soong transitive static dependencies and a verified build. |
| `817e5f2c9667fed087edcd06d8a3d3cc1db96a43` | Old `verity/BootSignature.java` attempts to count an extra device-tree section when the legacy header's `headerVersion > 4` | **REJECT BLIND PORT**. This code reads the legacy boot header field as an alternate QCDT-size interpretation. It must not redefine Android17 boot/vbmeta signing or relax AVB checks. Verify header compatibility and signable lengths against real fixture images, *without private keys*. |
| `8d81f71f953b459cb7ad15f2f2a65fffb6b3fbc7` | Old `BootSignature.java` restricts v1/v2 recovery-DTBO parsing to header versions 1..4, because same offset can be used as legacy QCDT data | **REJECT BLIND PORT**; security-relevant boot-layout interpretation. Official Android17 source intentionally does not include these old branches. Avoid modifying `BootSignature` or AVB2/vbmeta unless the exact real boot image format, signing path and security tests require it. |

Sources: old commit patch/diffs in the historical repository; official upstream `partition_tools/Android.bp` https://android.googlesource.com/platform/system/extras/+/refs/tags/android-17.0.0_r1/partition_tools/Android.bp and `verity/BootSignature.java` https://android.googlesource.com/platform/system/extras/+/refs/tags/android-17.0.0_r1/verity/BootSignature.java .

## Android17 graph differences and recovery/security impact

1. Official `partition_tools/Android.bp` exposes `liblpdump`, host/target `lpdump`, host `lpmake`, `lpadd`, target `lpflash`, `lpdumpd`, host `lpunpack`. `lpdumpd` now links modern snapshot interfaces (`libsnapshot_cow_defaults`, `libsnapshot_hal_deps`, `libfs_mgr_binder`, `libprotobuf-cpp-lite`) for dynamic partition metadata access. The old tree lacks this exact graph. Do not import its entire `partition_tools/Android.bp`.
2. `libfscrypt`, `ext4_utils`, `f2fs_utils`, `checkpoint_gc` and `verity` are coupled to `system/core` `fs_mgr`, `system/vold`, recovery, FBE metadata encryption and updater/recovery. Any changes must be validated as a complete snapshot/FBE/dynamic partition chain, not a standalone extra command.
3. AOSP17 `verity/BootSignature.java` remains a legacy helper and is **not proof** that the rom's AVB2 boot/vbmeta flow uses it. Prior user-specific recovery preflight found mismatched main/recovery fstab; the independent PE-Reborn device tree must fix/validate that separately.
4. New PE-Reborn Android17 `device/xiaomi/mondrian` and `device/xiaomi/sm8450-common` must be authored as independent product trees. Existing LF52406 LineageOS-derived hardware trees may inform actual physical partition layout and device drivers, but must not be automatically imported as a product base.

## Acceptance and release gates

- [x] Historical Android14 exact branch/commits classified; old static unpack helper and legacy BootSignature changes identified.
- [x] Official Android17 exact tree and modern partition/verity/crypto source ownership confirmed.
- [x] Historical sparse-checkout source inventory CI [PASS #41791807600](https://github.com/PixelExperience-Reborn/system_extras/actions/runs/41791807600).
- [x] Official AOSP17 r1 tagged Gitiles source tree, partitions/verity/FBE build input integrity [PASS #41791807782](https://github.com/PixelExperience-Reborn/system_extras/actions/runs/41791807782). Source-only checks, not an Android17 Soong build.
- [ ] Verify official Android17 full `system/extras` repo sync/Soong build with `system/core`, `vold`, `update_engine`, `libsnapshot` and `bootctl`.
- [ ] Test host `lpunpack` and dynamic partition metadata on known synthetic, non-sensitive fixtures; test optional `lpunpack_static` separately if required by extraction workflow.
- [ ] Verify actual `boot.img`, `vendor_boot.img`, `dtbo.img` layout, AVB/vbmeta chaining, rollback index, partitions and recovery/bootloader constraints on independent mondrian PE-Reborn trees.
- [ ] Test FBE unlocking, F2FS/ext4 filesystem check, snapshot-based OTA, recovery mounting, slot management and VTS/CTS on real mondrian.

**Decision: keep `platform/system/extras` in the staged Android17 manifest. No old boot signing patch or broad Android14 port, no unsafe AVB exemptions.**
