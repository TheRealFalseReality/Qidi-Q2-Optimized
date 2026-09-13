## 1. Define cumulative compatibility metadata

- [x] 1.1 Resolve every existing `supported_upgrade_sources.yaml` profile and capture the deduplicated union of allowed patch targets and source-patch provenance before removing the version mapping; verify all admitted profiles are represented.
- [x] 1.2 Replace per-version compatibility models and parsing with a schema-versioned cumulative envelope; verify malformed paths, duplicate targets or source provenance, invalid hashes, and unsupported roots are rejected by existing compatibility coverage.
- [x] 1.3 Replace `installer/supported_upgrade_sources.yaml` with the cumulative union while retaining explicit `package.known_versions`; verify the new envelope equals the captured old-profile union.
- [x] 1.4 Require the current package version in `known_versions` and current manifest targets and source variants to be subsets of the envelope; verify missing current coverage fails validation.

## 2. Integrate state and lifecycle validation

- [x] 2.1 Require prior installed state to match the manifest package ID and an explicitly known version before install or reinstall preflight; verify wrong identity and unknown versions fail before backup or mutation.
- [x] 2.2 Validate install and uninstall patch ledgers against the cumulative target envelope; verify historical-only recognized targets are accepted and unknown targets are rejected.
- [x] 2.3 Validate source ledgers against cumulative firmware/hash provenance; verify destination, firmware, preimage, live-drift, and first-preimage checks remain enforced.
- [x] 2.4 Replace enumerated config-only backup versions with an admitted-version-aware `26.07.26.1` external-manifest boundary using numeric components; verify unknown or malformed versions fail closed.
- [x] 2.5 Remove superseded release-profile lookup, inheritance, and backup-version parsing after integration; verify install, uninstall, restore, and rollback no longer depend on those representations.

## 3. Simplify release tooling

- [x] 3.1 Change `scripts/bump_installer_version.py` to update `package.version`, append the new known version once, and update optimized globals without adding a compatibility profile; verify an ordinary bump leaves the envelope unchanged.
- [x] 3.2 Update the known-version checker and bundle validation for current-manifest subset coverage; verify a compatibility-affecting addition fails until explicitly admitted.
- [x] 3.3 Update release-maintenance guidance that requires a per-version upgrade profile; verify it describes explicit version admission and cumulative envelope maintenance consistently with the tooling.

## 4. Preserve compatibility coverage

- [x] 4.1 Update existing compatibility coverage for the cumulative schema, malformed entries, duplicates, missing current coverage, unknown versions, and wrong package IDs; run the relevant checker and tests directly.
- [x] 4.2 Extend the existing lifecycle matrix for direct update and uninstall from the oldest admitted config-only release, a pre-source release, `26.07.26.1`, and the current release; verify no sequential migration is required.
- [x] 4.3 Cover historical-only targets and approved source provenance; verify unknown destinations, firmware/hash combinations, and live drift remain rejected or preserved according to the lifecycle contract.
- [x] 4.4 Cover backup classification immediately before and at `26.07.26.1`, plus unknown, malformed, and state-declared-source cases; verify external-manifest requirements remain fail closed.
- [x] 4.5 Update existing version-tooling coverage for append-only version identifiers and explicit envelope changes; verify ordinary releases do not duplicate compatibility data.

## 5. Consolidate configuration planning and transaction safeguards

- [x] 5.1 Reconcile the implementation baseline with concurrent saved-variable changes; verify the plan preserves live Moonraker writes, pending activation expectations, and exclusion of whole saved-variable files from compensation.
- [x] 5.2 Use one per-destination file-change plan for install/uninstall preview and execution, retaining independent postflight; verify identical validated inputs produce the same proposed writes and drift decisions, multiple edits compose correctly, and stale preimages are rejected before overwrite.
- [x] 5.3 Consolidate configuration preimage tracking, compensation, and recovery-blocker handling in a small shared transaction boundary; verify existing install, uninstall, and restore success/failure scenarios without introducing a generic operation engine.
- [x] 5.4 Add restore idleness validation after confirmation and before live replacement; verify printing, paused, unknown, and unavailable states prevent replacement for config-only and external-source archives, while idle recovery from an existing blocker remains possible.
- [x] 5.5 Compensate interrupted uncommitted configuration writes before CLI interruption handling; verify interruption before mutation, after mutation, during compensation, and after configuration commit preserves the correct files, recovery/activation obligations, and no-traceback behavior without later restart or reboot actions.

