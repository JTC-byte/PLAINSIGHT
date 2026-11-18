# app: the PLAINSIGHT store and its social web operating picture

This directory is Class C runtime code. It holds the case store, the ingest
door, and a stdlib HTTP server that renders one case as a focused web, a
read-only DOSSIER, PATHS, the COLLECTION board, and the Lineage Drawer. Nothing
here decides who may be a subject, what may be retained, or what may leave.
Those rules are in `doctrine/`, and the validation the door applies is
`tools/validate.py`, loaded by path.

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
The server refuses any other bind address with BIND_REFUSED_LOCAL, and a
`--port` that another socket holds with BIND_REFUSED_PORT.

## The showcase front end

`python -m app serve --ui showcase` serves a second front end, `app/showcase/`,
over the same routes and API. The classic front end in `app/static/` stays the
default, and `--ui classic` names it. Run the showcase beside the classic one
on another port:

```
python -m app serve --store %LOCALAPPDATA%\plainsight --analyst analyst-example --port 60542 --ui showcase
```

The showcase draws the seed as a profile page in the idiom of the 2026-11-02
social-platform pass: a profile header, seven tabs and one Lineage Drawer. Each
tab is a view of section 3 of the design, under the key 8.6 and amendment 9.10
give that view: Overview is DOSSIER (1), Sources is STREAM (2), Timeline is
CHRONOLOGY (3), Places is MAP (4), Tools is COLLECTION (5), Assessment is DRAFT
(6) and Connections is WEB (7).

- It reads through GET routes only. It sends no act, no deep dive and no
  workspace write, and keeps nothing in browser storage.
  `app/tests/test_showcase.py` scans its files for a request other than GET
  and for the rules `app/static` keeps, each check with a control.
- The tab, the selected node and the open drawer live in the URL fragment,
  which never reaches the server and carries a fixed word and uuids only.
- The case strip renders the header's states as one line of chips. Each chip
  opens the server's sentence verbatim with what it means. Red and the hatch
  appear only where the server's flag says the system does not vouch.
- Connections is drawn by the client from GET `/api/cases/<case>/web`: ring one
  in sector order clockwise from the top, each arc sized by the nodes behind
  it, and an outer node beside its parent. Lines are grouped by pair with one
  label in words, and the side panel prints each link's own sentence. This
  departs from the fixed sector angles of `app/model/layout.py`, which
  amendment 9.24 of the design records.
- Every request passes one gate in `app/showcase/lib/api.js`: at most four
  are open at once, and a request that does not arrive is tried twice more
  after a short pause. A refusal is an answer and is not retried. A part that
  still does not arrive is drawn as a calm note with a retry, and the rest of
  the page is drawn around it. `app/tests/test_showcase.py` runs that file
  under node, when node is on PATH, with a fetch that drops one request, and
  runs it again with `app/showcase/lib/words.js` and a case pack set; both
  runs pass through one process site, which the dispatch scan lists in a test
  module.
- `app/showcase/boot.js`, a classic script the page loads before the module,
  guards the first load: if the module graph does not arrive, it reloads the
  page once and then offers a reload button, reading from the browser's
  navigation entry whether this load was already that reload.
- `--overlay PATH`, with `--ui showcase` only, reads a JSON file of fictional
  display stand-ins for the corpus's placeholders and serves it as
  `/static/overlay.json`; the page draws them over every body it reads and
  marks the subject FICTIONAL PERSON, with a switch back to the stored values.
  A file that sets `presentation` to `live` drops the page's own test,
  fictional and placeholder labels instead, for a presenter's screen, and
  quiets what does not help an operator read the case: the case strip, the
  kicker and anchor lines, the process events in the feed, the Tools tab's
  System and log-count blocks, and each claim's provenance rows, which fold
  behind a toggle. A `case` in the file, a case pack, answers every API request
  for one fictional case from the page itself, so nothing reaches the store;
  in every string of it the reader refuses an email outside the reserved
  domains, a phone number outside 555-0100 to 555-0199 that is written in the
  North American shape, led by a plus sign or as a bare run of ten or eleven
  digits, a link, and a coordinate key. With a case pack set the label
  FICTIONAL PERSON is not a switch, because nothing stored stands behind a
  whole case, and the help panel says the case is answered from a display
  file. The page's other sentences are the product's own, and they still speak
  of the store while a case pack answers in the page.
  `app/http/overlay.py` refuses a file inside the repository, the store or any
  git working tree, a key that is not a corpus placeholder, an email on a
  domain other than example.com, example.org or example.net, a number outside
  555-0100 to 555-0199, and a handle that is the subject's plain first and
  last name. It cannot tell an invented name or handle from a real person's,
  so the author of the file answers for every one in it, and in a case pack it
  does not read a phone number in another shape or one written as a JSON
  number.
  Nothing enters the store. Restart without `--overlay` to switch it off.
