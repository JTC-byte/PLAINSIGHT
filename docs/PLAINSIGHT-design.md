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

---

## 9. Amendments of 2026-10-28: the app store and the social web

These amendments record where the application built on 2026-10-28 under `app/` departs from the sections above, as AGENTS.md section 3 requires of a Class C change that alters observable behaviour. Each one names the behaviour, what this design said, and why. None is ratified, and the maintainer decides each one. The text above this section is left exactly as it was written.

**9.1, 2026-10-28, store engine (section 8.3).** On the workstation the store is stdlib SQLite in rollback-journal mode, never WAL, holding only tracked, unmodified synthetic corpus files, which EG-1 and EG-2 permit as stratum 4. Section 8.3 says one Postgres. Postgres arrives with the ISOLATED VM: both dialects are kept as DDL of record in `app/store/ddl_sqlite.sql` and `app/store/ddl_postgres.sql`, with a parity test on table and column names, and the move is a replay of the append-only log rather than a schema migration. Each SQLite database corresponds to a Postgres schema, and each per-case database to the schema case_<id> that RT-3 drops. The reason is that no Postgres server or driver exists on the workstation and nothing may be installed there. The revert is to point `app/store/db.py` at Postgres once the VM exists. The maintainer decides whether this stands.

**9.2, 2026-10-28, the table set (section 8.3).** The store names twelve tables and splits them by stratum and by the shred boundary, where section 8.3 counts nine tables without naming them. The shared database, which survives the shred, holds case_registry, event_skeleton, run, coverage_interval and rollup_vocab. The per-case database, which the shred removes, holds event_payload, item, claim, node, edge, case_rollup and workspace_kv. The append-only log is split into a skeleton that triggers keep insert-only and a stratum-1 payload table that refuses UPDATE and that only the retention sweep will delete from, with the item and claim rows following it by cascade. The partitioned message table is deferred until a continuous connector exists, and the job queue belongs to the runner. The reason is that RT-1, RT-3 and contract section 12.2 require the split, and this design predates them. The count is a fact about this schema, not a target. The maintainer decides whether this stands.

**9.3, 2026-10-28, invalidation transport (section 8.3).** The transport is one Server-Sent Events stream per case, where section 8.3 specifies one websocket per case carrying invalidation notices only. The reason is that the standard library has no websocket server and the traffic is one-way. The property is kept and tested: a notice carries a sequence number, a kind, the case id and opaque ids, never a payload or a value, and a notice that fails `app/http/notice.schema.json` or the egress guard is dropped and counted rather than sent. A stream also polls the log, and when another process such as python -m app ingest has appended to the case it sends one notice of kind case, after which the client refetches. The maintainer decides whether this stands.

**9.4, 2026-10-28, blobs (sections 8.2 item 5, 8.3 and 5.7).** Raw bytes stay addressed by sha256, and their location is local disk under the store root, per case, where section 8.3 puts blobs on S3 or MinIO. A write is refused unless three conditions hold: the environment is ISOLATED, a per-case Encryptor is configured, and the pin of record stamps both EG-2 and RT-4, whose trigger is the first blob. No blob is written on LOCAL, and the raw pane renders "raw bytes not held" for the corpus's fixture digests. The reason is RT-4 and EG-2: encryption from the first blob cannot be retrofitted, and no stdlib or home-built cipher stands in for it. The AEAD library for the VM image is the operator's decision. The maintainer decides whether this amendment stands.

**9.5, 2026-10-28, RUN and CLAIM columns (section 2.1).** The run row carries argv_template and credential_id, raw bytes stay on the item by sha256, and review state is projected at read time from the latest VERIFY or DISPUTE and never stored. Section 2.1 lists argv, raw_blob_sha256 and credential_ref on RUN, and review_state on CLAIM. The reason is that the contract outranks this design here: its section 6 prohibits a filled argv and a credential value and places raw on ITEM, and its section 8 makes review state a projection (D3). The maintainer decides whether this stands.

**9.6, 2026-10-28, the watchdog's closing reason (section 8.2 item 2).** A closed coverage interval records its closer as the closing event's producer: runner-watchdog for a timeout, and the collector's own runner producer otherwise. Section 8.2 closes an interval with reason = watchdog_timeout. The reason is that PSE's COVERAGE_INTERVAL has no reason field, and no schema change is made for one. An open interval is a working row, and it becomes artifact, immutable by trigger, when its closing event is appended. runner/watchdog.py, which emits that closing event on a timeout, is not built in this change. The maintainer decides whether this stands.

**9.7, 2026-10-28, WEB enters v1 (sections 8.5 and 3).** The GRAPH canvas that CUT LIST B deferred ships as the view WEB on key 7, where section 3 says GRAPH is not in v1. The reason is the operator's words of 2026-10-28, "starting work on the social web operating picture all the data will be visualized with and interacted with". It ships on the terms CUT LIST B set: SVG only, a hard cap of 300 nodes and 600 edges that no parameter raises, and never WebGL. It is case-scoped and requires a focus, so CUT LIST A's ban on a global graph stands. The layout is deterministic and radial, with no force simulation, no persisted slots and no hub demotion, and no edge carries a weight. The 6 to 8 engineer-weeks section 8.5 costed are cut rather than built. PATHS ships alongside on key 8 over the same edges and, with the list twin on t, is the fallback past the cap. DOSSIER remains the landing view under section 3.1, and making WEB the landing view is one configuration value, LANDING_VIEW in `app/config.py`, which is the operator's decision. The maintainer decides whether this amendment stands.

**9.8, 2026-10-28, build order (section 8.1).** The first slice shows a read-only, focus-scoped WEB over the must-pass corpus, with the Lineage Drawer, a read-only DOSSIER and PATHS. Section 8.1 makes a lineage drawer and a table the only visible things in weeks 1 to 4. The reason is that the operator asked on 2026-10-28 for the social web picture. The spine ships in the same slice: Run, Item and Claim, motivated_by on every run, fusion only by an analyst act, content addressing, and coverage intervals as projected rows. The external watchdog that closes an interval on a timeout is not built yet. The maintainer decides whether this stands.

**9.9, 2026-10-28, the Lineage Drawer reaches the authorization (section 5.7).** The chain continues above RUN to COLLECT PERMITTED and to the authorization's GRANT, EXTEND and REVOKE, so every node walks to the human act that made it collectable. Section 5.7 ends the chain at RUN. The drawer shows argv_template and never a filled argv. A decision recorded after its authorization's revocation, and an expired authorization, render as flags and are not refused, because chain rules belong to the gate. A missing link renders "▨ chain broken at <event_id>", and the walk stops on that branch rather than skipping it. The maintainer decides whether this stands.

**9.10, 2026-10-28, keymap additions (section 8.6).** The additions, read from the single keymap file `app/static/keymap.json`, are 7 WEB, 8 PATHS, + and - for hops, and t for the list twin of the web. In WEB, f recentres the web without collecting anything, and p opens the Pivot Bar for one node. Section 8.6 binds 1 to 6 to the six views of section 3 and names no key for WEB or PATHS. The reason is that the two new views need keys, and 7 and 8 continue the row of view keys without displacing any key 8.6 binds. No existing key is rebound: there is no d, and Enter stays promote. The maintainer decides whether this stands.

**9.11, 2026-10-28, the deep dive from the web (sections 4.2 and 4.6, SS-16).** In WEB a deep dive takes exactly one node and one motivating claim per act, and a request naming two is refused with DEEP_DIVE_ONE_NODE_PER_ACT, because SS-16 makes breadth deliberate. The route records nothing and imports nothing from runner/. While runner/subject_guard.py does not exist it returns "NOT DISPATCHED, no subject gate exists yet (Step 10): nothing was collected" with the legal moves. While that file exists and the route is not connected to it, the route returns "NOT DISPATCHED, the subject gate is not connected to this route" with the same moves. The app never emits a COLLECT_EVENT or an authorization. Connecting the route to the subject gate is a separate change, Class F by effect, decided by the operator. The ROSTER multi-select pivot of section 4.6 is not changed. The maintainer decides whether this amendment stands.

**9.12, 2026-10-28, the door, the request rules and the store engine's environment (sections 8.3 and 5.7, EG-2 and EG-3).** The ingest door runs five steps in order: the source rule, the freshness of the generated artifacts, the row shape, validation by `tools/validate.py` loaded by path with no copy, and the store checks. A row is a {name, description, event} wrapper or a bare envelope, one JSON object per line and one case per batch. Any code the tool fires refuses the whole batch, and nothing is written. An event id repeated inside one batch is classified like a stored one: identical bytes are a no-op, and changed bytes are refused with EVENT_ID_CONFLICT. Under its write lock the ingest re-reads whether the case is registered and whether a planned event is already in the log, and an ingest that another one overtook is refused with INGEST_CONCURRENT and writes nothing. Node ids are opaque uuids the projections assign. The workspace keys are scroll, sort, columns, collapsed, focus, hops and drawer, and a workspace value is a number, a boolean, a closed token, a uuid, or a list of those. The SQLite engine serves LOCAL only: with PLAINSIGHT_ENVIRONMENT set to ISOLATED it refuses to open or create a store (STORE_ISOLATED_NOT_PROVISIONED), because the ISOLATED store is the operator's Postgres inside the VM under 9.1, and one environment variable must not lift the LOCAL source rule on the workstation. The server binds 127.0.0.1 and answers a Host header naming its own loopback address and port only. The route set is closed, and no route spans cases or ingests uploaded bytes. GET reads, and POST and PUT are limited to the deep-dive and workspace routes, each carrying the per-launch token set as an HttpOnly, SameSite=Strict cookie. A URL carries uuids and fixed words only: the query keys are focus, hops, sector, view, lineage, dir and after, plus from and to on the paths route, each with one shape, and a body is one JSON object of closed keys and shapes of at most 8 KiB. A case URL that names no view redirects to the landing view, so every URL the client keeps names a view. The egress guard holds the value set of every case the store holds and reloads it whenever the store's database files change, whichever process wrote them. Headers, titles, Location, error bodies and notice frames never carry case material, and a request whose path or query carries a held value is refused without echoing it. A log line is the fixed tuple of time, method, route template, status and duration. The web's sectors follow the categories the operator named for the social web on 2026-10-01. The reason is that the build brief that set these rules lives outside this repository, and a refusal must cite a rule its reader can open. The maintainer decides whether this stands.

