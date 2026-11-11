# conformance/connector-harness/must-fail/: manifests that must refuse

Each `*.manifest.yaml` here is a connector manifest written to break one rule, and
the sibling `*.expect` file holds the one code `tools/validate_manifest.py` must
refuse it with, on one line and with nothing else. `--all` walks this folder
before the real connectors. A manifest here that does not refuse with the code it
names is itself a refusal (MANIFEST_MUST_FAIL_PASSED), whether it refuses nothing
or refuses for other codes only. An `.expect` that is absent, empty, holds more
than one word or names no code of the tool is another
(MANIFEST_MUST_FAIL_EXPECT_ABSENT).

The walk reads every entry of the folder or refuses it. A file under any other
name, a subfolder, or an `.expect` with no manifest beside it is
MANIFEST_MUST_FAIL_UNREAD, and a folder with no manifest is
MANIFEST_MUST_FAIL_ABSENT, so a fixture cannot leave the walk by being renamed,
moved or deleted. This file is the one other entry the folder holds.

The first file, `retain-disposition.manifest.yaml`, is the self-test's baseline
manifest with a bystander disposition of `retain`, the one-line change that would
widen who can be collected on while reading as Class B (CLAUDE.md design gate 2).
SS-10's last paragraph asks for this fixture. The schema refuses it, so it fires
BYSTANDER_DISPOSITION_OUT_OF_SET and no other code. Every value in a file here is
a placeholder, so `tools/validate_retention.py --repo-scan` stays green over it.
