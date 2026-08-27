# PLAINSIGHT FOUNDATION
## What we already have, what transfers, and the five decisions that block the first line of code

**Status: DRAFT 2026-08-26. Nothing here is operator-ratified.** Sections 3 and 5 are decisions I am recommending, not recording. Section 2's DOES-NOT-TRANSFER list is the part I would most like argued with.

---

# 1. Vibe check — reading your program back to you

You have three codebases at three genuinely different maturity levels, and it took reading the actual files to see that they are not three stages of one thing. They are a standards body, an operational client, and a piece of honest scaffolding, and each is at exactly the maturity its job requires.

**ZMeta is the mature one, and it is mature in a specific and unusual way: prohibition is expressed as structure rather than prose.** `ZMeta/Documentation/zmeta-event-1.0.schema.json` has four required top-level fields — `["zmeta_version", "event", "source", "payload"]` — and then spends its `allOf` block making certain things *impossible* rather than *discouraged*. `"confidence": false` appears at schema lines 67, 184, 211, and 930: a JSON Schema `false` at a property makes presence a validation error, so "an observation may not carry confidence" is not a rule someone has to remember. `zmeta-spec/policy/semantics.yaml` extends this recursively — `observation_event.payload_must_not_contain: [track_id, entity_class, classification, label, class_name, confidence]`, with the comment that it is "Enforced recursively, so nesting inside claim sub-objects or free-form payload objects cannot launder fused identity or fused state into an inference." Somebody thought about the connector author who would try to smuggle a judgment through a nested object, and closed that door in policy rather than in a code review checklist. The `semantics-contract.md` is 2,482 lines. `AGENTS.md` tells clones not to edit the governed surfaces because "Local changes to those surfaces create a private dialect." This is a specification with a governance model, and it is the single most valuable asset in the program.

**ZISR COP is mature in the code and drifted in the docs, and the drift runs mostly in the direction people don't expect.** `app/` is 10,847 lines with no package.json, no bundler, no framework, and zero bare import specifiers — every dependency is vendored and script-tagged. That is not laziness; it is what makes the "no external calls, no CDN, no ion tier" posture verifiable by reading the directory. `docs/UIUX_DESIGN.md` §3 says any value not in its token list is a bug, and then `config.js` carries `SIM_LABEL_BACKGROUND_HEX = "#d054a8"` and `cesium_adapter.js` carries `CONFIDENCE_UNREPORTED_RING_HEX = "#9aa7b4"`. §9 documents four keyboard shortcuts and one is implemented. §4 documents five tabs and `wireNavTabs()` renders `Planned — slice ${slice}` into a single `<p>` for four of them. But the more interesting drift is the other way: **the reference-camera availability layer, the feed banner with its `bridgeStateLabel()` degraded-transport vocabulary, the session retention bound, and the imagery picker are the best patterns in the repo and appear nowhere in the design record.** The code got smarter than the document and nobody wrote it down.

**zisr-recon is scaffolding, and it is the correct kind.** `src/zisr_recon/guard.py` is a target gate; `docs/ENTRY_CRITERIA.md` is the criteria the gate points at; `cli.py:12-15` says there is "deliberately NO subcommand that launches a scan… wrapping it here would make it one flag away from happening by accident." The whole tool is built so that the permission it does not have cannot be accidentally exercised. `docs/ENTRY_CRITERIA.md` then adds the clause that makes the design productive: a `## What is explicitly NOT gated` section stating that the parser, classifier, schema, storage, and ZMeta adapter "were built on 2026-08-25 while every permission criterion above remained unmet. That is the point of the design: the capability is provable before the permission exists."

**`ZMeta/zmeta-field-capture` is the least-advertised and most directly relevant piece of the program**, because it is the one place where you already handle other people's sensitive data and had to decide what that means mechanically.

### The engineering values, read off the files rather than inferred

1. **Prohibition is structural.** `"confidence": false`. `payload_must_not_contain`. "There is deliberately NO subcommand that launches a scan." A rule that lives in a README is not a rule.
2. **Absence is a fact, never a default.** ZMeta §6.8: "Canonical `geo` is all-or-nothing… The `(0, 0, 0)` sentinel pattern is not valid evidence of unknown position." `adapters/README.md`: "Fallback timing is intentionally degraded timing." The COP's `notEvaluated("no position — never admitted, so never TTL-evaluated")`. PLAINSIGHT's `not_attempted`. Four independent derivations of the same idea.
3. **No invented numbers.** `classify.py:6-16` refuses a confidence score in prose — "a number implies a measurement, and there is no measurement here" — and `tests/test_recon.py:180-186` asserts `"confidence" not in c.to_dict()`. PLAINSIGHT §8.4 kills `precision_prior`, `evidentiary_weight`, and the ICD bands for the same reason and books the 6–8 engineer-weeks saved. Two components, no shared code, same rule. Treat it as settled program doctrine.
4. **A check that can pass for a reason other than the one claimed is not a check.** From `RETENTION.md`, learned the hard way when Cloudflare's cached read path made a deleted object appear to survive deletion. Same instinct in `evidence_common.verify_detached()`, which parses `--status-fd` rather than trusting gpg's exit code "because gpg returns 0 for a good signature from ANY key it happens to hold."
5. **Every removal names itself.** `capture_server.py:624 enforce_ring()` writes a `{"kind":"pruned","path","bytes","pruned_utc","reason"}` line per deleted file. The COP's retention boundary is deliberately expressible as a timestamp so it can present as "not available before X" rather than a silent gap. PLAINSIGHT §5.7 renders `▨ raw media expired 2026-05-01 · run record retained`.
6. **Rejected reasoning is recorded, not forgotten.** `ENTRY_CRITERIA.md:171-186` has a `[REJECTED READING — DO NOT RE-DERIVE IT]` block. PLAINSIGHT has CUT LIST A, with the reason and the weeks saved per row. Both of these exist because you have been burned by re-deriving a bad idea.
7. **Ratification is tracked per-item and unratified binds nothing** — `ENTRY_CRITERIA.md:16-18`, "One partially stamped item does not stamp the file" — and conclusion is ratified separately from basis, with a note that "No emitter should be built on a rationale the operator was never shown."

### The one pattern that is consistent and is a problem

**You write mechanisms where the failure mode is technical, and sentences where the failure mode is procedural.**

- Tier 0 in `RETENTION.md` is "Rolling ~2 hours." The mechanism is `enforce_ring()`, byte-denominated on `ZCAP_RING_BYTES`. It runs. It is also not what the doc says.
- Tier 1 is "Default expiry is 30 days from the pull." I grepped every `.py` in `zmeta-field-capture` for `expire|expiry|30 day|rmtree`. Nothing reads a pull date. Nothing deletes a pull directory. `pulled/20260815T003547Z/data/raw/20260815/undeclared/udp/port7100-20260815T00Z.ndjson` is on disk at 339,703,009 bytes right now. That's day 11 of 30 — nothing is violated. Nothing will act on day 31 either.
- `guard.py` line 54 is `from datetime import date`. It is the only occurrence of `date` as an import in the file, and it is never called. `authorized_on` is loaded as a free-text string and never parsed. `expires_on` does not exist. The expiry check was clearly intended and was not written.
- `OriginAuthorization` loads `scope` (`guard.py:103`), requires it (`:119`), prints it in `describe()` (`:219`), and `check()` never reads it. Once any complete authorization file exists, every non-NEVER address on earth is permitted, and `tests/test_recon.py:56-79` demonstrates exactly that with a file scoped `"test"`.

This is not sloppiness. It is a consistent seam: when the thing that can go wrong is a byte count or a bad datum, you build the guard. When the thing that can go wrong is somebody's judgment about permission or purpose, you write the sentence and mean it.

**The OSINT COP is the first system in the program where the procedural axis is the dangerous one.** Its subject is a third party who cannot be asked and did not consent, and the operator's own framing — experimentation only, findings not acted on, retained data deleted once its purpose is served, capabilities reviewed before availability — is a set of *procedural* commitments. So the recommendation running through this whole document is not an external requirement being imposed on you. It is: **do to retention and targeting what you already did to schema conformance.** Make the TTL a job that fires and the scope a gate that refuses, because your own `enforce_ring()` is the proof that you build it that way when you decide the failure matters.

---

# 2. What transfers

## 2.1 The ZMeta kernel — transfers, as a fork, not as emission