**9.13, 2026-10-28, the first connector and the subject gate (sections 6.2, 6.3 and 6.5).** Four behaviours of `connectors/sherlock/` and `runner/subject_guard.py` depart from the sections above. First, the Sherlock cassettes record the process boundary, the CSV export, stdout, stderr, the exit code and the duration, where section 6.3 specifies VCR-style HTTP cassettes captured during onboarding; Sherlock makes its own requests inside its container, so no HTTP exchange passes through code this repository runs, and the three cassettes in the tree are hand-built in Sherlock's recorded shape and were never captured. Second, the adapter maps each row to an outcome by the table in `adapter.py`'s docstring and to section 6.3's fixed enum: a Claimed row is a hit only at a 2xx status on a site outside the measured exclusion list and with a username slot in its url, a WAF or Unknown row is an error item with no negative class, and a run whose every row is Unknown is state error rather than blocked. Third, the adapter's `invoke()` builds argv from the manifest's `command_template` and starts the container, where section 6.2 has the runner capture argv; it does so only after a permitting Decision from `runner.subject_guard.evaluate()`, refuses a value that would read as a flag, a brace sweep or a path, and removes the scratch directory it made before it returns. Fourth, the subject gate returns a Decision that serializes as the COLLECT_EVENT the runner writes and names as the parent of the run's RUN_START, the app's deep-dive route, which 9.11 leaves unconnected to the gate, would never receive a permit once connected, because it cannot pass preflight, and the draft refuses S3, S4, N0, L0 and S1 at step 3 whatever the pin says. The reason is that Sherlock is the first connector, the first argv builder and the first caller of the gate, and the sections above were written before any of them. Reverting the first three means a runner-side argv builder and a recording proxy, and reverting the fourth means an option-aware binding read. Nothing here has run against a platform, an account or a person. The maintainer decides whether this amendment stands.

**9.14, 2026-10-28, a sweep's handle takes its platform from the item (sections 6.1 and 6.2, reading SH-R5).** An emit in a connector manifest may declare `platform_from_item: true` in place of `platform`, and then each claim it produces names the platform of the site its PROBE_EVENT ITEM locator names. `tools/validate_manifest.py` requires exactly one of the two where the key's registry form binds a platform, refuses both where it binds none, and permits `platform_from_item` only on a manifest whose `health.probe_unit` is endpoint, under MANIFEST_SELECTOR_PLATFORM (reading MF-R17). `connectors/sherlock/manifest.yaml` declares it on its handle emit, and the adapter writes each claim value as the site's platform token, a slash and the username, the token derived from the site name alone, with a Claimed row on a site whose name yields no token held as ambiguous (reading SH-R18). Section 6.1 writes a selector and its platform as one string, such as handle:instagram, with one platform per emit, and section 6.2 draws a tool that emits one selector across about 120 endpoints with probe_unit endpoint and does not say which platform each hit is on. The reason is that a handle's registry form binds a platform, Sherlock's hits land on a different site per item, and an invented token such as sherlock_site would name a platform that does not exist. Reverting means removing the field from schema/connector-manifest.schema.json and the check from the validator, after which the Sherlock manifest refuses again. The maintainer decides whether this amendment stands.

**9.15, 2026-10-28, a qualified site name gives no platform token (sections 6.1 and 6.2, reading SH-R18).** The review of the build added one case to SH-R18: a Sherlock site name carrying a parenthesised qualifier yields no platform token, so a Claimed 2xx row on such a site is ambiguous with no claim, and `emit()` refuses a hit there. At the pinned commit that is five sites on three platforms, Genius (Artists), Genius (Users), HackenProof (Hackers), Steam Community (Group) and Steam Community (User), beside the four names that begin with a digit. The reason is that the qualifier names an endpoint rather than a platform: the rule of 9.14 alone gave Steam and Genius two tokens each, and it recorded a hit on a group or artist directory as a handle on a platform named after that directory, where `ontology/selectors.yaml` files a group under channel. Reverting means removing the qualifier test from `platform_token()` in `connectors/sherlock/adapter.py` and its tests, after which those five sites emit claims under endpoint tokens again. The alternative is a written mapping from each qualified endpoint to its platform's one token, with the group and artist endpoints held ambiguous. The maintainer decides whether this amendment stands.

**9.16, 2026-11-09, analyst acts through the door, and where they land (sections 4.4, 4.5, 5.5, 5.6 and 8.3, EG-2).** POST /api/cases/{case}/acts mints one ADJUDICATE_EVENT (VERIFY, DISPUTE, NOTE, QUESTION, IGNORE, REVOKE, PROMOTE) or IDENTITY_EVENT (CLUSTER, EXCLUDE) per request from a closed body and sends it through the same door every corpus row passes: `tools/validate.py` loaded by path, the store checks, one transaction, then the notice. The server fills what no body may state, the event id, the timestamp, the producer (the session's `--analyst`), the source and the lineage with the target first, and refuses an unknown key or act before the door is reached. A code the validator fires comes back as ACT_REFUSED_BY_MODEL with the codes named, so the Merge Sheet can offer the circularity override with a note on MERGE_CIRCULAR and name the two evidence classes on BAND_UNSUPPORTED. The server copies no rule of the model: two members, a seam per member, a note with k, the band's classes and the circularity walk are the validator's; it checks shapes and the facts about the case the validator cannot see, an item already promoted, a target already revoked, a member that is not an entity or a referenced-only node, and the runtime half of ADJUDICATION_REASON_MISSING, which the layer model marks `when: runtime` because whether an IGNORE's target supports a live cluster or was promoted by another analyst is a fact about the case. Where an act lands departs from section 8.3's one store: on ISOLATED any held case. On LOCAL the route refuses to land any act (ACT_LOCAL_PENDING_DECISION) until the operator sets `LOCAL_ACTS` in `app/config.py`, because an act's payload is stratum 1 by the layer model and its prose is typed at run time rather than read from a tracked, reviewed synthetic file, so admitting it would widen what LOCAL may hold under EG-2, which is his decision and Class F by effect; with it set, an act still lands only in a case whose registry row says synthetic. The watchdog's system event, which carries no prose and no subject value, lands on LOCAL in a synthetic case under the same origin rule. The tests set the value in memory to exercise the mechanism. The review strip of section 4.5 appears in the Merge Sheet before an unreviewed basis claim is selected (in_course_of merge_basis) and in the Pivot Bar before an unreviewed motivating claim (pivot_motivation); citation into DRAFT is not in this slice, so in_course_of citation is accepted by the route and offered by no key. The reason is that the acts are the first writes the interface makes, and section 4.4's rule that nothing is approved by arrival holds only if each act is one event by a named human through the one door. Reverting means removing the route and its origin, after which the slice-3 keys answer that nothing is built again. The maintainer decides whether this amendment stands, and in particular whether to set `LOCAL_ACTS` so that an act may land in a synthetic case on LOCAL at all (reading APP-R31).

**9.17, 2026-11-09, undo is a cancel window (section 8.6).** Section 8.6 binds Backspace to "undo last disposition (10s toast)". In an append-only log a landed act is not undone, so Backspace is a cancel window: a single-key disposition (⏎, e, i, n, ?, x) is queued for ten seconds with its consequence shown and nothing recorded, Backspace cancels it, leaving the page inside the window cancels it, and on expiry it is sent to the case that was open when the key was pressed. After that the model offers no reversal except REVOKE of a PROMOTE, a CLUSTER, an EXCLUDE or a SAME_ENTITY link, so a landed NOTE, QUESTION, VERIFY, DISPUTE or IGNORE stands in the log, and the interface says so when a key is pressed. The Merge Sheet commits on its own button and is not queued, because a modal confirmed by hand is not a slip, and the review strip's ⏎ and d send at once for the same reason. The reason is that a toast that "undoes" a recorded event would have to delete from the log, which the skeleton's triggers refuse (amendment 9.2). Reverting means recording first and revoking on Backspace, which the model permits for four subtypes only. The maintainer decides whether this stands.

**9.18, 2026-11-09, the watchdog is the runner's command (section 8.2 item 2, amendment 9.6).** `runner/watchdog.py` closes an open coverage interval whose last verification is older than three poll intervals by appending one SYSTEM_EVENT COVERAGE_INTERVAL through the door, with t_end at the last verification, the producer runner-watchdog and the row's method, and the projector replaces the working row with the closed row, immutable by trigger; nothing is updated in place. It runs as `python -m runner.watchdog --store ROOT`, once or every N seconds, with `--now` for tests and replays. The design brief for the application named a watchdog subcommand under `python -m app`; it is not added there, because `app/` imports nothing from `runner/` (app/tests/test_http.py scans for such an import, so the deep-dive route cannot reach the gate by accident), and the brief's subcommand is read as this module's own command. The reason is section 8.2 item 2: coverage history cannot be reconstructed, so the closer ships before any continuous collector exists. Reverting means a subcommand under app that loads the runner module by path, which would dodge the scan rather than satisfy it. The maintainer decides whether this stands.

**9.19, 2026-11-09, the retention sweep's heartbeat lives in each case, and Step 11 lands refusing (section 8.2 item 2's neighbour, RETENTION.md RT-9 to RT-12).** `runner/retention_sweep.py` writes its RT-12 heartbeat as one SYSTEM_EVENT SWEEP_HEARTBEAT per held case through the door, with next_due read from `policy/retention.yaml`'s daily cadence step and no grace, and the case header renders the latest heartbeat whose time is not after now, the latest by time and then by arrival, against its own next_due. A case is held when its registry state is open and its case database is present. A case that is not held is listed and gets no heartbeat, because the door creates an absent case database and a heartbeat written there would recreate what was removed. A registry row that says open for a case whose database is absent makes that run exit 1, because `retain_until` cannot be enforced on a case with no database. The design has no plane-level event store and the corpus places the heartbeat in a case, so a store with no held case gets no heartbeat and has no header to render one on. The sweep decides every case before it writes anything and writes the heartbeat last. It refuses a held case whose `retain_until` or `frozen_until` it cannot read as a date, and that run exits 1. A case is due from the instant `retain_until` names. The sweep skips a held case past `retain_until` whose freeze is still in force (RT-17), and states every other held case past `retain_until` as due, refusing at the first step of RETENTION.md section 9's order that refuses: the RT-13 finding check, then the shred. A heartbeat the door refuses is reported with the door's refusal and its legal moves, and that run exits 1. It deletes nothing, takes no instant on its command line, and writes no SHRED_RECEIPT and no SHRED_FAILED, because SHRED_FAILED is evidence that a shred ran and did not verify and a refusal to start one is not that evidence. `runner/verify_shred.py` runs RT-9's five checks as dated facts, each PASS, FAIL or NOT RUN, and reports no pass while the fixture is unstamped. Check 1 reads no path and reports not_found, the failure RT-9 names, because what designates a witness ciphertext is undecided (SR-U1). Check 2 lists the blob directory on disk, fails on an object that remains, and is not run when none does, because the store records no count to compare (SR-U1). Check 3 fails before it opens anything when a file SQLite keeps beside the case database is on disk (-journal, -wal or -shm), because a rollback journal or a write-ahead log can hold pages of the case; with none on disk it opens the case file by path and passes only when the file is gone, or when every declared table errors with no such table and the file's schema lists no object; zero rows, an object the schema still lists and any other query error fail. It does not read the free pages of a database whose tables were dropped, and it does not look for such a file again after its read. Check 4 requires the skeleton rows, the shredded state and a receipt row carrying a receipt hash after the case's last stratum-1 event, and is not run when all three are present, because the receipt hash has no stated preimage (U-09). Check 5 compares a named canary's payload, claim and object counts against an inventory the caller recorded, and is not run when no canary and inventory are named (U-11). Checks 1, 2 and 4 have no passing path here, so no run reports a verified shred, and the program refuses a case the store never held and a canary that is the case itself. The header line's text carries no mark of its own; the stylesheet writes the mark on the server's flag. The reason is RT-12's own sentence, that a scheduled job that does nothing yet is a mechanism and a comment is not, and the 10-28 record's rule that Step 11 may land only refusing while retain_until and the shred stay the operator's. Reverting means removing the two modules, their eight refusal codes, their test module with its entry in `test_controls.py`, the header line and the `app/README.md` section, and restoring the control count in the app-tests gate entry's description in `tools/validate_conformance.py` and the gameplan's two register rows; nothing else depends on them. The maintainer decides whether this stands, and decides U-09, U-11 and SR-U1, which the modules name where they refuse or leave a check not run.