- Places draws no map, because the corpus holds no coordinate.
- Tools counts every event in the case from the rollup and marks the ones its
  own reads do not reach as counted only, so nothing is dropped. It does not
  read the COLLECTION route of amendment 9.25 yet.

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
and Backspace, which the Acts section below describes. Slice 4 builds 5
COLLECTION, which its own section below describes. When a button has
keyboard focus, Tab and Shift+Tab move focus and Enter presses the button;
elsewhere they run their keymap bindings.

## Routes

Every URL carries uuids and fixed words only. The query keys are focus, hops,
sector, view, lineage, dir, after, from and to; any other key is refused with
QUERY_KEY_REFUSED.

- GET `/`, `/c/<case>/<view>`: the page. The views are dossier, web, paths, list
  and collection.
  GET `/c/<case>` redirects to `/c/<case>/dossier`, the landing view.
- GET `/static/<file>`, `/keymap.json`, each from the front end `--ui` names.
  A front end that ships no keymap answers `/keymap.json` with
  ROUTE_NOT_FOUND.
- GET `/api/cases`, and under `/api/cases/<case>/`: `header`, `web`,
  `web.svg`, `web.list`, `node/<node>`, `lineage/<event>`, `paths`,
  `dossier`, `coverage`, `collection`, `blobs/<item>`, and `notices`, the
  Server-Sent Events stream. `/api/cases` also carries the RT-11 line.
- POST `/api/cases/<case>/deep-dives`: refused with its consequence, writes nothing.
- POST `/api/cases/<case>/acts`: one analyst act from a closed body, minted by
  the server and sent through the door (the Acts section below).
- GET and PUT `/api/kv/<case>/<view>`: workspace state, closed keys, opaque values.

A route reads the case its URL names under the registry's spelling of its id
(amendment 9.26). A URL's case id is read in lower case, and a case registered
under another spelling is served under the registry's. Two registry rows that
name one case database under other spellings cannot be told apart by a URL, so
that request is refused as CASE_NOT_HELD with a detail that says so.

## What the server checks

Every request must name the server in its Host header: 127.0.0.1 or localhost
with the bound port. A request sent under another host name, which is how a DNS
rebinding reaches this loopback, is refused with HOST_REFUSED, and so is a Host
sent on two lines, even when each names the server. The check does not stop a
page on another origin, whose browser names this server in Host; the write
checks below and the browser's same-origin policy answer that page.

A POST or PUT must carry this launch's token in the session cookie, which the
server sets on the page's response as `ps_token_<port>` with HttpOnly,
SameSite=Strict and Path=/; a missing or wrong token, or a Cookie header sent on
two lines, is refused with TOKEN_REFUSED before any byte of the body is read.
The name carries the port because a browser keeps one cookie per name for a
host whatever its port, so two launches on 127.0.0.1 keep their own tokens.