| Take | How, concretely |
|---|---|
| The four-field envelope | `{version, event{id,type,subtype,ts}, source{platform_id,node_role,producer}, payload}`. `source.producer` → connector id (`toutatis`). `source.node_role` → where the connector ran (`LOCAL`/`RUNNER`/`CLOUD`), which is the credential-exposure axis. `additionalProperties: false` everywhere. |
| UUIDv7 ids | §4.3: adapters "MUST regenerate `event_id` as UUIDv7… Legacy identifiers MAY be preserved in `payload.source_event_id`." RUN/ITEM/CLAIM ids become UUIDv7; `platform_uid`, `msg_id`, `snap_id` go in payload provenance. You get free sortability, dedup, and replay ordering, and you never confuse a site-native id with a system id. |
| The locked type enum + payload discriminator match | ZMeta's `$defs.subtypePayloadMatch` requires `OBSERVATION_EVENT/RF` to have `payload.modality == "RF"`. §7.3: "Producers MUST NOT use free-form subtypes." Keep the mechanism, change the tokens (§4 below). |
| `"confidence": false` on observations | PLAINSIGHT §1's "the system never prints a number it invented" becomes a schema error rather than a code-review norm. This one line is worth the whole fork. |
| `policy/semantics.yaml` recursive denylists | PLAINSIGHT §6.1 declares "CONNECTORS MAY EMIT ONLY layer: observation. This is structural." Right now that is a comment in a YAML example. ZMeta's `payload_must_not_contain`, enforced recursively, is what makes it true against a connector that nests `proposes: same_entity` two objects deep. |
| Typed lineage | `lineage: {based_on: [uuid, minItems 1], transform}` plus `policy/lineage.yaml`'s `allowed_parent_event_types` (`INFERENCE_EVENT: [OBSERVATION_EVENT]`, `STATE_EVENT: [FUSION_EVENT, STATE_EVENT]`) with `parent_type_mismatch_mode: reject`. That is PLAINSIGHT's CITATION object and Lineage Drawer graph shape, expressed as eight lines of policy instead of application code. |
| `transform: "translate:<schema_id>@<adapter_version>"` | This is the retroactive-invalidation mechanism PLAINSIGHT §7.5 needs and does not have. "Connector X version Y went SUSPECT on date Z — what does that poison?" becomes an index scan over `lineage.transform`, not a re-run. |
| The five-rung conformance ladder | `pytest` → `validate.py` → `check_compat.py` → `validate_adapter_conformance.py` → `validate_conformance.py --kernel-gate`. Rung 4 calls *your adapter* against JSONL fixtures. This is the machinery under PLAINSIGHT §6.5's "Prove It" step. |
| **`event_count: 0` refusal fixtures** | The harness doc: "`0` pins a fail-closed refusal the way the other keys pin emission… **Write one refusal fixture per schema-required input field.**" PLAINSIGHT's `known_negative` canary is mandatory but one-per-connector. ZMeta's is one-per-required-field, which is strictly stronger and already CI-enforced. Copy the per-field rule. |
| Mapping packs | `pack.json` + `mapping.yaml` + `enums.yaml` + `units.yaml` + `tests/{input,expected}.json`, with "no runtime engine executes `mapping.yaml`" — it is reviewed documentation that doubles as conformance evidence. This is exactly what PLAINSIGHT's connector field-map should be. |
| §4.5.1 external-state promotion | `external_state_promotion: {mode: reject, always_reject_loop_risk: true}` and "Confidence never increases just because an external system reported the track." This is the aggregator-laundering problem — ingesting a third party's pre-asserted identity link — already solved, including the `use_limits` matrix (`DISPLAY`/`ALERTING` allowed, `COMMAND_BASIS` prohibited). |
| §9.4 `data_ref` / raw-data-absent | "Raw-data absence is not a validation failure by itself. It is a trust and provenance condition." `{ref_id, store, kind, format, hash, size_bytes}` survives the blob it points at. This is what a claim means after media expiry. |
| The residue classes | Especially "datum-unlabeled plausible values" — see §3, decision D2. This is the single most transferable prose in the repository. |

**Changes for person-centric data:** `modality` is a five-value enum (`RF|EO|IR|ACOUSTIC|NETWORK`) with no legal token for an HTTP fetch, and `NETWORK` is a trap — `adapters/README.md` defines it as cooperative RF broadcast decode (ADS-B, AIS, rtl_433). `timing_quality`'s vocabulary (`GPS_PPS`, `NTP`, `PTP`, `HOLDOVER`) would sit permanently at `UNKNOWN`/`UNSYNCED`, and a flag that is always red is not a flag. `TrackStatePayload` requires `geo`. Those three are why this is a fork and not an emission — see D1.

## 2.2 zisr-recon's guard and entry criteria — transfers as shape, with three bugs to not carry over

**Transfers directly:**

- **Default-deny on the target, not on the tool** (`guard.py:21-24`). This is the sequencing answer for the whole project: build the Run/Item/Claim spine, the connector contract, both canaries, six views, every connector — against **your own accounts and synthetic personas** — with the subject gate refusing everything else. Weeks 1–13 of PLAINSIGHT §8.1 need no targeting permission at all under this model.
- **Hard refusals evaluated first, unconditionally** (`guard.py:175-182`), with a test proving a present authorization file does not unlock them (`test_recon.py:56-79`).
- **Partial is refused, not half-honoured.** `OriginAuthorization.load` sweeps seven required fields and raises: "A partial authorization is refused rather than half-honoured: every field answers a question a reviewer will ask." Reusable almost verbatim.
- **The refusal message pattern** (`:195-207`) — names the rule, the date, the authority, and the two legitimate ways forward. `test_recon.py:37-38` asserts message content because "The refusal has to explain itself, or someone will just delete it."
- **`describe()`** (`:214-224`) → the COLLECTION-view header. This replaces PLAINSIGHT's purely cosmetic `SCOPE ⟨none⟩` (design line 122) with a line that means something.
- **The whole ENTRY_CRITERIA architecture**: two artifacts pointing at each other, per-criterion ratification, conclusion stamped separately from basis, permission gates separated from conformance requirements ("Satisfying it grants nothing"), `[REJECTED READING]` tombstones, "excluded, not unimplemented" language, evidence recorded verbatim in the machine-readable file, and — critically — a `## What is explicitly NOT gated` section.

**Three defects must not be ported:**

1. `net.subnet_of(banned)` is one-directional and `_is_private()` judges a network by its two endpoints. Together they permit `0.0.0.0/0` and `::/0` with no authorization: `0.0.0.0` and `255.255.255.255` are both "private" in Python's table. The selector analogue is a wildcard or prefix pattern in an authorization record matching more than intended. Test that a *broad* pattern is refused, not just that a specific out-of-scope selector is.
2. `NEVER` is IPv4-only (`net.version == banned.version` against an all-IPv4 list), so no IPv6 target is ever hard-refused. Whatever the person-NEVER list is, enumerate the selector types it must cover, and test each.
3. `scope` and `authorized_on` are loaded and never enforced. Write the expiry check that line 54 was imported for.

**What changes, and it changes a lot:**

- **Ownership is verifiable; permission-to-investigate is not.** "This /24 is ARIN-assigned to us" is a fact-check. "We may investigate this person" is pure self-certification. `guard.py:43-46`'s honest caveat — not a security boundary, only a guard against forgetting — becomes the *entire character* of the person gate rather than a footnote on it.
- **The allowlist moves.** You cannot key it on the thing you are trying to establish; whether `handle:instagram/j_voss_88` belongs to the subject is the question the system exists to answer. So it is keyed on **selectors**, and the authorized selector set **grows with every accepted `same_entity` inference**. The host model never faces a moving allowlist.
- **The predicate is three-valued.** `net.subnet_of()` is a total, cheap containment test. There is no containment relation over people. `permitted | requires_extension | refused`, and the middle state is the *common* one, because it is where every pivot lands.
- **Collection on A collects on B.** Follower lists, Telegram channel membership (`kind: continuous, probe_unit: subscription`), faces in a group photo. `check(target) -> None | raise` has no shape for bystanders. Must be built new.
- **The person-NEVER list is not a pre-filter.** You cannot refuse to collect on a minor without collecting enough to know they are one. The honest mechanism is stop-and-escalate on indicator: a class of signals that halts the run in place, surfaces the trigger, and requires an operator decision before anything further is collected or retained.
- **The discovery/access bright line does not survive.** `README.md:79-84` — "Never connect to it, never authenticate to it, never pull a frame… after *Van Buren* the authentication gate is the thing that matters legally" — is honoured by construction in `classify.py`, which opens no sockets. PLAINSIGHT's toutatis connector authenticates with a pooled Instagram session and the manifest says so. The replacement line is not authentication but **interaction**: no contact with the subject, no request that induces a person to disclose, no access to content not visible to an ordinary authenticated viewer. That line is blurrier and has to be written and ratified, not inherited.

