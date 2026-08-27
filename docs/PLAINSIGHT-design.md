# PLAINSIGHT
## An OSINT Common Operating Plane — definitive design

---

# 1. The design thesis

**PLAINSIGHT is a case-scoped citation graph with six renderings of it.**

Everything a tool produces lands in the case automatically and immediately, wearing its provenance. Nothing is hidden, nothing is deleted, nothing is silently upgraded. The analyst does not approve data on arrival — approval on arrival is a receipt, not a judgment, and the red team is right that it degenerates into `⇧A` reflex within three days.

**The one organizing idea: adjudication happens at the moment of citation, not the moment of arrival.**

A claim is free to exist, free to be searched, free to be pivoted from. It becomes *load-bearing* only when the analyst uses it for something — as the basis of an identity assertion, as the source of a sentence in the assessment, as the motivation for a pivot. At that instant, and only then, the system stops and makes the analyst look at where it came from. That converts ~400 fake adjudications per case into ~15 real ones, each occurring at the exact moment the analyst has a reason to care, and it makes the audit trail true rather than merely present.

Everything else in this document falls out of that. The layer discipline (OBSERVATION → INFERENCE → FUSION → STATE) is preserved not as a gate on data entry but as a **structural property of the citation chain**: STATE is the assessment text, and every sentence in it walks back through a cluster, through rationale claims, through items, through a run, to argv and raw bytes. The chain is the product. The views are just six ways to look at it.

Second-order commitments that follow:

- **The plane is the case, not a canvas.** Six views, one focus, one selection, one confidence vocabulary. Switching views is free and lossless.
- **The system never prints a number it invented.** No confidence scores, no priors, no weights. It prints facts about provenance: how many tools, whether they were measurably independent, how old, whether the producing endpoint is currently trustworthy, whether anything contradicts it.
- **The system never asserts identity.** Machines propose; only a human with a name and a timestamp merges.
- **One color.** Red means exactly one thing: *the system does not vouch for this*. Everything else is achromatic, textural, or literal text.

---

# 2. The object model, in plain language

Eight nouns. An analyst can hold eight nouns.

| Noun | What the analyst thinks it is | Layer |
|---|---|---|
| **CASE** | The investigation. Everything lives inside one. Nothing exists outside one. | container |
| **SELECTOR** | A typed string you can pivot on: a handle, an email, a phone stub, a company, a bbox, a channel. Selectors are the currency of the whole product. | — |
| **RUN** | One tool invocation, or one open subscription. Has argv, a credential, timestamps, an exit code, and retained raw bytes. | OBSERVATION |
| **ITEM** | One thing that run touched. A single Sherlock probe. A single Telegram message. A single CrossLinked row. A single snap. Items have outcomes: `hit / miss / error / throttled / ambiguous`. | OBSERVATION |
| **CLAIM** | One field asserted by one item. "IG account uid 25025320 has email_hint `j•••••s@gm•••.com`." | OBSERVATION |
| **ENTITY** | An account, a person-candidate, an org, a channel, a place. **Accounts are anchored on `platform_uid`, never on handle.** | OBSERVATION |
| **CLUSTER** | "These accounts are the same person." An analyst assertion with an author, a date, and rationale codes. It *references* accounts; it never absorbs them. | INFERENCE → FUSION |
| **EXCLUSION** | "I looked at this candidate and it is affirmatively not the subject." First-class, with a basis. Survives into the report and the handoff. | FUSION |

Plus two objects that exist purely so the system can be honest, and that the analyst reads constantly without thinking of them as objects:

| **COVERAGE** | An interval saying "we were actually watching target X from T1 to T2, verified." Closed by a watchdog, not by the collector. |
| **CITATION** | The bond between a sentence in DRAFT (or a rationale in a cluster) and the claims that support it. Live, not copy-paste. |

## 2.1 The three-level storage decision (non-negotiable)

The engineer's first finding is correct and it is the single most expensive thing to retrofit. `Run → Item → Claim`, not `Run → Claim`.

```
RUN     argv · tool@version · credential_ref · started · ended · exit
        raw_blob_sha256 · manifest_hash · case_id · motivated_by_claim_id
  └ ITEM      locator (site_id | channel+msg_id | row_ordinal | snap_id)
              raw_span (offset into blob, or own blob ref) · outcome
       └ CLAIM     subject_entity · predicate · value · value_type
                   source_path (jsonpath or line no.) · extractor_version
                   review_state (unreviewed | verified | disputed)
```

Without the ITEM level: you cannot attach per-endpoint health to the specific Sherlock hit that endpoint produced (which kills the entire rot-detection story), informer writes 1KB of run envelope per 200-byte message, and CrossLinked rows have nowhere to hold independent disposition state.

## 2.2 Two model corrections the analyst red team forced

**Accounts anchor on `platform_uid`, not handle.** Handles get released and reassigned. If accounts key on `handle:instagram`, a handle-owner change renders as ordinary drift ("bio changed, follower count changed, email hint absent") when it is actually an identity catastrophe. Toutatis returns `platform_uid`; use it. `handle` becomes a **time-bounded claim**: `@j_voss_88 → uid 25025320, observed 2026-03-11 → 2026-08-26`. A handle-owner change then renders correctly as a *new account object* with a lineage note, which is what it is.

**Every temporal claim carries two timestamps and a provenance enum.**

```
observed_at      when WE saw it. Always trustworthy. Always present.
asserted_at      when the PLATFORM says it happened. Trust varies. Nullable.
time_provenance  collection_time | platform_declared | inferred_relative | absent
```

CHRONOLOGY renders `platform_declared` events on the lane and everything else in a hatched band beneath it. Without this, an analyst runs a posting-hour correlation where one lane is real event times and the other is *scrape* times, gets 0.61, and believes it.

**And: deleted/edited content is a state.** informer holds message versions. A message that existed and no longer does renders struck-through with `WITHDRAWN 2026-08-24 · content retained`. Somebody deleting a message is frequently better intelligence than the message.

---

# 3. The views

Six views. They are indexed by **how a claim can be interrogated**, not by which tool produced it. If an analyst can ever see "the toutatis screen," interoperation has already failed.

| Key | View | Question it answers | Primary object |
|---|---|---|---|
| `1` | **DOSSIER** | What do we hold about this entity, and what is it built on? | Entity / Cluster |
| `2` | **STREAM** | What came back — all of it, faceted, searchable? | Item |
| `3` | **CHRONOLOGY** | What co-occurred, and when were we blind? | Entity × time |
| `4` | **MAP** | Where do the coordinate-bearing minority land, and where did we sweep? | GeoItem |
| `5` | **COLLECTION** | What ran, what broke, what is quietly lying? | Connector / Endpoint / Subscription |
| `6` | **DRAFT** | What am I actually going to say, and can I defend every sentence? | Assessment text |

**GRAPH is not in v1.** See §8. It is replaced by a PATHS list, which answers the only question the graph is good at.

## 3.0 Shell layout, and the collision the lenses left unspecified

The red team caught that the Lineage Drawer and the Arrivals rail both wanted the right side, on the most common action pair in the product (peek an item, then walk its lineage). Resolution:

- **Left rail — ROSTER.** Entities, clusters, exclusions, filters. `[` collapses.
- **Center — the active view.**
- **Right rail — ARRIVALS / INSPECTOR** (tabbed). `]` collapses. Auto-collapses to a tab strip below 1440px viewport width.
- **Bottom — RUNS strip.** One line, always. Expands upward to 5 lines on `Ctrl+R`.
- **LINEAGE opens as a full-width bottom drawer** at 40% height, pushing the RUNS strip to its one-line state. It never covers the Arrivals rail, so you never lose your place in a queue.

Density budget, stated so nobody designs past it: at 1920×1080 with both rails open, the center column is ~780×600px. A claim row is 28px plus an optional 20px provenance sub-line. **That is 18 claim rows visible.** Design for 18.

## 3.1 DOSSIER — the default landing view

**Job:** accumulate and adjudicate claims about one entity or cluster. This is where the work product is made.