**9.20, 2026-11-10, the manifest gate reads a connector's command template and adapter for a write, and walks a must-fail folder (section 6.4, SS-14 item 3, SS-10).** Section 6.4 keeps one CI check, and `tools/validate_manifest.py` is that check with the doctrine checks a schema cannot express. Two join it. `--all` walks `conformance/connector-harness/must-fail/`: each manifest there must refuse with the code its `.expect` file names, and the walk reads every entry of the folder or refuses it, so the fixture SS-10's last paragraph asks for cannot leave the walk by being renamed, moved or deleted. Every manifest's `command_template` and the `adapter.py` beside it are read for a write. The adapter is parsed with `ast` and never imported or executed. A write verb on `requests` or `httpx`, on a client the file binds or on a name that ends in session or client refuses, and so does a command line that carries a write method or, after curl or wget, a body flag (MANIFEST_ADAPTER_WRITE_VERB). This is a shape check over names and literals in one file, and it is not the mechanism SS-14 item 3 describes in full, since a manifest declares no methods to check an adapter against. What the check can see it is not reading it prints as NOT READ and never refuses, and what it cannot see it passes without a word, so a pass is no finding that a connector writes nothing; the live canaries, the dispatch scanner and the subject gate remain the controls on what a connector does. A connector author meets the check as a refusal that names the line, the rule and the moves. Readings MF-R18 to MF-R22 in the tool carry the rules and their costs. Four of them are the maintainer's to decide: whether OPTIONS counts as a read, one false refusal the client rule keeps, the name rules refusing an object that is no HTTP client, and NOT READ lines showing in a direct run and in the pre-commit hook and not in the kernel gate's listing, in CI or in the conformance runner's DECLARE rung.

**9.21, 2026-11-11, the store writes only into a held case (section 8.3, RETENTION.md RT-3, RT-5 and RT-10, amendment 9.19).** A case is held when its registry state is open and its case database is present, the rule 9.19 gave the sweep, which now reads it through the door's own function. Every entry point that writes into a case refuses a case that is not held (CASE_CLOSED_TO_WRITES). `ingest_batch` in `app/store/ingest.py` is the entry point for events, whatever their origin: a corpus file, an analyst act, the watchdog's closing event or the sweep's heartbeat. It refuses before the stored log is read, so a batch that would change nothing is refused too, and a closed case is never reported as holding what was sent. The case database's file name is built from the case id in lower case and the registry's key is not, so the rule reads every registry row whose id names that file: another spelling of a closed case's id is refused with it, and a batch under another spelling of an open case's id is refused with CASE_ID_SPELLING_DIFFERS, because it would open a second registry row and a second retention clock under RT-5 onto one case database. The write holds the rule again before its attach, attaches a registered case without create and reads its file again after the attach, so a case database that is gone by then is refused and never recreated, and reads the registry's state, its spellings and the file's presence again under its write lock. A first batch refused under the lock keeps the case database it created when a registry row names that file by then, because another ingest registered it and wrote into it; before this change the rollback removed it, which on a system that lets an open file be deleted would delete that case's database. A file the rollback cannot remove, because another connection holds it open, is left, and the error that rolled the write back is the one its caller sees. The HTTP routes that write, the acts and the workspace store, refuse in `case_store` with a 409. `rebuild` in `app/store/replay.py` rebuilds only held cases and names each one it leaves alone once as NOT HELD with what the registry says of it, and `rebuild --verify` compares only the cases its copy rebuilds and says so when that is none. The library functions behind those entry points, `kv.put` and `replay_case`, read no registry state of their own: they attach without create and rely on their callers for the rule. Before this change the door landed an event in a case the registry marked shredded and created an absent case database, measured by the first read of item 7 on 2026-11-09, and the workspace store, the rebuild and the write's attach each wrote into a closed case or recreated a removed database, measured by the second-model reads of this change on 2026-11-11, so 9.19's reason for the sweep writing no heartbeat into a case that is not held, that the door would recreate what was removed, now reads: the store refuses it. The watchdog's closing event for a coverage row left open in a closed case is refused and reported, and the row stays open, because coverage rows are stratum 2 and outlive the case's material. A case database on disk with no registry row naming it is still written into by a first batch, which RT-10's reconcile job, not built, is to find. `python -m app rebuild --verify` still stops on a store holding a case whose database is gone, because the copy it verifies against reads every registry row; that predates this change and waits on what a migration does with a closed case, whose stratum-2 rows must survive it. The reason is RT-3's shred unit and RT-10's receipt: a shred removes a case's material and leaves the registry row as its record, and a store that writes into a shredded case puts back what the shred removed, with no receipt to say so. Reverting means removing the two codes with the one HTTP status, the rule's functions and their call sites in `app/store/ingest.py`, the write rule in `app/http/routes.py`, the attaches without create in `app/store/kv.py`, `app/store/replay.py` and the write, the rebuild's filter, `not_held` and the verify's comparison set, the NOT HELD line and the verify's summary in `app/__main__.py`, the rollback's two rules, the sweep's delegation in `is_held`, twenty-three controls with their checks in `app/tests/test_door.py`, `test_watchdog.py`, `test_acts.py`, `test_kv.py` and `test_spine.py`, the `app/README.md` section, and restoring the control count in the app-tests gate entry's description; amendment 9.22's change to `runner/verify_shred.py` and `runner/retention_sweep.py` reads `rows_for_file` and `STATE_NOT_NAMED` from this one, so it goes first. Where the guard lives was left to the shred's design (the handoff's section 4); this change puts it at every entry point that writes, and the maintainer decides whether it stands there.