**The enforcement point is the one thing that must be different.** `TargetGuard` is constructed in exactly two places, `cmd_status` (`cli.py:31`) and `cmd_check` (`cli.py:42`) — both user-facing queries. `parse.py` and `classify.py` never import it. The guard is an oracle a human consults, and it is safe because the tool cannot act. PLAINSIGHT's runner builds argv and executes on the analyst's behalf. **Porting the predicate without putting it on the dispatch path reproduces the reassurance without the protection.**

## 2.3 field-capture retention and evidence — transfers as mechanism, with the gap as the lesson

**Transfers directly:**

- **Tombstones.** `{kind, path, bytes, pruned_utc, reason}` per pruned file, and `test_ring.py:165` asserts "pruned file is actually gone from disk." Becomes `{kind:"shredded", blob_sha256, bytes, shredded_utc, reason, case_id}` and feeds PLAINSIGHT's existing `▨` hatch channel. No new UI vocabulary.
- **Dual hashing.** "the recorded hash covers the compressed and encrypted bytes, because that is what integrity has to be checkable against. The plaintext gzip hash is recorded alongside it." PLAINSIGHT's `raw_blob_sha256` is a single plaintext hash — correct for a content-addressed store, wrong the moment blobs are encrypted at rest. Store both.
- **Immutability at the store, not just the log.** `mint_evidence.py` refuses any existing artifact path; `upload_evidence.py` refuses a key whose stored bytes differ. PLAINSIGHT §8.3 asserts append-only over `{runs, items, claims, …}` — extend it explicitly to blobs.
- **`safe_component()`.** Refuses `..`, separators, drive letters, leading `~` on operator-supplied names joined into paths. The COP's object keys will be built from handles, emails, and channel names — *adversary-controlled strings*, strictly worse than operator-typed sender labels. Day one.
- **Split local action from egress.** "Minting never uploads. Nothing leaves this machine as a side effect of running this tool." PLAINSIGHT's export boundary currently enforces citation completeness; give it a second job.
- **`--remove-plaintext` gated on `decrypt_check == "matched"`.** Never delete the readable copy until the replacement is proven readable. That is the correct shape for every retention transition in the COP.
- **The evidence-registry properties** — signed, hash-anchored, versioned, "An object that is not listed here is not evidence" — and the four-object key set (`.jsonl.gz.gpg` / `.sidecar.json.gpg` / `.index.json` / `.index.json.asc`) where "one pinned signature anchors the whole set."
- **`reconcile_evidence.py` wholesale**, including its docstring as the standard: "the schedule rests on something that runs rather than on someone remembering what to compare." Diff in both directions.

**Changes:**

- **The registry container changes.** zmeta admits the object key leaks the sender label — "the sender label is the deliberate cost of it. Choose sender labels accordingly." The COP's equivalent leak is a third party's handle. Keep the properties; put **opaque case IDs** in the versioned registry and hold the ID→selector map in the encrypted store.
- **Purpose moves up a level.** zmeta mints at six named decision points and "never on a schedule. Anything else stays in tier 1 and expires." PLAINSIGHT is built on the opposite premise (line 10: "Everything a tool produces lands in the case automatically and immediately"). That is the product thesis, not a flaw. So the purpose record attaches to the **CASE**, not the object. `RETENTION.md`'s rule survives restated: **no qualifying purpose, no case.**
- **`consent` is the wrong primitive and should not be ported.** It works in field-capture because there is a counterparty — "The captures are the producer's data, not ours" — with separate `retention` and `publication` permissions and a real registry row honestly reading `not-asked` for both. The COP's data subject cannot be asked. What replaces it is the targeting authorization plus the recorded experimentation purpose, and that gate lives upstream at what may be pivoted on.

**The gap is the lesson.** Tier 0's ring is code and it runs. Tier 1's 30 days is a sentence in a Cadence bullet, and 339 MB is sitting on disk with nothing scheduled to act on day 31. That is the exact failure the OSINT COP cannot repeat, and it is why D4 exists.

## 2.4 COP app conventions — transfer selectively; the doctrine mostly does not

**Transfers:**

- **The `mountX({container, …}) → handle` convention** and the `el()` / `row()` / `kv()` / `sectionHeader()` primitives, which are currently copy-pasted verbatim into five files (`inspector.js`, `feed_panel.js`, `aor_panel.js`, `right_rail.js`, `labels_layer.js`). That duplication is the argument for extracting them.
- **The chip grammar**: fill = asserted/verified, outline = unverified, muted-dashed = expired (separated from solid-muted UNDECLARED specifically because "two chips that look identical inside the same panel would collapse 'nobody declared live-or-sim' and 'the producer stopped asserting' into one indistinguishable mark").
- **One predicate, three readers.** `isExpired(view, nowMs)` is imported by `main.js` rather than reimplemented, because "three readers… disagreeing about whether a given entity is expired is exactly how a picture starts lying about itself. One function, one answer." Never cached: "A cached verdict is how a frozen picture starts reading as a calm one."
- **Single writer for any shared surface.** `refreshStatusLine()`: "Two independent writers appending to the same element is how a line ends up claiming one thing while showing another." Applies directly to PLAINSIGHT's RUNS strip and provenance line.
- **Counts, never verdicts; absent until non-zero.** "a permanent '0 EXPIRED' would train the eye to skip the region where the real number will appear." And `bridgeStateLabel()` returns `null` when healthy, because OPERATIONAL_CONTRACT §4 "prohibits inferring 'link is fine' from the absence of a failure signal."
- **Filter-independent counts.** `feed_panel.js` computes LIVE/SIM from the whole feed, "never from what the map adapter currently has admitted/visible." PLAINSIGHT needs this exact rule for COLLECTION counts and STREAM facets.
- **Shared vocabulary tables between writer and reader**, with a test asserting every state the writer can emit has wording at the reader, `Object.create(null)` so a token named `constructor` cannot read as recognised, and unknown tokens rendered raw rather than dropped. This is the anti-drift mechanism for PLAINSIGHT's connector `render:` slots and its five health states.
- **States rendered as consequences, not tokens.** `parked` → "PARKED — this COP is NOT attached to this source. Nothing here is being refreshed, so what is drawn is as old as the catalogue: stale BY DECISION, not by fault." Because "an operator cannot act on the string 'forgotten'." Write PLAINSIGHT's five connector states this way.
- **A third data origin gets a third render path, structurally.** Reference cameras get their own data source, their own registry, their own resolver kept deliberately apart from `resolveRecord` ("a published catalogue entry must not reach the inspector through the same door as a ZMeta entity"), and a **reduced inspector with no tab strip** so it can never pick up a Provenance tab for data it doesn't have. PLAINSIGHT's GENERATED selectors and `no coordinate` place-name inferences need this structural separation, not a boolean.
- **The bridge model.** `tools/bridge/README.md`: "This bridge is **not** a feed producer… the bridge's job stops at getting bytes off the relay, onto disk, and getting that CLI invoked." One contract (`GET /feed` + SSE `feed`/`health`), two transports (local bridge, deployed Worker), app code written once. **Upsert-only**: "keys absent from a later snapshot are NOT deleted — falling out of that window is not evidence the entity is gone." PLAINSIGHT must state this for every polling connector or a quiet Telegram channel will silently delete messages from a case.
- **The evidence-gate structure** from `UIUX_DESIGN.md` §6, ported into the Merge Sheet and the cite action: authorizing identity "pulled from the authenticated session, never a free-text field"; cited evidence IDs "selected from this entity's actual history, not typed free-form; zero cited events cannot submit"; an explicit acknowledgment, "Not a pre-checked box"; and the audit record produced "before the command is considered sent, not best-effort logged after."

## 2.5 DOES-NOT-TRANSFER — the important list