A write is also authorized by the page that sent it (amendment 9.27). A page on
another port of this host is the same site, so the browser attaches the cookie
to that page's requests under SameSite=Strict. Before any byte of the body is
read, a write whose Origin header is present and is not exactly this server's
own origin, or whose Sec-Fetch-Site header is present and is neither
same-origin nor none, is refused with ORIGIN_REFUSED, and a write whose
Content-Type is not application/json, alone or with charset=utf-8, is refused
with CONTENT_TYPE_REFUSED. A header sent on more than one line is read as one
value, its lines joined by a comma, which none of these rules admits, even when
each line is admissible; a Content-Length sent on two lines gives no length, so
that write is refused with BODY_REFUSED. Only spaces and tabs around the
Content-Type's parts are ignored. A write that carries neither header, as a
command-line client sends, is admitted on the cookie and the Content-Type: a
page on another origin can send a POST without a preflight only as text/plain,
application/x-www-form-urlencoded or multipart/form-data, or with no
Content-Type, and a POST of application/json, or any PUT, only after a
preflight, which the server refuses, because OPTIONS answers METHOD_REFUSED.
The classic front end sends every write through `sendJSON` in
`app/static/app.js`, a fetch in the default cors mode, in which a page served
with no-referrer still sends its own origin. `app/tests/test_static.py` checks
that `sendJSON` names no mode, names its headers and credentials once each and
spreads or assigns no other object into its options, and refuses a request that
could write anywhere else under `app/static`.

A refused write is answered before any byte of its body is read. The server
then stops sending, reads and discards what the client sends of the body,
never parsing it, up to the declared Content-Length capped at 8 KiB and for at
most one second, and closes. The client's body may still be on its way when
the answer is written, and a server that closed at once would meet it with a
reset, after which a Windows client's stack drops the answer it had received,
so the page would see a network error in place of the refusal and its moves.
Any answer given before a declared body is read, a Host refusal and
BODY_REFUSED for a length past 8 KiB among them, is followed by the same
discard, except the notice stream's, which holds its connection until the
stream ends and is then closed. The one second is a reading that awaits the
maintainer's confirmation (amendment 9.27). A request the standard library's
parser refuses before routing is closed at once, as before.

The listening socket shares its port with no other socket. On Windows it is
bound with SO_EXCLUSIVEADDRUSE and with SO_REUSEADDR off, because there
SO_REUSEADDR lets another process bind the port. Elsewhere it is bound with
SO_REUSEADDR on, as the standard library binds it, because Linux refuses a
second bind to a listening port whatever that option says and, without it,
refuses a restart on the port while the port's last connections wait out
TIME_WAIT. SO_REUSEPORT is off everywhere. A `--port` that another socket holds
is refused with BIND_REFUSED_PORT, and the serve command exits 1.

Every response carries Cache-Control: no-store, the Content-Security-Policy
default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action
'none', Referrer-Policy: no-referrer, X-Content-Type-Options: nosniff,
Cross-Origin-Resource-Policy: same-origin and Permissions-Policy: camera=(),
microphone=(), geolocation=(). A route's own header never replaces one of them.
An exception raised outside the dispatcher is logged by its type name and
prints no traceback.

Every input and textarea either front end builds, the act forms, the Merge
Sheet's notes and the showcase's search box among them, carries
spellcheck="false", autocomplete="off", autocapitalize="off", autocorrect="off"
and translate="no", and both pages carry translate="no" on the document and the
notranslate meta. A browser's spellcheck and translation can send what is typed
to a remote service, and its autofill keeps typed values in its form history,
outside the store the shred reaches. Each front end's element helper, `el` in
`app/static/app.js` and `h` in `app/showcase/lib/dom.js`, sets the five
attributes after the caller's own. `app/tests/test_static.py` pins the text of
`el`, of `h` with the `apply` and `append` it calls, of `s`, the showcase's SVG
helper, whose tag is a parameter as well, and of `svgNamespace`, whose answer
`s` passes on, so a change to one of them is refused until its pin is updated.
It reads both pages as an HTML parser reads them, so a look-alike of
translate="no", a meta inside a comment, and a tag inside a noscript or
template element, where a browser does not apply it, do not count. It refuses
each other way of making a field that it lists: written as markup without the
five, its attributes read as an HTML parser reads the tag; made by
createElement outside the helpers, however the call is written; a customized
built-in element, in a script that names customElements, which must register
one before it can be made, or that names HTMLInputElement or
HTMLTextAreaElement other than in an instanceof test; or an editable surface.
It also refuses a script that names one of the five outside the helpers' list,
which could turn one back on after the helper returns; a call to translate(),
the transform function, is not read as the attribute unless a brace follows it
on its line, as one does where a method named translate is written, since a
function set as that property turns the attribute on. The scan reads source
text, so a tag, a name or markup assembled at run time from pieces is not read,
and neither is a script that removes a node's attributes by walking them
without naming one.

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

