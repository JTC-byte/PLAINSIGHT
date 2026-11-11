# app: the PLAINSIGHT store and its social web operating picture

This directory is Class C runtime code. It holds the case store, the ingest
door, and a stdlib HTTP server that renders one case as a focused web, a
read-only DOSSIER, PATHS, and the Lineage Drawer. Nothing here decides who may
be a subject, what may be retained, or what may leave. Those rules are in
`doctrine/`, and the validation the door applies is `tools/validate.py`, loaded
by path.

On LOCAL the store holds tracked, unmodified synthetic corpus files only (EG-2),
and no connector runs (EG-1). The SQLite store refuses to open or create itself
when PLAINSIGHT_ENVIRONMENT is ISOLATED (STORE_ISOLATED_NOT_PROVISIONED),
because the ISOLATED store is the operator's Postgres inside the VM. The deep-dive route refuses and records nothing
until a subject gate is connected to it, which is a separate change the
operator decides.

## Open the web on the corpus

The store root must be outside every git working tree. A root inside this
repository is refused with STORE_PATH_IN_REPOSITORY before anything is created,
because git history is the one store the shred cannot reach (RT-15). The
default root is `%LOCALAPPDATA%\plainsight`, and `--store` or `PLAINSIGHT_HOME`
names another.

Run these from the repository root, on a clean checkout:

```
python -m app init --store %LOCALAPPDATA%\plainsight
python -m app ingest --store %LOCALAPPDATA%\plainsight conformance/must-pass.jsonl
python -m app serve --store %LOCALAPPDATA%\plainsight --analyst analyst-example
```

The ingest lands 44 events in one case. The serve command binds 127.0.0.1 on a
free port and prints two URLs per case: the landing view, which is DOSSIER, and
the web focused on the seed. Open the web URL in a browser on the same machine.
The server refuses any other bind address with BIND_REFUSED_LOCAL.

## What the web shows and what it refuses

- Every web has a case and a focus. A request without a focus is refused with
  FOCUS_REQUIRED, and no route crosses cases.
- The canvas draws at most 300 nodes and 600 edges. Past either cap no SVG is
  drawn, and the view serves the list twin (t) and PATHS (8) instead.
- The layout is radial and deterministic: the ring is the hop count, and each
  sector has a fixed angle. No node or edge carries a weight, a score or a
  percentage.
- A proposed inference is a dashed line whose label leads with "NOT ACCEPTED".
  A proposal an analyst revoked reads "PROPOSAL WITHDRAWN". Dash means
  inference and nothing else: every node box is solid. A cluster has corner
  brackets, and a revoked one stays as a struck tombstone.
- A state line on the canvas wraps and is never cut, so its consequence always
  prints. Only a selector's value is cut to the box; the INSPECTOR prints it in
  full.
- Every node is inert. Selecting one fills the INSPECTOR and collects nothing.

## Keys

The keymap is `app/static/keymap.json`, one source for the app and the docs.
This slice builds j and k, Tab and Shift+Tab, l (or Ctrl+click), Shift+L, esc
esc, ??, 7 WEB, 1 DOSSIER, 8 PATHS, f refocus, v mark, + and - hops, t the list
twin, and p the Pivot Bar. Slice 3 builds the act keys, Enter, e, i, n, ?, m, x
and Backspace, which the Acts section below describes. When a button has
keyboard focus, Tab and Shift+Tab move focus and Enter presses the button;
elsewhere they run their keymap bindings.

## Routes

Every URL carries uuids and fixed words only. The query keys are focus, hops,
sector, view, lineage, dir, after, from and to; any other key is refused with
QUERY_KEY_REFUSED.

- GET `/`, `/c/<case>/<view>`: the page. The views are dossier, web, paths and list.
  GET `/c/<case>` redirects to `/c/<case>/dossier`, the landing view.
- GET `/static/<file>`, `/keymap.json`.
- GET `/api/cases`, and under `/api/cases/<case>/`: `header`, `web`,
  `web.svg`, `web.list`, `node/<node>`, `lineage/<event>`, `paths`,
  `dossier`, `coverage`, `blobs/<item>`, and `notices`, the Server-Sent Events
  stream.