| Thing | Why not | What to do instead |
|---|---|---|
| **Emitting `zmeta_version: "1.0"`** | `payload.modality` is a closed five-value enum with no token for an HTTP/API observation, and `event_subtype` must equal it (§7.3). §20.2 lists `CYBER` and `SIGINT` as *reserved, not valid*. Minting a token is the "private dialect" `AGENTS.md` forbids. | Fork the kernel. D1. |
| **ZMeta's `STATE_EVENT`** | `TrackStatePayload` requires `["track_id","geo","valid_for_ms"]`. There is no coordinate-free operator state, because STATE exists to become a CoT point (`payload.geo.lat → event.point.@lat`). | Build a STATE-equivalent with `geo` optional, keeping `valid_for_ms` and the raw-artifact denylist. |
| **`timing_quality`** | `GPS_PPS`/`NTP`/`PTP`/`HOLDOVER` is clock discipline. Every OSINT event sits at `UNKNOWN`/`UNSYNCED` forever, which is honest and useless. | Keep the *discipline* — mandatory, degraded by default, folds field-locally, never repaired when corrupt. Swap the fields for `{observed_at, asserted_at, time_provenance}`. |
| **ZMeta Profiles L/M/H** | Bandwidth thinning for constrained radio links. The COP is one pane of glass. Porting imports a large validation surface for zero benefit. | Drop. |
| **`COMMAND_EVENT`, deconfliction, the altitude prohibition, track lifecycle, the CoT egress path** | The COP issues no commands to platforms and has no tracks. | Drop entirely. |
| **§6.1–6.6 units and geodesy** | No units problem exists here. | Keep only §6.7 "Unit Inference Is Forbidden," generalized: *absence of a declared meaning does not imply a default.* |
| **`guard.py`'s two-valued `check()` and its containment arithmetic** | There is no containment relation over people, and `subnet_of` has no selector analogue. | Three-valued `SubjectGuard`. |
| **The guard's placement as a CLI oracle** | Safe only because zisr-recon cannot act. | Put it inside the runner, between pivot-selection and argv construction, before any credential is drawn. |
| **The discovery/access line (`Van Buren`, "never authenticate to it")** | PLAINSIGHT's connectors authenticate by design. | The interaction line. Must be written new. |
| **`consent` as a field** | No counterparty exists to ask. Porting it produces a field permanently reading `not-asked`, which is theatre. | Targeting authorization + recorded experimentation purpose. |
| **The evidence registry as a git-versioned markdown table** | It leaks the subject's handle into a repo. | Same properties, opaque case IDs, selector map in the encrypted store. |
| **Map-first interaction doctrine** (`UIUX_DESIGN.md` §2a: "The map is the control surface, not a display") | PLAINSIGHT §3.4 makes MAP one of six views, "thin, scoped, and mostly about where we swept," and §3.1 argues landing there "is an empty basemap for ~90% of cases." The AOR grammar, the five retask gestures, the layering rule, the acceptance-confirmation loop all presuppose a globe as the primary object. | Inherit §1 (principles, map-agnostic). Discard §2 wholesale. **Forcing map-first onto a claim-centric product is the single most likely way the "family resemblance" goal produces a worse product.** |
| **All of Cesium** | ~90% of cases are `MAP(0)`. A vendored Cesium build for a thin sweep-coverage view is not justified. | Keep the *adapter seam* so the choice is reversible; skip the engine. `staleBucket` / `symbolStyle` may be directly reusable if PLAINSIGHT wants ATAK-style decay. |
| **The AOR grammar and admission machinery** | `ECOSYSTEM_CONTRACT` §4: "**An AOR is a scope filter. It is never an authorization object.**" PLAINSIGHT's scope object is the case, and its gate is a *person* gate — a different authority class. | Case-scoping, already in the design. |
| **Empty-by-default** | ZISR's map is empty by default so you don't "pop open the map and are immediately blasted with dots." PLAINSIGHT §3.1: DOSSIER "is **never empty**" — opening a case instantiates a provisional entity. | Do not port. The case is already the container. |
| **ZISR's seven classification hues** | PLAINSIGHT §5.2: exactly one hue, red = *the system does not vouch*. Note ZISR's inspector already uses `--red` for STALE/ABSENT/FABRICATED KEY/BASIS NOT STATED — the same meaning. | Share chrome tokens; each app owns its semantic palette. |
| **ZISR's `▨` hatch meaning "absent"** | PLAINSIGHT's `▨` means "do-not-vouch." Direct collision if a component library is shared. | One of the two moves. Decide before extraction. |
| **The auth model** (operator/analyst/commander, per-AOR visibility, command authority as its own class) | PLAINSIGHT v1 is single-writer-per-case with a presence lock. | Defer. |
| **The Durable-Object-per-AOR fan-out** | PLAINSIGHT §8.3: one Postgres, nine tables, one websocket per case carrying invalidation notices only. Fundamentally different scaling shape. | Boring architecture, as designed. |
| **`window.prompt()` for New Task** | Noted only so nobody copies it. | — |

---

# 3. The decisions that block building

Five. Each is expensive-to-impossible to reverse. Everything else is recoverable and should not be decided now.

### D1 — Does the OSINT COP emit ZMeta, a ZMeta-derived dialect, or its own model?

**Options.** (a) Emit valid ZMeta 1.0. (b) Extend ZMeta via a governed version branch. (c) Fork the kernel into a separate, explicitly ZMeta-derived model. (d) Design from scratch.

**Recommendation: (c). Fork the kernel. Call it PSE — PLAINSIGHT Semantic Envelope — version 1.0, with `derived_from: "zmeta-event-1.0"` as a declared field and a divergence section in the design doc.**

(a) is not available. `payload.modality` has no legal token for an HTTP or API observation and `event_subtype` must equal it; `TrackStatePayload` requires `geo`; `policy/producer-authority.yaml` has no wildcard for an OSINT connector and `PRODUCER_NOT_ALLOWED` fires "before any semantic check runs." (b) is disproportionate: §20.2 requires a new observation class to specify "Required fields. Units. Optional fields. Prohibited fields. Timing/window behavior. Quality metadata. Layer boundaries. Conformance tests" as a governed change to a hash-pinned spec — for a project you describe as experimentation. And ZMeta's own §2.6 argues against it: "Core semantic changes SHOULD NOT be accepted unless there is an observed implementation failure… that cannot be solved through policy, profiles, adapters, governed extension branches, conformance classes, or mission-specific logic." Person-centric OSINT is a new data class, not an ambiguity in an existing one. ZMeta's governance says: build it beside, not inside. (d) throws away the 80% that already fits.

The decisive finding, and the one I expected to go the other way: **ZMeta is not geospatially biased at the envelope.** Zero of the four required top-level fields is spatial. `ObservationPayload` requires only `["modality","features"]`. `InferencePayload` has *no geo field at all* and requires `["inference_type","claim","model","based_on"]` — so "these two handles are one person, model `handle-match@2.1`, confidence 0.4, based_on [obs1, obs2]" is a **native, unforced shape**. `FusionPayload` requires `["track_id","members","stability","last_seen_ts"]` with geo only inside an optional `estimated_state` — PLAINSIGHT's CLUSTER maps field-for-field. And positionlessness is a shipped, tested case, not a degradation: `adapters/ingress/adsb/README.md` lists "Mode S only, no position | a real detection of a real emitter, positionless."

**ZMeta is the wrong carrier only because its observation vocabulary is locked and closed.** That is a narrow, fixable-by-fork problem, and it means the fork keeps almost everything.

**Cost of getting it wrong.** Choosing (a) or (b): you either mint an illegal `modality` token and create the private dialect `AGENTS.md` exists to prevent — poisoning ZMeta conformance for the whole program — or you spend months in governance for a model you may throw away. Choosing (d): you re-derive layer separation, recursive denylists, confidence prohibition, typed lineage, and the conformance ladder, badly, and end up unable to reason about the two models together. Choosing (c) *without saying so in writing*: in eighteen months nobody can tell which fields mean the same thing in both models, which is the worst outcome of all. **The document that records the divergence is part of the decision, not an artifact of it.**

### D2 — Is the selector vocabulary closed, and are its names semantically qualified at the extract boundary?

**Recommendation: yes to both, and this is the decision I would most defend.**

ZMeta's sharpest residue class is "datum-unlabeled plausible values":

> "A wrong-datum altitude is present, finite, in range, and plausible, so it passes schema validation, plausibility bands, and every anti-zero-fill guard: all of those key on absence, and this value is not absent, it is wrong… The only guard that works is naming the datum at the decode boundary (`alt_hae_m` vs `alt_msl_m`) so that a value of unproven datum structurally cannot reach the canonical field… never map by name similarity."

The OSINT isomorph is exact. Toutatis returns a masked recovery hint. PLAINSIGHT's manifest annotates it `fp_mode: "platform returns recovery hint for a LINKED account, not necessarily owner"`. **That is a comment, and a comment does not hold.** The field must be named `email_hint_recovery_masked`, never `email`, so a value of unproven semantics *structurally cannot* reach the canonical field an analyst reads as "this person's email." Same for `phone_hint` vs `phone`, `handle` vs `platform_uid` (§2.2 of the design already got there independently), `asserted_at` vs `observed_at`, and `email_generated_permutation` vs `email`.

