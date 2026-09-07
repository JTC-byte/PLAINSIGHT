# PLAINSIGHT worklog archive

Entries moved here from `docs/plainsight_worklog.md` when adding one would have
taken it past its cap of ten live entries, oldest first, without edit. A process record is never
restyled, and the live worklog's header states the rules both files follow,
including that neither may quote a case, a selector value, a handle, a subject
name, or a finding about a person.

---

## 2026-08-26, Wave 0. Repository cut.

**Class:** A (documentation) plus F (doctrine skeleton, unratified, binding
nothing).

Cut `plainsight/` beside `ZMeta/` and `zisr-recon/` under `Z-ISR/`. Created the
directory tree from `docs/THE-GAMEPLAN.md` §1.2, including the empty lanes
`connectors/`, `runner/`, `app/`, and `synthetic/`.

Copied in unchanged: `DOCUMENT_STANDARD.md`, `PLAINSIGHT-design.md`,
`PLAINSIGHT-FOUNDATION.md`, `OSINT-COP-tool-review.md`, `THE-GAMEPLAN.md`. The
originals remain at the `Z-ISR/` root and are byte-identical. See D-002.
`PLAINSIGHT-FOUNDATION.md` keeps its DRAFT status header. Stamping it is Step 2
and is the operator's act. Editing that line before the stamp would be the
half-stamping `zisr-recon/docs/ENTRY_CRITERIA.md` warns about.

Wrote `CLAUDE.md`, advisory: North Star, eight-rank authority order with the
argument for doctrine outranking the semantic contract, eight design gates, two
voice registers, attribution.

Wrote `AGENTS.md`, normative: dialect declaration with the licensing clause from
`ZMeta/zmeta-spec/AGENTS.md` quoted exactly, change classes A through F with F
new and defined by effect rather than path, Execution Limits, required local
workflow, documentation matrix, ratification rule.

Wrote `doctrine/DOCTRINE_STATUS.md` with sixteen items pending, zero ratified,
and three rejected readings recorded so they are not re-derived.

Installed `.githooks/pre-commit` calling `tools/validate_retention.py
--repo-scan --staged`, and set `core.hooksPath`. The tool is a stub that exits 0
and prints that it checked nothing. Replaced at Step 8.

**Refused this session:** nothing was collected, no connector was executed, no
platform was touched. No file in the repository contains a selector belonging to
a natural person.

**Not done, deliberately:** no commit was made. `CLAUDE.md` §5 carries ZMeta's
human-only attribution rule pending R6, and the first commit is the operator's.

### Deferred issue register

- **D-001** `tools/validate_retention.py --repo-scan` is a stub. Real
  implementation is Step 8. Until then the pre-commit hook is a wired mechanism
  with no check behind it. This is a known gap, not an oversight.
- **D-002** Five documents exist twice, byte-identical, at the `Z-ISR/` root and
  under `plainsight/docs/`. The repository copy is canonical. Two copies of a
  governed document is the drift condition this framework exists to prevent, and
  the originals predate the repository so deleting them is the operator's call.
  Resolution is one of: delete the root copies, or replace them with a one-line
  pointer to the repository path. Not urgent, and it gets worse the first time
  one copy is edited.

### Closeout, same session

Added `README.md` as the cold-start entry point, naming the read order and the
three rules that bind before any doctrine is ratified. Corrected the wording
above from "moved in" to "copied in", which is what actually happened.

Session context that lives outside this repository and is not reproducible from
it is listed in `plainsight_handoff.md` section 6.

**Next:** Step 2. The operator stamps or amends D1 through D5 in
`doctrine/DOCTRINE_STATUS.md`.

---

## 2026-08-26, Step 3. Doctrine drafted. Not ratified, not finished.

**Class:** F (doctrine drafts, unratified, binding nothing) plus A (process
records). Drafting Class F is permitted and expected. Nothing was landed.

New session rooted at `plainsight/`, cold-started from `README.md`. Harvested
the Wave 0 origin session in full: transcript
`b94b0c75-dfa8-4ed6-b1e6-6854a95710d6.jsonl` under the `Z-ISR/Sherlock` project
directory, 3.4 MB, 1,070 records, 9 operator prompts, 2026-08-19 to 2026-08-26.

Step 2 was not touched. It is the operator's act.

Drafted `doctrine/SUBJECT_SELECTION.md`, fifteen criteria SS-1 through SS-15,
and `doctrine/RETENTION.md`, seventeen criteria RT-1 through RT-17. Both carry
the `ENTRY_CRITERIA.md` header pattern: DRAFTED, AWAITING RATIFICATION, nothing
binds, per-criterion markers with conclusion and basis stamped separately. Both
carry a `## What is explicitly NOT gated` section and a rejected-readings
section.