- POST `/api/cases/<case>/deep-dives`: refused with its consequence, writes nothing.
- POST `/api/cases/<case>/acts`: one analyst act from a closed body, minted by
  the server and sent through the door (the Acts section below).
- GET and PUT `/api/kv/<case>/<view>`: workspace state, closed keys, opaque values.

## Acts

The slice-3 keys record an analyst act. Each is one POST to
`/api/cases/<case>/acts` with a closed body naming the act, its target and the
fields the layer model requires of that subtype; the server mints the envelope
under the session's `--analyst`, sends it through the same door as a corpus row
(`tools/validate.py` by path, the store checks, one transaction) and publishes
the notice, so a second tab learns of it without a reload. An unknown key or
act is refused before the door; a code the validator fires comes back as
ACT_REFUSED_BY_MODEL with the codes named, and nothing is written.

- Enter promotes the item behind the selected selector node to an entity
  (Account, PersonCandidate, Org, Channel, Place, Media or ManualTask),
  anchored on that claim; an Account anchored on a type the registry does not
  let anchor refuses (SELECTOR_ANCHOR_PROHIBITED), and an item promoted once is
  not promoted again while its promotion stands (ACT_TARGET_ALREADY_PROMOTED).
- e excludes the selection, affirmatively not the subject, with its basis and
  the claim the exclusion rests on; the node stays in place, struck through.
- i ignores the selection: soft and reversible, it stays in the log and in
  lineage. A reason is needed only when the target supports a live cluster or
  was promoted by another analyst (ACT_REASON_REQUIRED, design 4.4).
- n notes and ? raises an open question on the selection.
- m opens the Merge Sheet, the one modal, over the marked nodes (v, two or
  more entity or referenced-only nodes): seams per member (h e n b i t g k),
  the band, the basis claims, a note. An unreviewed basis claim shows the
  review strip first (Enter verified, d dispute, in the course of
  merge_basis). Every rule is the model's: two members, a seam per member, a
  note with k, two evidence classes for almost_certain, and the circularity
  walk, which the sheet answers with an override note on MERGE_CIRCULAR. A
  proposal between the members enters the cluster's lineage as accepted.
- x revokes the selection's cluster, exclusion or promotion, with a reason;
  the tombstone stays, struck through and walkable, and is not revoked again.
- Backspace cancels the act queued in the last ten seconds, as does leaving
  the page. A single-key act
  waits ten seconds before it is sent and records nothing until then; after it
  lands the model offers no reversal except x on a cluster, an exclusion, a
  promotion or a SAME_ENTITY link (amendment 9.17). The Merge Sheet commits on
  its own button and is not queued.

On LOCAL an act lands nowhere until the operator sets `LOCAL_ACTS` in
`app/config.py` (ACT_LOCAL_PENDING_DECISION, amendment 9.16, reading APP-R31:
an act's payload is stratum 1 and its prose is typed at run time, so admitting
it is his decision under EG-2), and then only in a case the registry marks
synthetic (ACT_LOCAL_SYNTHETIC_CASE_ONLY). The INSPECTOR lists every adjudication of
the selected node's events under ADJUDICATIONS, each as its consequence.

## The store writes only into a held case

