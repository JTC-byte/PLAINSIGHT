"""python -m app: init, ingest into, rebuild and serve a PLAINSIGHT store.

serve starts the stdlib HTTP server on 127.0.0.1 (app/http/server.py) and
prints the URL of the landing view. A watchdog subcommand arrives with
runner/watchdog.py, which docs/PLAINSIGHT-design.md amendment 9.6 records as not
built, and is not offered here until it exists.

Exit codes: 0 done, 1 refused, 2 the command line could not be read.
"""

from __future__ import annotations

import argparse
import sys
import tempfile

from app import config
from app.refusals import Refusal


def _store_help() -> str:
    return f"store root; default ${config.ENV_HOME}, else %%LOCALAPPDATA%%\\plainsight"


def cmd_init(args) -> int:
    from app.store.db import Store

    with Store.init(args.store) as store:
        print(f"store ready at {store.root}, environment {store.environment}, {len(store.cases())} case(s) held")
    return 0


def cmd_ingest(args) -> int:
    from app.store.db import Store
    from app.store.ingest import ingest_path

    with Store.open(args.store) as store:
        result = ingest_path(store, args.path)
    case = f"C-{result.case_id[:8]}" if result.case_id else "no case"
    print(f"ingested into {case}: {result.landed} event(s) landed, {result.held} already held and left as they were")
    return 0


def cmd_rebuild(args) -> int:
    from app.store import replay
    from app.store.db import Store

    with Store.open(args.store) as store:
        cases = replay.rebuild(store)
        for case_id in cases:
            print(f"rebuilt C-{case_id[:8]}: projection digest {replay.digest(store, case_id)}")
        if args.verify:
            with tempfile.TemporaryDirectory(prefix="plainsight-verify-", ignore_cleanup_errors=True) as scratch:
                diffs = replay.verify(store, scratch)
            bad = {c: t for c, t in diffs.items() if t}
            for case_id, tables in bad.items():
                print(f"C-{case_id[:8]}: a fresh replay differs from this store in {', '.join(tables)}")
            if bad:
                return 1
            print(f"verified: a fresh replay of {len(diffs)} case(s) matches this store row for row")
    if not cases:
        print("no case held, so nothing was rebuilt")
    return 0


def cmd_serve(args) -> int:
    from app.http import server as http_server
    from app.model import reads
    from app.store.db import Store

    srv, app = http_server.make_server(args.store, host=args.host, port=args.port, analyst=args.analyst)
    with Store.open(app.root) as store:
        cases = store.cases()
        seeds = {}
        for case_id in cases:
            if store.attach_case(case_id, create=False):
                seeds[case_id] = reads.seed_focus(store.conn, case_id)
    base = f"http://127.0.0.1:{app.port}"
    print(f"serving {len(cases)} case(s) on {base}/ as {app.analyst}; press Ctrl+C to stop")
    for case_id, seed in seeds.items():
        focus = f"?focus={seed}" if seed else ""
        print(f"  C-{case_id[:8]}: {base}/c/{case_id}/{config.LANDING_VIEW}{focus}")
        if seed:
            print(f"  C-{case_id[:8]} web: {base}/c/{case_id}/web?focus={seed}&hops=2")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        app.close()
        srv.server_close()
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app", description="Initialize, ingest into, rebuild and serve a PLAINSIGHT store.")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create the store root, its plane database and the rollup vocabulary")
    p.add_argument("--store", help=_store_help())
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("ingest", help="ingest one JSONL file through the door")
    p.add_argument("--store", help=_store_help())
    p.add_argument("path", help="on LOCAL, a tracked and unmodified file named in SYNTHETIC_SOURCES")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("rebuild", help="drop the projections and replay them from the log")
    p.add_argument("--store", help=_store_help())
    p.add_argument("--verify", action="store_true", help="also replay into a fresh scratch store and compare row for row")
    p.set_defaults(func=cmd_rebuild)

    p = sub.add_parser("serve", help="serve the web, the dossier and the lineage drawer on 127.0.0.1")
    p.add_argument("--store", help=_store_help())
    p.add_argument("--analyst", required=True, help="the session's human identity; on LOCAL, analyst-example")
    p.add_argument("--host", default="127.0.0.1", help="the bind address; anything but 127.0.0.1 is refused")
    p.add_argument("--port", type=int, default=0, help="the port; 0, the default, takes a free one")
    p.set_defaults(func=cmd_serve)

    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    try:
        return args.func(args)
    except Refusal as refusal:
        print(refusal.render(), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
