## Context

`installer/package.yaml` declares the current package version and explicit `package.known_versions`. `installer/supported_upgrade_sources.yaml` repeats uninstall target and source-patch provenance profiles for those versions. The migration must derive its cumulative envelope from every admitted profile at implementation time, including releases added since this change was proposed.

Direct install validates a prior state's package version against `package.known_versions`. Upgrade and uninstall use the per-version compatibility entry to admit patch-ledger target tuples and source-ledger firmware/hash provenance. Every admitted release converges directly to the current manifest; no sequential migration chain executes.

`installer/runtime/backup.py` separately enumerates releases whose archives may omit the external-source manifest. Historical release bundles remain available from GitHub and do not need to be reconstructed by the current installer.

Configuration preview and execution classify targets separately. Plain and Rich reporters duplicate presentation logic, and release shell launchers parse options also defined by Python. Host optimization combines production operations with fake-root simulation and appends already-current results to persisted action history.

The restore path reaches live replacement without an idle-printer gate. Configuration rollback handlers catch `Exception` but not `KeyboardInterrupt`, while several host restorations replace preimages without comparing installer-owned live state. These safety findings shape the transaction cleanup; they are not reasons to remove packaged system optimizations. Concurrent saved-variable work uses live Moonraker operations and must remain outside whole-file configuration compensation.

## Goals / Non-Goals

**Goals:**

- Keep exact admission of explicitly released package versions.
- Represent historical ownership validation with one cumulative compatibility envelope.
- Make an ordinary version bump add a version identifier without copying a compatibility profile.
- Preserve fail-closed validation of package identity, ledger targets, source destinations, firmware, hashes, and backup format.
- Preserve direct upgrade, reinstall, uninstall, rollback, and restore paths for every currently admitted version.
- Keep system optimizations in the same package and operator flow with explicit configuration and host commit boundaries.
- Share file-change planning, transaction safeguards, reporting content, and argument parsing without a generic operation framework.
- Keep recovery state bounded and test simulation separate from production decision logic.

**Non-Goals:**

- Remove historical version identifiers or changelog entries.
- Permit arbitrary version ranges or unknown package versions.
- Support installing an older release through the current installer.
- Rewrite Git history or materially reduce clone size.
- Change installer-owned targets, desired configuration, source payloads, or existing enrollment and optimization defaults.
- Split system optimizations into a separate package or operator command.
- Remove plain/Rich output, demo mode, existing flags, prompts, or authorization requirements.
- Introduce a plugin engine, replace Python with shell, or change serialization formats merely to reduce dependency counts.

## Decisions

### 1. Keep explicit package-version admission

Retain `package.known_versions` as the complete set of package versions accepted in installed state, including the current version. Direct install and uninstall additionally require `state.package_id == manifest.package.id`.

An explicit list is preferred over a minimum version or version range. Date-like comparison would admit unpublished, malformed-but-sortable, or otherwise unreviewed package identities. Historical release identifiers cost one short line per release and provide a clear support boundary.

### 2. Replace version profiles with one cumulative envelope

Change `installer/supported_upgrade_sources.yaml` from a `versions` mapping to one compatibility envelope containing:

- `allowed_patch_targets`: the union of target tuples that may appear in a valid historical patch ledger;
- `source_patches`: the union of approved source-patch identities, destinations, firmware baselines, original hashes, and desired hashes.

The schema version advances because the document shape and parser contract change. Compatibility models represent the envelope directly rather than materializing an `UpgradeSource` for each package version.

The initial envelope is generated from the union of every currently supported profile before the old mapping is removed. Union generation avoids relying on the latest profile containing all historical entries.

A cumulative envelope is preferred over inheritance chains or deduplicated profile aliases. Aliases would reduce file size but preserve release-to-profile maintenance and parser complexity. The envelope records the actual trust boundary: a known package version plus recognized installer-owned ledger content.

This intentionally stops asserting that a particular target or source record first appeared in one exact historical release. Safety remains content-based: unknown versions, targets, destinations, firmware/hash provenance, malformed state, and live drift fail closed. Exact historical manifests remain in their release artifacts and Git history.

### 3. Validate current manifest coverage without requiring equality

Compatibility validation requires:

- `manifest.package.version` to occur exactly once in `package.known_versions`;
- every current manifest patch target to be present in the cumulative target envelope;
- every current manifest source variant to be present in the cumulative source envelope;
- no duplicate or malformed envelope entries.

Envelope entries not present in the current manifest are valid because uninstalling an older installed state may require recognizing ownership that the current release no longer creates.

Runtime validation requires:

```text
state.package_id       == manifest.package.id
state.package_version  in manifest.package.known_versions
state.patch_ledger     subset of allowed_patch_targets
state.source_patches   subset of approved source_patches
state.runtime_firmware == detected firmware where firmware is required
```