**Closed** means: a connector emitting a selector type not in the registry is refused at the manifest gate, and PLAINSIGHT §6.5 step 4 already has the flow — map to an existing selector, propose an ontology addition (reviewed once, benefits all connectors), or park in the raw pane.

**Cost of getting it wrong.** An open or loosely-named vocabulary is not a schema problem, it is a *findings* problem: a masked recovery hint reaching a field called `email` will produce a dossier line an analyst reads as an established fact, and it will be wrong in a way no validator can catch — every guard in the system keys on absence, and this value is present. Retrofitting means rewriting every adapter and re-adjudicating every claim already extracted.

### D3 — Append-only on the wire, or mutable rows?

`review_state (unreviewed | verified | disputed)` is a column on CLAIM in PLAINSIGHT §2.1. ZMeta §4.2 forbids modifying an emitted event and lists the immutable fields.

**Recommendation: append-only adjudication events on the wire; `review_state` as a materialized projection over the latest adjudication in the read model.** This is ZMeta's own carve-out — "Profile exports MAY be represented as projections of the same event" — and it matches PLAINSIGHT §8.3's existing split (append-only log for `{runs, items, claims, inferences, dispositions, exclusions, notes, questions, revocations}`; plain mutable KV for workspace state).

**Cost of getting it wrong.** Mutable `review_state` means "who verified this, when, and on what basis" is destroyed by the next edit — which is precisely the audit trail adjudication-on-citation exists to produce. §2.1 already names Run→Item→Claim as "the single most expensive thing to retrofit"; this is the same class of decision on the same table.

### D4 — Is retention a mechanism or a sentence?

**Recommendation: per-case crypto-shred, from the first blob written, with `retain_until` as a column that a scheduled job acts on.**

Concretely:
1. Every blob under a case is encrypted with a per-case data key; case keys are wrapped by a vault key. Deleting one case key renders every blob for that case unreadable in a single atomic act — regardless of MinIO replicas, snapshots, backups, or page cache, all of which defeat `rm`. Field-capture already names this property as its worst risk: "losing them makes every stored specimen permanently unreadable." **One key per case converts that liability into the deletion mechanism**, and it is the only way "deleted" is verifiable for data you cannot enumerate every copy of.
2. `retain_until` is a column. Expiry without an explicit extension — carrying an author, a timestamp, and a reason, the same shape §5.5 already demands for a cluster assertion — shreds the case key. **Extension is an analyst act in the audit log; inaction is deletion.** Field-capture's default is the opposite, which is exactly why 339 MB is still on that disk.
3. Shred leaves the skeleton: runs/items/claims survive as structure with `▨ case material shredded 2026-11-04 · purpose served`, in the existing hatch channel. This is what lets "the record that an experiment happened and what it concluded remains auditable" and "the PII it ran on no longer exists" both be true.
4. Verify the shred from outside the tool that performed it: attempt a real decrypt of a known blob and *require failure*; check absence over the S3 endpoint. Never a DELETE's exit code, never a cached read — "A check that can pass for a reason other than the one claimed is not a check."
5. Bidirectional reconcile on a schedule that runs.

**This must be decided before the first blob is written, because unencrypted blobs cannot be retroactively crypto-shredded.** That is the whole reason it is on this list.

**Cost of getting it wrong.** The operator's stated posture — "retained data exists only to enable internal experimentation, is deleted once its purpose is served" — becomes a sentence with no code behind it, exactly as tier 1 is today. And note that PLAINSIGHT §5.7's current rule is `retain: {text: forever, media: 90d}`. `text: forever` is in direct tension with the stated posture when the text is a person's bio, follower list, and message history. **That conflict is live and should be resolved deliberately, not quietly.** My reading: `text: forever` is correct *within* a case's `retain_until`, and wrong as an absolute.

### D5 — Where does the subject gate sit, and how many values does it return?

**Recommendation: inside the runner, between pivot-selection and argv construction, before `lineage.command_template` is filled and before any credential is drawn from a pool. Three-valued: `permitted | requires_extension | refused`.**

There is already an ideal hook: **`motivated_by` on every run** (§8.2 item 3 — "Case-scoped, never scan-scoped, with `motivated_by` on every run. The pivot chain *is* lineage"). Every run already carries the claim that motivated it, which is exactly the provenance a scope check needs to answer "is this selector inside the case's authorization, or is this a pivot that enlarged it?" **Scope-drift detection falls out of the pivot chain for free** — the one place where PLAINSIGHT's existing structure is better suited to the person problem than zisr-recon's is to the host problem.

**Cost of getting it wrong.** A gate the analyst consults rather than passes through is reassurance without protection, and it will be discovered the first time a pivot chain walks three hops from the seed into somebody who was never in scope. Retrofitting a gate onto a dispatch path that already has fifteen call sites is how you end up with fourteen gated ones.

**Not on this list, deliberately:** connector governance (§6.4 already cut it to one CI check — keep that), GRAPH, the keymap, hypothesis forks, and every UI question except the one in §5. Those are recoverable.

---

# 4. The standardization layer

How heterogeneous OSINT tool I/O becomes one interoperable standard. Four artifacts: the **selector vocabulary**, the **PSE envelope**, the **connector manifest**, and the **conformance ladder**.

## 4.1 The selector vocabulary — closed, typed, semantically qualified

```yaml
# ontology/selectors.yaml — the closed registry. A connector emitting a type
# not in here is refused at manifest validation. Additions are reviewed once
# and benefit every connector (PLAINSIGHT §6.5 step 4).

selectors:
  # ── ANCHORS: stable, platform-issued, safe to key an entity on ────────────
  platform_uid:
    form: "platform_uid:<platform>/<opaque_id>"
    stability: stable
    may_anchor_entity: true
    note: "The ONLY selector class an Account entity may be anchored on."

  # ── HANDLES: time-bounded, reassignable, MAY NOT anchor ───────────────────
  handle:
    form: "handle:<platform>/<string>"
    stability: reassignable
    may_anchor_entity: false          # structural. §2.2.
    requires: [valid_from, valid_to]  # a handle claim is an interval, not a value

  # ── CONSTRAINTS OVER A SPACE, NOT VALUES IN IT ────────────────────────────
  email_hint_recovery_masked:
    form: "email_hint_recovery_masked:<mask>"
    constraint_semantics: prefix_suffix_mask
    matcher: hints.email.v1           # library + fixtures, never a manifest enum
    resolves_to: email                # a RELATION, never an assignment
    fp_mode: "platform returns the hint for a LINKED account, not necessarily owner"
    may_anchor_entity: false
    may_be_cited_as: email            # false — see prohibitions
  phone_hint_recovery_masked:
    form: "phone_hint_recovery_masked:<mask>"
    constraint_semantics: suffix_mask
    matcher: hints.phone.v1
    resolves_to: phone

  # ── GENERATED: never observed. provenance is permanent. ───────────────────
  email_generated_permutation:
    form: "email_generated_permutation:<addr>"
    generation_method: format_permutation
    provenance_state: GENERATED       # permanent until an explicit promotion act
    requires_validation_by: [smtp_probe, breach_corpus_match]
    may_anchor_entity: false
    circularity_class: derived_from_name   # read by the merge circularity check

  # ── OBSERVED VALUES ───────────────────────────────────────────────────────
  email:        { form: "email:<addr>",           may_anchor_entity: false }
  phone:        { form: "phone:<e164>",           may_anchor_entity: false }
  person_name:  { form: "person_name:<string>",   may_anchor_entity: false }
  org_name:     { form: "org_name:<string>",      may_anchor_entity: false }
  channel:      { form: "channel:<platform>/<id>",may_anchor_entity: true  }
  domain:       { form: "domain:<fqdn>",          may_anchor_entity: false }
  geo_area:     { form: "geo_area:<bbox|polygon>",may_anchor_entity: false }
  time_window:  { form: "time_window:<iso8601/iso8601>" }
  image_phash:  { form: "image_phash:<hex64>",    may_anchor_entity: false }

prohibitions:
  # A hint selector may never be rendered, exported, or cited under the name
  # of the value it constrains. Enforced at the render slot and the export
  # boundary, not by convention.
  - selector: email_hint_recovery_masked
    must_not_render_as: email
    must_not_satisfy_citation_for: email
  - selector: email_generated_permutation
    must_not_satisfy_citation_for: email
    unless: promoted_by_analyst_act
```

**Entity types** (closed, same file): `Account` (anchored `platform_uid`), `PersonCandidate`, `Org`, `Channel`, `Place`, `Media`, `ManualTask`. A `PersonCandidate` is materialized only by an analyst act — never by a connector, never by a hit with no uid. `AUTHORING.md`'s Identity Gate names the failure exactly: "Inventing a fake per-detection identity to force the reference projector is the one option that is always wrong: it mints tracks nothing observed."