## COLLECTION and the RT-11 line

Key 5 opens COLLECTION, a read-only board for one case (amendment 9.25, on the
maintainer's rulings 1C, 2A and 3B of 2026-11-12). Its rows come from two
sources, and each row says which.

- **The connectors this checkout carries**, one row per manifest folder under
  `connectors/`, read from the working tree on every request. A row prints what
  the file declares as text: id, version, capability, kind, probe unit, canary
  cadence, the canaries' names and the declared class of their target. A value
  YAML reads as a number, a date or a list prints as "not declared as text", and
  a manifest's canary inputs are never printed, because a canary declaration
  carries its target (RT-15). A manifest that cannot be read, or declares no id,
  is listed under its folder's name, which the manifest gate makes the
  connector's id, and is never skipped. The board does not grade a manifest;
  `tools/validate_manifest.py` does.
- **The health records this case holds**, its SYSTEM_EVENT CONNECTOR_HEALTH
  events. A record sits on the row of the connector it names. A record that
  names a connector no manifest folder here carries is listed apart, which is
  where the corpus's one health event goes.

No row states a present health state other than UNVERIFIED. On LOCAL the line
reads "UNVERIFIED, no canary runs from this machine, because LOCAL executes no
connector (EG-1): this connector's state is unknown here". In ISOLATED a
recorded state would be the present one only inside a freshness window, and no
manifest declares one, so the board reads none as present there either (reading
APP-R35).

A recorded state is a dated record: the state its producer recorded, its time,
its producer and canary, design section 7.1's definition of that state quoted
as the design's, its recorded reason when it carries one, and why it is not the
present state. The board vouches for no recorded state, so every record is
painted with the red mark, as every present state is (APP-R36).

- A record of the connector as a whole is one stream. The latest, by time and
  then by arrival, supersedes the earlier ones, which are counted and not
  listed.
- An endpoint or subscription record names no endpoint, because the payload
  carries none, so two of them may concern two endpoints. They are grouped by
  the state they record, and the latest of each state is shown with the count
  of that state's records. A SUSPECT record is never hidden behind a later
  record of another state.
- A record dated after now, or with no readable time, connector, probe unit or
  state, is set aside and counted, on the board and on the row of the connector
  it names.

Rows are sorted by the most dangerous record they show, SUSPECT first, and
"CAPABILITY ... HAS NO HEALTHY MEMBER" prints for every declared capability,
because no member is healthy here. The l button on a record opens the Lineage
Drawer on its event; the keys act on the INSPECTOR's node, as in every view.

The board reads one case. Its route sits under the case, its read takes the case
as its one scope argument, and the board says its scope in words. The filter
tabs, the sparkline, differential health, the impact review, the buttons and the
30-second refresh of design section 7.4 are not built.

The RT-11 line above every view states its evidence and its limit. It names the
first SHRED_FAILED that halts, by arrival, by its case's short id, its time and
its failed check, and counts the others that halt. It says that this build reads
no clearing, because verify_shred has no passing path, and on LOCAL that nothing
dispatches in any case (EG-1). The read takes the shared skeleton alone, so the
case list carries the line too, and it is the one read that spans cases: RT-11
makes a failed shred a fact about the mechanism and not about the case. A
SHRED_FAILED whose payload cannot be read as an object, or does not say whether
it halts, is read as halting (APP-R38). The line is lit on every store that
holds the corpus, whose log carries one failed shred, and nothing in this tree
clears it: the halt's clearing, its source of truth and its enforcement are left
to the shred's design.

`app/tests/test_collection.py` pairs every check with a control that removes its
mechanism. No check there knows the health of a connector, because no canary
runs on LOCAL: each claims coverage of the board's mechanism on the corpus and
on variants built from it. The view's JavaScript is checked by reading its
source, as slices 1 to 3 check theirs, and not by running it.

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
it, and `rebuild --verify` copies and compares only held cases, says how many
it did not compare, and says so when that is none; the same copy used as a
migration refuses a store holding a case that is not held (amendment 9.23). A
verify exits 1, with a STORE FAULT line, when a registry row says open for a
case database that is gone, because `retain_until` cannot be enforced on a case
with no database; a row that says shredded or shred_failed is a closed case and
does not change the exit code (amendment 9.26). The library functions behind
those entry points, `kv.put` and `replay_case`, read no registry state of their
own: they attach without create and rely on their callers for the rule. The
watchdog reports the door's refusal for a coverage row left open in a closed
case, and the sweep writes no heartbeat into a case that is not held.

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
it out of the pre-commit hook and `make preflight`: it took 11 minutes 19
seconds on the Windows 11 workstation with Python 3.14.0 on 2026-11-17, and it
guards runtime behaviour rather than what enters git history, which the hook's
repository scan guards. The test client's two connections are made in
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
`retain_until` cannot be enforced on a case with no database. So does a
registry state the schema does not name, which the run reports as such and does
not raise on. A held case whose `retain_until` or `frozen_until` cannot be read
as a date is refused (SWEEP_REFUSED_DATE_UNREADABLE) and the run exits 1. A
case is due from the instant `retain_until` names, 00:00:00Z on that date, as
the store's own `is_past` reads it. A held case past `retain_until` whose
freeze is still in force is skipped and said so (RT-17). Every other held case
past `retain_until` is stated as due with the pre-shred sequence of
RETENTION.md section 9, and refused at its first step: the RT-13 finding check
the kernel gate lists as PENDING (SWEEP_REFUSED_FINDING_CHECK_PENDING), then
the shred, refused on LOCAL (SWEEP_REFUSED_LOCAL_STORE), refused while
`policy/retention.yaml` carries no dated row (SWEEP_REFUSED_POLICY_UNRATIFIED),
and refused after both because this draft holds no shred
(SWEEP_REFUSED_SHRED_NOT_BUILT). The run then appends one SYSTEM_EVENT
SWEEP_HEARTBEAT per held case through the door (producer runner-sweep, next_due
one day on, read from the policy's daily cadence). A heartbeat the door refuses
is reported as "HEARTBEAT REFUSED" with the door's refusal and its legal moves,
and the run exits 1. On LOCAL the door lands a system event only in a case the
registry marks synthetic (ACT_LOCAL_SYNTHETIC_CASE_ONLY). A run that wrote no
heartbeat says "no heartbeat written" and why. The sweep deletes nothing and
writes no SHRED_RECEIPT and no SHRED_FAILED. A run reads the pin of record only
when a refusal needs it, so a run that reaches no shred, which is every run of
this draft, does not depend on the pin reader.

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
checks as dated facts, each PASS, FAIL or NOT RUN, and refuses to report a pass
while the shred fixture carries no dated row (VERIFY_SHRED_UNRATIFIED). Check 1
fails as not_found on every run. What designates a witness ciphertext is
undecided (SR-U1), so the check has nothing to attempt a decrypt on and reads
no path, and RT-9 names not-found a failure. A file named witness in the case's
blob folder is an object check 2 counts. Check 2 fails on an object that
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
(VERIFY_SHRED_CANARY_IS_THE_CASE). A case id is read under any spelling of its
letters, because the case database's file name is built from it in lower case,
and the registry's spelling is used for every check.
`app/tests/test_retention_sweep.py` pairs every check with a control that
removes its mechanism. Each behaviour the two modules state has a control of
its own, among them the four the third read of item 7 found without one: a
heartbeat whose time equals now is read as a run, a due case's refusal is
printed with its legal moves, the heartbeat is written after every case is
decided, and the canary is opened read-only. Three of check 3's controls (zero
rows, one table read, any query error) fail on the wording of the fact alone,
because the schema count stops the same false pass; they stay, because the why
is the part of the fact an operator reads.