Install classification still uses the current manifest and prior ledger to converge live files. Uninstall still restores only ledger entries whose live values remain installer-owned.

### 4. Make version bumps append identifiers only

`scripts/bump_installer_version.py` updates:

- `package.version`;
- `package.known_versions`, adding the new version once;
- optimized `variable_package_version`.

It does not modify the compatibility envelope for an ordinary macro or installer release. A change that introduces a new patch target or source provenance must update the envelope explicitly in the same release. Final compatibility validation detects omission because the current manifest must be covered by the envelope.

This keeps one command as the version authority while preventing automatic duplication of historical metadata.

### 5. Express backup compatibility with an admitted-version boundary

Replace `LEGACY_CONFIG_ONLY_PACKAGE_VERSIONS` with a named external-manifest introduction version, currently `26.07.26.1`, evaluated only after confirming that the parsed package version occurs in `package.known_versions` or equivalent validated compatibility input.

An archive requires an external manifest when any of these conditions is true:

- installed state declares source patches;
- the package version is absent or not explicitly admitted;
- the package version is at or after the external-manifest introduction boundary.

Numeric four-component versions are parsed into integer tuples for boundary comparison; string comparison is not used. This preserves rejection of unknown old-looking versions while removing a second historical version enumeration.

If passing manifest compatibility into archive validation creates undesirable coupling, the compact alternative is to retain one explicit set of config-only versions. The preferred implementation centralizes admitted versions so package compatibility and backup compatibility cannot diverge.

### 6. Preserve historical-release installation through release artifacts

The current bundle installs only its own `package.version`. `package.known_versions` means “accepted installed-state sources,” not “versions this bundle can install.” Selecting an old GitHub release remains the supported path for installing that old release.

`CHANGELOG.md` remains unchanged except for the normal entry required by the package version shipped with the implementation.

### 7. Keep integrated host optimization with explicit commit boundaries

Normal install, automatic update, and uninstall retain their existing system-optimization policy and prompts. Separate packages or manual follow-up commands are rejected because system optimizations are part of the packaged behavior.

Configuration postflight and state commit define the configuration transaction boundary. Host work retains its own recoverable preimages and compensation boundary; an ordinary host failure must not trigger rollback of a verified configuration result. Incomplete host compensation persists a recovery blocker and stops later activation, release advancement, or reboot work. Uninstall retains the information needed to recover unfinished host restoration before deleting ownership state.

Do not merge source activation, host reboot, and configuration recovery markers simply because they are all state files. They describe different outstanding obligations. Preserve idle checks, persisted enrollment, checksum advancement after activation, and reboot authorization.

### 8. Use one file-change plan and a small transaction boundary

Build proposed file contents once per destination, including all guarded option, section, and include edits for that file. Preview renders these changes; execution verifies their preimages still match and applies the same proposed contents. Postflight remains an independent verification of results. Managed-tree and source-patch changes retain their existing ownership and provenance checks.

Complete admission and planning before backup or mutation. A small shared transaction helper handles preimage tracking, compensation, and recovery-blocker creation for configuration install, uninstall, and restore. It handles interruption before the outer CLI emits the interruption result. Compensation failures, including interrupted compensation, leave durable recovery evidence. After configuration commit, interruption preserves that result and pending activation or host recovery rather than reverting already committed work.

Restore validates idleness after confirmation and before replacement for both config-only and external-source archives. Restore remains available to repair an existing recovery blocker and does not clear that blocker until recorded recovery verification succeeds.

Do not put Moonraker saved-variable writes into a file plan or restore `saved_variables.cfg` from a stale whole-file preimage. Preserve live value verification and pending saved-variable activation expectations. Host operations retain their distinct policy and transaction behavior from decision 7; the file plan is not a general-purpose command executor.

### 9. Make host restoration ownership-aware and bookkeeping bounded

For each host operation, retain its first restoration preimage and the last verified installer-applied state needed to distinguish owned content from user changes. Restoration is a no-op when live state already matches the preimage, reverts when it matches the installer-applied state, and otherwise preserves and reports drift. Apply this to files, symlinks, assets, services, and the guarded root-mount operation. Immediate rollback of the current transaction remains distinct from ownership-aware uninstall restoration.

Persist policy, first preimages, current per-operation outcomes, and unresolved transaction evidence instead of an ever-growing action list. Historical diagnostics belong in logs. Determine whether a write is needed before creating a new backup; already-current metadata patches must not create additional preimages.

Read existing host ledgers and compact them only after validating and retaining restoration records and pending transaction identifiers. Rockchip journal recovery currently matches identifiers against action history; replace that dependency with explicit committed-transaction evidence before removing history. If an old ledger cannot establish the installer-applied state safely, preserve and report the affected live target rather than guess. Never prune a backup referenced by retained state or unresolved recovery.

### 10. Share reporting and parse command-line options once