## 4.2 The PSE envelope

```jsonc
{
  "$id": "https://zisr.local/schema/pse-event-1.0.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PLAINSIGHT Semantic Envelope 1.0",
  "description": "Derived from zmeta-event-1.0. Divergences are documented in FOUNDATION §2.1 and §4.2. This is NOT ZMeta and MUST NOT be validated as ZMeta.",
  "type": "object",
  "required": ["pse_version", "derived_from", "case_id", "event", "source", "payload"],
  "additionalProperties": false,

  "properties": {
    "pse_version":  { "const": "1.0" },
    "derived_from": { "const": "zmeta-event-1.0" },

    // DIVERGENCE 1 from ZMeta: case_id is REQUIRED at the envelope.
    // ZMeta has no container object. PLAINSIGHT §8.2 item 3 makes case scope
    // non-negotiable, and D4 makes case_id the crypto-shred key selector.
    // Nothing exists outside a case, so nothing may be emitted without one.
    "case_id": { "$ref": "#/$defs/uuid7" },

    "event": {
      "type": "object",
      "required": ["event_id", "event_type", "event_subtype", "ts"],
      "additionalProperties": false,
      "properties": {
        "event_id": { "$ref": "#/$defs/uuid7" },
        "event_type": {
          // DIVERGENCE 2: ZMeta's six sensor-layer types, retokenized.
          // The MECHANISM is unchanged: locked enum + payload discriminator
          // that must match + per-type required/prohibited envelope fields.
          "enum": ["PROBE_EVENT",    // a RUN or an ITEM   — ZMeta OBSERVATION
                   "EXTRACT_EVENT",  // a CLAIM            — ZMeta OBSERVATION
                   "LINK_EVENT",     // proposed same_entity— ZMeta INFERENCE
                   "CLUSTER_EVENT",  // asserted identity  — ZMeta FUSION
                   "EXCLUDE_EVENT",  // affirmative not-the-subject — FUSION
                   "ASSESS_EVENT",   // operator state     — ZMeta STATE, geo OPTIONAL
                   "SYSTEM_EVENT"]
        },
        "event_subtype": { "type": "string" },   // bound per type, and to the
                                                 // payload discriminator, in $defs
        "ts": { "$ref": "#/$defs/utcDateTime" }  // collection time. ALWAYS.
      }
    },

    "source": {
      "type": "object",
      "required": ["platform_id", "node_role", "producer"],
      "additionalProperties": false,
      "properties": {
        "platform_id": { "type": "string" },
        "node_role":   { "enum": ["LOCAL", "RUNNER", "CLOUD"] },  // exposure axis
        "producer":    { "type": "string" },   // connector id; governed wildcards
        "sw_version":  { "type": "string" }
      }
    },

    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "lineage": {
      "type": "object",
      "required": ["based_on"],
      "additionalProperties": false,
      "properties": {
        "based_on":  { "type": "array", "minItems": 1,
                       "items": { "$ref": "#/$defs/uuid7" } },
        "transform": { "type": ["string", "null"] }
        // "translate:<schema_id>@<adapter_version>" — retroactive invalidation
        // becomes an index scan (PLAINSIGHT §7.5).
      }
    },
    "payload": {}
  },

  "allOf": [
    { "if":  { "properties": { "event": { "properties":
                 { "event_type": { "const": "PROBE_EVENT" } } } } },
      "then": { "properties": { "payload":    { "$ref": "#/$defs/ProbePayload" },
                                "confidence": false } } },
    { "if":  { "properties": { "event": { "properties":
                 { "event_type": { "const": "EXTRACT_EVENT" } } } } },
      "then": { "properties": { "payload":    { "$ref": "#/$defs/ExtractPayload" },
                                "confidence": false } } },
    { "if":  { "properties": { "event": { "properties":
                 { "event_type": { "const": "LINK_EVENT" } } } } },
      "then": { "required": ["confidence", "lineage"],
                "properties": { "payload": { "$ref": "#/$defs/LinkPayload" } } } },
    { "if":  { "properties": { "event": { "properties":
                 { "event_type": { "const": "CLUSTER_EVENT" } } } } },
      "then": { "required": ["lineage"],
                "properties": { "payload": { "$ref": "#/$defs/ClusterPayload" } } } }
  ],

  "$defs": {
    "ExtractPayload": {
      // ONE claim: one field asserted by one item.
      "type": "object",
      "required": ["selector_type", "value", "source_ref", "extractor",
                   "temporal", "negative_state"],
      "additionalProperties": false,
      "properties": {
        "selector_type": { "type": "string" },  // MUST be in ontology/selectors.yaml
        "value":         { "type": ["string", "number", "boolean", "null"] },
        "subject_ref":   { "$ref": "#/$defs/uuid7" },   // the ENTITY this is about
        "source_ref": {
          "type": "object",
          "required": ["item_id", "source_path"],
          "properties": {
            "item_id":     { "$ref": "#/$defs/uuid7" },
            "source_path": { "type": "string" },  // JSON pointer or line no.
            "raw_span":    { "type": ["array", "null"] }  // best-effort; §5.7
          }
        },
        "extractor": {
          "type": "object",
          "required": ["name", "version"],
          "properties": { "name": {}, "version": {} }
        },

        // DIVERGENCE 3: ZMeta's timing_quality, replaced wholesale.
        // Discipline preserved: mandatory, degraded by default, folds
        // field-locally, NEVER repaired when corrupt.
        "temporal": {
          "type": "object",
          "required": ["observed_at", "time_provenance"],
          "additionalProperties": false,
          "properties": {
            "observed_at":     { "$ref": "#/$defs/utcDateTime" },  // when WE saw it
            "asserted_at":     { "oneOf": [{ "$ref": "#/$defs/utcDateTime" },
                                           { "type": "null" }] },  // platform's claim
            "time_provenance": { "enum": ["collection_time", "platform_declared",
                                          "inferred_relative", "absent"] }
          }
        },

        // Four states, stored from v1, rendered as evidence only once
        // always_present is canary-proven (§8.5).
        "negative_state": { "enum": ["present", "attempted_and_absent",
                                     "not_attempted", "attempt_failed"] },

        // Prohibited — recursively — by policy/semantics.yaml.
        "proposes":   false,
        "cluster_id": false,
        "confidence": false,
        "review_state": false      // D3: adjudication is a separate event.
      }
    },

    "LinkPayload": {
      "type": "object",
      "required": ["link_type", "claim", "model", "based_on"],
      "properties": {
        "link_type": { "enum": ["same_entity", "associated_with",
                                "co_located", "controls"] },
        "claim":     { "type": "object",
                       "properties": { "cluster_id": false, "members": false } },
        "model":     { "type": "object",
                       "required": ["name", "version"] },
        "based_on":  { "type": "array", "minItems": 1 },
        "accepted":  { "const": false }   // structural: a LINK is always PROPOSED.
                                          // Acceptance is a CLUSTER_EVENT by a human.
      }
    },

    "ClusterPayload": {
      // ZMeta FusionPayload, field-for-field.
      "type": "object",
      "required": ["cluster_id", "members", "asserted_by", "rationale_codes",
                   "last_supporting_ts"],
      "properties": {
        "cluster_id":         {},
        "members":            { "type": "array", "minItems": 2 },
        "asserted_by":        { "type": "string" },  // from the session. never free text.
        "rationale_codes":    { "type": "array", "minItems": 1 },
        "last_supporting_ts": { "$ref": "#/$defs/utcDateTime" },
        // Per-member seams, always; aggregated never (§8.4).
        "member_seams":       { "type": "object" },
        "confidence":         false     // no rollup. ever.
      }
    },

    "AssessPayload": {
      // DIVERGENCE 4: ZMeta TrackStatePayload requires geo. This does not.
      "type": "object",
      "required": ["subject_ref", "text", "valid_for_ms"],
      "properties": {
        "subject_ref":  {},
        "text":         { "type": "string" },
        "geo":          { "$ref": "#/$defs/geo" },   // OPTIONAL
        "valid_for_ms": { "type": "integer" },
        // ZMeta §7.7 raw-artifact denylist, kept:
        "raw":          false, "features": false, "measurement": false
      }
    }
  }
}
```

**Policy, alongside the schema, in the ZMeta shape:**

