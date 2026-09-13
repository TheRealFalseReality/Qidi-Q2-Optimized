## 1. Print-start motion and contracts

- [x] 1.1 Update the start-print path contract for mixed-speed pre-scrape motion, every existing cooldown wipe stage and condition, three post-rectangle circles, and safely positioned four-cycle 200 mm/s post-scrape finishing with waste release; verify the contract describes fresh Box, external spool, retained reuse, and hardware-unavailable boundaries without weakening existing invariants.
- [x] 1.2 Implement state-preserving mixed-speed pre-scrape wiping in the optimized payload and select it at the existing approved print-start cleanup sites; verify rendered branch coverage preserves purge quantities, cooldown thresholds, stage counts, guards, and non-start callers.
- [x] 1.3 Add safe chute return, the existing fast finishing pattern, and waste-release positioning after the cooled scrape; verify ordering before leveling for fresh Box and external-spool starts and no added scrape/finish on retained reuse.
- [x] 1.4 Extend existing macro integration coverage rather than adding an overlapping test module; verify helper state preservation, intermediate cooldown stage present/absent, Box object present-but-disabled/absent, and unchanged manual, unload, end, and vendor behavior with `python3 scripts/run_installer_core_tests.py`.

## 2. Release and validation

- [x] 2.1 Include nozzle cleaning in release `26.09.09.1`, align package metadata using `python3 scripts/bump_installer_version.py 26.09.09.1`, and consolidate operator-visible changelog entries under that release; verify version alignment and release history with `python3 scripts/check_installer_known_versions.py`, updating supported upgrade sources only if new guarded provenance requires it.
- [x] 2.2 Format macros with `python3 scripts/format_klipper_configs.py`, regenerate path views using `python3 scripts/check_gcode_paths.py --write`, and verify `python3 scripts/check_gcode_paths.py`, `python3 scripts/check_optimized_slicer_macros.py`, and `openspec validate --all --strict` pass; include generated Markdown and Mermaid outputs.
- [x] 2.3 Validate release packaging with `python3 scripts/build_installer_bundle.py --output-dir dist --channel dev --build-id local --smoke-test`; verify the bundle contains the intended macro payload and no unintended stock-mapped edits.
- [ ] 2.4 Obtain separate authorization for idle-printer validation and record observed repeated cooldown wipes, rectangular scrape plus three circles, safe chute return, four fast finishing cycles, and waste discharge; do not claim cleaning effectiveness from software checks alone.