**9.22, 2026-11-11, the sweep reads the pin when a refusal needs it, reports a registry state the schema does not name, and verify_shred reads a case under any spelling of its id (amendment 9.19).** Three observable behaviours of `runner/retention_sweep.py` and `runner/verify_shred.py` change, each an open finding of the third read of item 7 on 2026-11-09. A run reads the pin of record only when a refusal needs it, and no run of this draft reaches one, because the RT-13 finding check refuses first; before this change every run read the pin, so a missing pin reader stopped a run that had nothing due before its heartbeat, which RT-12 asks for on every run. A registry state the schema's CHECK does not name is reported as such and makes the run exit 1, where it raised a KeyError before any heartbeat. A case id is read under any spelling of its letters, because the case database's file name is built from it in lower case, and the registry's spelling is used for every check; before this change an id in upper case was refused as never held, which states something false about a case the store holds. The four behaviours the third read found without a control of their own now have one each, and the run's decision and its write are two functions so that the order RS-R7 states can be broken by a control. The reason is the read's findings, each recorded on 2026-11-09 as his to order fixed, and the parent's audit of 2026-11-11, which listed them as buildable. Reverting means restoring the eager read of the pin, the strict lookup of a registry state, the exact lookup of a case id, and the single sweep function, removing eight controls with their checks from `app/tests/test_retention_sweep.py`, and restoring the control count in the app-tests gate entry's description. The maintainer decides whether this stands.

**9.23, 2026-11-12, the verify copies held cases only, and a migration refuses a store holding a case that is not held (amendment 9.21, RETENTION.md RT-1 and RT-10).** The maintainer adopted option B2 of the options read for amendment 9.21's second open question, by his click "Yes, adopt B2" in the PLAINSIGHT chat on 2026-11-12. `replay_into` in `app/store/replay.py` has two uses, kept apart by its `held_only` argument. The verify passes it true: the copy takes the cases `held_cases` returns, the registry saying open and the case database present, and never reads a case it leaves out, so `python -m app rebuild --verify` on a store holding a case whose database is gone names that case as NOT HELD, compares the rest, adds how many it did not compare, and exits 0. Before this change the copy read every registry row and stopped on such a case with an uncaught error, finding 14 of the second-model read of 2026-11-11, which amendment 9.21 recorded as waiting on what a migration does with a closed case. The migration use, the default, refuses a store holding any case that is not held with MIGRATION_CASE_NOT_HELD before the destination is written, because a copy that left the case out would drop the registry row, skeleton rows and receipt RT-1 and RT-10 keep. What a migration carries for a closed case is left to the shred's design, which has to state the end state of a shredded case on disk, its surviving rows, the receipt's preimage (U-09), what becomes of a failed shred, and where a copy of case material may exist outside LOCAL. Whether the verify should exit 1 on a registry row that says open for a case database that is gone, as the sweep does under amendment 9.19, is the maintainer's to say; it exits 0 and names the case. Two checks with their controls in `app/tests/test_spine.py`: the verify on such a store, whose breaker makes the copy take every case, and the migration's refusal, whose breaker removes it; the control "a verify that compares every case" widens the copy as well, since a case not copied has no database to compare. Reverting means restoring `replay_into`'s read of every registry row, removing `held_cases`, the refusal and its code, the summary's count in `verify_lines`, the two checks with their controls and the breaker's widening, and this paragraph. No stored row changes, because a verify writes only to its scratch store.

**9.24, 2026-11-13, the showcase front end, a second front end beside the classic one (sections 3, 3.0, 3.1 to 3.6, 5.2, 7.4, amendments 9.7 and 9.10).** `python -m app serve --ui showcase` serves a second front end, `app/showcase/`, over the same routes and API, and the classic front end of slices 1 to 3 stays the default. It draws the seed as a profile page in the idiom of the 2026-11-02 social-platform pass, which the maintainer worked through over eight rounds on a private canvas and tabled with adjustments still to come. Eight behaviours depart from the sections above. First, the shell of section 3.0 (ROSTER on the left, ARRIVALS and INSPECTOR on the right, the RUNS strip at the bottom) becomes a profile header with seven tabs, Overview, Timeline, Connections, Sources, Places, Tools and Assessment, which are DOSSIER, CHRONOLOGY, WEB, STREAM, MAP, COLLECTION and DRAFT under the keys 8.6 and 9.10 give them; the Lineage Drawer stays a full-width bottom drawer. Second, the case header's states become one line of chips, each a consequence in a few words that opens the server's own sentence verbatim with what it means; red and the hatch appear only on the server's flags, and a token that every node or every claim carries is stated once for the web or the card rather than on each. Third, WEB keeps a deterministic radial layout with no force simulation and no weight, and departs from the fixed sector angles of `app/model/layout.py`: ring one takes the sector order clockwise from the top with each arc sized by the nodes behind it, a cluster sits beside the ring-one node it holds, a node further out sits beside its parent, and each pair of nodes carries one line and one label in words, with every link's own sentence in the side panel; a revoked link is solid and darker, labelled revoked, because dotted is deleted by section 5.2. Fourth, STREAM is one feed per producer in the log, the connector's led by its runs, because the corpus holds one connector. Fifth, CHRONOLOGY lays out one lane per kind of actor over the case's window with a mark per minute and the verified coverage as a band, rather than one lane per account, because the corpus holds one account; every time is COLLECTED on the runner's clock and the page says so. Sixth, MAP stays reachable with a count of 0 and states why no map is drawn, where the 11-02 board disabled the tab. Seventh, COLLECTION shows what ran and what decided and claims no health state, because no route served CONNECTOR_HEALTH when it was built; amendment 9.25 adds one, and the showcase does not read it yet; it lists every mechanism's state in the server's words and counts every event in the case from the rollup, marking those no route reaches. Eighth, DRAFT is read-only: each sentence with its citations, what has happened to them and the chain to the authorization, and no writing surface or export. The showcase reads through GET routes only, at most four requests open at once and a dropped request tried twice more, draws a part that still does not arrive as a calm note with a retry, guards its first load with a classic script that reloads once when the module graph does not arrive, writes no workspace state, keeps the tab, the selection and the open drawer in the URL fragment, and uses system fonts, because the CSP admits no web font. Its request layer is checked under node, where node is on PATH, which adds one process site in a test module to what the dispatch scan lists. On the maintainer's request of 2026-11-13, `--overlay` serves a file of fictional display stand-ins that the page draws over the corpus's placeholders, marked FICTIONAL PERSON with a switch back to the stored values, or, when the file sets its presentation to live, drawn without the page's own test, fictional and placeholder labels for a presenter's screen, with the case strip, the process events and the system blocks hidden and each claim's provenance folded; a case pack in the file answers every API request for one fictional case in the page, so nothing reaches the store; with one set the label is not a switch, because nothing stored stands behind a whole case, and the help panel says the case is answered from a display file, while the page's other sentences are the product's own and still speak of the store; the pack's reader refuses, in every string, an email outside the reserved domains, a phone number outside 555-01xx written in the North American shape, led by a plus sign or as a bare run of ten or eleven digits, a link and a coordinate key; a name or a handle is not checked and a number written as a JSON number is not read, which the reader's docstring states; the file lives outside the repository, the store and every git working tree, its reader admits placeholders only, reserved email domains, 555-01xx numbers and handles that are not the subject's plain name, and nothing it holds enters the store. `/keymap.json` answers ROUTE_NOT_FOUND for a front end that ships no keymap. The reason is the maintainer's request of 2026-11-13 for a front end that looks and works like a proper social web tool for that day's showcases, built from the 11-02 pass, the UI/UX harvest of 2026-10-05 and this document. Reverting means removing `app/showcase/`, the `--ui` option and its two parameters in `app/http/server.py`, the `UIS` table and the static root parameter in `app/http/routes.py`, `app/tests/test_showcase.py` with its twenty-nine controls and its entry in `app/tests/test_controls.py`, `app/http/overlay.py` and the `--overlay` option, the `app/README.md` section, and restoring the control count in the app-tests gate entry's description. The maintainer ruled on 2026-11-14 that this amendment stands as a second front end beside the classic one: his click "All as recommended" at 14:31:34 EST on the parent session's roll-up of that day, whose item 13 reads "amendment 9.24 stands as a second front end beside classic, and the profile idiom follows after slice 4". Whether the 11-02 idiom becomes the design's direction is his separate decision, which that ruling places after he has seen slice 4 in it, and this amendment does not make it.

