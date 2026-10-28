"""Boundaries: tools/ never imports app/, no value leaves through a refusal, a notice
or a filename, and every registry selector type sits in exactly one sector."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import yaml

from app import config
from app.model import sectors
from app.store import door, ingest
from app.tests.helpers import CASE, corpus_events, corpus_strings, named, refusal_of, value_hashes

GOVERNED = ("tools", "spec", "schema", "ontology", "policy")


def importers_of_app(roots) -> list[str]:
    found = []
    for root in roots:
        for path in sorted(Path(root).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                    names = [node.module]
                if any(n == "app" or n.startswith("app.") for n in names):
                    found.append(path.name)
    return found


def check_governed_trees_never_import_app(ctx):
    roots = [config.REPO_ROOT / d for d in GOVERNED] + ctx.extra_roots
    assert importers_of_app(roots) == []


def break_planted_importer(ctx):
    root = ctx.tmp / "planted-tools"
    root.mkdir()
    (root / "reader.py").write_text("from app.store import db\n", encoding="utf-8")
    ctx.extra_roots.append(root)


def test_governed_trees_never_import_app(ctx):
    check_governed_trees_never_import_app(ctx)


def check_no_value_in_refusals_notices_or_files(ctx):
    texts = []
    s = ctx.store()
    events = corpus_events()
    named(events, "extract-claim-handle")["payload"]["confidence"] = 0.5
    texts.append(refusal_of(ctx.ingest, s, events).render())
    events = corpus_events()
    claim = named(events, "extract-claim-hint")
    claim["payload"]["value"] = claim["payload"]["value"][1:-1]
    texts.append(refusal_of(ctx.ingest, s, events).render())
    notices = []
    ctx.mp.setattr(ingest, "LISTENERS", [notices.append])
    ctx.ingest(s)
    assert notices, "the ingest published notices"
    texts.extend(json.dumps(n) for n in notices)
    events = corpus_events()
    note = named(events, "adjudicate-note")
    note["payload"]["text"] = note["payload"]["text"].upper()
    texts.append(refusal_of(ctx.ingest, s, events).render())
    texts.extend(p.name for p in s.root.rglob("*"))
    joined = "\n".join(texts)
    assert not [v for v in corpus_strings() if v in joined], "a corpus value reached a refusal, notice or filename"
    assert not [h for h in value_hashes() if h in joined], "a hash of a corpus value reached a refusal, notice or filename"
    for n in notices:
        assert set(n) == {"seq", "kind", "case_id", "ids"} and n["case_id"] == CASE and len(n["ids"]) <= 50


def break_refusal_quotes_the_payload(ctx):
    real = door.render_failures

    def leaky(failures):
        first = next(iter(failures.values()))[0]
        return real(failures) + "\n" + json.dumps(first.get("payload"))

    ctx.mp.setattr(door, "render_failures", leaky)


def test_no_value_in_refusals_notices_or_files(ctx):
    check_no_value_in_refusals_notices_or_files(ctx)


def check_every_selector_in_one_sector(ctx):
    registry = yaml.safe_load((config.REPO_ROOT / "ontology" / "selectors.yaml").read_text(encoding="utf-8"))
    assert sectors.unplaced(registry["selectors"]) == {}
    entities = set(registry["entities"]) - {"ManualTask"}
    assert sectors.unplaced(entities) == {}


def break_sector_table_missing_a_key(ctx):
    table = {k: tuple(v for v in members if v != "domain") for k, members in sectors.SECTORS.items()}
    ctx.mp.setattr(sectors, "SECTORS", table)


def test_every_selector_in_one_sector(ctx):
    check_every_selector_in_one_sector(ctx)


CONTROLS = [
    ("a planted module imports app", check_governed_trees_never_import_app, break_planted_importer),
    ("a refusal quotes the payload", check_no_value_in_refusals_notices_or_files, break_refusal_quotes_the_payload),
    ("a sector table missing one key", check_every_selector_in_one_sector, break_sector_table_missing_a_key),
]