Preserve plain and Rich output modes, prompts, demo behavior, and debug diagnostics. Build shared semantic messages and summaries once, then render them through thin plain or Rich adapters. Derive progress from actual plan or phase results rather than maintain a second operation model for the UI. Reporter selection must not affect mutation, confirmation, or error classification. Removing the live UI or its vendored dependency is outside this cleanup.

Shell launchers locate the bundle and invoke isolated Python; Python owns option parsing, compatibility aliases, help, version output, and invalid-combination handling. Preserve existing `install.sh`, `restore.sh`, and `auto-update.sh` command forms and safe bootstrap behavior. Help, version, and demo modes must not access the printer or create backups.

### 11. Exercise production decisions through bounded test I/O

Retain temporary filesystem roots. Move fake service and mount-state behavior into test fixtures behind the minimum command/I/O boundary needed by production operations. Avoid a broad host abstraction hierarchy. Tests must execute production classification, authorization, restoration, and recovery logic with deterministic I/O; they must not require real network requests, sudo, service changes, or reboot.

Extend existing lifecycle matrices and bundle smoke coverage for stale file plans, busy restore, interrupted mutation, failed compensation, host drift, old-ledger migration, and repeated already-current reconciliation. Model Klipper process identity as changing on restart, not on an assumed number of queries, so additional live saved-variable checks cannot consume a scripted PID sequence and trigger real restart timeouts. Diagnose the observed core-suite timeout and preserve the repository's under-five-second core-test budget without shortening production activation waits.

## Risks / Trade-offs

- **[The cumulative envelope accepts a historically impossible version/ledger combination]** → Require an explicitly admitted package version and validate every ledger element against the same ownership and provenance constraints used today. Do not treat the state version as proof of ownership. Package identity validation narrows admission further.
- **[A historical-only ownership target is accidentally dropped]** → Build the initial envelope as the set union of all existing resolved profiles and add a migration test comparing old-profile unions to the new envelope.
- **[A new manifest target is omitted from the envelope]** → Make current-manifest coverage a mandatory compatibility and bundle-build check.
- **[Unknown pre-source release labels bypass external archive metadata]** → Apply the format boundary only to explicitly admitted versions; unknown versions continue requiring the external manifest.
- **[Version ordering becomes ambiguous]** → Restrict boundary parsing to the existing four-component numeric package format and fail closed for nonconforming values.
- **[Line-count reduction becomes the goal]** → Measure removal of duplicate decisions and bounded runtime state. Retain Rich and lifecycle safeguards where existing functionality requires them; do not promise a particular bundle-size reduction.
- **[Host state compaction discards recovery proof]** → Validate migration against existing ledgers and pending journals before removing historical records; retain first preimages and explicit committed-transaction evidence.
- **[A shared transaction helper rolls back live vendor state or a completed phase]** → Keep Moonraker saved-variable operations and committed host/configuration phases outside inappropriate whole-file compensation.
- **[Preview decisions become stale]** → Revalidate file preimages immediately before applying them and fail closed rather than silently recomputing ownership decisions.
- **[Concurrent saved-variable work changes lifecycle assumptions]** → Re-read its resulting code and specs before implementation and preserve live persistence, activation markers, and non-owning rollback semantics.

## Migration Plan

1. Resolve every current version profile and calculate the union of patch targets and source provenance.
2. Add parser and model support for the cumulative compatibility schema, installed package-ID admission, and current-manifest subset validation.
3. Replace the compatibility YAML with the union envelope and verify it equals the union captured from the old schema.
4. Update install, uninstall, source-state, backup-format, version-bump, and compatibility-check call paths.
5. Update lifecycle and bundle tests to cover the oldest admitted config-only release, a pre-source release, the source-patch introduction release, the current release, an unknown version, a wrong package ID, historical-only ledger content, and current manifest coverage failure.
6. Remove superseded per-version profile and legacy backup-version parsing code.
7. Consolidate configuration planning and transaction safeguards, including restore admission and interruption compensation, before changing reporting or launchers.
8. Make host restoration drift-aware and introduce validated migration to bounded host bookkeeping while preserving integrated install/update/uninstall policy and recovery boundaries.
9. Consolidate reporting and argument parsing; move host simulation into fixtures and extend existing lifecycle and bundle coverage.
10. Advance the package version with `scripts/bump_installer_version.py`, add a matching changelog section covering all shipped cleanup and safety fixes, and run installer compatibility, core, bundle smoke, and OpenSpec validation. Sync the lifecycle delta only after implementation verification.

The metadata-envelope refactor does not require rewriting printer ledgers. Host-state compaction does require compatibility handling: retain the pre-compaction ledger as a recoverable migration preimage until the new state is verified, and never discard referenced restoration backups or unresolved journals. A source revert alone is not a sufficient rollback once compacted host state has been written; reverting that representation requires the validated migration preimage. Historical release bundles remain unchanged.