**9.25, 2026-11-14, the COLLECTION board on key 5, and the RT-11 line states its evidence and its limit (sections 3.5, 7.1 and 7.4, amendments 9.12 and 9.19, EGRESS.md EG-1, RETENTION.md RT-11).** The maintainer ruled slice 4's three decisions on 2026-11-12 by his clicks "Yes, 1C", "Yes, 2A" and "Yes, 3B" in the PLAINSIGHT chat, on the options read of that day. First, `GET /api/cases/{case}/collection` and the view `/c/{case}/collection` on key 5 serve the COLLECTION board, read-only, from `app/model/collection.py`. Its rows come from two sources and each says which: the manifests under `connectors/`, one row per manifest folder, read from the working tree on every request, and the case's SYSTEM_EVENT CONNECTOR_HEALTH events. Section 7.4 draws a board of present states. This board states no present state other than UNVERIFIED, section 7.1's fifth state, as its consequence: on LOCAL no canary runs, because LOCAL executes no connector (EG-1), and in ISOLATED a recorded state would be the present one only inside a freshness window, which no manifest declares, because `schema/connector-manifest.schema.json` has no field for one and section 5.1 lets the builder pick no number (reading APP-R35). A recorded state is printed as a dated record: the state its producer recorded, its time, its producer and canary, section 7.1's definition of that state quoted as the design's, section 7.4's instruction for a SUSPECT one, its recorded reason when it carries one, and why it is not the present state. The board vouches for no recorded state, so red and the hatch mark every record and every present state, on the server's flags; marking a HEALTHY record apart from the others is the maintainer's to choose. A record of the connector as a whole is one stream: the latest, by time and then by arrival, supersedes the earlier ones, which are counted and not listed. An endpoint or subscription record names no endpoint, because the payload carries none, so two of them may concern two endpoints and neither supersedes the other: they are grouped by the state they record, the latest of each state is shown with the count of that state's records, and a SUSPECT record is never hidden behind a later record of another state. A record dated after now, or with no readable time, connector, probe unit or state, is set aside and counted, on the board and on the row of the connector it names (APP-R36). A record whose connector no manifest folder carries is listed apart, as recorded in this case for a connector this checkout does not carry, which is where the corpus's one health event goes. Rows are sorted by the most dangerous record they show, SUSPECT first, as section 7.4 orders them, then by id, and the line "CAPABILITY ... HAS NO HEALTHY MEMBER" prints for every declared capability, because no member is healthy here. A manifest row prints what the file declares as text: id, version, capability, kind, probe unit, canary cadence, canary names and the declared class of the canaries' target. A value YAML reads as a number, a date or a list prints as not declared as text, and a manifest's canary inputs are never printed (RT-15). A manifest that cannot be read, or declares no id, is listed under its folder's name, which the manifest gate makes the connector's id, holds the records that name it, and is not skipped, because a connector missing from a health board reads as one with nothing wrong (APP-R37). The board does not grade a manifest; `tools/validate_manifest.py` does. Not built: the filter tabs, the field-yield sparkline, differential health, the impact review, the buttons and the 30-second refresh of section 7.4. The board holds no health of a named endpoint, because no event names one. The keys act on the INSPECTOR's node, as in every view, so a record's lineage opens from its own l button. Opening the view saves workspace state under the view token collection, which the workspace store already admitted. Second, the board is case-scoped. The route sits under the case, the read takes the case as its one scope argument, and the board says its scope in words. Amendment 9.12's route set gains this one route and stays closed. The showcase front end of amendment 9.24 does not read it: its Tools tab stays as that amendment's seventh departure describes it, and drawing this board there is a later change. Where a scheduled canary's event lands, in every held case, in a plane-level store or elsewhere, is left to the runner's canary design. Third, the RT-11 line states its evidence and its limit. `halt_line` in `app/model/reads.py` reads every SHRED_FAILED in the shared skeleton, as it did, and the line now names the first one that halts, by arrival, by its case's short id, its time and its failed check, counts the others that halt, and says that this build reads no clearing because verify_shred has no passing path (amendment 9.19). On LOCAL it says that nothing dispatches in any case (EG-1). Outside LOCAL it says that no dispatch path reads the halt and that the deep-dive route refuses in every state, because the line may not claim an enforcement nothing performs. Before this change the line read "HALTED, a shred failed: no new run will dispatch system-wide (RT-11)". The read takes the skeleton alone and needs no case attached, so `GET /api/cases` carries the line and the case list shows it; before, the list showed none. This is the one read that spans cases. Amendment 9.12 says no route spans cases, and the header and the case list now name another case's short id, time and failed check, because RT-11 makes a failed shred a fact about the mechanism and not about the case. A SHRED_FAILED whose payload cannot be read as an object, or does not say whether it halts, is read as halting, because a line whose absence means no halt must not go dark on a row it cannot read; one whose payload says it does not halt is not counted, as before (APP-R38). The line is lit on every store that holds the corpus, whose log carries one failed shred, and nothing in this tree clears it, so the case list can show a case as open, from the registry, beside a line that says its shred failed, from the log. The halt's source of truth between the event and the registry state, its clearing act, where a SHRED_FAILED can be written, and which dispatch path reads the halt are left to the shred's design by name. The override that RT-11's text describes and the pin's row denies is not among them: the maintainer decided on 2026-11-14 that no override lifts the halt, and that amendment of RT-11 lands in its own commit. The reason is that the worklog entry of 2026-11-08 named this slice, the board has no dependency on the shred, and a line that is always lit and states nothing of its evidence stops carrying information. Reverting means removing `app/model/collection.py`, the route and its handler in `app/http/routes.py`, `app/static/views/collection.js`, key 5's row in `app/static/keymap.json` with its action, its view and its button in `app/static/app.js`, and `app/tests/test_collection.py` with its fifty-five controls and its entry in `app/tests/test_controls.py`; restoring `halt_line` and the header's call to it; removing the `halt` field of `GET /api/cases`, the case list's fill of the line and the sentence in the routes' docstring; restoring, in `app/tests/test_http.py`, the route walk's four entries, the header's expected line and the halt breaker's signature; and restoring the `app/README.md` text and the control count in the app-tests gate entry's description. No stored row changes, because the board and the line are reads. The maintainer decides whether this stands.

**9.26, 2026-11-14, the verify exits 1 on an open row whose case database is gone, and the HTTP routes read a case under the registry's spelling of its id (amendments 9.19, 9.21, 9.22 and 9.23).** Two follow-ups the options paper for amendment 9.21 left to the maintainer, each answered by his click "All as recommended" on the parent's roll-up of 2026-11-14, whose item 13 names both. First, `python -m app rebuild --verify` exits 1 when a registry row says open for a case whose database is gone, and prints why as a STORE FAULT line: `retain_until` cannot be enforced on a case with no database, the reading amendment 9.19 gave the sweep, which exits 1 on the same row. Amendment 9.23 left the exit code to him and exited 0. The case is still named NOT HELD, nothing of it is copied or compared, and the count of cases not compared is unchanged. A row that says shredded or shred_failed for a database that is gone is a closed case and does not change the exit code. `rebuild` without `--verify` still names the case and exits 0, which is his to say. Second, a route reads the case its URL names under the registry's spelling. A URL's case id is read in lower case, as before, and the registry key is the id as it was first sent, so a case registered under another spelling was answered CASE_NOT_HELD, the false statement amendment 9.22 removed from verify_shred. Now, when no registry row carries the URL's id exactly and one row names the same case database, the route serves that case under the row's spelling: its header, its views, its notice stream, its workspace state and its acts. Two rows that name one case database under other spellings cannot be told apart by a URL, and that request is refused as CASE_NOT_HELD with a detail that says so. The door has refused the write that would create such a pair since amendment 9.21 (CASE_ID_SPELLING_DIFFERS). Only the case id is read this way: an event, node or item id is matched as it was, in lower case. The reason is his answer, and that a route which says a held case is not held states something false to the analyst. Reverting means removing `open_and_gone` and its line from `app/__main__.py` and restoring the exit code and the check in `app/tests/test_spine.py` with its two controls; removing `registry_spelling` from `app/store/ingest.py`, `registered` and `other_spellings` from `app/http/routes.py` with the call in `app/http/server.py` and the detail in `case_store`, and the check with its three controls in `app/tests/test_http.py`; and restoring the `app/README.md` sentences and the control count in the app-tests gate entry's description. No stored row changes. The maintainer decides whether this stands.

