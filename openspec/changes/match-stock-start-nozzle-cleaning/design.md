## Context

Both repository slicer packs enter optimized filament preparation rather than firmware `PRINT_START` or `CLEAR_NOZZLE`. In `installer/klipper/tltg-optimized-macros/filament.cfg`, fresh Box starts perform purge cleanup and repeated wipes through conditional cooldown stages before `_OPTIMIZED_REAR_BED_SCRAPE`. External-spool starts use `OPTIMIZED_WIPE_AND_SCRAPE_NOZZLE`. Neither scrape path includes a post-scrape chute wipe.

The shared `_OPTIMIZED_WIPE_NOZZLE` also serves retained-filament, unload, and end cleanup. Replacing its behavior globally would change unrelated operations. See proposal.md for scope.

Stock references are Qidi-Max4-Defaults firmware baseline `0b25fd3` (01.01.06.05): `qidistudio_gcode/start.gcode`, `config/klipper-macros-qd/qd_macro.cfg`, and the recovered `box_extras.so` cleanup scripts. The slicer repeats mixed-speed wiping after scraping; firmware `CLEAR_NOZZLE` instead finishes with four fast cycles. These are different command paths, not interchangeable names for one routine.

## Goals / Non-Goals

**Goals:** Preserve the optimized cooldown schedule while selecting different wipe motion before and after scraping. Keep the existing scrape geometry, temperature safety gate, cable-chain orientation, and hardware guards.

**Non-Goals:** Copy the entire stock startup, alter purge quantities or retained-filament reuse, change manual loading/unloading or end cleanup, redefine vendor commands, or deploy to a printer as part of planning.

## Decisions

### Preserve the cooldown schedule and use mixed-speed pre-scrape motion

Use a separate state-preserving mixed-speed helper for pre-scrape cleanup rather than changing the shared fast helper. Each invocation commands `M204 S10000`, two `X163 F8000` / `X145 F5000` cycles, then three `X175 F6000` / `X163 F6000` cycles. Explicit feed rates avoid dependence on inherited modal feed settings. The helper has no extrusion, temperature changes, dwell, or Y/Z positioning.

Fresh Box startup retains its purge cleanup and all existing pre-scrape wipe sites: the initial cooling stage, the conditional purge-temperature-minus-30 stage, and the scrape-temperature gate. Preserve the conditions and temperature thresholds, including configurations that omit the intermediate stage. Use mixed-speed motion for the existing print-start purge cleanup as well. If that cleanup entrypoint has non-start callers, select the start-specific behavior without changing those callers' defaults.

External-spool cleanup retains its existing heat/wait behavior and optional-hardware guard; do not add Box extrusion or additional cooldown stages. Retained-filament starts retain their existing fast wipe and do not gain a scrape.

### Finish the cooled scrape with four fast cycles

Preserve the existing rectangular scrape followed by three small circles, not the firmware macro's additional pre-rectangle circles. After the existing Z lift and safe rear-bed exit, position at the chute through the guarded optimized travel helper before invoking the existing fast wipe: four `X176 F12000` / `X163 F12000` cycles and exit to `X180 F12000`.

Complete waste-release positioning before bed/chamber waits and leveling. Apply the post-scrape sequence to fresh Box and external-spool branches only where the existing hardware availability boundary permits chute cleanup. Do not issue compiled vendor cleanup commands when their owning object is absent.

The operator selected this hybrid instead of a second mixed-speed wipe. Stock firmware provides precedent for fast finishing after a cooled scrape, but it does not establish superior physical cleaning. Feed rates are commanded values; short strokes may not attain their nominal speed.

### Keep wiping and waste release separate

Retain `CLEAR_FLUSH` after the existing pre-scrape wipes and add it after the post-scrape finish where available. Its recovered script moves to X180 and calls `MOVE_TO_TRASH`; it is not another repeated wipe or an extrusion command. Preserve that travel rather than replacing it with an X-only shortcut.

The operator reports a mechanically operated waste-retaining gate. Static motion evidence supports preserving the release travel but does not establish the exact gate actuation direction or successful waste discharge. Leave `CLEAR_OOZE`, `CLEAR_FLUSH`, and `CLEAR_NOZZLE` vendor-owned.

### Contract branch order, not just helper speeds

Update the start-path contract to distinguish mixed-speed pre-scrape and fast post-scrape motion, retain every conditional cooldown wipe site, require all three scrape circles, and require safe chute positioning and waste release after scraping. Preserve retained-filament exclusions and unavailable-hardware behavior. Keep exhaustive command sequences in the contract, with focused existing integration coverage for rendered branches and caller-state preservation.

## Risks / Trade-offs

- [A shared helper change affects unload or end cleanup] → Leave the fast helper's existing behavior intact and select mixed-speed motion only at approved start cleanup sites.
- [Post-scrape X strokes execute while still over the bed] → Require Z clearance and safe chute positioning before the first finishing stroke.
- [Stock-copy simplification removes useful cooldown wipes] → Contract every existing stage, predicate, and threshold; change motion within each invocation rather than collapsing stages.
- [Absent Box objects make vendor cleanup unavailable] → Retain existing guards and test external spool with the object present but disabled and with it absent.
- [Fast strokes or altered residue release perform poorly physically] → Obtain separately authorized idle-printer validation and observe both nozzle residue and waste discharge; software checks cannot prove cleaning effectiveness.

## Migration Plan

Implement only in the optimized payload and preserve existing slicer entrypoints, so previously sliced files using those entrypoints receive the behavior. Include the behavior in package release `26.09.09.1`, align version metadata with the version script, and consolidate its release notes under that version. Change upgrade-source metadata only if new guarded source provenance is introduced. Validate the package and generated contract views before any separately authorized deployment. If physical validation rejects the finish, revise the change or restore a known prior managed payload through the supported installer workflow; do not modify stock macros to compensate.
