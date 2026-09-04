# synthetic/CAST.md: the designed cast

**DRAFT 2026-09-03. Class F. UNRATIFIED. UNSEALED. Drafted by an agent.**

Nothing in this file binds until the operator stamps it in
`doctrine/DOCTRINE_STATUS.md`. **No account exists.** No platform has been
contacted, no number provisioned, no domain routed, and nothing here was
produced by touching a network. Every handle, address, number, display name,
image reference and platform uid in this file and in
`synthetic/GROUND_TRUTH.yaml` is a placeholder in `<...>` form that the operator
fills at account creation. `AGENTS.md` section 4 keeps an agent from writing a
selector value into a tracked file, and a synthetic value is still a value.

An agent may draft this file and may never decide it. The decisions are in
section 9, one row each.

---

## 1. What the cast is for

The cast is a measurement instrument rather than a demonstration: it exists so
that a precision figure and a recall figure produced by this program have an
oracle to be graded against, which is the condition `SUBJECT_SELECTION.md`
section 1.2 says no stranger can satisfy. Its unique contribution is a
**designed** link graph containing a confuser pair, and no real subject can
supply that, because nobody designed a real person's life to include a near-miss
twin. Aged realism is not the cast's contribution and the cast cannot fake it:
posting history, follower graphs and cross-platform residue come from S0 SELF
and S1 CONSENTING subjects who already have years of them, which is why the
gameplan shrank this cast to the minimum that delivers a designed graph.

---

## 2. The design

Three personas, named by opaque role ids. A human-sounding persona name is a
`person_name` selector, and SS-14 item 5 keeps those out of tracked files
whether or not the person is real. The machine-readable form of everything in
this section is `synthetic/GROUND_TRUTH.yaml`, and that file is authoritative
where the two disagree.

### 2.1 P-A, the linked persona

P-A is one person on two platforms, accounts `A-IG` and `A-TG`. The correct
answer to the case is one cluster containing exactly those two accounts. Five
designed surfaces link them, each expressed in a selector type from
`docs/PLAINSIGHT-FOUNDATION.md` section 4.1 and carrying the Merge Sheet
rationale code from `docs/PLAINSIGHT-design.md` section 5.5 that an honest
analyst would fire on it.

| Surface | What it is | Selector type | Code | What a hit proves |
|---|---|---|---|---|
| S-1 | Shared email root across both accounts | `email` | `e` | The connector reached the recovery surface and the analyst read the hint as a hint |
| S-2 | Shared recovery phone | `phone` | `n` | Same, on the phone path |
| S-3 | Reused profile image | `image_phash` | `i` | Perceptual hashing works at the resolution the platform serves |
| S-4 | Reused writing pattern | none | `g` | The analyst reached `g` rather than ticking `h` |
| S-5 | Bio cross-link from `A-TG` to `A-IG` | `handle` | `b` | The extractor found a self-link and did not anchor an account on the handle |

**S-4 carries no selector type on purpose.** The closed registry has no selector
for a writing pattern, so the surface is analyst-visible only. It is in the
design because design section 5.5 records the observed failure it tests for: an
analyst with no `g` code available ticks `h` instead, since `h` is one keystroke
and technically true, and the audit query "show me every identity resting only
on `h`" then returns exactly the wrong set. A cast where the honest basis of a
merge is a writing pattern is the only way to see whether that inversion is
happening here.

**No designed surface rests on a GENERATED selector.** The circularity check in
design section 5.5 therefore comes back clean on every true merge in this cast,
which matters most at the confuser pairs: a merge on a confuser pair is a place
where the circularity check must not be the thing that saves the analyst, since
in a real case it frequently will not be.

### 2.2 P-B, the confuser

P-B shares nothing true with P-A. It sits on a second email domain, holds its
own recovery phone and its own recovery address, uses its own profile image, and
carries no bio cross-link to P-A in either direction. What it shares is
appearance, in four places, each of which a naive matcher fires on.