Every entry point that writes into a case refuses a case that is not held, one
the registry does not say is open or whose case database is absent (amendment
9.21, reading APP-R34). `ingest_batch` is the entry point for events, whatever
their origin: a corpus file, an analyst act, the watchdog's closing event or
the sweep's heartbeat. It refuses such a case with CASE_CLOSED_TO_WRITES before
the stored log is read, so a batch that would change nothing is refused too and
a closed case is never reported as holding what was sent. An event landed in a
shredded case would put material back, and the attach that writes it would
recreate a case database that is gone. The case database's file name is built
from the case id in lower case, so the rule reads every registry row that names
that file: another spelling of a closed case's id is refused with it, and a
batch under another spelling of an open case's id is refused with
CASE_ID_SPELLING_DIFFERS, because it would open a second registry row and a
second retention clock onto one case database. The write holds the rule again
before its attach, attaches a registered case without create and reads its file
again after the attach, so a case database that is gone by then is refused and
not recreated, and reads the registry's state, its spellings and the file's
presence again under its write lock. A first batch refused under the lock keeps
the case database it created when another ingest registered that file
meanwhile, and leaves one it cannot remove because another connection holds it
open; the caller sees the write's own error. The HTTP routes that write, the
acts and the workspace store, refuse a case closed to writes with a 409 in
`case_store` before anything is written. `rebuild` rebuilds only held cases and
names each case it leaves alone once as NOT HELD with what the registry says of
it, and `rebuild --verify` compares only the cases its copy rebuilds and says
so when that is none. The library functions behind those entry points, `kv.put`
and `replay_case`, read no registry state of their own: they attach without
create and rely on their callers for the rule. The watchdog reports the door's
refusal for a coverage row left open in a closed case, and the sweep writes no
heartbeat into a case that is not held.

## Watchdog

`python -m runner.watchdog --store <root> --once` closes every open coverage
interval whose last verification is older than three poll intervals by
appending one SYSTEM_EVENT COVERAGE_INTERVAL through the door, with t_end at
the last verification and the producer runner-watchdog (design 8.2 item 2,
amendments 9.6 and 9.18). Without `--once` it sweeps every 60 seconds, or
every `--every` seconds. The projector replaces the working row with the
closed row, which the trigger then keeps immutable; nothing is updated in
place. The command lives under runner because app imports nothing from runner.

## Tests

`python -m pytest app -q` runs every test under `app/tests`. Each store lives
under a temporary directory outside the repository, and each check is paired
with a negative control in `app/tests/test_controls.py`, which fails the suite
when a check stays green with its mechanism removed.

Since 2026-10-28 the suite is the kernel gate's app-tests entry, a line of
`make test`, and CI's Application tests step, each run as
`python -m pytest app -q --tb=short -p no:cacheprovider`. Reading APP-R30 keeps
it out of the pre-commit hook and `make preflight`: it runs about three minutes,
and it guards runtime behaviour rather than what enters git history, which the
hook's repository scan guards. The test client's two connections are made in
`app/tests/conftest.py` with 127.0.0.1 named on the call, so
`tools/validate_authorization.py --dispatch-paths` reads them as loopback test
connections, and the no-socket check keeps each original it patches beside the
patch, which the scan reads as no dispatch in a test module only (VA-R6,
applied as the session's reading of 2026-10-28 and decided Class B by the
maintainer the same day; without it the scan would list those four references
outside the gate).

## Retention sweep and verify_shred, drafted refusing

