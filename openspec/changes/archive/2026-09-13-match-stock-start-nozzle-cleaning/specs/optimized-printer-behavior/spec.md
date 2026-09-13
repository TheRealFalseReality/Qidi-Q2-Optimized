## MODIFIED Requirements

### Requirement: Safe print transitions and helpers
Optimized cut, purge, cooldown, cleaning, calibration, and cancellation helpers SHALL preserve caller state, guard optional hardware, and avoid delayed or error-path actions that can affect a subsequent print. Print-start cleaning SHALL preserve staged cooldown wiping with mixed-speed pre-scrape motion and use fast finishing after the cooled rear-bed scrape, with detailed motion and branch ordering controlled by `openspec/contracts/gcode-paths/start-print.path.json`.

#### Scenario: Cut and cleanup preserve caller state
- **WHEN** optimized cut, purge, chute, chamber, or Box-heater helpers run
- **THEN** motion modes, extrusion modes, and temporary acceleration are restored
- **AND** optional Box objects are called only when available and valid
- **AND** fixed waits are reduced without replacing required motion completion waits

#### Scenario: Pre-scrape wiping retains the cooldown stages
- **WHEN** a fresh Box or external-spool start reaches an existing guarded pre-scrape chute wipe
- **THEN** each wipe uses two broad alternating-speed cycles followed by three finishing cycles at commanded 100 mm/s
- **AND** existing repeated cooldown wipe stages, temperature thresholds, conditional execution, purge quantities, and waste-release positioning are preserved rather than collapsed into one wipe
- **AND** the existing cooled rectangular rear-bed scrape is followed by three small circles with its cable-chain orientation and temperature safety gate intact

#### Scenario: Cooled scraping finishes with fast chute wiping
- **WHEN** a fresh Box or external-spool start completes its rear-bed scrape and guarded chute cleanup is available
- **THEN** the nozzle lifts clear and returns safely to the chute before performing four back-and-forth finishing cycles at commanded 200 mm/s
- **AND** waste-release positioning completes before leveling
- **AND** unavailable vendor cleanup objects are not called

#### Scenario: Optimized cleanup uses fast non-extruding silicone wipes
- **WHEN** retained-filament startup, non-start purge cleanup, unload cleanup, or staged end cleanup reaches an existing silicone-wiper pass
- **THEN** it retains four back-and-forth finishing cycles at commanded 200 mm/s and its existing exit motion
- **AND** no mixed-speed pre-scrape pattern is substituted into these unrelated cleanup paths

#### Scenario: Wipe motion preserves state and unrelated cleanup
- **WHEN** either optimized wipe pattern executes with the nozzle already positioned at the rear wiper
- **THEN** it preserves caller motion and extrusion modes, feed settings, and acceleration
- **AND** the wipe itself performs no extrusion, Y/Z repositioning, heater changes, fixed dwell, or bed scraping
- **AND** retained-filament startup, non-start purge cleanup, manual loading, unload cleanup, staged end cleanup, vendor cleanup commands, and slicer filament-change sequences retain their existing behavior
- **AND** retained-filament startup does not gain a rear-bed scrape or post-scrape sequence

#### Scenario: End-print performs staged cooldown safely
- **WHEN** normal slicer end G-code runs
- **THEN** the toolhead reaches the chute, filament preparation and heater shutdown occur, and staged cooling and wiping complete before print end
- **AND** bed lowering follows the shared slicer rule
- **AND** delayed fan shutdown cannot turn off a fan used by a new or paused print
- **AND** OrcaSlicer may apply configured completion exhaust while QIDI Studio passes zero and omits unsupported indexed completion-air placeholders

#### Scenario: Error cancellation is motion-free
- **WHEN** optimized error cancellation executes
- **THEN** heaters, fans, optional Box heat, pause state, and print state are cleaned up before base cancellation
- **AND** no parking, wiping, or other toolhead motion occurs

#### Scenario: Operator helpers remain guarded and available
- **WHEN** optimized macros load
- **THEN** supported bed-screw, probe-accuracy, Box-temperature, mapping-reset, and startup reporting helpers are available
- **AND** each helper validates required printer state and hardware bounds before acting