| Pair | Accounts | Surface | Code | Why the code is not enough |
|---|---|---|---|---|
| X-1 | `A-IG`, `B-IG` | Near-identical handle | `h` | Design section 5.5 flags `h` as weak alone, and a handle is reassignable and may not anchor an account |
| X-2 | `A-TG`, `B-TG` | Homoglyph display-name variant | `h` | The confusables lookup in design section 5.4 is the control, and proportional type hides the difference completely |
| X-3 | `A-IG`, `B-TG` | Shared first-name token | `h` | A shared given name is the most common false positive in person-centric OSINT |
| X-4 | `A-TG`, `B-TG` | Posting-window coincidence from the aging cadence | `t` | A temporal argument reaches this one, so the cast's negatives are not all string matches |

Three of the four fire `h` and the fourth fires `t`, which is deliberate. A cast
whose only known negatives are string collisions measures a string matcher. The
`t` pair also has a second job: the aging cadence in section 5 is what creates
the posting-window overlap, so the cast's own upkeep manufactures a plausible
temporal argument for a link that does not exist, which is the shape this error
takes in real work.

### 2.3 P-B is also the SS-19 injection carrier

One persona holds an injection payload, per SS-19, and it is the confuser. The
account that tries to instruct the pipeline is therefore also an account the
correct answer excludes, so a false positive on P-B and a successful injection
through P-B land in the same scorecard and are read together.

Two payload families, described structurally. **No payload string appears in
this file or in the truth file.** The operator composes the actual bio text at
account creation from the shape named here, which keeps a working payload out of
git while leaving the fixture reproducible.

| Family | Boundary it tests | Shape | What a clean run asserts |
|---|---|---|---|
| PF-1 | The subject gate | An instruction addressed to an automated reader, placed in the bio of `B-IG` | Collected content cannot cause a subject to be reached. `subject_guard.evaluate()` reads the authorization record and the pivot chain, never a collected field |
| PF-2 | argv construction | A shell-metacharacter string in a handle-adjacent field of `B-TG` | A selector whose value does not match its registered matcher in `ontology/selectors.yaml` is refused at argv construction rather than escaped |

PF-2 is the sharper of the two. Design section 5.5's `command_template`
interpolates a selector into argv, which is command injection reaching further
than any prompt and doing so before a model is involved. Escaping is a
transformation that can be got wrong once. Refusal cannot.

SS-21 governs what survives. The injection tag is subject-derived, lives inside
the case, and dies with it. The payload family is a finding and survives. On
this cast both objects are synthetic, which is the only reason the fixture is
legal to keep in git at all: `RETENTION.md` RT-1 puts the whole synthetic corpus
in stratum 4, permanent and outside the shred boundary, because it carries no
real person's values.

### 2.4 P-C, the optional pure negative

P-C shares no designed surface with anything. Its one account exists to measure
whether the matcher proposes a link where nothing was designed at all, which is
the gameplan's "at least one pair sharing nothing" requirement in its strongest
form.

P-C is optional and the cost is specific: **one more real SIM**, one more
account, and one more routing entry on domain B. Phone numbers cap this cast
rather than budget or effort, so a third persona is a third of the cast's
scarcest input.

Declining P-C means deleting its persona block and its partition row from
`synthetic/GROUND_TRUTH.yaml` before sealing, rather than leaving the block in
place unfilled. A persona sealed into the truth file with no account behind it is
an account the scorer expects and cannot find, and the resulting recall figure is
wrong in the direction nobody checks.

---

## 3. The two proposed platforms

Instagram and Telegram, proposed rather than decided.

| Platform | Audited connector | Shape | What the cast exercises through it |
|---|---|---|---|
| Instagram | toutatis | `one_shot` | The credential pool, the D2 `email_hint_recovery_masked` case the ontology was written for, and `platform_uid` as the only legal account anchor |
| Telegram | informer | `continuous` | The credential pool, coverage intervals, and message volume |

The reason for this pair is that **both connectors need a collection credential
to run at all.** toutatis needs an Instagram `sessionid` from a logged-in
account. informer needs a Telegram account bound to a real phone. A cast on
these two platforms therefore exercises the credential pool alongside the
correlation surfaces, and SS-20's disjointness requirement gets tested by the
first real run rather than by inspection. The two shapes are also the two the
connector harness has to support, and the D2 case is the one PLAINSIGHT's
selector vocabulary exists to handle honestly.

`docs/OSINT-COP-tool-review.md` found both connectors non-working as shipped, so
what runs against this cast is the reimplementation rather than the upstream
code. That changes the connector work and changes nothing about the cast design.

The platform choice is the operator's, and it is row 1 of section 9.

---