**9.27, 2026-11-14, 2026-11-16 and 2026-11-17, a write is authorized by the page that sent it, its refusal reaches that page, and every text field keeps what is typed into it on this machine (amendments 9.12, 9.16 and 9.24, EGRESS.md EG-2 and EG-3).** A read-only second-model review of the HTTP boundary, `http_boundary_adversarial_2026-11-12_opus55_2026-11-14.md`, read the code at commit 09caa88 on 2026-11-14 for the maintainer's parent session, ran nothing, and wrote nothing in this repository; it lives outside it, beside its sha256, and every line it cites was located again on the tree this amendment builds on. Its two must-fix findings, and the hardening it found that is small enough to pair with a control, are built here. The change was built on 2026-11-14, when two adversarial verifications asked for more controls, a wider field scan, stricter header reads and a stricter reading of the pages and of sendJSON, which are built here as well. It was reworked on 2026-11-16, when it was placed on commit 59cb0cf: a last reader of 2026-11-15 had left two should-fixes, six notes and a design point open, and the rework closes them, holds the deep-dive route to the application's environment, reads a repeated Host, Cookie or Content-Length as a repeated Origin is read, and builds the review's finding 8. A second reader ran the rework on Windows and on Linux on 2026-11-16, found no must-fix, and left six should-fixes, which are built on 2026-11-17: the socket's options are chosen per platform, the discard after an answer other than the four write rules' and its one second each gain a control, a cookie value holding a character outside ASCII is a wrong token where it was a fault, a port the platform refuses to bind is refused with its moves, and the account of the discard names its one exception. First, a POST or PUT is authorized by the page that sent it as well as by the session cookie (its finding 1). A page on another port of this host is the same site, so the browser attaches the cookie to that page's requests under SameSite=Strict, and its browser names this server in Host, so neither the token nor the Host check of amendment 9.12 refused it; a POST it sends as text/plain needs no preflight, and the server parsed any body as JSON, so with LOCAL_ACTS set such a page could mint an act into the case. Each write rule is now decided before any byte of the body is read: the server refuses with ORIGIN_REFUSED a write whose Origin header is present and is not exactly its own origin, http://127.0.0.1:<port> or http://localhost:<port>, the two spellings the Host check accepts, and one whose Sec-Fetch-Site header is present and is neither same-origin nor none; with TOKEN_REFUSED one whose cookie does not carry the launch token, as before; and with CONTENT_TYPE_REFUSED one whose Content-Type is not application/json, alone or with charset=utf-8. A header sent on more than one line is read as one value, its lines joined by a comma, as HTTP combines repeated field lines, and no rule admits that value, so no one of its lines can stand for the request, even when each is admissible: a Host, Origin, Sec-Fetch-Site or Content-Type sent on two lines is refused under its own rule, and a Content-Length sent on two lines gives no length, so its write is refused with BODY_REFUSED. A Cookie sent on two lines carries no token, because the cookie parser reads a joined value as one cookie list in which the last value of a repeated name wins, so joining its lines would let the last one stand for the request. Only spaces and tabs around the Content-Type's parts are ignored, as HTTP's optional whitespace. A write that carries neither Origin nor Sec-Fetch-Site, as a command-line client and the test client send, is admitted on the cookie and the Content-Type, where the review asked for a refusal in a browser context, which a server cannot tell from the request. That does not reopen the cross-port case: a browser sends Origin on every POST and PUT, so a page on another port presents a header the rule refuses, and a browser that sent neither could send a write from another origin without a preflight only as a POST of text/plain, application/x-www-form-urlencoded or multipart/form-data, or with no Content-Type, each of which the Content-Type rule refuses, while a POST of application/json, and any PUT, needs a preflight, which the server refuses, since OPTIONS answers METHOD_REFUSED. The classic front end sends its writes through one fetch in the default cors mode, the one mode fetch offers in which a page served with Referrer-Policy: no-referrer sends its own origin on a POST rather than null, and no file of that front end names a request that could write anywhere else. Second, a refusal reaches the page that sent the write. The answer is written before any byte of the body is read; the server then half-closes, reads and discards what the client sends of the body, never parsing it, up to the declared Content-Length capped at MAX_BODY and for at most DISCARD_SECONDS, and closes. Any answer written before a declared body is read, a Host refusal and BODY_REFUSED for a Content-Length past MAX_BODY among them, is followed by the same discard; the notice stream holds its connection until it ends, a stream the server stops is closed without the discard, and one its client closes, or one a fault ends, reaches the discard once it is over, which finds no body to read from a page's stream, since that stream declares none; and a request the standard library's parser refuses before routing is closed at once, as before. Until 2026-11-16 the server closed at once with the body unread, and a body still on its way met a reset: with the test client's body 50 ms late, the last reader saw all four write checks fail with ConnectionAbortedError on the Windows workstation, whose stack drops an answer it has received when a reset arrives, so a page whose write was refused, for a stale token after a restart for instance, would see a network error in place of the refusal and its moves. RFC 9112 section 9.6 describes this staged close and gives no number for it, and the design gives none. DISCARD_SECONDS is one second, a reading of 2026-11-16 that awaits the maintainer's confirmation: in 800 POSTs from http.client measured on this workstation that day, the body reached a server that had already read the head in 758 and came at most 0.62 ms after it; the controls see a refusal reach a client whose body comes 200 ms late; and a client that declares a body and never sends it holds one server thread for one second after its answer was written. A control holds the deadline from above as well as from below: timed from the server's side, the discard for a client that sends nothing after its head must end within half a second of the deadline, because a discard that waited twice as long left every check green until 2026-11-17. The alternative, kept on record, is the plain close, with every test's refused write sent in one send. It keeps the tests deterministic, and it leaves a real page whose body follows its head to meet the reset and see a network error in place of the refusal. Third, every input and textarea the two front ends build, the act forms, the Merge Sheet's notes and the showcase's search box among them, carries spellcheck="false", autocomplete="off", autocapitalize="off", autocorrect="off" and translate="no", which each front end's element helper sets after the caller's attributes, and both pages carry translate="no" on the document and the notranslate meta (finding 2): a browser's spellcheck and translation can send typed text to a remote service, and its autofill keeps typed values in its form history, outside the store the shred reaches, two channels the egress guard cannot see. Fourth, smaller changes: the session cookie's name carries the port, because a browser keeps one cookie per name for a host whatever its port, and a second launch's page overwrote the first one's token (finding 4); every response adds Cross-Origin-Resource-Policy: same-origin (finding 5) and Permissions-Policy: camera=(), microphone=(), geolocation=(), and the CSP adds form-action 'none', because every form here is sent by script (finding 9); a route's own header no longer replaces a security header (finding 9); an exception raised outside the dispatcher is logged by its type name and prints no traceback (finding 7); HOST_REFUSED's text names DNS rebinding and says that a page on another origin passes the Host check, where it said that a page served from another origin cannot read the server (finding 6); the launch token is compared with the cookie's value as bytes, because hmac.compare_digest raises a TypeError for a string holding a character outside ASCII, and a cookie whose value held one was answered SERVER_FAULT where it carries a wrong token; and the listening socket shares its port with no other socket, by options chosen per platform (finding 8): where the platform offers exclusive use, which is Windows, it is bound with SO_EXCLUSIVEADDRUSE and with SO_REUSEADDR off, because there SO_REUSEADDR, which the standard library's HTTPServer sets, lets another process that sets it too bind the port this server holds, and elsewhere with SO_REUSEADDR on, as the standard library and socket.create_server bind it; SO_REUSEPORT is off everywhere. On this workstation on 2026-11-16, with the standard library's bind a second server that set SO_REUSEADDR bound the port a first one held, and with SO_REUSEADDR off, or with exclusive use, it was refused; the exclusive use, which Microsoft documents as refusing every second bind whatever its options, is therefore read from the socket rather than shown by a second bind. On Linux the second reader saw on 2026-11-16, in a container with no network running Linux 6.6 and Python 3.12, that a second server that set SO_REUSEADDR was refused whether or not the first set it, and that only SO_REUSEPORT on both shared a port, so there SO_REUSEADDR off refuses nothing that SO_REUSEPORT off does not; and that with SO_REUSEADDR off a server restarted on a port that had just served one request was refused for 60.3 s, where with the standard library's bind, which the Linux branch now makes, it bound at once. The rework of 2026-11-16 set SO_REUSEADDR off on every platform; since 2026-11-17 it is off only where exclusive use exists, as socket.create_server leaves it off on Windows alone. The build of 2026-11-14 left finding 8 unbuilt, because a hardened bind can be seen to hold on Windows only and this repository's CI runs on Linux, and because exclusive use on Windows was said to refuse a restart on a fixed port while old connections close. The first reason is met by a check of the bind that runs on Windows and is skipped elsewhere with its reason stated, beside a check of the socket's options that runs everywhere and, on Windows, reads the branch the other platforms take as well, from a server bound as they bind. The second was not observed on Windows: measured on this workstation on 2026-11-16, a listener bound for exclusive use was bound again on its port 0.4 s after a predecessor closed with a server-side connection in TIME_WAIT, as listeners with SO_REUSEADDR and with neither option were, and the second reader saw a restart bind at once while a client still held its end of an old connection. On Linux the same cost was real for SO_REUSEADDR off, as the second reader observed, and the Linux branch above avoids it. The server binds a free port unless --port names one, and a port the platform refuses, one another socket listens on among them, is refused with BIND_REFUSED_PORT, which python -m app serve prints with what was refused, the rule and the moves, where until 2026-11-17 the bind's error reached the operator as a traceback. The Host check, the token check and the cookie's HttpOnly, SameSite=Strict and Path=/ had no control that removed them, and each now has one (finding 3). The deep-dive route's consequence is held to the environment the application read at launch by a check of its own, as the header, the case list and the COLLECTION board are, because a hand mutant that passed LOCAL to the route's read survived the suite until that check. The checks: in `app/tests/test_http.py`, one each for the Origin, Sec-Fetch-Site and Content-Type rules, the last with CONTENT_TYPE_REFUSED's corrected rule, the Host check, the token, a cookie value outside ASCII among the wrong ones, the cookie's attributes, two launches on one host, the header precedence, the exception outside the dispatcher, a refusal that reaches a client whose body comes late, after a Host refusal and BODY_REFUSED for a length as after the four write rules, a refusal answered before any byte of its body arrives, with each discard ending at its client's close, the discard's byte and time bounds, its deadline timed from the server's side, and a connection closed at once after a body the server read, a repeated Host, Cookie or Content-Length, the listening socket's options on each platform's branch, a second bind to its port, a port another socket listens on and the deep-dive route's environment, beside the security headers' check, with fifty-six new controls among them; in `app/tests/test_static.py`, a scan of both front ends that refuses a field written as markup without the five attributes, its attributes read as an HTML parser reads the tag, one made by createElement outside the element helpers, however the call is written, or with a tag the scan cannot read there, a customized built-in element, in a script that names customElements, which must register one before it can be made, or that names HTMLInputElement or HTMLTextAreaElement other than in an instanceof test, an editable surface, and a script that names one of the five outside the helpers' list or writes a method named translate, and that reads the attributes in each helper, and in each page as an HTML parser reads it, outside any noscript or template element, and pins the text of el, h, s, svgNamespace, apply and append, and a check that the classic front end's writes keep the cors mode and application/json, with no mode named, headers and credentials named once each and no other object spread or assigned into the options, and that no file of it names a request that could write outside sendJSON, with forty-three controls; and in `app/tests/test_showcase.py`, a write scan that reads the word method alone, as the classic front end's scan does, so a method written as a shorthand property or a quoted key is refused, with one new control, for which `app/showcase/views/timeline.js` renames a local variable the word would have matched. The application's controls number 369, one hundred more than the 269 at commit 59cb0cf. A confirming reader of 2026-11-17 saw the held-port check pass with the platform's message in the refusal's detail in place of the error's code; the check now reads the code, and a control that puts the message there fails it; a second reader of that day found BIND_REFUSED_PORT's rule still saying that every port in use is refused, and a control restores those words, so the controls number 371. The late-body check reads the two platforms differently: a Windows client loses the answer when the reset arrives, and a Linux client reads it and keeps the reset as the socket's pending error, which the check also reads. The scan reads source text, so a tag, a name or markup assembled at run time from pieces is not read, and neither is a script that removes a node's attributes by walking them without naming one. The security headers' check no longer asserts the cookie's attributes and the Host refusal, which moved into the checks above. No browser was run: the emission of Origin and Sec-Fetch-Site, preflights, CORP, form-action, the effect of the five attributes and a browser's reading of the discard are argued from the standards. Not built, each the maintainer's to decide: a request timeout beyond the discard's deadline, which needs a number the design does not give and would bound a client that holds a connection open without declaring a body, which the discard does not reach; in_course_of among the guard's value keys, which would hold the corpus's word citation as case material, where closing the field to the three tokens amendment 9.16 names is the narrower fix; dropping the localhost spelling from the Host check, which the Origin rule mirrors and HOST_REFUSED's moves name; a log line for a request the parser refuses, which the review called an observability note and not a leak; and Cross-Origin-Opener-Policy, which the review offered as a consideration and no finding needs. The write rules do not stop a page on another origin from reading, which the same-origin policy and Cross-Origin-Resource-Policy do; they do not authenticate a client that is not a browser beyond the cookie it presents, which the page route sets for any client that names this server in Host; and they do not set LOCAL_ACTS, which stays the maintainer's decision under amendment 9.16, the decision the review placed after its finding 1. The rules also leave a page on another origin able to open this server's own page at a URL it chooses: that page's boot saves the URL's view state, an id, a hop count of 1 to 3 and the drawer's state, through a write the rules admit, because this server's own page sends it, while an act and the deep dive start only from a key or a click. Reverting means removing ORIGIN_REFUSED and CONTENT_TYPE_REFUSED with their statuses, `json_content_type` with `OWS`, `with_security_headers`, `WRITE_FETCH_SITES`, `DISCARD_SECONDS`, `App.authorities`, `App.origins`, `App.cookie_name`, `Server.handle_error`, `EXCLUSIVE_USE`, `Server.server_bind` with the two reuse attributes, `bind_server` with BIND_REFUSED_PORT, `Handler._header_value`, `Handler._discard_unread_body` with its call and its flag, and the three write checks from `app/http/server.py`, with the token compared as text again and the reads of Host, Cookie and Content-Length restored to their first line, the two headers and form-action from `SECURITY_HEADERS`, the five attributes and the lines that set them from `app/static/app.js` and `app/showcase/lib/dom.js`, and translate="no" and the notranslate meta from both pages; restoring the text of HOST_REFUSED and TOKEN_REFUSED, BODY_REFUSED's detail for a Content-Length and the cookie's unqualified name; removing the checks and their controls named above, the test client's header argument and `merge_headers` in `app/tests/served.py` and the `app/README.md` sections; restoring the write scan in `app/tests/test_showcase.py` and the variable's name in `app/showcase/views/timeline.js`; restoring the session cookie and Host assertions in the security headers' check; and restoring the control count and the suite's time in the app-tests gate entry's description. No stored row changes. The maintainer decides whether this stands, and whether DISCARD_SECONDS stands at one second.