**One deviation from the Step 3 done-condition, stated rather than quiet.**
`docs/THE-GAMEPLAN.md` §3.1 requires the rejected-readings section to start
empty. Both files start it populated instead. §5.4 had already derived and
rejected the HMAC membership oracle, and `DOCTRINE_STATUS.md` already carries
three rejected readings. An empty section would have discarded work already
done. The operator can refuse this reading.

Two citations were verified rather than trusted before being written into a
rank-1 file. `ZISR COP/docs/OPERATIONAL_CONTRACT.md:272` does carry the
prohibition on inferring that a link is fine from the absence of a failure
signal, inside §4, so the RT-12 citation stands. `PLAINSIGHT-design.md:747` is a
connector-manifest `lineage:` field rather than a global storage rule, so it is
already the legal form under RT-8; the flat prose claim at `:648` is the actual
R5 conflict. RT-8 currently names both and is wrong about `:747`.

Ran an adversarial review as a seven-lens workflow with per-lens refutation:
the guard.py defect class, doctrine lane escape, sentence-versus-mechanism,
coverage against the source corpus, cross-document consistency, operator-posture
fidelity including over-restriction as a failure mode, and voice register.

**Stopped at 13 of 14 agents on an approaching usage limit.** All seven attack
lenses completed. Six of seven verification agents completed. Banked result: 123
findings raised, 52 refuted, 28 downgraded, 17 confirmed, 26 unverified because
the seventh verifier did not run. Heavy duplication across lenses, so the
distinct issue count is well below 123.

No findings were applied. Both drafts stand exactly as written, which is the
correct state to pause in: the review is evidence about the drafts, not a
change to them.

**Refused this session:** nothing was collected, no connector was executed, no
platform was touched. No file in the repository contains a selector belonging to
a natural person, re-checked on both new files.

**Not done, deliberately:** no commit. No row added to `DOCTRINE_STATUS.md`,
because the review's confirmed findings include the SS and RT id spaces having
no rows there, and adding rows before the id space settles would create churn in
the pin of record.

### Deferred issue register, additions

- **D-003** The review's confirmed and downgraded findings are unapplied. The
  two blockers are a cross-reference in SS-11 pointing at the wrong RT item, and
  SS-14 item 5 stating in the present tense that it is enforced by a tool that
  is currently the D-001 stub. Findings and the workflow journal are at
  `Z-ISR/_session-artifacts/2026-08-26-plainsight-doctrine-review/`.
- **D-004** 26 findings are unverified. The seventh verification agent did not
  run. They are listed in that same `FINDINGS.md` under UNVERIFIED and must not
  be treated as confirmed.
- **D-002 correction.** The handoff recorded the audited tool clones and the
  Wave 0 workflow journals as not durable and expected to be gone. Both survived
  and were still present on 2026-08-26. Handoff §5 is corrected in this session.

**Next:** apply the confirmed findings, finish the verification of the 26, then
Step 2 remains the operator's.

---

## 2026-08-26, Step 3 continued. Review findings applied.

**Class:** F (doctrine drafts, still unratified) plus A (process records).

Resumed the stopped review workflow from cache. **The seventh verification agent
had not completed when the findings below were applied, so the 26 unverified
findings are still unverified.** They carry no verdict and were not applied. That
is D-004 and it is open.

One consequence to be aware of when that verifier does return: it began reading
the drafts before these edits and will finish after them, so a verdict of
REFUTED from it may mean the finding was already fixed rather than that it was
never real. Read its reasons against the current text, not the verdict alone.

Applied both confirmed blockers and all nine distinct confirmed majors, plus six
findings from the downgraded set that were real on inspection. The full list is
in `plainsight_handoff.md` §4 under D-003. Two of the six downgraded items
changed an obligation rather than a wording, and both are recorded here because
a reader of the drafts will want to know they were added after review rather
than designed in:

- **Class N0 NON-PERSON was added to SS-1.** The class set covered only natural
  persons. CrossLinked's function is to enumerate an organization, and a company
  domain is nobody's personal data, so with no class for it the set either
  silently forbade a wanted capability or forced an analyst to file an
  organization under a person class. N0 authorizes the organization and never its
  members, and it is not self-certifying.
- **The RT-17 freeze is capped at 180 cumulative days.** The drafted version gave
  the freeze an expiry and allowed unlimited renewal, which is the same loophole
  reached one logged act at a time, and it nullified RT-5's ceiling.