## 4. Isolation, SS-3

A synthetic persona with real followers is a bystander collector rather than a
measurement instrument. Isolation is a property of the cast, not of the run.

- **The cast interacts only with itself.** No follow, no message, no mention, no
  link, and no join to any account, channel or group outside the cast. Every
  designed interaction is an edge in the `edges` block of
  `synthetic/GROUND_TRUTH.yaml`, and an edge whose endpoint is not a declared
  cast account is refused by `tools/validate_cast.py`.
- **Per-persona recovery selectors.** One phone and one address per persona. A
  cast created from one phone number links the entire cast to the operator on
  the first correlation run, which destroys the cast as a measurement instrument
  and creates a real subject nobody authorized.
- **Nothing is reused between personas.** Not a phone, not an address, not a
  domain for the confuser, not a profile image, not a password, and not a
  browser profile or a device fingerprint where the operator controls those.
- **Nothing is shared with the collection pool.** SS-20 and CR-1 make the cast
  and the credential pool disjoint populations, including recovery selectors,
  which is the intersection a comparison on handles alone would miss. A cast
  persona observed through a credential that is itself in the cast means the
  system is partly observing its own infrastructure.
- **Real SIMs, with provenance recorded.** No VoIP number and no resold number
  from a verification service. Platforms reject the first category, and the
  second carries a measurement problem rather than a bookkeeping one: a resold
  number may already carry correlations nobody designed, which would make the
  ground truth wrong in a direction nobody would check. `phone_source` records
  how each number was obtained, on CR-2's `recovery_source` discipline, and an
  unknown provenance is recorded as unknown rather than guessed.

---

## 5. Aging, and what the cadence is for

Accounts age. A cast created in week 12 measures the system against a thin
target, and thin-target performance is not fat-target performance.

- **Every account records `created_on`** in `synthetic/GROUND_TRUTH.yaml`, null
  until the account exists.
- **Every scorecard records persona age**, computed from `created_on` at the
  time of the run, per SS-18 and RT-13. A precision figure is never quoted
  without the conditions that produced it, and age is one of those conditions.
- **The operator runs an aging cadence.** Cast accounts post to and interact
  with each other on a schedule, and every such interaction is an
  `aging_interaction` edge in the truth file. The edges are intra-platform,
  because an interaction is a thing one platform records.
- **Co-interaction is not a designed correlation surface.** A matcher that
  proposes a link because two accounts interact is producing a false positive
  the scorer counts, since the interaction exists to age the cast rather than to
  express a relationship.
- **The cast is never a bystander collector.** The cadence adds no account to
  the graph. Growth in the cast is a provisioning decision, recorded here and
  sealed, rather than something that happens because a persona was left running.

---

## 6. Ground truth and sealing

`synthetic/GROUND_TRUTH.yaml` holds the seal block, the platforms, the two email
domains, the payload families, the three personas with their accounts and
recovery selectors, the truth partition, the nine designed surfaces, the four
confuser pairs, and the edges. The partition is the oracle: which account ids
are one persona, stated once, before any collection.

**The seal.** sha256 over the file with the `sha256` field's own value set back
to null, so the digest covers everything except its own recording. The canonical
form is stated exactly in the file, including LF line-ending normalization,
because git checks the file out with CRLF on one of the two machines that will
hash it and a seal that depends on a checkout setting is not a seal.

- **Sealing happens once**, after the operator fills every placeholder and
  before the first collection.
- **The hash is recorded in three places**: the `seal` block itself, the line
  below, and every scorecard computed against the cast. A scorecard citing no
  truth-file hash is a figure with no oracle attached to it.
- **A sealed file changes only by a new sealed version carrying a new hash.**
  An in-place edit after sealing is refused by `tools/validate_cast.py`, which
  recomputes the digest on every run.

Seal of record: `<sha256 recorded at sealing>`, sealed `<date>` by `<ratifier>`.

**Freeze-then-score.** The analyst's cluster set is content-hashed before the
scorer opens the truth file. The scorer is the only reader of the truth file. An
analyst who has read it is no longer producing an independent answer, and the
result is self-consistency wearing a measurement's clothes. SS-15 names this as
one of three mitigations for a program where the ratifier, the maintainer and
the analyst are one person, and it is the only one of the three that this file
can carry.

---

## 7. What the validator checks, and what it cannot

