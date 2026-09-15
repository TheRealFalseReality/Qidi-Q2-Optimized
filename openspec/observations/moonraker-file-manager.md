# Max 4 Moonraker file-manager review

## Evidence boundary

The source snapshot is QIDI Max 4 `moonraker/components/file_manager/file_manager.py`, captured on 2026-09-15. Its SHA-256 is `b0c26fdb2930911ff3c018f3cd68380bbf74682a64049a39a004b66e19d27302`.

**Runtime-confirmed:** the captured source is the file present on the printer. Firmware identity and loaded-process/source equivalence were not verified. **Config-confirmed:** the source paths below exist in that capture. Their presence does not establish measured latency, a live failure, or external exploitability.

All 2,701 lines were reviewed. Line references below refer to the unmodified capture. The retained test fixture contains its `MetadataStorage` class and original metascan handler. Local Python harnesses exercise source against fake service dependencies; they are not live Moonraker validation or the compiled-vendor evidence category used for QIDI Box observations.

## Metadata work addressed by the installer

- `initialize()` at 1944 calls recursive `scan_node()` at 1594. Non-empty supported archives reach `parse_3mf_thumbnail()` at 2602 and queue extraction without checking the cache.
- `_has_valid_data()` at 2431 explicitly rejects any `_3mf_path`, regardless of size and modification time.
- `_process_3mf_metadata_update()` at 2583 drains the shared queue without the general worker's cache checks. Which worker runs depends on which entrypoint first finds the queue idle.
- `_process_metadata_update()` at 2618 does not remove already-valid requests before continuing. Such a request can spin synchronously forever. Both workers also copy the entire pending dictionary to select each first item, creating quadratic queue-selection work.
- `_run_extract_metadata()` at 2659 clears cached `print_start_time` and `job_id` after successful extraction. Skipping unchanged archives avoids that reset; rebuilding unstamped metadata still follows vendor extraction behavior.
- `_handle_metascan_request()` at 434 removes metadata and thumbnail files before queuing ordinary parsing. QIDI added 3MF to the accepted extensions without supplying `_3mf_path` here, so manual archive rescans omit the extractor's `-m` flag.

The installer uses one cache-aware worker, removes completed cached requests, and selects the next request without copying the queue. A successful 3MF extraction records an extractor stat stamp and object-processing policy. Size or modification-time differences, an absent stamp, extractor changes, or policy changes invalidate cached archive metadata. Missing extractor stat data fails closed. A replacement during extraction cannot be stamped as the newer extractor because the stamp is captured before launching it.

Manual 3MF rescans now force archive-aware extraction through the same queue, or join extraction already pending for that archive. They do not delete QIDI thumbnail files. Failure returns an error and preserves prior metadata rather than presenting a failed refresh as successful. The new archive branch validates resolved root containment and reserved paths; the ordinary G-code handler remains unchanged.

Local checks cover persistent-cache reload, unchanged upload/observer requests, changed archives and extractor policy, cached queued requests, mixed G-code/3MF work, manual rescans, thumbnail preservation, and recovery after failed extraction. No Max 4 startup-delay measurements were taken. Q2 patch comments report multi-minute delays, but those numbers are not Max 4 results.

## Upstream comparison and CPU impact

Comparison with upstream Moonraker commit `1cfb0c41e468645951a371621f06d32777b6107c` (2026-09-09) distinguishes QIDI's 3MF additions from inherited behavior. The general metascan handler, temporary upload naming, directory listing, visited-set logic, and notification worker are identical in that source. The cached-request loop, whole-queue copies, and upload prefix check also remain upstream. The discarded UFP escaping result exists in upstream v0.8.0; current upstream passes extraction parameters through a configuration file instead.

The cached-request loop can consume a core continuously; repeated archive extraction also spends CPU and I/O unnecessarily. The patch addresses both, plus quadratic metadata queue selection. The separate notification queue still uses `pop(0)`, which shifts the remaining list on each event and can add quadratic overhead during large bursts; that upstream queue is unchanged. Directory requests still enumerate and stat the tree; offloading that work would improve event-loop responsiveness but would not inherently reduce total CPU work. Retry cost depends on what the extractor does during a failure: a 300-second timeout alone is not evidence of 300 seconds of busy CPU. The captured code initiates scans on startup and filesystem/API activity, not through a periodic full-archive polling loop. No live CPU profiling was performed.

## Other findings not changed by this patch

| Priority | Location | Evidence and impact | Smallest follow-up |
|---|---|---|---|
| High | `_parse_upload_args()`, 845 | Uses string-prefix containment after joining a client filename. A local invocation accepted `../gcodes-sibling/probe.gcode` outside a configured `gcodes` root. Reserved-path checks do not provide general root containment. | Validate resolved destination containment, including symlink parents, before any upload write. Test against QIDI's intentional cache/symlink use. Authentication and network reachability were not reviewed. |
| High | `_handle_metascan_request()`, 434 | The inherited ordinary-G-code path joins the requested filename without a root/reserved-path check. The new 3MF branch has its own containment and reserved-path checks. | Address general metascan containment upstream; the ordinary-G-code branch is outside this patch. |
| Medium | `_process_gcode_notifications()`, 2274 | An exception from one notification leaves `_gc_notify_task` non-null. A local reproduction showed subsequent notifications queued without scheduling a replacement worker. | Recover per-notification failures and clear task ownership reliably, without swallowing cancellation. |
| Medium | `gen_temp_upload_path()`, 813–817 | Names temporary uploads using integer loop time. Calls within the same second produce the same path; the later `finalize_upload()` lock cannot establish unique earlier upload storage. | Allocate unique temporary files. Confirm caller ownership and cleanup in the upload handler before changing the naming contract. |
| Medium | `get_file_list()`, 1012–1060 | Every file-list request walks the tree synchronously and stats/resolves paths. Metadata caching does not remove this event-loop filesystem work. | Measure folder-size impact when idle; consider thread offload before introducing a separate directory cache. Full listing itself is expected API behavior. |
| Medium | `_run_extract_metadata()` and worker retry loops, 2627–2684 | A 3MF subprocess gets at least a 300-second timeout and up to three attempts. A stalled archive can still hold later requests for roughly 15 minutes with the default timeout, excluding overhead. | Measure failures and define an explicit retry/timeout policy; do not silently parallelize extraction on the embedded host. |
| Low | `scan_node()`, 1594–1603 | Membership checks an `os.stat_result`, but the visited set stores `(device, inode)` tuples. Its default set is also shared across calls. Inotify's duplicate-watch rejection provides another guard, so infinite recursion was not demonstrated. | Use a fresh visited set per traversal and compare the same inode-key type. |
| Low | `_run_extract_metadata()`, 2672–2677 | Quote escaping for UFP/3MF paths discards the returned string. Quoted archive names can produce a malformed command argument string. | Construct arguments consistently after checking the shell-command component's tokenization contract. Shell injection was not established. |

Directory enumeration, new/changed archive extraction, QIDI print-time decompression, and vendor retry limits remain unchanged. General upload/metascan path containment, notification recovery, and the other upstream findings remain separate follow-ups.