**Why it lands here** (and I'll defend it against each alternative):

1. It is the **only view that renders all four layers simultaneously**, stacked vertically — STATE at the top, OBSERVATION at the bottom. Layer discipline is therefore enforced by the default screen rather than by policy, and *scrolling down is literally walking lineage backwards*. That is worth more than any amount of documentation.
2. It is **never empty.** Opening a case instantiates a provisional entity from the seed selector. A username seed → `Person(provisional)`. A CrossLinked company seed → `Org(provisional)` whose candidate band is the 300 employees. Same shell, both cases, first frame.
3. **The alternatives each teach the wrong lesson.** Landing on STREAM teaches "OSINT is a list of hits" and strips results of the entity context that makes them mean anything. Landing on MAP is an empty basemap for ~90% of cases and implies geography is the organizing principle when it is a minority signal. Landing on COLLECTION is infrastructure. Landing on CHRONOLOGY is the closest runner-up, but time is only interesting *after* you have candidate accounts. Landing on a graph teaches "everything is connected," which is the exact false-certainty failure the whole design exists to prevent.
4. **It matches the deliverable.** The output of person-centric OSINT is an adjudicated entity with a defensible basis. The default screen should be the thing you are building, with the evidence beneath it in the order you would defend it.

```
┌ PLAINSIGHT ─ C-2291 "Volga recruiting" ───────────────────────────────── mreid ─ 3d ─┐
│ FOCUS ▸ CLUSTER-004 "J. Voss"  ⌐likely⌐  3 accounts · 1 excluded · 4 open candidates   │
│ SCOPE ⟨none⟩  ·  esc esc clears all scopes            COLLECTION  13 ok  3 SUSPECT  1 DOWN │
├────────────────┬───────────────────────────────────────────────────┬──────────────────┤
│ ROSTER      41 │ 1 DOSSIER │2 STREAM│3 CHRON│4 MAP(3)│5 COLLECT│6 DRAFT│ ARRIVALS  62 ▾│
│                │ contents: focus CLUSTER-004 · no scope filters    │ INSPECTOR        │
│ ⌐ CLUSTER-004◀ │                                                   │──────────────────│
│   ig  25025320 │ ══ STATE ═══════════════════════════════════════  │ 14:22 informer   │
│   re  t2_9x4k1 │  ✔ ASSERTED 08-24 mreid · likely                  │  msg @jv_ ch/9812│
│   tg  99413007 │    IG uid 25025320 ≡ TG uid 99413007 ≡ RE t2_9x4k1│  ▸ tripwire "Volga"│
│   ⊘ EXCLUDED 1 │    rationale  b (bio self-link) · h (handle) · g   │ 14:19 informer   │
│                │    cited by  DRAFT ¶3, ¶7                    [l]  │  join @kmb_ 9812 │
│ ⌐ CLUSTER-007  │                                                   │ 13:58 sherlock   │
│   2 accounts   │  ⊘ EXCLUDED 08-25 mreid                           │  6 hits / 400    │
│                │    @jvossen_real (ig uid 41880212) — homoglyph     │  ⚠ 3 from failing│
│ ▪ ACME Corp    │    impersonation; acct created 2026-07, no overlap │    endpoints     │
│   300 rows     │    basis  claim#4471, claim#4479             [l]  │ 13:41 snapmap    │
│                │                                                   │  3 media, 1 bbox │
│ ● ch/9812  ●LIVE│ ══ FUSION ══════════════════════════════════════  │──────────────────│
│ ● ch/4471  ⚠GAP │  ⌐ CLUSTER-004  asserted mreid 08-24 · reversible │ SINCE YOU LEFT   │
│                │  ┆ ig 25025320  @j_voss_88   seam: b,h            │ 14h 22m          │
│ + add entity   │  ┆ tg 99413007  @jv_         seam: b,h            │ +311 tg msgs     │
│                │  ┆ re t2_9x4k1  /u/j_voss_88 seam: h  ← only basis │ ✕ soig auth fail │
│ ── FILTERS ──  │    per-member seams shown; never rolled up   [m][x]│ ⚠ 2 inferences   │
│ review         │                                                   │   basis unverified│
│  unreviewed 388│ ══ INFERENCE ═══════════ 4 proposals, unaccepted ═ │   19d [re-verify]│
│  verified   15 │  ┄ @jvoss_ (tw uid 8812443) may be same person     │ ⊘ 1 candidate    │
│  disputed    1 │    FOR   handle 6/8 char overlap                   │   reappeared     │
│ source         │          posting-hour overlap (both lanes are      │   (excluded 4d)  │
│  toutatis   8  │          platform_declared — comparison valid)     │──────────────────│
│  soig   ✕DOWN  │    AGAINST  acct created 2013 vs ig 2021           │ [review ▸]       │
│  informer  ●   │             no shared selector of any type         │                  │
│  sherlock 400  │             handle stem is dictionary-common       │                  │
│  crosslinked   │    ⚠ this proposal has never been reviewed   [m][e]│                  │
│  snapmap    3  │                                                   │                  │
│  ✍ manual   4  │ ══ OBSERVATION ═══════════════════ 41 claims ════  │                  │
│                │  email_hint  j•••••s@gm•••.com                 ⧉  │                  │
│                │    2 tools · 1 measured source · 2h · unreviewed   │                  │
│                │  phone_hint  +1 •••-•••-4471                   ⧉  │                  │
│                │    1 tool (soig ran, field absent) · 2h           │                  │
│                │  full_name   "J. Voss"  ⚡ "Jordan Foss"       ⧉  │                  │
│                │    2 tools · 2 measured sources · CONFLICT         │                  │
│                │  geo         41.8827,-87.6233                  ⧉  │                  │
│                │    snapmap · declared ±100m · 2019-06 · 3y ago    │                  │
│  acct_hit    vsco/j_voss_88                     ⧉  │                  │
│    ▨ endpoint known-negative canary FAILING 3d    │                  │
│    ▨ system does not vouch · [triage endpoint ▸]   │                  │
├────────────────┴───────────────────────────────────────────────────┴──────────────────┤
│ RUNS  ▸#0147 sherlock 312/400 ·  ●#0121 informer LIVE gap:0 ·  ✕#0149 soig auth  Ctrl+R│
└───────────────────────────────────────────────────────────────────────────────────────┘
```

**Key interactions**

1. **Cite (`c`)** — the central verb. On any claim, cluster, or item: opens the citation picker and drops a live citation chip into DRAFT at the cursor. **If the cited object is `unreviewed`, an inline review strip appears first** (§4.4). Citation is the moment adjudication becomes real.
2. **Assert identity (`m`)** — opens the Merge Sheet (§5.5). The only modal in the product.
3. **Exclude (`e`)** — the affirmative "this is not them," with a basis. Distinct from ignore. Survives into report and handoff and pre-suppresses the candidate on future sweeps (shown pre-marked, never hidden).
4. **Pivot (`p`)** — §4.
5. **Lineage (`l`)** — bottom drawer, §5.6.

## 3.2 STREAM — high-volume triage and the only full-text search

**Job:** work a queue of hundreds without touching the mouse. This is where Sherlock's 400 probes, CrossLinked's 300 rows, and informer's 3M messages actually get worked.

**Primary object:** ITEM. Not claim, not entity — the raw returned thing.

The left rail is Kibana Discover's field sidebar: every field with value-frequency bars, click to add as column, click to filter. The active filters are **pills** — individually removable, negatable, temporarily disable-able, out of order. Filter state is never invisible.

**Full-text search is a first-class part of this view, not a command-palette afterthought.** The red team is right that message-body search is a fifteen-times-an-hour action. `/` inside STREAM searches item content (Postgres FTS over the partitioned message table), supports regex, auto-highlights registered case selectors, and every result row carries a `→ chron` handle that jumps to its lane position in CHRONOLOGY.

```
┌ 2 STREAM ─────────────────────────────────────────────────────────────────────────────┐
│ contents: 4,102 items ▸ from: search "логистик" + pill[src=informer] + pill[ch=9812]   │
│ ⌕ логистик|logistik                                        [regex] [selectors ON]  ⏎  │
│ ⌫src=informer  ⌫ch/9812  ⌫¬withdrawn         + add filter        snapshot @14:31 ▾14 new│
├──────────────┬────────────────────────────────────────────────────────────────────────┤
│ FIELDS       │  outcome  when              locator          content                  │
│ platform     │  ▸ hit    08-26 14:22 pd    ch9812/m44120    "…логистика через…"   ⧉ │
│  ig     4201 │  ▸ hit    08-26 13:04 pd    ch9812/m44098    "…схема логистик…"    ⧉ │
│  tg  ███ 2904│  ▸ hit    08-24 09:11 pd    ch9812/m43770    [WITHDRAWN 08-24]      ⧉ │
│  li     1102 │      ▨ message existed and was deleted · content retained             │
│  snap    455 │  ▸ hit    08-21 22:40 pd    ch4471/m1188     "…logistik hub…"       ⧉ │
│ outcome      │                                                                        │
│  hit    3891 │ ── 41 items have NO platform-declared time (collection_time only) ──   │
│  miss    350 │  ▸ hit    coll 08-26 13:58  sherlock/vsco    /j_voss_88             ⧉ │
│  error    41 │      ▨ endpoint canary FAILING · not usable as evidence               │
│ review       │                                                                        │
│  unrev  4088 │                                                                        │
│  verif    14 │  j/k move · space peek · p pivot · c cite · e exclude · i ignore · l lin│
└──────────────┴────────────────────────────────────────────────────────────────────────┘
```

**Snapshot rule (states an engineering constraint as a UX law):** every list is a **snapshot** taken when it gained focus. Live arrivals accumulate in a header bar (`▾ 14 new · R to refresh`). The cursor never moves because of a background event. This applies to STREAM, ARRIVALS, CHRONOLOGY lanes, and the ROSTER. Counts may update live — counts don't move anything.

**The Sherlock result renderer**, which is a shape not a tool, and which is where the rot story pays off:

```
┌ RUN #0147 · username.enumerate · "j_voss_88" · 400 probes · 41s ──────────────────────┐
│ ✓ 6 HITS from endpoints whose known-negative canary passed <24h                       │
│     tiktok · github · pinterest · reddit · flickr · about.me           [promote ▸]    │
│                                                                                        │
│ ▨ 3 HITS FROM ENDPOINTS WITH A FAILING KNOWN-NEGATIVE CANARY                          │
│ ▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨ │
│     vsco   canary failing 3d — returns hits for random strings                        │
│     ello   endpoint 404s since 08-19 — probe cannot distinguish                       │
│     tumblr error-signature drift 08-24                                                │
│     these cannot be cited without an override note              [triage endpoints ▸]  │
│                                                                                        │
│ ○ 350 NEGATIVES — usable as absence evidence (canary passed <24h)          [receipt ⧉]│
│ ▨ 41 NEGATIVES — NOT usable. Endpoints unverified 9–22d. Treat as NO INFORMATION.     │
│                                                                             [re-run ▸]│
└───────────────────────────────────────────────────────────────────────────────────────┘
```

Note what is *not* here: no "accept all." A hit is an item. It stays an item, visible and pivotable, until someone **promotes** it to an Account — one at a time or on a filtered multi-select. **Entity creation is always proportional to analyst attention.** `⇧A` on a Sherlock run would create 400 floating Account objects, which is not a cheap action, it is a mess the analyst then has to clean up.

## 3.3 CHRONOLOGY — the cheapest real evidence in the toolset, and the honest-blindness view

**Job:** temporal correlation between candidate accounts, and — equally important — showing when we were *not watching*.

Same handle on two platforms is near-worthless. **Activity-pattern correlation across two accounts is real evidence and no OSINT tool surfaces it.** This view exists mostly for that, and secondarily to make silence legible.

Three mark classes per lane:
- point events (posts, snaps, messages, account creation)
- **coverage bands** — the interval a collector was *verifiably* running against that target
- the **undated band** — a hatched strip below every lane holding items whose `time_provenance` is `collection_time` or `absent`. They are never dropped. Kibana's mandatory time picker silently deleting null-dated records is a filtering violation and it is banned by name.

```
┌ 3 CHRONOLOGY ─────────────────────────────────────────────────────────────────────────┐
│ contents: CLUSTER-004 + 2 candidates · brush ⟨none⟩                                    │
│              2025-11        2025-12        2026-01        2026-02        2026-03        │
│ ig @j_voss_88  ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰  │
│  platform_declared  · ·   ··  ·        ·· ·    ·          ·  ··· ·   ·                │
│  ▨ undated (4)      ▨▨▨▨                                                              │
│                                                                                        │
│ tg @jv_        ░░░NO COVERAGE░░░▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▨GAP:47▨▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰  │
│  platform_declared               ·· ·  ·   ·  ··          ·   ·· ··  ·                │
│    ↑ gap is QUANTIFIED: we hold msg ids 4410-4455, channel max was 4502 = 47 missing   │
│                                                                                        │
│ tw @jvoss_ ┄?┄  ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰  │
│  platform_declared  ·  ·· ·          · ·     ··          ··  ·   ·  ·                 │
│                                                                                        │
│ ═ OVERLAY  ig @j_voss_88 × tw @jvoss_ ══════════════════════════════════════════════  │
│   both lanes are platform_declared — comparison is valid                              │
│   hour-of-day co-occurrence: 0.61 · same statistic on 118 random pairs in this case    │
│   exceeded 0.61 in 34% of cases                                                        │
│   READING: consistent with coincidence. Not evidence of common authorship.             │
│   [make proposal ┄]  [record as negative result]                                       │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

Two details that carry the whole view:

- **The overlay states negative results as plainly as positive ones**, and it compares against a null model computed from *this case's own accounts*. `0.61` alone is a lie; `0.61, exceeded in 34% of random pairs here` is a finding. This is the one place the system computes a number, and it computes it from data in the case rather than from a manifest author's guess.
- **A gap with no coverage band under it means "we weren't watching."** A gap *with* a verified coverage band under it means "they were silent." Those are categorically different claims and every timeline in every OSINT product gets it wrong.

**Coverage bands are proven, not self-reported.** A heartbeat from the informer process proves the process is alive; it does not prove you are receiving from a specific channel. A session removed from a channel, a channel gone private, an MTProto update gap, per-channel FLOOD_WAIT — five failure modes that leave a heartbeat green while the lane silently lies. So: `kind: continuous` connectors must declare a **coverage proof**, a cheap positive read of the specific target. For Telegram it is `getHistory(limit=1)` every 5 minutes recording `(channel, max_message_id, wall_clock)`. Gaps become quantified and backfill becomes a bounded, resumable job. **Any continuous connector that cannot supply a coverage proof gets a permanently hatched lane, honestly labeled.**

## 3.4 MAP — thin, scoped, and mostly about where we swept

**Job:** three things, none of which is "where is the target."

1. Plot the coordinate-bearing minority (snapmap) with visible staleness decay. A 2019 snap and a yesterday snap must never render identically — steal ATAK's `staleTime` outright.
2. **A pin requires a machine-emitted coordinate.** Bio strings, LinkedIn city fields, place names in messages are listed in a side panel as `place-name inference · no coordinate`, never rendered as geometry. (Uncertainty polygons are deferred — §8.)
3. **Disconfirmation.** The swept-bbox coverage overlay, dimmed, so "no snaps here" reads correctly as "we never queried this tile in this window." You already store the bbox; this is free.

The tab is disabled-with-a-count, never hidden: `4 MAP(0) — 0 coordinates · 3 place-name inferences`. Hiding it would be a filtering violation at the navigation level.

## 3.5 COLLECTION — see §7.

## 3.6 DRAFT — the writing surface, and why it is in v1

The red team's largest finding: **there is no writing surface, so on day two the analyst exports to Word, and every citation chain in this beautiful lineage model dies at the clipboard boundary.** That single failure downgrades the entire product to a fancy collection manager. It is worth ~1.5 engineer-weeks and it goes in v1.

DRAFT is a plain prose editor with one special object: the **live citation chip**.

```
┌ 6 DRAFT ─ C-2291 assessment ─────────────────────────────── 4 citations · 1 flagged ─┐
│                                                                                        │
│  ¶2  The subject maintains an Instagram presence under @j_voss_88 ⟦claim#0114⟧ and    │
│      a Telegram presence under @jv_ ⟦claim#0119⟧. These are assessed as the same       │
│      person ⟦CLUSTER-004 · likely · mreid 08-24⟧ on the basis of a direct self-link    │
│      in the Telegram bio ⟦claim#0203⟧.                                                 │
│                                                                                        │
│  ¶3  ⚑ A Reddit account /u/j_voss_88 ⟦claim#0181⟧ is included in CLUSTER-004 on the    │
│      basis of handle match alone.                                                      │
│      ⚑ CITATION FLAG: CLUSTER-004 member `re t2_9x4k1` rests only on rationale `h`.    │
│        Cases citing an `h`-only seam require an explicit caveat in text. [insert] [why]│
│                                                                                        │
│  ¶5  A VSCO account was reported ⟦claim#0410 ▨⟧.                                       │
│      ▨ CITATION FLAG: producing endpoint's known-negative canary has been FAILING      │
│        since 08-23. This claim cannot be exported without an override note. [override] │
│                                                                                        │
│  ¶7  Forty of the forty-one CrossLinked candidates were excluded ⟦EXCL#001-040⟧.       │
│                                                                                        │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ EXPORT  ▸ .docx / .pdf / .md · citations become footnotes carrying tool@version, argv, │
│           credential ref (redacted), timestamp, and raw-blob sha256                    │
│ BLOCKED: 1 unresolved citation flag (¶5)                            [resolve] [export] │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

Behavior that earns it:

- Typing `⟦` or pressing `c` from any view inserts a chip **bound to the object**, not a copy of its text.
- If a cited cluster is later revoked, or a cited claim's endpoint goes red, or a cited claim's value changes on re-run, **the containing paragraph flags.** The document cannot rot silently.
- **Export is the enforcement boundary.** This is where the frictions the analyst refused to accept mid-flow get collected: gestalt rationales need their note here, `possible`-band clusters need their caveat here, hatched claims need an override here. The analyst writes those five notes at the end, when they are writing anyway, and they are better notes than the ones typed mid-triage.

---

# 4. The pivot — end to end

This is the product. Everything else is scaffolding around this loop.

## 4.1 Invocation

Every selector rendered anywhere in the app — in a table cell, a Dossier claim, a Telegram message body, a map callout, a DRAFT citation — is a **live selector chip** with a faint dotted underline on hover. Reachable by keyboard from any view: `j/k` moves the row cursor, `Tab` moves between selector chips within the focused row.

Press `p`. The **Pivot Bar** drops from the top of the center stage. Not a modal. Does not steal the view. Does not lose your place.

## 4.2 The analyst pivots on capabilities, not tools

Connectors declare `capability: instagram.account_profile`. toutatis and SoIG both declare it. The menu offers the **capability**; the tools are an implementation detail expandable on demand. Asking the analyst to choose between toutatis and SoIG is asking them to hold an operational fact — which scraper works this week — that the system knows better and that changes constantly.

But **fan-out is not automatic** (the engineer cut the fan-out policy engine, correctly). The capability row is pre-checked with the healthy members and the analyst sees exactly what will run before pressing enter.

```
┌ PIVOT FROM  handle:instagram = "j_voss_88"  ⟨OBSERVED · toutatis #0142 · 2h⟩ ─────────┐
│ RECIPE  [Handle sweep ▾]   ⌥1 Handle sweep  ⌥2 IG deep  ⌥3 Corp entry                 │
│                                                                                        │
│ ▸ NO EXPOSURE · FREE                                                                   │
│  ▣ username.enumerate (sherlock)          400 probes    ⚠ high FP by design            │
│      312 endpoints verified · 47 FAILING known-negative · 41 stale     [detail ▸]     │
│                                                                                        │
│ ▸ LOGGED EXPOSURE · SESSION                                                            │
│  ▣ instagram.account_profile              2 tools                                      │
│      ▣ toutatis 1.4.2   ✓ canary 12m                                                   │
│      ▢ soig 0.9.2       ✕ DOWN — auth, session pool empty      [refill pool ▸]        │
│      ⓘ measured concordance with toutatis: 99.8% over 212 co-runs → TREAT AS ONE      │
│      credential ig_sess_04 · heat 12/40 this hour                                      │
│                                                                                        │
│ ▸ MANUAL                                                                               │
│  ▢ instagram.technique_pack               4 methods apply · no exposure                │
│                                                                                        │
│ ▸ UNAVAILABLE — shown with reason, never hidden                                        │
│  ⊘ telegram.channel_monitor      needs channel:telegram — entity has none               │
│  ⊘ linkedin.org_to_people        needs org_name — 1 linked Org available     [use ▸]   │
│  ⊘ snapchat.public_map_scrape    needs geo_area — [draw one ▸]                          │
│                                                                                        │
│ PRE-FLIGHT  credential ig_sess_04 heat 12/40 · exposure LOGGED, attributable            │
│                                                       [esc]  [⏎ run]  [⇧⏎ run & watch] │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

Three deliberate decisions here:

**Ineligible tools are shown greyed with their unmet precondition, never filtered out.** Annotate-never-filter applied to the tool menu itself. `needs org_name — 1 linked Org available ▸` is a one-click *fix*, not an error. Hiding tools teaches analysts that the menu is a mystery and drives them back to terminals.

**Health lives in the pivot menu.** Not in Settings → Integrations, which nobody opens on hour nine. The moment of tool selection is the only moment the analyst is thinking about that tool. Sherlock's `47 FAILING` is visible *before* the run, so the analyst pre-discounts the result rather than trusting it and being burned three hours later.

**The pre-flight block shows only credential heat, exposure, and credit cost.** The red team killed `est. 95s`: a duration estimate that is wrong three times trains the analyst to stop reading the entire pre-flight block, *including the exposure line that actually matters*. Duration is shown live during the run as a surfaces-checked counter, never predicted.

## 4.3 Running: the RUNS strip

Pivots never block and never modal.

```
┌ RUNS ──────────────────────────────────────────── 3 active · 1 failed · Ctrl+R ───────┐
│ ▸ #0147 sherlock   j_voss_88   ███████████░░░░  312/400 probes  0:47  ▸ 9 hits   [⏹] │
│ ▸ #0148 toutatis   j_voss_88   ✔ 0:04                                ▸ 6 claims  [↻] │
│ ✕ #0149 soig       j_voss_88   auth_failed · session pool empty       ▸ retry?   [↻] │
│ ● #0121 informer   ch/9812     LIVE · 1,204 msgs · gap 0 · verified 0:12s ago    [⏸] │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

- **Partial results land immediately.** Sherlock's 9th hit is workable at t=47s.
- **Failure is a persistent first-class result, not a toast.** `auth_failed` stays visible with its exit code. A rate limit or an auth failure is analytically meaningful — *"we did not look"* is not *"we looked and found nothing"* — and dismissing it takes a deliberate keystroke that is logged.
- **`⏹` cancels but keeps what was collected**, flagged `PARTIAL — 312/400 probes`. Any negative claim from that run is permanently annotated *"absence over an incomplete sweep."*
- Progress is denominated in **probes/items**, never a percentage bar.

## 4.4 Arrival: everything lands, nothing is approved

**Results enter the case immediately, in state `unreviewed`.** They are searchable, filterable, pivotable, and visible in every view — carrying the `unreviewed` marker. There is no gate, no `⇧A`, no 400-item approval queue, and therefore no rubber stamp and no false audit record.

The **ARRIVALS rail** is a novelty feed, not an inbox. It tells you what showed up and lets you act:

- `⏎` **promote** an item to an entity (the only way entities are created)
- `e` **exclude** — affirmative not-them, with basis
- `i` **ignore** — soft-hide from arrivals, no reason required, fully reversible, and the item remains in STREAM and in lineage forever
- `p` pivot, `c` cite, `l` lineage

Ignore requires a reason **only** when the item is currently supporting a live cluster or was promoted by another analyst. The red team is right that 400 × (`d` + reason key) means the analyst learns one reason key and poisons the taxonomy within a week.

## 4.5 The review gate: adjudication on citation

This is the mechanism the whole design turns on. When an `unreviewed` claim is used for anything load-bearing — cited into DRAFT, selected as a merge rationale basis, or used to motivate a pivot — the action pauses for one inline strip:

```
  ▸ REVIEW BEFORE CITING  claim#0114  handle = "j_voss_88"
      toutatis 1.4.2 · run #0142 · 2026-08-26T12:08:41Z · exit 0 · endpoint ✓ 12m
      source_path  $.username        [open raw ⧉]
      ⏎ verified     d dispute     esc cancel citation
```

One keystroke, at the moment the analyst has an actual reason to think about the claim. The record then says `claim#0114 verified by mreid 2026-08-26T14:22Z, in the course of citing it into DRAFT ¶2` — which is **true**, unlike "400 observations accepted at 09:14:22Z."

Roughly 15 real reviews per case instead of 400 fake ones.

## 4.6 Fan-out: the CrossLinked case

CrossLinked breaks the one-selector-one-pivot model: a company in, 41 people out, most of whose emails are permutation guesses. It routes to the **ROSTER**, a bulk staging grid, never 41 arrival cards.

```
┌ ROSTER · ACME Corp · crosslinked #0151 ────────────────────────── 41 candidates ──────┐
│ ▣ │ name           │ ~username  │ ~email               │ pivots │ hits │ disposition   │
│ ▣ │ Jordan Voss    │ ~jvoss     │ ~jvoss@acme.com      │ ⏵ 3    │  2   │ → CLUSTER-004 │
│ ▣ │ Priya Raman    │ ~praman    │ ~praman@acme.com     │ ⏵ 3    │  0   │ ⊘ EXCLUDED    │
│ ▢ │ M. Okafor      │ ~mokafor   │ ~mokafor@acme.com    │ –      │  –   │ open          │
│ …                                                                                      │
│ ⚠ ALL 41 EMAILS ARE GENERATED (format permutation). Never observed on any surface.     │
│   They render with ~ and italics everywhere, forever, until some other surface          │
│   observes the same string — at which point promotion to OBSERVED is logged and visible.│
│ [⇧A select all] [p pivot selected · Handle sweep]     j . j . j .  ← the throughput key │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

Generated selectors are a distinct provenance state (`GENERATED`) with a permanent `~` prefix and italics. This is also where **circularity detection** gets its teeth (§5.5): a merge whose email rationale rests on a never-observed permutation is self-confirming, and the system hard-blocks it.

## 4.7 The two odd shapes

**Continuous (informer).** `w` on a `channel:telegram` selector creates a **standing collection**, not a run. Output flows to STREAM and to a CHRONOLOGY lane; it escalates into ARRIVALS only when it trips a **tripwire**. Without tripwires a monitor with 1,204 messages destroys triage.

Tripwires must ship with:
- a **rate governor**. `max_fires_per_hour`, and above it automatic collapse into one digest item: `selector "Volga" fired 312× in 1h — [open as filtered stream]`. A tripwire without a cap is a self-inflicted denial of service on the analyst's attention.
- **novelty tripwires**, which are the only ones useful early in a case when you have no selectors yet: *first-time-seen sender in this channel*, *first-time-seen external link domain*, *first message after >N hours of silence*.
- a visible **firing rate** per tripwire (`fired 340× / 24h`) with a one-key downgrade.

**Reference (DiscordOSINT).** It appears in the same pivot menu, marked `⌨ manual`, so the analyst never has to leave the plane to remember tradecraft exists. Selecting it creates a Task card with real checkboxes; `+ paste evidence` accepts a URL, text, or screenshot and mints a real observation with `tool: manual`, `analyst`, `captured_at`, `sha256`, and the method id as its argv-equivalent. **Human collection gets identical lineage treatment to machine collection**, distinguished only by a `✍` source chip — because "an analyst says they saw this" has a different failure mode than "a parser extracted this."

A docs tab gets read once during onboarding and never again. A greyed-out entry in the pivot menu gets read every time.

---

# 5. Confidence and lineage in the UI

## 5.1 The cut: no invented numbers, anywhere

The lens designs contained four parallel confidence vocabularies — `precision_prior` (0–1), `evidentiary_weight` (none/moderate/strong), `zero_confidence_ceiling`, and a pip strip implying arithmetic — which someone would eventually have to combine with a function that is **entirely invented**. There is no ground truth anywhere in this system against which `precision_prior: 0.97` was calibrated. It is a number a connector author typed.

Principle 3 says the system must never present a guess as a fact. **A computed confidence score is the system presenting a guess as a fact, wearing the one costume — a number — that most reliably defeats scrutiny.** All of it is cut. Savings: ~6–8 engineer-weeks, one class of "why does it say 0.61" support tickets, and the design's only self-inflicted principle violation.

What replaces it is a **provenance line**: only facts you could defend in a deposition.

```
│ email_hint   j•••••s@gm•••.com                                                   ⧉ │
│   2 tools · 1 measured source · 2h · unreviewed                                     │
│                                                                                      │
│ full_name    "J. Voss"  ⚡ "Jordan Foss"                                          ⧉ │
│   2 tools · 2 measured sources · CONFLICT · unadjudicated · both retained            │
│                                                                                      │
│ phone_hint   +1 •••-•••-4471                                                     ⧉ │
│   1 tool · soig ran and this field was absent (declared always_present) · 2h        │
│                                                                                      │
│ acct_hit     vsco/j_voss_88                                                      ⧉ │
│ ▨ 1 tool · producing endpoint canary FAILING 3d · absence and presence both undeter- │
│ ▨ mined · not citable without override                                               │
```

Every line is a fact. None is a number the system made up.

**"Measured source," not "declared upstream."** A manifest declaring `upstream: instagram.web_api.i_user_info` becomes a lie the moment SoIG switches endpoints in a patch release — and it fails in the dangerous direction, stacking correlated evidence as independent corroboration with a false assurance attached. Instead: the system already runs both tools in a capability group and already stores every co-run. Compute observed concordance over the last N co-runs, *including agreement on unusual and malformed values*. Two tools agreeing 99.8% of the time on 212 co-runs **are one source**, whatever their manifests claim. Declared upstream is a prior for the first 20 co-runs and is then overridden by measurement. ~200 lines, self-healing, cannot be defeated by a stale manifest.

## 5.2 The visual system: two textures, one color, and text for everything else

The lens designs correctly banned color-based encoding collapse and then committed the identical sin in texture — dash carrying two variables, hatch carrying three, dotted-vs-dashed at 1–2px being non-discriminable at hour six. And they cited NOAA charts as prior art while ignoring what NOAA actually does: NOAA doesn't hatch, **NOAA prints `PA`, `ED`, `Rep` — letters, next to the feature.** Text is the highest-precision annotation channel and it is nearly free at 28px row height.

**Channel 1 — border geometry → epistemic layer only. Three states.**
```
OBSERVATION   ▪ 1px solid
INFERENCE     ┄ 2px dashed
FUSION        ⌐ solid with corner brackets — visibly a container holding things
STATE         ═ double rule + analyst signature line
```
Dotted is deleted. `GENERATED` selectors are carried by `~` prefix + italics, which is already unambiguous and readable from four feet.

**Channel 2 — hatch fill `▨` → exactly one meaning: *the system does not vouch for this*.** Rot, failing canary, unverified endpoint, stale past threshold, unproven coverage, expired raw blob — all of them collapse to that one honest statement, and a **text token adjacent to it says which**. One pattern, learned once, works everywhere. Deliberately ugly, deliberately not color-only: survives colorblindness, projectors, and screenshots pasted into reports.

**Channel 3 — freshness → a literal right-aligned text token.** `2h` · `9d` · `31d ⚑`. Readable, sortable, unambiguous. Not a gradient, not a gutter rule.

**Channel 4 — adjudication state → text, in the provenance line.** `unreviewed` · `verified mreid 08-26` · `disputed` · `excluded`.

**Color: exactly one hue.** Red = *the system does not vouch* (paired with the hatch, for redundancy). Everything else is achromatic. Platform is a two-character monospace chip — `ig` `tg` `li` `re` `sc` `dc` — which is more discriminable than six hues, is already redundantly encoded in the handle format and the lane, and does not break for the colorblind analyst on the team.

**Deleted from the lenses: the pip strip `▪▫▫▫`.** The denominator is fake — for `display_name` on Instagram there are exactly two tools in existence, so it reads `▪▪▫▫` forever and the two hollow pips look like negative evidence while meaning nothing. Worse, the hollow "a surface looked and didn't find it" pip **cannot be computed safely**: it is derived by diffing a run's returned fields against the manifest's `emits`, so an over-optimistic `emits` list *manufactures negative evidence from a YAML typo*, rendered with the full authority of the confidence system.

Replaced by four explicitly stored per-(run, field) states, never inferred at render time:
```
observed              the value came back
attempted_and_absent  field declared always_present:true, run succeeded, field missing
not_attempted         field not in this connector's emits, or run partial/failed
conflicting           two sources, two values
```
Default is `not_attempted`. **`always_present: true` must be proven by the known-positive canary** or the field cannot claim it. That single rule is what lets `attempted_and_absent` be real evidence instead of fiction — and it is also, from the other direction, the differential signal that catches SoIG rotting (§7).

**And the hard rule that makes all of it trustworthy: degrade the chrome, never the type.** Low confidence never means low-contrast text. Stale data is never greyed toward illegibility. The analyst must be able to *read* weak evidence perfectly — it just must never *look* solid. Uncertainty renders as structural incompleteness and adjacent text, never as visual whisper.

**Banned outright, by name:** green checkmarks on machine output, traffic-light dots, 0–100 scores, aggregate "confidence: 87%", progress-bar-as-confidence, and any silent reconciliation of two conflicting values into one.

## 5.3 Conflict and volatility

- **Conflict on a stable field** → never auto-resolved. Both values render side by side with `⚡`, both sources chipped, permanently, until an analyst adjudicates it as an inference.
- **Disagreement on a field the manifest marks `volatile: true`** (follower counts, online status) → shown as a range with both timestamps, and **not** flagged as conflict. Without per-field volatility declarations, every follower-count refresh becomes a fake conflict, analysts learn to ignore the conflict state, and it then fails to work when it matters.

## 5.4 Homoglyphs

Every machine string renders in monospace with a Unicode-confusables lookup flagging `rn`/`m`, `l`/`I`, Cyrillic `а`. Impersonation handles are the single most common way an analyst attributes activity to the wrong human being, and proportional type hides it completely. ~50 lines, prevents a top-three analyst error.

```
  @jvossen_reaI          ⚠ homoglyph: final char is U+0049 LATIN CAPITAL I
```

## 5.5 The Merge Sheet — the only modal in the product

Select accounts (`v`, `⇧j/k`), press `m`.

```
┌ ASSERT IDENTITY ──────────────────────────────────────────────────────────────────────┐
│  ig uid 25025320 @j_voss_88     tg uid 99413007 @jv_     re t2_9x4k1 /u/j_voss_88     │
│  2 tools/1 src · 2h             1 tool · 31m             1 tool · 12m                  │
│                                                                                        │
│  RATIONALE (≥1 required, applies per member)                    ig    tg    re         │
│   h  same handle, exact                    ⚠ weak alone         ▣     ▣     ▣          │
│   e  shared email / hint consistent                             ▢     ▢     ▢          │
│   n  shared phone / hint consistent                             ▢     ▢     ▢          │
│   b  bio cross-reference / self-link                            ▣     ▣     ▢          │
│   i  image / pHash match                                        ▢     ▢     ▢          │
│   t  temporal co-location or pattern                            ▢     ▢     ▢          │
│   g  analyst gestalt / cumulative pattern    ← no note required ▢     ▢     ▢          │
│   k  external knowledge                      ← note required    ▢     ▢     ▢          │
│                                                                                        │
│  BASIS   3 claims selected · 1 unreviewed → will prompt for review    [pick claims ▸] │
│                                                                                        │
│  BAND    ( ) possible      (•) likely      ( ) almost certain                          │
│          possible → citable only with an inline caveat in DRAFT                        │
│          almost certain → requires 2 rationale codes from DIFFERENT evidence classes    │
│                           (a string match + a temporal match; not two string matches)   │
│                                                                                        │
│  ⚠ member `re t2_9x4k1` rests on rationale `h` ALONE — flagged in DRAFT on citation    │
│  ✓ CIRCULARITY CHECK: clean                                                            │
│                                                                                        │
│  NOTE ▏TG bio links directly to the IG profile. Handle match alone would not suffice.  │
│                                    Creates INFERENCE #A-0031 · mreid · [⏎] [esc]      │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

Four things the critiques forced:

**`g — analyst gestalt` is a first-class rationale code with no note requirement at merge time.** The closed taxonomy previously had no code for the most common honest basis of a senior analyst's merge — *I have read 400 of this person's messages and the register, timing, and grievances match* — so it got shoved into `k`, which demands prose and reads in the audit like a confession. The observed consequence: the analyst ticks `h` instead, because it's one keystroke and technically true, and now **the audit query "show me every identity resting only on `h`" returns exactly the wrong set**. Adding `g` un-inverts the query. The note is required at the export boundary instead.

**The band is consequential or it doesn't exist.** A three-option field with zero downstream effect always receives the middle option. So: `possible` clusters cannot be cited without an inline caveat, and `almost certain` mechanically requires two rationale codes from different evidence classes.

**No confidence rollup.** A cluster is never "displayed at the confidence of its weakest seam" — that hides *which member* is the problem. Per-member seam codes are shown always, aggregated never.

**Circularity check** — before commit, walk the evidence graph of every rationale. If any supporting selector traces to a `GENERATED` origin, or to an observation produced by pivoting on a value emitted by one of the accounts in this merge:

```
  ⛔ CIRCULAR EVIDENCE
     rationale `e` rests on ~jvoss@acme.com
     ~jvoss@acme.com was GENERATED by crosslinked #0151 (format permutation)
     it has never been observed on any surface
     → this merge would be self-confirming
     [override with note]  [cancel]
```

Override is possible, requires a note, and stamps the inference with a permanent `⟳ circular` badge that follows it into every view and into the export footnotes. This is the highest-value automation in the product: the machine is excellent at graph-walking and terrible at judgment, so it does the graph-walking. ~2 days.

## 5.6 Merge is a lens; split is free

The cluster **references** the account ids. Nothing is absorbed, moved, or rewritten. Accounts remain first-class and independently addressable with their own lineage.

Consequences:
- **Split (`x`) is a revocation, not an unmerge.** Nothing was moved, so nothing must be restored. Split is cheap and safe, which means analysts will actually use it. An expensive, scary split leaves bad merges in place forever.
- A revoked cluster becomes a **tombstone**: struck through, still walkable, still naming who asserted and who revoked. Annotate-never-filter applied to your own mistakes.
- Competing clusters may reference the same account. The account renders with `⑂ 2`.

**One engineering constraint on this, accepted:** a case has **one active hypothesis set** at a time. Competing readings exist as named forks (`working` / `alt: Rivera's reading`) in a switcher. The system materializes one `account → cluster` resolution map per active set and caches it; switching forks invalidates the cache. This keeps every read path at one join instead of a hypothesis-parameterized resolution step in six renderers, and it costs nothing analytically — you still hold competing hypotheses, you just look at one at a time.

## 5.7 The Lineage Drawer

**Rule: every rendered value has a lineage affordance `⧉`, with zero exceptions.** If something is on screen and cannot be walked back, it is a bug.

`l` on anything, or `Ctrl+click` any value. Opens the **bottom drawer**, full width, 40% height. Wireshark's three tiers — summary chain, decoded record, raw bytes — because it is the correct structure and analysts already know it.

```
┌ LINEAGE · "j•••••s@gm•••.com" ──────────────────────────────────────────────── esc ───┐
│ CHAIN                                                                                  │
│   6 DRAFT ¶2  ── cited by mreid 08-26 14:22                                    [open] │
│   ═ STATE · assessment sentence                                                        │
│   ⌐ CLUSTER-004 (fusion) · mreid 08-24 · likely · rationale b,h                [open] │
│   ┄ INFERENCE #A-0031                                                          [open] │
│   ▪ ACCOUNT ig uid 25025320  ← promoted from item by mreid 08-26 12:09                │
│   ▪ CLAIM  email_hint · reviewed: verified mreid 08-26 14:22                          │
│      extracted by toutatis parser 2.1.0, field `obfuscated_email`, $.obfuscated_email  │
│   ▸ ITEM   locator ig/25025320 · outcome hit · raw_span 0..1841                        │
│   ● RUN    #0142                                                                       │
│                                                                                        │
│ RUN #0142                                                                              │
│   tool       toutatis 1.4.2   container sha256:9c1f…a3b0   manifest sha256:2b7e…       │
│   argv       toutatis -s ▮▮▮▮▮ -u j_voss_88                                            │
│   credential ig_sess_04 (redacted in export)                                           │
│   started    2026-08-26T12:08:41Z   ended 12:08:45Z   exit 0   HTTP 200                │
│   motivated_by  claim#0098 (handle observed in crosslinked row #12)                   │
│   endpoint health at time of run: ✓ canary passed 08-26 11:58                          │
│   [⧉ copy repro]  [↻ re-run this exact pivot]  [⇩ export run record]                   │
│                                                                                        │
│ RAW  blob sha256:4e0b…77c2 · retained (text: forever)          3 matches · 1 shown ⌃⌄ │
│   {                                                                                    │
│     "username": "j_voss_88",                                                           │
│ ►   "obfuscated_email": "j•••••s@gm•••.com",     ◄ this value                          │
│     "obfuscated_phone": "+1 (•••) •••-••42",                                           │
│   }                                                              [full ⤢]  [/ find]   │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

Implementation honesty, per the engineer:

- **Highlight is best-effort, and says so.** Storing byte spans requires a span-preserving JSON parser (`json.loads` throws offsets away) and is impossible for derived claims. So: store `source_path` (JSON pointer or line number) per claim, and in the raw pane do a client-side literal search for the value string, highlighting **all** matches with a `3 matches` counter. 95% of the time there is exactly one and it looks like magic. When there are zero — Sherlock's "not found" is derived from the *absence* of a string — show the manifest's `observation_statement` verbatim instead: *"HTTP probe of {url} returned 200 without error signature."* Two days of work instead of two weeks of parser surgery, and the failure mode is honest rather than wrong.
- **`↻ re-run this exact pivot`** replays the identical argv and pinned tool version and presents a **diff**. It creates a *new* observation; the old is never overwritten. The claim grows a version stack (`⌄ 3 observations`), so "this field used to say something else" and "this value has disappeared" become first-class visible facts. Disappearance is a finding, and a scan-scoped model cannot express it.
- **Retention is split by blob class and rendered when it expires.** Text blobs are tiny (a 400-site Sherlock run is single-digit MB) — **retained for the life of the case**. (Corrected 2026-08-26 under `doctrine/RETENTION.md` RT-8, stamped as R5: `forever` is legal as a within-case blob policy and illegal as a case-level value, so a text blob never outlives its `retain_until`.) Media (snap thumbnails, Telegram attachments) is 90d, after which the claim shows `▨ raw media expired 2026-05-01 · run record retained`. A `retain_raw: 90d` that silently voids the lineage promise is worse than an honest tombstone.
- **`⇧L` — forward lineage.** "What depends on this claim / what would break if it were wrong." Same table, read in the other direction, two hours to build. Genuinely valuable at hour six, used twice per case — so it lives on `⇧L` and in the right-click menu, not on a prime single key.
- Secrets in argv render `▮▮▮▮▮` and are redacted in exports; everything else is exact and copy-pasteable.

---

# 6. The connector contract

**The one rule: no connector may contribute UI. Connectors contribute declarations; the platform owns every pixel.** Every OSINT aggregator that rotted did so identically — tool #7 had weird output, someone wrote `<ToutatisResultPanel />`, and by tool #30 the app was thirty apps in a tab strip. The fix is not discipline; it is making bespoke UI structurally impossible.

But the *actually enforceable* line is not "no bespoke UI" — that gets quietly violated the first time someone needs Telegram reply threading. **The enforceable line is: new tools are free, new shapes are expensive.**

```
kind:  one_shot | expansion | continuous | reference | geo
```

A connector whose output fits one of the five shapes gets in with zero platform code. A connector that doesn't fit is **rejected until the platform adds a shape**, which is a platform release reviewed by the platform team. That's defensible and CI-checkable.

## 6.1 The manifest

```yaml
# ── IDENTITY ────────────────────────────────────────────────────────────────
id: toutatis
version: 1.4.2
capability: instagram.account_profile     # the redundancy grouping key
kind: one_shot                            # one of the five shapes. gate.
cardinality: one_to_one

# ── INPUT ───────────────────────────────────────────────────────────────────
consumes:
  required: [{ selector: handle:instagram, as: username }]
  optional: [{ selector: platform_uid:instagram, as: user_id }]
  preconditions:
    - expr: "creds.instagram_sessions.available > 0"
      unmet_message: "No valid Instagram session in the credential pool"

params:                    # auto-generates the run form. FROZEN 8-type vocabulary:
  - key: fetch_avatar      # string int bool enum selector_ref geo_area time_window secret_ref
    type: bool
    default: true
    label: "Download profile image (enables pHash pivot)"

# ── OUTPUT ──────────────────────────────────────────────────────────────────
emits:
  - selector: platform_uid:instagram
    layer: observation
    always_present: true            # MUST be proven by the known_positive canary
  - selector: email_hint            # NOT an email. A constraint over the email space.
    layer: observation
    always_present: true
    constraint_semantics: prefix_suffix_mask
    fp_mode: "platform returns recovery hint for a LINKED account, not necessarily owner"
  - selector: phone_hint
    layer: observation
    always_present: true
  - entity: Account
    layer: observation
    fields:
      - { name: display_name,   always_present: true }
      - { name: bio_text,       always_present: false }
      - { name: follower_count, volatile: true }      # disagreement ≠ conflict
      - { name: is_verified,    always_present: true }

# CONNECTORS MAY EMIT ONLY layer: observation. This is structural.
# A tool that wants to assert identity declares a hint, which the platform
# materializes as a PROPOSED, UNACCEPTED inference:
#   inference_hint:
#     proposes: same_entity
#     rationale_template: "handle string identical to {source_handle}"
#   observation_statement: "HTTP probe of {url} returned 200 without error signature"

# ── NEGATIVE SEMANTICS ──────────────────────────────────────────────────────
zero_means: absence_evidence        # absence_evidence | inconclusive | never_conclusive
distinguishable_negatives: [account_does_not_exist, account_private, account_deleted]

# ── COST / EXPOSURE / AUTH ──────────────────────────────────────────────────
cost:     { class: session, units: "1 authenticated request", credits_per_call: 0 }
exposure: { level: logged, detail: "authenticated read, attributable to session acct" }
rate_limit: { scope: per_credential, calls: 40, per: 1h,
              on_429: { backoff: exponential, cooldown: 15m, quarantine_credential: true } }
auth:     { credential_pool: instagram_sessions }   # ref only. see 6.3

# ── HEALTH ── mandatory. no manifest merges without both canaries. ──────────
health:
  probe_unit: connector             # connector | endpoint | subscription
  canaries:
    - id: known_positive
      input: { username: "instagram" }
      expect: { platform_uid:instagram: "25025320", always_present_fields: all }
    - id: known_negative            # MANDATORY. this is what catches precision drift.
      input: { username: "zzq7x-nonexistent-4471" }
      expect: { result_count: 0, negative_class: account_does_not_exist }
  cadence: round_robin              # see §7.3
  golden_fixture: ./fixtures/golden.json

# ── LINEAGE ─────────────────────────────────────────────────────────────────
lineage:
  command_template: "toutatis -s {credential_ref} -u {username}"
  capture: [stdout, stderr, exit_code, http_status_chain, duration_ms, credential_id]
  retain: { text: forever, media: 90d }

# ── RENDER — slot declarations only. no markup, no CSS. ─────────────────────
render:
  shape: record
  title_template: "@{username} · Instagram"
  columns: [display_name, follower_count, is_verified, email_hint, phone_hint]
```

**Continuous adds one mandatory field and it is the important one:**

```yaml
id: informer
kind: continuous
capability: telegram.channel_monitor
continuous:
  coverage_proof:                   # NOT a heartbeat. A positive read of the TARGET.
    method: max_id_poll             # getHistory(limit=1) per subscribed channel
    interval: 5m
    establishes: "we hold everything up to message_id X for channel Y as of T"
  backfill: { supported: true, max_depth: 10000 }
health: { probe_unit: subscription }   # health is PER CHANNEL, not per connector
render: { shape: chat, timeline_lane: "tg/{channel}" }
```

**Expansion:**

```yaml
id: crosslinked
kind: expansion
capability: linkedin.org_to_people
emits:
  - selector: person_name
    layer: observation
    fp_mode: "search-result scraping picks up non-employees and former employees"
  - selector: email
    layer: observation
    generation_method: format_permutation     # → provenance state GENERATED, forever
    requires_validation_by: [smtp_probe, breach_corpus_match]
routing: roster                               # never lands as arrivals cards
```

**Reference:**

```yaml
id: discord_osint_pack
kind: reference
executable: false
emits: [{ entity: ManualTask, layer: observation, collector: human }]
methods:
  - { id: dsc-014, title: "Resolve Discord snowflake → account creation timestamp",
      applies_to: [platform_uid:discord], output_selectors: [time_window],
      steps_ref: ./methods/dsc-014.md, exposure: { level: none } }
```

## 6.2 Rendering a tool the UI has never seen

Drop in `holehe` — email → which sites have an account. Nobody has ever heard of it. Manifest: `capability: email.account_enumeration`, `kind: one_shot`, `consumes: [email]`, `emits: [acct_hit @ ~120 endpoints]`, `probe_unit: endpoint`, both canaries, `zero_means: absence_evidence`, `render.shape: table`.

With zero platform code:
- It appears in the pivot menu on **every email selector in the product**, grouped under its cost/exposure class, with its live health sparkline and canary age.
- Its run form is generated from `params`.
- Its results render in the platform table renderer, each field wrapped in the standard claim chip with `⧉`.
- Its 120 probes become items with per-endpoint canary state, so hits from failing endpoints automatically get the hatch and the "not citable without override" treatment.
- Its lineage drawer works, because `motivated_by`, argv, and raw blob are captured by the runner, not by the connector.
- Its rot is detected by the same one rule as everything else.
- Because it emits `acct_hit` with an `inference_hint`, its findings produce **proposed, unaccepted** inference edges in the Dossier — dashed, with a FOR/AGAINST panel — and it never gets to assert that the account is the person.

The connector author wrote a YAML file and an adapter. They did not touch the UI, and they could not have.

## 6.3 Where the contract honestly leaks — write these down before someone wastes a month

**Auth acquisition is out of scope for the manifest, permanently.** Harvesting an IG session from a browser profile; Telegram's phone + SMS + 2FA interactive login that must be redone when the session dies; LinkedIn's captcha walls; Discord tokens — five different acquisition flows with five different UIs. No fixed slot vocabulary contains an SMS-code prompt. Credential acquisition lives in a **separate credential admin tool**, per platform, with bespoke flows. The connector contract knows only `credential_ref`, `valid | invalid | quarantined`, and `heat`.

**Error classification is adapter code, not a YAML regex.** `failure_signature: "redirect to /accounts/login"` works for exactly one case; Instagram soft-bans are behavioral (200s with degraded content, no signal), Telegram returns structured `FLOOD_WAIT(n)`, search engines return captchas with a 200. The adapter must return one of a **fixed enum**: `{ok, empty, throttled(retry_after), auth_failed, blocked, malformed, error}`. The manifest declares what those states *mean analytically* (`zero_means`); the adapter decides which one *occurred*. That keeps the leak inside code the platform team reviews.

**The hint matcher is a library with fixtures, not a manifest enum.** `prefix_suffix_mask` describes Instagram; X masks differently; phone-hint semantics vary by country code. Build it as a registry with test fixtures from day one, not as an `if platform == 'instagram'` that metastasizes.

**Record/replay is mandatory day-one infrastructure.** You cannot hit live Instagram in CI. VCR-style HTTP cassettes per connector, captured during onboarding, replayed in CI. Without it no connector change can ever be tested and the entire extensibility story dies quietly.

## 6.4 Governance: cut almost all of it

Maturity tiers, registry lint rules, `spec_version` migration windows, deprecation policy — all presuppose an ecosystem of third-party connector authors. You will have six connectors written by two people who sit near each other. **Keep exactly one CI check: the manifest validates against the schema, both canaries pass live during onboarding, and the golden fixture replays green.** Add governance when there are outside authors, which may be never.

**Keep one governance item, because it protects evidence:** per-case version pinning. A case records exact connector versions and manifest hashes. Reopening it in eight months shows `toutatis 1.4.2 (superseded by 2.0.0 — output shape changed)` rather than silently re-running under new semantics and producing a different answer to the same question.

## 6.5 Onboarding: "Prove It"

```
┌ ADD CONNECTOR ── step 3 of 4 ── ● ● ◐ ○ ────────────────────────────────────────────┐
│  1 SOURCE    ✓ git+https://…/soig @ v0.9.2 · manifest found                          │
│  2 MANIFEST  ✓ 38 fields · 0 errors · 1 warning                                       │
│                ⚠ `upstream` not declared — independence will be MEASURED from co-runs │
│                                                                                        │
│  3 PROVE IT ─────────────────────────────── cannot be skipped ──────────────────────  │
│     known_positive  ✓ 1.2s · all always_present fields emitted                        │
│     known_negative  ✓ 0.8s · 0 results · class=account_does_not_exist                 │
│     always_present  ✕ FAIL  declared always_present: [phone_hint] but canary did not   │
│                            return it. Either the declaration is wrong or the tool is.  │
│                            [view diff] [edit manifest] [re-run]                        │
│     ▸ golden fixture captured · HTTP cassette recorded for CI                          │
│                                                                                        │
│  4 ONTOLOGY MAP   3 output fields unmapped   (blocked until 3 passes)                  │
│                                            [back]  [blocked: 1 check failed]           │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

Step 3 is Grafana's "Test connection" with teeth: it does not verify the tool *runs*, it verifies the tool does **what its manifest claims, including the negative case**. No connector enters the registry without a passing known-negative — which means every connector in the system is, by construction, capable of being caught when it rots.

Step 4 is the junk-drawer firewall. Unmapped fields have exactly three dispositions: map to an existing selector, propose an ontology addition (reviewed once, benefits all connectors), or park in the raw pane. There is no "render this specially," so there is no path by which a bespoke panel ever gets written.

---

# 7. Tool health and rot detection

**The premise: a scraper that silently starts returning zero is byte-identical, at the UI layer, to a clean negative.** Sherlock's real-world version is worse — a site changes its 404 page, the stored error signature stops matching, and every probe becomes a *false positive*: hundreds of confident hits that are all wrong. That is worse than downtime, because downtime is loud and self-correcting while silent drift teaches the analyst to trust a broken source.

## 7.1 Five states, and the fifth is the entire point

```
 ✓ HEALTHY     canaries pass, yield within band, fresh
 ⚡ DEGRADED    works but impaired: throttled, partial endpoints, latency 3× p95
 ⚠ SUSPECT     returns 200 OK and zero/wrong results. NO ERROR.  ← the dangerous one
 ✕ DOWN        hard failure: auth, network, non-zero exit, schema violation
 ○ UNVERIFIED  no canary in the freshness window; state genuinely unknown
```

Most platforms ship three and fold SUSPECT into HEALTHY, because from the runtime's view a 200-with-empty-array is a successful call. That fold is what destroys trust in the entire system.

## 7.2 Detection: four mechanisms, and one deliberately dumb rule

1. **Known-positive canary** — a fixture that must always return results.
2. **Known-negative canary** — the one everybody forgets and the one that catches Sherlock-class precision drift. If a guaranteed-nonexistent input starts returning a hit, the tool's error detection has broken and **every positive it has emitted since the last passing run is untrustworthy.**
3. **Per-field non-empty rate, 30-day sparkline, and exactly one hardcoded rule:** *a field that was >80% present for 14 days and is now <20% for 3 consecutive days raises SUSPECT.* EWMA with change-point detection is a statistics project that will emit false alarms for a year — a scraper's non-empty rate depends on what analysts happened to look up that week, and a case full of private accounts tanks the yield with nothing broken. Ship the one rule, ship the sparkline, let humans read the sparkline for everything else.
4. **Differential health.** Within a capability group, when toutatis returns `phone_hint` and SoIG does not across 89% of co-runs, that is either a real capability difference or SoIG rotting — and it is free. **Redundancy's biggest payoff is not coverage, it is the cheapest continuous integration test you will ever get on a scraper.**

**Field-level resolution, not connector-level**, is what catches real rot. Connector yield stays flat at "94% non-empty" while the single most valuable field silently dies.

## 7.3 Canary economics — the part nobody costed

Per-endpoint canaries every 30 minutes on Sherlock is `400 × 2 × 48 = 38,400 requests/day` — 96/day to *each individual small site*, forever, from your infrastructure. They will block you, and your health system will then report the endpoint as broken, which is true and entirely self-inflicted. On the metered side it is worse: Instagram canaries consume the *same session pool the analysts use*, eating ~15% of a 40/hr budget continuously.

So:
- **Round-robin the 400 Sherlock endpoints on a 24h cycle** — ~17 probes/hour total, each endpoint checked ~twice daily. Rot doesn't happen in 30-minute windows; detection latency is unchanged in practice, traffic is 1/50th.
- **Canary-on-use.** Any endpoint that returns a *hit* for a real case fires its known-negative canary immediately after, on the same connection. Health verification becomes proportional to analytic reliance, which is exactly where you want it.
- **Metered connectors canary hourly from a dedicated credential that is never in the analyst pool**, with its consumption shown on the health board so the cost of monitoring is visible.

## 7.4 The COLLECTION board — sorted by danger, so SUSPECT outranks DOWN

DOWN is loud and self-announcing. SUSPECT is quietly corrupting the case file.

```
┌ 5 COLLECTION ────────────────────── 23 connectors · 9 capabilities · ⟳30s ────────────┐
│ [all] [suspect 3] [down 1] [degraded 2] [unverified 4]                                 │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠ SUSPECT — returning 200 OK. verify before citing.                                    │
│                                                                                        │
│  soig 0.9.2          instagram.account_profile          field yield ▅▅▅▄▃▂▁▁           │
│    phone_hint present on 11% of runs since 08-21 (was 96%). Rule fired 08-24.          │
│    ← detected by DIFFERENTIAL: toutatis returns it, soig does not, 89 co-runs          │
│    canaries pass · no errors · canaries do not cover phone_hint                        │
│    [promote this drift into a new canary]  [demote in group]  [impact review ▸]        │
│                                                                                        │
│  username.enumerate  47 / 400 endpoints                            ▁▁▂▃▅▇█ FP RISK    │
│    47 endpoints failing KNOWN-NEGATIVE → emitting false positives                      │
│    worst: vsco(3d) ello(7d) tumblr(2d)                             [endpoint list ▸]  │
│    ⓘ 3 hits in 2 open cases are affected                          [impact review ▸]  │
│                                                                                        │
│  informer 2.1.0      tg/#logistics_ru        coverage proof ⚠ last verified 41m ago    │
│    declared interval 5m · max_id poll failing                                          │
│    ⚠ 41m of this channel's timeline is UNKNOWN, not EMPTY. Lane hatched in 2 cases.    │
│    known gap: msg ids 4456–4502 (47 messages)              [resubscribe] [backfill ▸] │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ ✕ DOWN                                                                                 │
│  toutatis 1.4.2      instagram.account_profile      auth · session pool 0              │
│    all 4 sessions hit login redirect in last 22m                                       │
│    ⚠ CAPABILITY instagram.account_profile HAS NO HEALTHY MEMBER                        │
│      (only other member: soig, SUSPECT)                            [refill pool ▸]    │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ ○ UNVERIFIED (4) — no canary in window                                  [run all ▸]   │
│ ✓ HEALTHY (13)                                                                    ▸   │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

The line that earns this whole screen: **"CAPABILITY HAS NO HEALTHY MEMBER."** Redundancy creates a dangerous illusion of safety, and the moment a group degrades to one SUSPECT member the analyst must be told *at the capability level*, not asked to infer it from two separate connector rows.

And `[promote this drift into a new canary]` closes the loop: every rot event caught late becomes a canary that catches it early next time. **The health contract ratchets.**

## 7.5 Retroactive invalidation — hatch what's cheap, list what's expensive

A canary fails at T; the tool last passed at T−72h. Everything produced in that window is now of unknown validity, and some of it already supports live clusters.

The lens design wanted cross-view hatch propagation down the whole provenance DAG. That requires a reactive dependency engine and touches every renderer. Cut. The compromise that keeps the honesty:

- **Claims produced directly by a currently-red endpoint render hatched, everywhere.** This is one join against a small `endpoint → current_health` lookup table, resolved at render time. No DAG traversal. It covers the case that matters most, because a hatched claim cannot be cited without an override.
- **Downstream inferences and clusters do NOT auto-hatch.** They appear in an **impact review list**, computed on demand from the health board:

```
┌ IMPACT REVIEW · vsco endpoint · known-negative canary FAILING ────────────────────────┐
│ last known-good 2026-08-23 09:12 · uncertainty window 77h                              │
│                                                                                        │
│ 4 claims produced in window                                          [inspect ▸]      │
│ 1 inference built on them   #A-0033 "vsco/j_voss_88 → same person"  ASSERTED           │
│ 1 cluster depends on it     CLUSTER-004 ← account re/vsco                              │
│ 1 DRAFT paragraph cites it  ¶5                                       [go to ¶5]       │
│                                                                                        │
│ The cluster is NOT auto-reverted. Your adjudication stands until you change it.        │
│              [re-run 4 claims]  [revoke #A-0033]  [acknowledge & keep, with note]      │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

**The system must not silently revert the analyst's assertion.** That would violate principle 3 in the opposite direction, with the machine overruling the human. It hands over the impact tree and lets the analyst adjudicate. This is computable *only* because layers were never collapsed — it is the payoff for the whole discipline.

## 7.6 What replaces "INFERENCE weakened"

The lens promised continuous re-checking of whether the evidence under a live inference still exists. That requires continuous re-collection against every supporting observation — a massive, credential-burning, exposure-generating background load, in direct contradiction with the credential-heat budget on the same page. It is a demo lie.

Honest replacement, ~3 days: inferences store explicit `supported_by: [claim_id…]`. A batch job on case-open checks whether each supporting claim's *latest version* still holds the same value, and the Return Brief shows **basis verification age**:

```
  ⚠ 2 inferences rest on claims not re-verified in 19d
      #A-0027 · basis: 3 claims · [re-verify — 2 session calls, heat 2/40]
```

True, cheap, actionable, and it doesn't secretly burn a session pool.

## 7.7 The Return Brief

```
┌ SINCE YOU LEFT · 14h 22m ─────────────────────────────────────────── esc dismiss ────┐
│ ● tg/#9812   +311 messages · coverage verified, no gaps · 2 tripwires fired  [3 ▸]   │
│ ⚠ tg/#4471   coverage proof failed 41m · 47 messages unretrieved             [▸]     │
│ ✕ soig       auth failed 4× · session pool empty · capability now single-source      │
│ ⚠ vsco       endpoint canary failing · 4 claims in this case affected  [impact ▸]    │
│ ⚠ 2 inferences rest on claims unverified 19d                          [re-verify ▸] │
│ ⊘ 1 excluded candidate reappeared in run #0151 (excluded 4d ago, pre-marked)         │
│ ⚑ DRAFT ¶5 has an unresolved citation flag                            [go ▸]        │
│ YOUR OPEN QUESTIONS (4)                                                [open ▸]      │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

**Open Questions are a first-class list, not a notes file.** `?` on any object files one against it. They appear in the Return Brief and are **mandatory in the handoff packet**. What the previous analyst didn't know is the most valuable and most commonly lost artifact in an investigation.

---

# 8. What v1 is

Two engineers plus a designer who can also write front-end. **~18 weeks to a v1 an analyst can work a real case in.**

## 8.1 Build order

**Weeks 1–4 — the spine.** Run/Item/Claim schema. Content-addressed blob store. Runner containers + Postgres-backed job queue. Three connectors, one per shape: toutatis (one_shot), sherlock (one_shot/endpoint), crosslinked (expansion). Manifest schema + validator + HTTP cassettes. Lineage drawer. *Nothing is visible except a lineage drawer and a table — and that is correct. If the store is wrong you find out now, not in month five.*

**Weeks 5–8 — triage.** STREAM with facets, pills, and FTS. Arrivals rail. Pivot Bar generated from manifests. RUNS strip with streaming partials and persistent failures. Recipes and `.`. *An analyst can now work Sherlock and CrossLinked volume faster than in a terminal. This is the first point the product is worth using — put it in front of a user here.*

**Weeks 9–13 — the picture.** DOSSIER with four layer bands. Merge Sheet, clusters-as-lenses, free split, circularity check. Exclusions. Assertion log. informer with coverage-proof polling, coverage intervals, watchdog, tripwires with rate caps and novelty rules. CHRONOLOGY with lanes, coverage bands, undated band, overlay with null model.

**Weeks 14–18 — honesty and handoff.** COLLECTION board (5 states, round-robin + on-use canaries, per-field sparkline, one rot rule). Re-run + diff. Impact review. DRAFT with live citation chips and export-boundary enforcement. MAP (thin). Return Brief. Open Questions. Handoff packet. Keyboard map, density modes, hardening.

## 8.2 The five things that must be right on day one

Everything else is recoverable. These are not:

1. **Run → Item → Claim.** Retrofitting the item level rewrites every adapter, every lineage path, and every stored claim.
2. **Coverage intervals with an external watchdog.** A crashed collector does not write "I stopped." Intervals must be closed by a watchdog (`now - last_verified_at > 3 × poll_interval → ended_at = last_verified_at, reason = watchdog_timeout`). ~50 lines. Coverage history **cannot be reconstructed retroactively** — ship without it and every case's timeline is permanently unknowable for the period before you added it.
3. **Case-scoped, never scan-scoped, with `motivated_by` on every run.** The pivot chain *is* lineage; if runs don't point at the claim that motivated them, you can never draw it.
4. **Nothing enters FUSION without an analyst act recording author, rationale code, and timestamp.** The moment one code path creates a cluster automatically, every cluster in the database becomes retroactively untrustworthy and you cannot tell which ones.
5. **Raw bytes retained and content-addressed from the first run.** You cannot go back and capture stdout you threw away.

## 8.3 The boring architecture, stated so nobody reaches for something exotic

One Postgres. No Neo4j, no Elasticsearch cluster, no Kafka. Nine tables. At 2k edges per case a recursive CTE returns in under a millisecond; the "graph" is four tables. Messages go in a **separate partitioned table** (by case, then month) with an FTS index — 100k–3M rows per case versus 500–3,000 claims, a three-order-of-magnitude difference that must not contaminate the analytic store. Blobs on S3/MinIO by sha256. One websocket per case carrying **invalidation notices only** (`claims changed for entity X`), never payloads — the client refetches, which eliminates an entire category of state-sync bugs for one round trip nobody notices. Counts come from a `case_rollup(case_id, dimension, bucket, n)` table maintained on write, never `COUNT(*)` — the Dossier alone issues ~12 queries, several of them counts over the message table, and those die at 3M rows.

**Event-sourcing is split:** append-only log for {runs, items, claims, inferences, dispositions, exclusions, notes, questions, revocations} — that *is* the artifact. Plain mutable KV for workspace state (scroll, collapse, sort, columns) keyed `(case, analyst, view)`. Replaying 40,000 `scroll_changed` events to reconstruct a session is absurd and every UI schema change would become an event migration.

## 8.4 CUT LIST A — killed outright by the critiques, not deferred

| Killed | Why |
|---|---|
| **Per-item accept gate ("The Box" as approval queue)** | 400 items with zero judgment content produces `⇧A` reflex, and the audit trail then records a lie ("400 accepted at 09:14:22Z") that a supervisor reads as review. Replaced by auto-land + **adjudication on citation**. |
| **Mandatory one-key dismiss reason on everything** | 800 keystrokes; the analyst learns one key and uses it universally, poisoning the taxonomy within a week. Reason now required only when ignoring something another analyst promoted or that supports a live cluster. |
| **All machine confidence arithmetic** — `precision_prior`, `evidentiary_weight`, `zero_confidence_ceiling`, computed ICD bands | Invented numbers with no calibration ground truth anywhere in the system. A computed score is the machine presenting a guess as a fact in the costume most resistant to scrutiny — the design's only self-inflicted violation of its own principle 3. Replaced by the provenance line. ~6–8 engineer-weeks saved. |
| **The pip strip `▪▫▫▫`** | Fake denominator (two tools exist for IG display_name, so two hollow pips mean nothing while looking like negative evidence); 4×4px needing a permanent legend; and the hollow "looked and didn't find" pip **manufactures negative evidence from a YAML typo**. Replaced by text and by four explicitly stored per-field states gated on canary-proven `always_present`. |
| **Dotted borders** | Not discriminable from dashed at 1–2px on a laptop at hour six. `~` + italics already carries GENERATED unambiguously. |
| **Hue assigned to platform** | Platform is type, and type is the least interesting variable; it's already redundantly encoded in handle format, lane, and URL. Two-char monospace chips are more discriminable and survive colorblindness. Exactly one hue remains: red = *the system does not vouch*. |
| **Confidence rollup on clusters ("displayed at weakest seam")** | A strong pair plus a doubtful third is not a weak cluster, and the rollup hides *which member* is the problem. Per-member seams, always, aggregated never. |
| **Ordinal assessment as a consequence-free field** | A three-option field with no downstream effect always receives the middle option. Kept only because it is now mechanically consequential (`possible` needs a caveat to cite; `almost certain` needs two rationale codes from different evidence classes). |
| **Quiet Mode as a persistent global toggle** | A global invisible mode that silently changes what tools may do is a textbook mode error. Exposure is now a per-run pre-flight line only. |
| **`est. 95s` in pre-flight** | Wrong three times and the analyst stops reading the whole pre-flight block, including the exposure line that matters. Replaced by a live surfaces-checked counter. |
| **`upstream:` as authoritative independence** | Unverifiable, silently falsified by a patch release, and it fails in the dangerous direction. Replaced by **measured concordance** over co-runs. |
| **Heartbeat as proof of continuous coverage** | Proves the process is alive, not that you're receiving from a channel. Green-strip-plus-empty-lane would be a lie in at least five real Telegram failure modes — and a lie the analyst was explicitly taught to trust. Replaced by mandatory **coverage proof** (per-target max-id poll) with quantified gaps. |
| **Live "inference weakened" reactive detection** | Requires a reactive dependency engine and continuous re-collection that contradicts the credential-heat budget on the same page. Replaced by batch **basis verification age** in the Return Brief. |
| **Cross-view hatch propagation down the provenance DAG** | Touches every renderer for a query-time DAG bit. Replaced by: direct-claim hatch via a one-join endpoint-health lookup, plus an **impact review list** for downstream objects. |
| **EWMA + change-point yield detection** | A statistics project on a non-stationary series driven by user behavior; false alarms for a year. Replaced by one hardcoded rule that catches the actual documented failure. |
| **Per-endpoint 30-minute canaries** | 38,400 requests/day and you get blocked by the sites you're monitoring. Replaced by round-robin (~400/day) + canary-on-use. |
| **Automatic capability fan-out with a cost-class policy engine** | Show the grouping, show the correlation warning, pre-check healthy members, let the analyst see what will run. |
| **Maturity tiers, registry lint, spec_version migration windows, deprecation policy** | Six connectors, two authors who sit near each other. One CI check remains. |
| **Keybinding divergence across the three lenses** | Resolved into one keymap (§8.6), read from a single source file by both the app and the docs. |
| **A global "show everything" graph** | It has never once answered a question. There is no such button, in v1 or ever. |

## 8.5 CUT LIST B — deliberately deferred to v1.1+

| Deferred | Why, and what stands in for it |
|---|---|
| **GRAPH canvas** | 6–8 engineer-weeks (persisted deterministic slots, expansion budgeting, hub demotion, edge-layer toggles, bounded path search, selection sync into five views) for a view that, in a 40-entity case, tells you less than the Dossier. **Replaced in v1 by a PATHS list**: select two entities, get a table of routes ≤3 hops, each row a chain of labeled predicates with the weakest link marked — same information, no canvas, ~4 days. When it does ship: SVG, hard cap 300 nodes / 600 edges, never WebGL. The legibility ceiling with this design's encoding is ~50 cards on screen; anything beyond that is the graph being misused as a database browser. |
| **`attempted_and_absent` as displayed negative evidence** | Requires canary-proven `always_present` across the connector fleet. The field is *stored* from v1; it is only *rendered as evidence* once proven. |
| **Dispute / multi-analyst realtime** | Single writer per case in v1, with presence lock and a "M. Rivera has C-2291 open" banner. Handoff is an export/import with a content hash and a "changes since handoff" diff. Dispute is a note type. Full concurrent editing in v1.1 — noting that every in-house tool the red team has used died at exactly this point, so it is v1.1, not v2. |
| **Inferred-location uncertainty polygons** | Geometry work. In v1, place-name inferences are list entries marked `no coordinate` and are structurally incapable of getting pin geometry. |
| **Brief Mode with suppression counts** | Real need, but it's a second renderer over the same data. DRAFT export covers the briefing case in v1. |
| **Auto-promotion of GENERATED → OBSERVED** | v1 logs the match and offers the promotion as a one-key action; automatic promotion waits until the matcher library has fixtures. |
| **Hypothesis forks beyond one active set** | v1 ships the fork switcher and `⑂ n` glyph with one active set materialized. |

## 8.6 The single keymap (one source file, read by both app and docs)

```
NAV     j/k row     Tab/⇧Tab selector chip     1–6 view     Ctrl+1..9 case
        /  search in view     Ctrl+K palette     f set focus     [ ] collapse rails
        esc esc  CLEAR ALL GLOBAL SCOPES   ← the cheapest change in this document
ACT     p pivot        . repeat last recipe      ⌥1-9 recipe direct
        ⏎ promote item→entity    e exclude (affirmative)    i ignore (soft, reversible)
        c cite into DRAFT        m assert identity          x revoke
        w watch (standing)       n note                     ? open question
        l lineage                ⇧L forward lineage
SELECT  v multi-select     ⇧j/k extend     ⇧A select all in run
UNDO    Backspace undo last disposition (10s toast)     Ctrl+Z canvas-level
GOTO    R refresh snapshot     Ctrl+R expand RUNS     ?? legend over focused object
```

Resolutions from the divergences the red team found: lineage is `l` (not `\`); view switch is `1–6` (not `g`+letter, which is a keystroke slower on the most frequent action); there is no `d`, because there is no accept/dismiss pair — the disposition verbs are `⏎` promote / `e` exclude / `i` ignore, none of which sit adjacent to a destructive twin; undo moved to `Backspace`, where the hand already is; rejected and excluded items **stay in place, struck through**, and are also queryable as a filter — they never move to a tab you have to remember exists.

**No modals except the Merge Sheet.** Everything else is a drawer or an inline expansion, because a modal severs case context. Every view is a URL with working back-navigation. Per-case, per-view state autosaves so switching views costs nothing and thinking is never punished.

---

## The five things worth switching for

Stated plainly, because a design that claims everything is equally important is claiming nothing:

1. **Coverage bands with quantified gaps.** A silence with no verified coverage under it is "we weren't watching," and no product does this.
2. **The known-negative canary and the SUSPECT state.** This catches the Sherlock error-signature drift that turns a scraper into a false-positive generator while every dashboard stays green.
3. **Circularity detection on merge.** The machine does the graph-walking it is good at and refuses to let a permutation-generated email confirm an identity.
4. **Adjudication on citation.** Fifteen true reviews instead of four hundred false ones, and an audit trail that says something a supervisor can rely on eight months later.
5. **Immutable observations where re-run produces a diff rather than an overwrite** — which makes *disappearance* a finding, and there is no other way to see it.