## 6. Simplify integrated host optimization and restoration

- [x] 6.1 Keep every declared system optimization in the existing package and install/update/uninstall flow with persisted policy, prompts, and reboot authorization; verify existing integrated lifecycle and automatic-update scenarios still invoke enabled host work without a separate operator command.
- [x] 6.2 Separate verified configuration commit from host compensation and result handling; verify host apply/restore failure cannot erase a verified configuration install or discard unresolved restoration state, and failed compensation blocks later unsafe actions.
- [x] 6.3 Record sufficient last-applied host state and enforce ownership-aware restoration for files, symlinks, assets, services, and root-mount state; verify desired state reverts, preimage state is a no-op, and user-modified or unprovable state is preserved and reported, including explicit keep policy.
- [x] 6.4 Replace accumulated action history with bounded policy, first preimages, latest outcomes, and explicit recovery evidence; verify old-ledger migration, pending Rockchip transaction matching, reboot markers, and first restoration preimages remain recoverable before removing history.
- [x] 6.5 Check whether a write is needed before capturing additional backups, and keep historical diagnostics outside recovery state; verify repeated already-current reconciliation leaves recovery-state size and backup count bounded and never prunes a referenced recovery preimage.

## 7. Consolidate reporting and command-line handling

- [x] 7.1 Share semantic reporting, summaries, and progress inputs across thin plain/Rich renderers; verify both modes preserve prompts, drift reporting, errors, dry-run, demo, and debug behavior without affecting operation decisions.
- [x] 7.2 Move argument parsing, aliases, help, version reporting, and combination validation into Python; verify existing install, restore, and auto-update shell command forms and exit behavior through launcher/bundle coverage.
- [x] 7.3 Reduce shell launchers to bundle discovery and isolated Python startup, removing superseded parsing and UI bookkeeping; verify help/version/demo need no printer access or backup and retain bootstrap import safety.

## 8. Simplify test I/O and exercise safety boundaries

- [x] 8.1 Move fake service and mount-state behavior into fixtures behind a minimal command/I/O boundary while retaining temporary filesystem roots; verify tests execute production classification and recovery logic without real network, sudo, service, printer, or reboot effects.
- [x] 8.2 Diagnose the automatic-update child lifecycle timeout and model process identity changes on restart rather than query count; verify added saved-variable queries do not consume scripted activation identities, and production restart waits remain at least 60 seconds.
- [x] 8.3 Extend existing lifecycle, host optimization, and bundle matrices for the scenarios in sections 5–7; remove superseded or overlapping tests and verify the core suite remains below five seconds without weakening failure or safety coverage.

## 9. Release and validate

- [x] 9.1 Use the unreleased package version `26.09.09.1` as directed by the release owner, run `python3 scripts/bump_installer_version.py 26.09.09.1`, and consolidate the matching `CHANGELOG.md` section covering metadata condensation, cleanup, and operator-visible safety fixes, including changes merged since the preceding changelog version; verify version authorities and release notes agree.
- [x] 9.2 Run `python3 scripts/check_installer_known_versions.py` and `python3 scripts/run_installer_core_tests.py`; verify both pass and record core-suite duration.
- [x] 9.3 Run `python3 scripts/build_installer_bundle.py --output-dir dist --channel dev --build-id local --smoke-test`; verify the bundle retains integrated optimizations, launchers, reporting modes, and compatibility assets.
- [x] 9.4 Verify implementation against the lifecycle delta, sync the affected main requirements without overwriting concurrent saved-variable changes, and run `openspec validate --all --strict`; inspect the final diff for unintended vendor, payload, policy, or operator-interface changes.