`DOCTRINE_STATUS.md` now carries a per-criterion row for all thirty-two Step 3
criteria. Before that, both documents declared their own tables to be an index
into a pin of record that had no rows for them, so no criterion was actually
stampable. Pending count is now 48 of 48, zero ratified. `README.md` and the
handoff counts were corrected from sixteen.

Two citations in the drafts were checked against their sources rather than
trusted. `ZISR COP/docs/OPERATIONAL_CONTRACT.md:272` does carry the prohibition
RT-12 attributes to it. `PLAINSIGHT-design.md:747` is a connector-manifest
`lineage:` field and is already legal under RT-8, so RT-8's action-on-stamping
note was narrowed to the prose claim at `:648`, which is the actual conflict.

One claim was removed rather than supported. A drafted line in RT-15 said the
cast-versus-live distinction was discovered when a Wave 0 sweep flagged the
design's fictional cast. The worklog records no such sweep and the only tool
that could have run one is the D-001 stub, so the line now states the same
requirement as an inference from the files, and says no sweep has been run.

**Refused this session:** nothing collected, no connector executed, no platform
touched. PII sweep re-run over every authored file, clean. Voice gate clean on
all five edited files.

**Not done, deliberately:** no commit, no stamp. The remaining downgraded
findings are wording precision and do not change an obligation.

**Next:** Step 2 is the operator's. Step 4, the synthetic cast, is unblocked and
has lead time that cannot be recovered later.

### Second pass, same session. The seventh verifier returned.

It completed after the entry above was written, so the note above about the 26
unverified findings is superseded rather than wrong: it was true when written.
Final review tally across all fourteen agents: **123 raised, 66 refuted, 5 of
the remaining 26 confirmed, the rest downgraded.** Three of those five
confirmations were findings already fixed in the first pass, and
`doctrine-status-has-no-rows-and-no-machine-form` came back REFUTED because the
verifier read the rows that had been added by then, which is the caveat above
working as intended.

Ten findings were applied in this pass. Four changed an obligation and are
recorded here.

- **The authorization record had no stratum.** It is the one object that
  necessarily carries both a live selector and a named person, since an S1
  consent record names who consented, and the drafted strata table gave it no
  store, no TTL, and no shred path. It is now stratum 1, inside the case
  boundary under the case key, never in the repository. RT-1 is one of the four
  criteria with no later date on which it can be decided, which is what made
  this the pass's one blocker.
- **`verify_shred` check 1 violated the rule printed three lines below it.** The
  drafted check decrypted "a known stratum-0 blob for the case", which check 2
  requires to be gone, so check 1 would have passed on a not-found error while
  reporting that the key had been destroyed. A check that can pass for a reason
  other than the one claimed is not a check, and this one was in the criterion
  that says so. It now runs against a witness ciphertext held outside the
  enumerable delete path, and a not-found, permission-denied, or malformed-input
  result is a verification failure.
- **SS-8's gate fixture could not be built.** It called for a fixture naming a
  "NEVER-listed selector", and no such object exists or may exist, because a
  per-selector never-collect list is exactly what SS-14 item 5 and RT-15 forbid.
  The fixture is now built on a NEVER item the gate can evaluate, and SS-14
  carries a table naming where each of its six items is actually enforced, which
  stops the list reading as six mechanisms when two of them are rules pending
  R7.
- **The RT-17 freeze cap was replaced with a better rule.** The first pass
  capped cumulative freeze time at 180 days. Frozen days now count toward RT-5's
  ceiling instead, so a freeze buys no case more total life than any other case
  gets, and each renewal must name the obligation it serves and an expected
  resolution date. The uncomfortable half is argued in place: if an obligation
  outlives 180 days, this system is the wrong holder of the material.

Also: SS-14 item 3 claimed the system was structurally incapable of mutating a
platform, which it is not, and the vocabulary that would make it so is R7 and is
undrafted. It now carries the conservative reading on the same footing as item 1.
SS-6's dispatch check now covers a credential draw, which it did not.
`purpose` is constrained to a sentence that does not name the subject, because
`RETENTION_LEDGER.md` copies it into a tracked file that survives every shred.

**Refused this session:** nothing collected, no connector executed, no platform
touched. Voice and PII gates clean on all edited files. Cross-references,
criterion counts, and table integrity re-checked mechanically.

**Not done, deliberately:** no commit, no stamp. Eight findings stand refuted and
were not applied. The remaining downgraded items are wording precision.

**Next:** Step 2 is the operator's. Step 4 is unblocked.
