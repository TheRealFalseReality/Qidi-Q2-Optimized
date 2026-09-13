## Why

Optimized print-start cleanup uses the firmware `CLEAR_NOZZLE` macro's 200 mm/s finishing strokes rather than the different mixed-speed wipes embedded in stock QIDI Studio start G-code. Fresh Box and external-spool starts also lack a chute wipe after the rear-bed scrape.

## What Changes

- Preserve the repeated pre-scrape wipes at the existing print-start cooldown stages, including their temperature thresholds and conditional execution. Do not collapse the staged cleanup into a single pre-scrape wipe.
- Use the stock slicer mixed-speed pattern for those pre-scrape wipes: two broad cycles at commanded 133.3/83.3 mm/s, followed by three finishing cycles at 100 mm/s. Stock matching applies to each wipe's motion, not the overall number or timing of cleanup stages.
- Preserve the rectangular rear-bed scrape followed by three small circles, its temperature safety gate, and the cable-chain orientation traverse.
- Return safely to the chute after scraping and perform four back-and-forth finishing cycles at commanded 200 mm/s, followed by waste-release positioning, before leveling.
- Preserve waste-release positioning separately from wiping; do not redefine vendor `CLEAR_OOZE`, `CLEAR_FLUSH`, or `CLEAR_NOZZLE`.
- Keep existing purge quantities, retained-filament reuse, manual load/unload, end cleanup, and slicer filament changes outside this change.
- Keep both slicer packs functionally aligned through printer-side implementation and update the start-path contract and release notes during implementation.

The selected sequence deliberately combines optimized staged cooldown, stock-slicer mixed-speed pre-scrape wipes, and the stock firmware macro's fast post-scrape finish. It is not an exact copy of the stock slicer startup, and faster finishing is not claimed to provide better cleaning without physical validation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `optimized-printer-behavior`: Preserve staged print-start cooldown wiping with stock-slicer wipe motion, followed by rear-bed scraping and a post-scrape wipe, without changing unrelated cleanup callers.

## Impact

- `installer/klipper/tltg-optimized-macros/filament.cfg` and existing macro integration coverage.
- `openspec/contracts/gcode-paths/start-print.path.json` and generated views.
- Installer package version, aligned macro version, and changelog at implementation time; source-upgrade metadata changes only if new guarded provenance is introduced.
- No firmware snapshot changes, vendor binary changes, printer deployment, or new dependencies.
