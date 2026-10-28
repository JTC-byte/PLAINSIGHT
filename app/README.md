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
twin, and p the Pivot Bar. The slice 3 act keys answer that they are not built
and record nothing. When a button has keyboard focus, Tab and Shift+Tab move
focus and Enter presses the button; elsewhere they run their keymap bindings.

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
- GET and PUT `/api/kv/<case>/<view>`: workspace state, closed keys, opaque values.

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
