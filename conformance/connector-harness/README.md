# Connector harness

A harness fixture is one line of a connector's fixtures file, a JSONL file under
`connectors/<id>/`. Each line names the connector at a version, gives the adapter
one input, and pins what the adapter must return: a list of events with an exact
`event_count`, zero included, or a refusal with a code declared in
`spec/layer-model.yaml`. `fixture.schema.json` in this directory lints every line,
so an unknown key is refused rather than ignored.

Fixture inputs carry placeholders only, in the `<...>` form
`tools/validate_cast.py` enforces on the cast, narrowed by
`tools/validate_manifest.py` to a slot name, a lowercase word in angle brackets,
or a typed token `synthetic/GROUND_TRUTH.yaml` carries. A line that repeats a key
is refused, because JSON keeps only the last value. A fixture is a tracked file, and git
history is the one store a crypto-shred cannot reach, so a selector value in a
fixture is permanent (`doctrine/RETENTION.md` RT-15). Cassettes a fixture replays
are captured against S2 or N0 targets only.

A connector manifest names one refusal fixture per required input in
`health.refusal_fixtures`. `tools/validate_manifest.py` checks that each named
fixture exists, lints against the schema, refuses, belongs to the manifest's
connector and version, withholds the input it names, supplies every other
required input, and is named by one entry only.

A fixture pins an event count or a refusal code and nothing else. The presence,
absence, lineage and `forbidden_paths` expectations
`docs/PLAINSIGHT-FOUNDATION.md` section 4.4 names have no key in the schema yet,
so a line carrying one is refused as an unknown key (reading MF-R15).

The runner that calls an adapter against these fixtures,
`tools/validate_connector_conformance.py`, arrives with the first connector. Until
then no fixture is executed, and a fixture that lints is a fixture whose shape is
known, not a connector whose behaviour is proven.
