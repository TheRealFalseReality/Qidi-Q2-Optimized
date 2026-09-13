## Why

The installer repeats ownership and source-provenance metadata for historical package versions even though every supported version upgrades directly to the current release. Its planning, reporting, argument parsing, and host-state bookkeeping also duplicate work. Consolidating these paths reduces maintenance while correcting inconsistent restore, interruption, and drift protection.

System optimizations remain part of the same packaged install, update, and uninstall experience. Cleanup must preserve their persisted policy, recovery, and reboot behavior rather than move them into a separate product or require another operator command.

## What Changes

- Retain explicit historical package-version admission and replace per-version ownership profiles with one cumulative compatibility envelope.
- Keep the current manifest authoritative for convergence; simplify version bumps and historical backup-format classification without weakening package identity or source-provenance validation.
- Use one validated file-change plan for preview and execution, grouping edits by destination and rejecting stale preimages before mutation.
- Consolidate configuration transaction safeguards across install, uninstall, and restore, including idle-printer admission and rollback on interruption.
- Keep system optimizations integrated, with host compensation and results separate from an already verified configuration result; preserve user-modified host state during restoration.
- Bound persisted host recovery state and avoid new preimage backups for already-current operations while retaining first restoration preimages and pending recovery evidence.
- Share reporting content between plain and Rich renderers and move command-line parsing into Python while preserving existing entrypoints, flags, prompts, and output modes.
- Move simulated host-service and mount behavior into test fixtures so tests exercise production decision logic without real network, service, or printer access.
- Preserve historical release bundles and changelog history; extend existing lifecycle and bundle coverage rather than add a generic installer framework.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `installer-lifecycle`: clarify restore admission, interrupted-transaction compensation, preview consistency, integrated host optimization, drift-safe host restoration, and bounded reconciliation state.

## Impact

Affected areas include compatibility metadata and models, configuration planning and transactions, host optimization state and restoration, reporting, release launchers, version tooling, existing lifecycle tests, bundle smoke coverage, and release-maintenance guidance. `installer/runtime/` remains the packaged runtime; system optimizations are not split into a separate package or workflow.

Implementation must preserve live Moonraker saved-variable handling and pending activation verification from concurrent installer work. The package version and matching changelog section advance with implementation, including the safety fixes as well as metadata condensation. No vendor configuration, optimized values, or source payload changes are intended.