`python -m runner.retention_sweep --store <root> --once` is Step 11's sweep in
the shape Step 10 took. A run reads every registry row and decides before it
writes anything. A case is held when the registry says open and its case
database is present. A case that is not held is listed as not held and gets no
heartbeat. The door refuses a write into such a case (CASE_CLOSED_TO_WRITES),
so the sweep does not attempt one. A row that says shredded or shred_failed is
verify_shred's to judge and does not change the exit code. A row that says open
for a case whose database is absent makes the run exit 1, because
`retain_until` cannot be enforced on a case with no database. A held case whose
`retain_until` or `frozen_until` cannot be read as a date is refused
(SWEEP_REFUSED_DATE_UNREADABLE) and the run exits 1. A case is due from the
instant `retain_until` names, 00:00:00Z on that date, as the store's own
`is_past` reads it. A held case past `retain_until` whose freeze is still in
force is skipped and said so (RT-17). Every other held case past `retain_until`
is stated as due with the pre-shred sequence of RETENTION.md section 9, and
refused at its first step: the RT-13 finding check the kernel gate lists as
PENDING (SWEEP_REFUSED_FINDING_CHECK_PENDING), then the shred, refused on LOCAL
(SWEEP_REFUSED_LOCAL_STORE), refused while `policy/retention.yaml` carries no
dated row (SWEEP_REFUSED_POLICY_UNRATIFIED), and refused after both because
this draft holds no shred (SWEEP_REFUSED_SHRED_NOT_BUILT). The run then appends
one SYSTEM_EVENT SWEEP_HEARTBEAT per held case through the door (producer
runner-sweep, next_due one day on, read from the policy's daily cadence). A
heartbeat the door refuses is reported as "HEARTBEAT REFUSED" with the door's
refusal and its legal moves, and the run exits 1. On LOCAL the door lands a
system event only in a case the registry marks synthetic
(ACT_LOCAL_SYNTHETIC_CASE_ONLY). A run that wrote no heartbeat says "no
heartbeat written" and why. The sweep deletes nothing and writes no
SHRED_RECEIPT and no SHRED_FAILED.

The case header renders the heartbeat as RT-12's consequence, and reads only a
heartbeat whose time is not after now. The latest run is the heartbeat with
the latest time, and two heartbeats at one time are settled by arrival. The
line is "RETENTION SWEEP HAS NOT RUN SINCE <ts>" from next_due on, with no
grace, "RETENTION SWEEP HAS NEVER RUN HERE" when the case holds no heartbeat,
"NO RETENTION SWEEP RUN IS ON RECORD HERE" when every heartbeat the case holds
carries a time after now or no readable time, and a statement that the next
due time cannot be read when it cannot. Each of those is painted red with the
stylesheet's mark in front, on the server's flag. Otherwise the line gives the
last run and the next due time. A line that stands on a run while other
heartbeats carry a time after now or no readable time says how many it did not
read as a run, and is painted red as well. A heartbeat row that lacks a ts, a
seq or an object payload is read as carrying none and does not make the line
raise.

`python -m runner.verify_shred --store <root> --case <id> [--canary <id>
--canary-payloads N --canary-claims N --canary-blobs N]` runs RT-9's five
checks as dated facts, each PASS, FAIL or NOT RUN, and refuses to report a
pass while the shred fixture carries no dated row (VERIFY_SHRED_UNRATIFIED).
Check 1 fails as not_found on every run. What designates a witness ciphertext
is undecided (SR-U1), so the check has nothing to attempt a decrypt on and
reads no path, and RT-9 names not-found a failure. A file named witness in the
case's blob folder is an object check 2 counts. Check 2 fails on an object that
remains and is not run when none does, because the store records no count to
compare (SR-U1). Check 3 fails before it opens anything when a file SQLite
keeps beside the case database is on disk (-journal, -wal or -shm), because a
rollback journal or a write-ahead log can hold pages of the case. With none on
disk it passes only when the case database is gone, or when every table the DDL
declares errors with no such table and the file's schema lists no object. Zero
rows, an object the schema still lists, any other query error and a file that
cannot be read all fail. The check does not read the free pages of a database
whose tables were dropped, where text of the case was seen to remain, and it
does not look for such a file again after its read. Check 4 fails when the
skeleton rows, the tombstone state, or a receipt row carrying a receipt hash
after the case's last stratum-1 event is missing, and is not run when all three
are present, because the receipt hash has no stated preimage (U-09). Check 5
compares the canary's payload, claim and object counts with the inventory the
caller recorded, and is not run when no canary and inventory are named (U-11).
Checks 1, 2 and 4 have no passing path here, so no run reports a verified
shred. The program refuses a case this store never held
(VERIFY_SHRED_CASE_NEVER_HELD) and a canary that is the case itself
(VERIFY_SHRED_CANARY_IS_THE_CASE). `app/tests/test_retention_sweep.py` pairs
every check with a control that removes its mechanism. Four behaviours the two
modules state have no control of their own, so the suite stays green when one
is changed: a heartbeat whose time equals now is read as a run, a due case's
refusal is printed with its legal moves, the heartbeat is written after every
case is decided, and the canary is opened read-only. Three of check 3's
controls (zero rows, one table read, any query error) fail on the wording of
the fact alone, because the schema count stops the same false pass.