```yaml
# policy/semantics.yaml — recursive. Nesting cannot launder a layer violation.
probe_event:
  payload_must_not_contain: [cluster_id, proposes, link_type, confidence, review_state]
extract_event:
  payload_must_not_contain: [cluster_id, members, proposes, confidence, review_state]
link_event:
  payload_must_not_contain: [cluster_id, members, accepted_at, asserted_by]
assess_event:
  payload_must_not_contain: [raw, features, source_path, raw_span, credential_ref]

# policy/lineage.yaml
allowed_parent_event_types:
  EXTRACT_EVENT:  [PROBE_EVENT]
  LINK_EVENT:     [EXTRACT_EVENT]
  CLUSTER_EVENT:  [EXTRACT_EVENT, LINK_EVENT, CLUSTER_EVENT]
  EXCLUDE_EVENT:  [EXTRACT_EVENT, LINK_EVENT]
  ASSESS_EVENT:   [CLUSTER_EVENT, EXCLUDE_EVENT, ASSESS_EVENT]
parent_type_mismatch_mode: reject
payload_based_on_subset_mode: reject

# policy/producer-authority.yaml
producer_wildcards:
  PROBE_EVENT:   ["connector-*"]
  EXTRACT_EVENT: ["connector-*"]
  LINK_EVENT:    ["matcher-*", "connector-*"]     # proposals only
  CLUSTER_EVENT: []    # NO WILDCARD. Named analyst identities only.
  EXCLUDE_EVENT: []    # NO WILDCARD.
# ZMeta: "There is no state-projector wildcard… because an unnamed
# authoritative track is an injection path." Same reasoning, same shape:
# an unnamed identity assertion is the injection path here.
```

That last block is PLAINSIGHT §8.2 item 4 — "Nothing enters FUSION without an analyst act recording author, rationale code, and timestamp" — made structural. A connector *cannot* create a cluster, because it has no producer authority for that event type and the check fires before any semantic validation runs.

## 4.3 The connector manifest — three additions to §6.1

The manifest in PLAINSIGHT §6.1 is already the right artifact. Three blocks are added, each closing a gap this survey found:

```yaml
# ── TARGETING CLASS ── new. step 0 of ADD CONNECTOR, and it is not about the tool.
targeting:
  reaches_beyond_named_selector: true
  bystander_classes:
    - { class: followers,  enumerable: false, disposition: count_only }
    - { class: co_appears_in_media, enumerable: false, disposition: refuse }
  # disposition ∈ retain | count_only | refuse
  # Read by the SubjectGuard at dispatch. A connector that reaches non-subjects
  # with no declared disposition is refused at manifest validation.
  interaction_class: passive_authenticated_read
  # ∈ passive_unauthenticated | passive_authenticated_read | induces_disclosure
  # induces_disclosure is EXCLUDED, not unimplemented. See §2.2.

# ── PURPOSE BINDING ── new. inherits from the case, is not declared per-run.
purpose_binding:
  requires_case_purpose: true
  min_authorization_state: permitted   # permitted | requires_extension

# ── FIELD SEMANTICS ── new. the datum-labelling rule, per emitted field.
emits:
  - selector: email_hint_recovery_masked   # NOT `email`. D2. structural.
    layer: observation
    always_present: true
    constraint_semantics: prefix_suffix_mask
    matcher: hints.email.v1

# ── HEALTH ── extended: refusal fixtures per required input field, not one per connector.
health:
  canaries:
    - { id: known_positive, input: {...}, expect: {...} }
    - { id: known_negative, input: { username: "zzq7x-nonexistent-4471" },
        expect: { event_count: 0, negative_class: account_does_not_exist } }
  refusal_fixtures:            # ZMeta harness rule: one per schema-required field
    - { id: refuse_no_username, input: {}, expect: { event_count: 0 } }
    - { id: refuse_null_uid,    input: { user_id: null }, expect: { event_count: 0 } }
```

`kind` stays the gate: `one_shot | expansion | continuous | reference | geo`. New tools are free; new shapes are a platform release.

## 4.4 The adapter contract — DECLARE / IMPLEMENT / PROVE

**DECLARE.** A `schema_id` (`vendor:<tool>:<version>`), an `ADAPTER_VERSION`, a layer chosen from the §4.2 table ("Emit at the layer that describes what your input is, never the layer you wish it were"), a producer name matching a governed wildcard, and a mapping pack (`pack.json` + `mapping.yaml` + `tests/{input,expected}.json`) that no runtime engine executes — it is reviewed documentation that doubles as conformance evidence.

**IMPLEMENT.** One or more `translate_<subject>` functions, each taking one parsed input object and returning `list[dict]` of PSE events, **or refusing with `[]`/`None` when the input cannot honestly become one**. The `SYSTEM_EVENT`/`SCHEMA_VIOLATION` diagnostic for a refused input is caller-side; the adapter's fail-closed `[]` is what signals the refusal. Error classification returns one of the fixed enum `{ok, empty, throttled(retry_after), auth_failed, blocked, malformed, error}` — adapter code, never a YAML regex (§6.3). **Do NOT guess silently.**

**PROVE.** The five-rung ladder, narrowest first:

```
1. pytest connectors/<id>                                   # colocated unit tests
2. tools/validate.py --file <events>.jsonl --strict         # PSE schema + policy
3. tools/check_ontology.py <events>.jsonl                   # every selector_type is registered
4. tools/validate_connector_conformance.py --fixtures ...   # calls YOUR adapter, incl. event_count:0
5. tools/validate_conformance.py --kernel-gate              # nothing else regressed
```

Rung 4 is what PLAINSIGHT §6.5 step 3 already describes as "Grafana's Test connection with teeth." The fixtures are JSONL, each line lints against a fixture schema so "an unknown expectation key is a caught typo, not a silent no-op." A fixture pins math, presence, absence, and lineage in one object — and `forbidden_paths` is where "this tool has no noise floor, so it must not fabricate one" is enforced. Record/replay cassettes (§6.3) make rung 4 runnable in CI without touching a live platform.

---

# 5. Separate app, mode, or sibling?

**Siblings, sharing a thin token-and-primitives library plus a shared contract vocabulary. Not a mode. Not a monorepo component library.**

**Against a mode inside ZISR COP, the code forbids it before the doctrine does.** `boot()` instantiates Cesium first and hands the adapter to every UI module — `mountAorPanel`, `mountRightRail`, `mountFeedPanel`, and `mountInspector` all take `adapter` or are wired through `adapter.init`'s callbacks, and none of them mean anything without a globe. There is **no view router**: `wireNavTabs()` toggles `mapView.hidden` against a single `placeholderView` containing one `<p>`. Adding a sixth tab that is a whole second application means rebuilding the shell first, which puts the OSINT COP's schedule behind the COP's for no analytic gain.

**And the doctrine forbids it directly.** `ARCHITECTURE.md` §7: "**Share artifacts and contracts, never a codebase.** A shared repo would drag Praesens's validation-plane invariants into the COP and vice versa — the two systems have opposite failure modes and must stay separately deployable." That ruling was made about Praesens vs. ZISR COP, and PLAINSIGHT vs. ZISR COP is the same relationship. No new argument is needed.

Two more reasons the code supplies:

- **The scope objects are different authority classes.** `ECOSYSTEM_CONTRACT` §4: "**An AOR is a scope filter. It is never an authorization object.**" PLAINSIGHT's gate is a person gate — a different class entirely. Folding it into a shell whose scope object is a polygon is a category error at exactly the point this ecosystem is most careful about (invariant 4: authority classes that "never promote into one another by convenience or fallback").
- **The retention regimes conflict, and in the dangerous direction.** ZISR keeps an append-only history ledger and treats temporal queries as first-class. The OSINT COP's retained data is deleted once its purpose is served. Two deletion policies in one codebase is how one of them quietly becomes the other — and given that most of ZISR's honesty machinery is *about* not deleting things, the drift would run toward keeping the PII.

**Against a fully separate app sharing nothing:** the duplication is already measurable *inside one repo* — `el(tag, className, text)` appears verbatim in five files. More seriously, the **honesty vocabulary would drift**. If ZISR says `UNDECLARED` and PLAINSIGHT says `not_attempted` for the same epistemic state, the ecosystem has two words for one fact. That vocabulary is the operator's actual intellectual product across all three systems and is the thing most worth holding constant.

**Share exactly four things:**

