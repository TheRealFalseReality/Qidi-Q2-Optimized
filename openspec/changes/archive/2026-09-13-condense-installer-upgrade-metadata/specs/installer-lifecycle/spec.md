## MODIFIED Requirements

### Requirement: Recoverable configuration lifecycle
Install, reinstall, restore, and uninstall SHALL execute as serialized, idle-printer transactions with validated inputs, recoverable preimages, atomic committed state, and drift-safe reversal.

#### Scenario: Mutation begins only after complete preflight
- **WHEN** a mutating operation starts
- **THEN** it validates printer state, prior state, targets, paths, bundle contents, and required storage before backup or writes
- **AND** printing, paused, unknown, malformed, concurrent, or recovery-blocked state fails closed

#### Scenario: Installation commits atomically
- **WHEN** installation changes validated targets
- **THEN** a configuration backup and recoverable preimages are created automatically before the first write without requesting installation confirmation
- **AND** the managed tree and guarded patches converge to the selected release
- **AND** installed state is committed only after postflight verifies the resulting files and ownership ledger
- **AND** failure restores preimages or records a recovery blocker when compensation cannot complete

#### Scenario: Uninstall respects ownership
- **WHEN** uninstall processes a valid ownership ledger
- **THEN** only unchanged installer-owned state is reverted
- **AND** user-modified state is preserved and reported
- **AND** installed state is removed only after successful postflight

#### Scenario: Restore reconstructs the archived runtime
- **WHEN** restore receives explicit confirmation for a validated installer archive
- **THEN** it validates printer idleness after confirmation and before replacing live runtime state, including for config-only archives
- **AND** printing, paused, unknown, or unavailable printer state prevents live replacement
- **AND** archived configuration and eligible external members are staged before replacing live runtime state
- **AND** partial failure restores the pre-restore state
- **AND** every restored root is verified before success and recovery remains blocked until incomplete compensation is resolved

#### Scenario: Non-mutating and interrupted runs remain safe
- **WHEN** dry-run, help, demo, alternate reporting, or interruption is selected
- **THEN** safety decisions remain equivalent to the normal flow
- **AND** no unapproved backup, pruning, or live mutation occurs
- **AND** interruption prevents later actions and exits without a traceback
- **AND** interruption after an uncommitted configuration write restores recoverable preimages or records a recovery blocker if compensation cannot complete
- **AND** interruption after configuration commit preserves the verified result and any outstanding activation or host-recovery obligation without reporting unfinished work as complete
- **AND** compensation does not restore a whole vendor saved-variable file over live Klipper state

#### Scenario: Preview and execution agree on file changes
- **WHEN** install or uninstall evaluates the same validated files, release, and operator policy
- **THEN** dry-run reports the same proposed file changes and preserved drift as execution
- **AND** execution rejects changed preimages before overwriting them rather than silently applying a stale decision
- **AND** live runtime interactions retain their own readiness, idleness, and authorization checks

### Requirement: Opt-in recoverable host optimization
The installer SHALL apply host OS optimizations only under explicit persisted policy, preserve recoverable preimages, and keep host-operation failures separate from a verified printer-configuration result. System optimizations SHALL remain available through the same packaged install, update, and uninstall flow without requiring a separate package or operator command.

#### Scenario: Enabled policy reconciles only recognized host state
- **WHEN** system optimizations are enabled
- **THEN** each declared operation validates its live preconditions before mutation
- **AND** installer-owned drift is reconciled without replacing first restore preimages
- **AND** unowned, unknown, or user-modified state is preserved and reported
- **AND** operation failure rolls back journaled host work without deleting a verified configuration install
- **AND** incomplete host compensation retains a recovery blocker and does not report the overall operation as complete

#### Scenario: Multi-plate 3MF metadata follows the selected plate
- **WHEN** enabled Moonraker optimization reads a `.gcode.3mf` archive
- **THEN** G-code, metadata, and thumbnail selection use its valid selected plate index
- **AND** missing or invalid plate metadata falls back to plate 1

#### Scenario: Uninstall follows the operator's host-state decision
- **WHEN** uninstall finds host restore preimages
- **THEN** accepted restoration reverts only unchanged installer-owned targets
- **AND** targets already at their retained preimages are left unchanged
- **AND** user-modified files, symlinks, assets, or service states are preserved and reported
- **AND** declined restoration or explicit keep policy leaves current host state unchanged

#### Scenario: Reconciliation retains bounded recovery state
- **WHEN** repeated checks find host optimizations already current
- **THEN** installer recovery-state size and restoration-backup count do not grow with the number of checks
- **AND** first restoration preimages and unresolved transaction or reboot evidence remain available
- **AND** previously installed host ledgers remain recoverable when their historical action records are compacted

#### Scenario: Host reboot is deferred until safe
- **WHEN** an applied operation requires a host reboot
- **THEN** the requirement is persisted without embedding executable commands
- **AND** reboot is scheduled only after successful transaction completion, explicit authorization, and a fresh idle-printer check
- **AND** later execution clears the requirement only after post-boot verification succeeds
- **AND** dry-run, active, or unknown printer state performs no reboot