**9.28, 2026-11-18, the egress guard compares what can carry a case value, a cookie another app set stops no write, every text field opts out of writing suggestions, and a port outside the range and a uuid followed by a newline are refused (amendments 9.12 and 9.27, EGRESS.md EG-2 and EG-3).** A read-only review of the HTTP boundary, queued as P6 on the maintainer's team account and run there, read the tree at commit 1393687, ran nothing in this repository and wrote nothing in it; its file, `http_boundary_adversarial_2026-11-12.md`, lives outside the repository beside its sha256. The PLAINSIGHT lane weighed it against commit 34c442b on 2026-11-18, on the maintainer's click "Yes, review it" in the PLAINSIGHT chat, and built the five findings this amendment names on his click "Yes, build them". A second-model read of the build on 2026-11-18 returned two must-fixes, both taken here: a query the route's shapes refuse is compared whole, so a held value whose own text holds & or = is not split and missed, and a Location's parts are compared as a request's. Commit 34c442b changed no executable line the review read, so each finding stands at it as written. First, the egress guard compares a held value with what can carry a case value, and, outside the two places named below, no longer with this server's own words (its A1). The guard holds every string of six characters or more that a case's payloads carry under a value key, the text of an analyst's note among them, and matches each as a substring, so a held value that is an ordinary word matched a route's literal segments, a static file's name, a Content-Type, a header's name, a refusal's governed prose or a notice's kind on every request. A note whose text was static refused every script and style sheet of both front ends; one whose text was Cookie stripped the session cookie from the page and replaced TOKEN_REFUSED with EGRESS_GUARD_REPLACED. The effect held for every case in the store, since the guard holds every case's values, and it outlived a REVOKE, since every payload stays held. Where acts land, which is ISOLATED and, once the maintainer sets LOCAL_ACTS, a synthetic case on LOCAL, one typed word reached it, and the way back was to build the store again, which loses every act typed into it. The 22 strings the guard holds from the must-pass corpus, the one file a LOCAL store ingests, occur in none of these words, by a count of 2026-11-18. The server now compares the parts of a request target that `routes.request_parts` names, which are each path parameter and each query key and value except a route's literal segments, a view token, the name of a file the front end serves, a query key the route takes, and a hops, sector, view or dir value of its closed shape; a header's name unless it is Content-Type, Set-Cookie or Location, the three the routes send; a header's value unless it is a Content-Type the routes name or this launch's session cookie; a Location's parts, as a request target's; a refusal's detail, and not the registry's text, rule and moves; the page title and a route's own error body, as before; and a notice's parts other than its schema's own words. A target whose path matches no route, or whose query the route's shapes refuse, is compared whole. Two places still compare a server word whole, and no fix here reaches them: a refusal's detail, which can name a header, a query key or a workspace key, and the deep dive's own refused body; a held value that is such a word still replaces that refusal with EGRESS_GUARD_REPLACED. This amendment reads the change as Class C, a precision rule of the guard and not an exemption: every part that can carry a case value is compared, and what is no longer compared is the server's own text, which no request or case reaches. The precedent is reading VA-R6, which the maintainer decided Class B on 2026-10-28 as a precision rule of a scanner. Whether this change is Class C is the maintainer's to decide. Second, the session cookie is read pair by pair (its A4). A browser sends every cookie it holds for 127.0.0.1 in one header, whatever the port that set it, and the standard library's cookie parser, which read the token, read no cookie at all from a header that held one it rejected, such as a value with a space, or a bare value or a value in JSON before the token. A cookie any other app on this host set therefore stopped every write until it was cleared, and TOKEN_REFUSED's moves did not cure it. The token is now carried when one pair under this launch's name holds it; a pair another page set under that name cannot hold a token it does not know, and a Cookie header on two lines still carries none. Third, every input and textarea either front end builds also carries writingsuggestions="false" (its A3). Microsoft Edge's text prediction offers to complete what is typed in a text field, and from version 124 a page turns it off for a field by that attribute, by Microsoft's Edge blog of 2024-04-23. Whether the prediction sends typed text off the machine, and whether spellcheck="false" already turns it off, were not checked; the attribute keeps what is typed on this machine either way. Fourth, two edges (its A15 and A10). A --port outside 0 to 65535 is refused with BIND_REFUSED_PORT and its moves, where the standard library's OverflowError, which is not an OSError, reached the operator as a traceback. `db.UUID_RE` ends in \Z, because every caller uses match and $ also matches before a final newline, so a uuid followed by a newline was stored as a workspace focus and passed the query check, while reaching no sink. The checks: in `app/tests/test_http.py`, one that lands four notes through the acts route with LOCAL_ACTS set in memory, whose text is a word this server writes, static, javascript, Cookie and coverage, and asserts that the script, its Content-Type, the session cookie, TOKEN_REFUSED and a coverage notice each answer as they do with nothing held, while a held word sent as a focus is still refused, with five controls, one for each part the change stops comparing; one that writes with a cookie another app set beside the token, before it and after it, in five shapes, with a control that reads the token through the standard library's parser again; one for a port outside the range, through make_server and the serve command, with a control that catches OSError only; and one for a uuid followed by a newline, in the workspace route and in the query, with a control whose pattern ends in $. In `app/tests/test_static.py`, the sixth attribute is in the expected list and in the name scan, with three controls: either helper's list without it, and a planted script that turns it on. The application's controls number 384, thirteen more than the 371 at commit 34c442b; the A1 check also holds dossier and people, a refused query holding a made-up locator, and the redirect to the landing view, with two of the thirteen controls for the last two. No browser was run: Edge's reading of the attribute is from Microsoft's documentation, and a browser's Cookie header from RFC 6265. Not built, each the maintainer's to decide or the lane's next change: a credential on reads, or a recorded decision that the loopback is the trust boundary on a deployment that holds case material (its A2); the page rule on reads (A5); a deadline before the answer (A9, which needs a number); one shape for each workspace key (A8); act keys after the window gains focus and Cross-Origin-Opener-Policy (A7); closing in_course_of, entity_type, anchor_selector_type and band at the acts route, which the model already refuses as ACT_REFUSED_BY_MODEL, so that the review's sequence for its A6 lands nothing; its nits A11 to A14 and A16 to A19, and A15's other half, a --port of 80, which binds and then refuses every browser request; the server words still compared inside a refusal's detail and the deep dive's body; controls for the half of the guard that is still compared (the second read's S1); and the notice schema's uuid pattern, which still admits a uuid followed by a newline. Reverting means removing `routes.request_parts`, `query_refused`, `VIEW_WORDS`, `WORD_KEYS` and `SERVER_CONTENT_TYPES`, `server.cookie_values`, `SERVER_HEADER_NAMES`, `server_header_value`, `location_parts` and `refusal_variable_text` with their calls, `notices.notice_parts` with its call, and bind_server's OverflowError branch, so that the guard compares the whole target, every header, the whole refusal body and the whole notice again and the token is read through SimpleCookie; restoring $ in `db.UUID_RE`; removing writingsuggestions from both helpers' lists, from the name scan and from the expected list in `app/tests/test_static.py`; removing the checks and their thirteen controls named above; restoring the docstrings of `app/http/guard.py`, `app/http/server.py` and `app/http/notices.py`, the comments of both helpers and the sections of `app/README.md` this amendment changed; and restoring the control count in the app-tests gate entry's description. No stored row changes. The maintainer decides whether this stands, and whether the guard's change is Class C.

**9.29, 2026-11-18, three reading aids in the showcase for a first viewing (amendment 9.24).** The maintainer chose a runbook and one lean UI pass of the showcase on 2026-11-18, ahead of a talk to leadership and operators on 2026-11-19, and the parent session passed the pass to a side session of the lane plainsight-9. It adds no route, no write, no data source, no browser storage and no external host, and it changes no rule the server enforces. First, the key to the lines on Connections, which names observed, proposed, asserted and revoked links and the corner brackets of a cluster, is drawn above the web rather than below it. Below the web it sat under the fold of a 900-pixel screen, so a viewer met the dashed lines before their meaning. Second, the Guide button shows the ? key that opens it, and the guide lists that key beside the others; the key already opened the guide and was printed nowhere. Third, the top bar keeps the case id on one line and keeps the word SYNTHETIC on screen. Before this change the case id broke into two lines at a narrow width and the search box covered the SYNTHETIC chip. The crumb no longer shrinks, the search box gives way instead, and at 1100 pixels and below the chip drops its trailing words and keeps the word SYNTHETIC, whose title still names the environment. At 720 pixels and below the chip is still hidden, as before, and the case strip still states the synthetic corpus. The Guide button's wider label pushed it off a 375-pixel screen, so at 720 pixels and below the button drops the ? mark and the analyst's name drops to its initials; at 375 pixels the page is 375 pixels wide and the button ends at 359, measured in the app's browser pane. `app/tests/test_showcase.py` reads each aid from the files, because layout needs a browser, and its CONTROLS hold twelve breaks: the key drawn below the web, the key above it without its spacing rule, the Guide button without its key, the ? key unbound, the guide without its own row, the case id free to wrap, the crumb free to shrink, the search box keeping its width, the chip's trailing words in no span of their own, a narrow screen that keeps the trailing words, a narrow screen that hides the whole chip, and a top bar wider than a phone. A second model, claude-fable-5-2, read the pass before it landed and returned COMMIT WITH FIXES; its four should-fixes and two of its nits are taken, and the read is in `Z-ISR/_session-artifacts/2026-11-18-plainsight-lane/`. Nothing was viewed on the projector's own screen.

**9.30, 2026-11-18, the Lineage Drawer names where data came from and what handled it, and reads as an audit trail (section 5.7, amendments 9.9 and 9.24).** It follows amendments 9.28, committed as `abb7778`, and 9.29, committed as `c135e4c`, and changes neither. The maintainer asked on 2026-11-18 for the lineage to make the auditing trail clearer: the named locations data came from and the tools that grabbed or processed it. Two things change. First, each chain entry's summary carries more closed fields. A PROBE_EVENT ITEM names the site its locator names, the part before the first slash, after its kind: "fetched from site <id>" for a site locator, whose first part is a site id by section 2's ITEM convention, or, for a sherlock-site locator whose site `connectors/sherlock/site_facts.json` lists, "fetched from platform <site>" with the verb Sherlock probes it by, said to be as this repository's site facts record it, which may differ from the version the run pinned, and, where the site facts record one, the host the probe is sent to rather than the displayed site. A sherlock-site id the site facts do not list is not quoted. An item whose outcome is not a hit reads "probed" in place of "fetched from", because nothing was fetched. It adds method_id and the HTTP status chain when the payload carries them, and the raw blob's sha256 shortened to 12 hex and marked with an ellipsis; where the bytes are not held, the line says the item names that digest and this store does not hold it, so it does not read as a digest of something held. A PROBE_EVENT RUN_START keeps its lines, reads its egress line as "collected through egress identity <id> on <environment> egress", and adds the machine its skeleton names as source.platform_id with the producer and its version, and the manifest hash shortened to 12 hex, marked the same way. An EXTRACT_EVENT CLAIM adds its lineage transform, read as the adapter that shaped the output. Second, the back chain's response carries a new field, audit: the same entries ordered oldest first, one row per step, each {step, label, event_id, ts, lines}, with step one of authorized, gate, collected, fetched, processed, proposed, asserted, reviewed and assessed, and a step the chain holds no event for absent. Rows are ordered on the parsed time, so a time with fractional seconds sorts after the same second without them, and two rows at one time take the order of that list, so a review follows what it acts on; an item that is not a hit takes the heading Probed. Its lines are the time and the producer that recorded the event, then the entry's summary. The reviewed rows add the VERIFY and DISPUTE acts on every claim in the chain, read with one query of the case's ADJUDICATE events, the one read the audit adds; two acts at one time keep the log's order, and the later one says it is the claim's review state now. Forward lineage carries no audit. The showcase draws audit as an AUDIT TRAIL block at the top of the back lineage's left column, one row per step with its heading in the gutter, and each heading but the head's own is a button that re-centres the drawer on its event, as an entry's button does; a chain with a break below says the trail is incomplete, and the chain's flags, such as a decision recorded after its authorization was revoked, are shown inside the trail as well as above the chain. The chain list below it is unchanged, and the classic front end does not draw the field. What is not quoted, and why: a summary line still quotes no payload value that can carry a case value. The part of a locator after its first slash carries the subject's path on the site, and a locator of any kind other than site and sherlock-site may carry a channel or another case value before its slash, so the drawer names neither and says the decoded envelope holds the locator; a claim's value, a filled argv and the full locator stay in the decoded-envelope tier, which shows them already. A review row names the act, the analyst and the claim, never the analyst's reason. The egress identity is named as an egress identity and not as a persona account, because EG-6 defines it as the environment's egress identity, and the account a platform records as having looked is the credential, which the credential line names. The site facts name a platform by Sherlock's site name, which SH-R18 records is not a name a registry of platforms has confirmed; the ontology holds no platform list, so no other mapping exists. Not built: a mapping for any other connector's sites, the classic front end's rendering of the trail, the RUN_END in the trail, which the walk does not reach because nothing is parented on it, and any acts on items or clusters other than those the walk reaches. The checks: in `app/tests/test_http.py`, one that the audit reads oldest first from the grant through the claim's reviews and that forward lineage carries none, with three controls, and one that an ITEM line names the site and never the locator's part after the slash, that a miss reads as probed, that an unlisted Sherlock site is not quoted, that no summary or audit line quotes a corpus claim value or analyst prose of six characters or more, and that Sherlock's site facts resolve a site, with five controls; in `app/tests/test_showcase.py`, one that the drawer draws the block at the top of the left column with buttons, the chain's flags and its style, read from the files, with four controls. The application's controls number twelve more, 408. A claude-fable-5-2 read before the merge returned COMMIT WITH FIXES; its seven should-fixes and two of its nits are taken, and the read is in the lane folder of 2026-11-18. Reverting means removing `audit`, `_audit_key`, `_reviews`, `_step_of`, `fetched_from`, `site_facts`, `transform_text`, `_skeleton`, `_short_hash` and their constants from `app/model/lineage.py` and restoring its three summary branches and its docstring, removing `auditTrail` and its call from `app/showcase/views/lineage.js` and the audit rules from `app/showcase/app.css`, removing the checks and controls named above and the `app/README.md` bullet, and restoring the control count in the app-tests gate entry's description to 396 since 9.29. No stored row changes. The maintainer decides whether this stands.