1. **`tokens.css`** — surfaces, text, muted, border, `--font-ui`, `--font-mono`, `--space: 8px`, `--radius: 4px`, and the 28px hit-target floor *with its justification* ("text density and hit-target size are independent constraints, never traded against each other"; PLAINSIGHT states the same 28px and never justifies it). **Not** the classification hues, and **not** a shared semantic palette — conflict C1 is real and irreconcilable at token level.
2. **A ~200-line primitives module** — `el()`, `row()`, `chip()`, `collapsiblePanel()`, `sectionHeader()`, `kv()`. The API is already stable because it's already been written five times.
3. **The honesty vocabulary as a shared, tested table** — the `LIFECYCLE_TEXT` pattern promoted to an ecosystem artifact. One closed set of epistemic-state tokens, each carrying its **consequence sentence** ("an operator cannot act on the string 'forgotten'"), backed by `Object.create(null)`, unknown tokens rendered raw, and a test **in each repo** asserting every state its producers can emit has wording at its reader.
4. **The feed/health transport contract** — `GET /feed` + `GET /events` SSE with event names `feed` and `health`, `relay_connected`, `last_rebuild.status`, and the 3×-heartbeat silence rule. PLAINSIGHT's connector runners serve this shape and inherit the degraded-banner logic nearly unchanged.

Share nothing else. Specifically not the Cesium adapter, the entity model, the AOR machinery, the auth model, the storage layer, or a build system.

**Mechanism: vendor, don't package.** `ARCHITECTURE.md` §7 already lists the discipline — "`app/vendor/*/[*]_VENDOR.md`, `.gitattributes -text`. Pin + aggregate hash + upgrade rule." Vendor `zisr-ui` into both repos with a `ZISR_UI_VENDOR.md` pin, so a token change in one app is a deliberate reviewable event in the other rather than silent drift.

**One caveat that constrains the whole plan:** `app/` has no package.json and no build step, and every import is relative. That is what makes the no-CDN, zero-external-calls posture verifiable by inspection. A shared library must not cost it — plain ES modules by relative path, or a vendored copy. An npm package that drags ZISR into a toolchain to match PLAINSIGHT's build is the tail wagging the dog.

**Two collisions to settle before extraction:** `▨` means "absent" in ZISR's confidence fill and "the system does not vouch" in PLAINSIGHT. And ZISR's `hollow` currently carries four meanings (`stale`, `assumed_friend`, `expired`, `unverified affiliation`), disambiguated by exactly PLAINSIGHT's prescribed remedy — an adjacent text token (`[SIM EXPIRED +14m NEUTRAL? NO-PROV CONF?]`). The two designs converged independently, which is good evidence the rule is right; `UIUX_DESIGN.md` §5 just hasn't caught up to its own code.

---

# 6. Build order

## Blocked until a decision above is made

| Cannot start | Blocked on | Why it cannot be retrofitted |
|---|---|---|
| The event schema, every adapter, the validator | **D1** | Every adapter is written against the envelope. |
| `ontology/selectors.yaml`, every `emits:` block, the extract boundary | **D2** | A hint that reached a field named `email` has already produced a wrong finding, and nothing downstream can detect it. |
| The storage layer, `review_state`, the adjudication path | **D3** | §8.2 item 1: retrofitting rewrites every adapter, every lineage path, every stored claim. |
| **The blob store** | **D4** | Unencrypted blobs cannot be retroactively crypto-shredded. This blocks the *first run*. |
| The runner's dispatch path | **D5** | A gate added after fifteen call sites exist will cover fourteen of them. |

## Weeks 0–1 — the decisions, and only the decisions

Write `FOUNDATION.md` (this, ratified), `ontology/selectors.yaml`, `schema/pse-event-1.0.schema.json`, `policy/{semantics,lineage,producer-authority}.yaml`, and `docs/ENTRY_CRITERIA.md` for the person gate — with per-criterion ratification markers, a `## What is explicitly NOT gated` section, and a `[REJECTED READING]` section that starts empty. No application code. This week is cheap and the alternative is expensive.

## Weeks 1–4 — the spine (PLAINSIGHT §8.1, plus four things)

Run/Item/Claim schema. Content-addressed blob store — **encrypted per-case from the first write, with `retain_until` as a column and the shred job stubbed and scheduled from day one**, because a scheduled job that does nothing yet is a mechanism and a comment is not. Runner containers + Postgres job queue. Three connectors, one per shape: toutatis (one_shot), sherlock (one_shot/endpoint), crosslinked (expansion). Manifest schema + validator + HTTP cassettes. Lineage drawer.

Additions to the design's week 1–4:
- **`SubjectGuard` on the dispatch path**, three-valued, refusing everything but self and project-operated personas. ~70 lines, stdlib only, no network, fully testable — and it means weeks 1–13 need no targeting permission at all, which is the whole point of zisr-recon's design.
- **`safe_component()`** on every path built from a selector. Adversary-controlled strings.
- **Rung 4 conformance harness** with `event_count: 0` refusal fixtures per required input field.
- **The reconcile job**, bidirectional, scheduled, flagging every blob whose case is past `retain_until` and every case row pointing at blobs already gone.

Nothing is visible except a lineage drawer and a table. That is correct.

## Weeks 5–8 — triage

STREAM with facets and FTS. Arrivals rail. Pivot Bar generated from manifests — **with the guard's three states rendered on the pivot menu**, so `requires_extension` is visible before the click, not after. RUNS strip. Recipes. First point the product is worth using; put it in front of a user here.

## Weeks 9–13 — the picture

DOSSIER with four layer bands. Merge Sheet with the four mandatory evidence-gate elements from `UIUX_DESIGN.md` §6 (session identity, evidence selected from actual history, explicit acknowledgment, audit record written *before* the act). Clusters-as-lenses, free split, circularity check. Exclusions. informer with coverage-proof polling, watchdog, tripwires. CHRONOLOGY.

## Weeks 14–18 — honesty and handoff

COLLECTION board with the five states written as consequences, not tokens. Re-run + diff. Impact review. DRAFT with live citation chips and export-boundary enforcement — **now doing two jobs: citation completeness and data minimization**. MAP (thin, no Cesium). Return Brief. Open Questions. Handoff packet. `zisr-ui` extraction.

## What is genuinely undecided, and should stay that way for now

- **The person-NEVER list's contents.** The *ordering discipline* (hard refusals before any config lookup, with a test proving a present authorization file does not unlock them) transfers today. What is on the list requires the operator, and stop-and-escalate-on-indicator is a mechanism that must be built new — a pre-filter is logically impossible.
- **The interaction line.** "No contact, no induced disclosure, no access to content not visible to an ordinary authenticated viewer" is my draft, not a ratified rule, and it is blurrier than the `Van Buren` line it replaces.
- **Bystander disposition beyond `count_only | refuse`.** The manifest field is designed; the operator flow that resolves a `requires_extension` is not.
- **`text: forever` vs. the stated posture.** I read it as correct *within* a case's `retain_until` and wrong as an absolute. That is a live conflict between the design as written and the operator's own framing, and it should be settled explicitly rather than absorbed.

---

**Files cited.** `Z-ISR/PLAINSIGHT-design.md` · `Z-ISR/OSINT-COP-tool-review.md` · `ZMeta/Documentation/zmeta-event-1.0.schema.json` · `ZMeta/Documentation/zmeta-translator-adapter-contract.md` · `ZMeta/Documentation/zmeta-to-cot-mapping.md` · `ZMeta/zmeta-spec/spec/semantics-contract.md` · `ZMeta/zmeta-spec/adapters/{AUTHORING.md,README.md,ingress/adsb/README.md,ingress/template/README.md}` · `ZMeta/zmeta-spec/policy/{semantics,lineage,roles,producer-authority}.yaml` · `ZMeta/zmeta-spec/conformance/adapter-harness/must-pass.jsonl` · `ZMeta/zmeta-spec/AGENTS.md` · `ZMeta/zmeta-field-capture/{RETENTION.md,evidence-registry.md,evidence_common.py,mint_evidence.py,upload_evidence.py,reconcile_evidence.py,capture_server.py,test_ring.py,r2_s3.py}` and `pulled/20260815T003547Z/{pull_record.json,verify.txt}` · `zisr-recon/{README.md,docs/ENTRY_CRITERIA.md,config/own-hosts.allow,src/zisr_recon/{guard,classify,parse,cli}.py,tests/test_recon.py}` · `ZISR COP/docs/{UIUX_DESIGN.md,ARCHITECTURE.md,ECOSYSTEM_CONTRACT.md,SYMBOLOGY_REVIEW_2026-08-26.md}` · `ZISR COP/app/{index.html,styles.css,src/config.js,src/main.js,src/render/cesium_adapter.js,src/ui/{inspector,feed_panel,aor_panel,right_rail}.js,src/data/live_feed.js}` · `ZISR COP/tools/bridge/README.md` · `Z-ISR/Sherlock/sherlock/CAPABILITIES.md`