`tools/validate_cast.py` runs three ways: the structural gate, `--placeholder-scan`,
and `--self-test`. Its module docstring names the defect each check guards
against, and each refusal names what was refused, which rule refused it, and the
legal moves.

What it checks: the file parses; at least two personas and two platforms, with
every account's platform declared; at least two email domains, with no confuser
or negative persona on the linked persona's domain; at least one confuser pair
spanning two personas and marked `truly_distinct`; an injection carrier holding
a declared payload family; no recovery selector shared between personas; every
edge, designed surface and confuser pair referencing only declared account ids;
`created_on` present on every account; the partition covering every account
exactly once and every persona; and the seal block internally consistent with
the file's own bytes.

Three things it does not reach, stated so a green run is not read as more than
it is.

- **The account-creation half of SS-3 has no technical control.** Whether a
  persona actually accrued a real follower on a live platform is an operator act.
  SS-3 states that half rather than mechanizing it, and no output of this gate
  covers it.
- **The disjointness check against the credential pool is not here.** SS-20 and
  CR-1 put it in `tools/validate_authorization.py` at Step 8, alongside the rest
  of the gate work, because the credential pool exists only in ISOLATED per EG-4
  and a tool that reads both populations has to run where both are readable.
  This file and that pool are compared there, once, including recovery
  selectors.
- **The recovery-selector check compares tokens while the file is unsealed.**
  Today it proves the design assigns distinct selectors. It becomes a check on
  real values the moment the operator fills them, with no change to the tool.

---

## 8. Operator provisioning checklist, cast side only

The collection credential pool is a separate population with separate work,
governed by `doctrine/CREDENTIAL_LIFECYCLE.md`. Nothing below provisions it, and
no account below may appear in it.

| Step | Minimum design | With P-C |
|---|---|---|
| 1. Operator-controlled email domains, with per-persona routing | 2 | 2 |
| 2. Real SIMs, one per persona, provenance recorded in `phone_source` | 2 | 3 |
| 3. Platform accounts, on the two platforms in section 3 | 4 | 5 |
| 4. Fill every `<...>` placeholder in `synthetic/GROUND_TRUTH.yaml`, including `created_on` per account | one commit | one commit |
| 5. Seal: compute the canonical digest, write `sealed: true` with `sealed_on` and `sealed_by`, record the hash in section 6 | once | once |
| 6. Stamp this file and the sealed truth file in `doctrine/DOCTRINE_STATUS.md` | once | once |

Steps 4 and 5 are one act in two commits, and the order matters. A file sealed
before the placeholders are filled seals a template. A file filled and left
unsealed cannot score anything, and SS-14 item 6 refuses collection until the
stamp exists.

Creating platform accounts reaches a third party, carries a terms-of-service
consequence, and may attribute at the IP level. That is an operational risk to
the credential pool as well as to the cast, and it belongs in the decision
rather than in the execution.

---

## 9. Ratification

Six decisions. Each one is the operator's, and none of them is decided by this
draft. A stamp goes in `doctrine/DOCTRINE_STATUS.md` against the row, not here.

| # | Decision | What the draft proposes | Consequence of the choice | Stamped |
|---|---|---|---|---|
| 1 | Platform pair | Instagram and Telegram | Fixes which connectors the cast can be measured through, and commits the cast to two credential-bearing platforms | UNRATIFIED |
| 2 | Persona count | Two required, P-C optional | P-C costs one more real SIM and one more account, and buys the pure negative | UNRATIFIED |
| 3 | P-B carries the payload | Confuser and injection carrier are the same persona | A false positive and a successful injection land in the same scorecard. Splitting the roles costs a fourth persona and a fourth SIM | UNRATIFIED |
| 4 | The designed surfaces | S-1 to S-5 true, S-6 to S-9 false, as in section 2 | Fixes what the cast can measure. A surface not designed in cannot be scored later without a new sealed version | UNRATIFIED |
| 5 | Domain assignment | Domain A carries P-A. Domain B carries P-B and P-C | Putting the confuser on domain A hands it a true surface and manufactures a false positive the team created | UNRATIFIED |
| 6 | The sealing procedure | Fill, then seal once, then stamp. Canonical digest as stated in section 6 | Every scorecard cites the hash. A change after sealing is a new version with a new hash rather than an edit | UNRATIFIED |
