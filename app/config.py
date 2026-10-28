"""Deployment configuration the store and the door read.

Each value here is configuration, not doctrine. Changing SYNTHETIC_SOURCES
widens what a LOCAL store may hold, which is Class F by effect (AGENTS.md
section 3): adding the sealed cast is the operator's act, and an agent edits no
allowlist.
"""

from __future__ import annotations

import os
from pathlib import Path

#: The repository root. The store refuses any root inside a git working tree,
#: this one first among them.
REPO_ROOT = Path(__file__).resolve().parents[1]

#: The only files a LOCAL store may ingest, as repository-relative POSIX paths.
#: Each must also be tracked and unmodified at ingest (app/store/door.py).
SYNTHETIC_SOURCES = ("conformance/must-pass.jsonl",)

#: The view the analyst lands on (docs/PLAINSIGHT-design.md section 3.1).
#: Making WEB the landing view is the operator's decision.
LANDING_VIEW = "dossier"

#: The environment variable naming the store root.
ENV_HOME = "PLAINSIGHT_HOME"

#: The environment variable naming the deployment environment, LOCAL or
#: ISOLATED (doctrine/EGRESS.md EG-1). Unset means LOCAL.
ENV_ENVIRONMENT = "PLAINSIGHT_ENVIRONMENT"

#: The environment variable carrying the human identity list in ISOLATED, comma
#: separated. The list is deployment configuration and never lives in a tracked
#: file (spec/pse-semantics-contract.md section 10).
ENV_HUMANS = "PLAINSIGHT_HUMANS"

#: The human identities on LOCAL: the conformance corpus's synthetic analyst.
LOCAL_HUMANS = frozenset({"analyst-example"})

ENVIRONMENTS = ("LOCAL", "ISOLATED")

#: The only addresses the HTTP server binds. The interface is a view on the
#: store served to this machine's loopback (doctrine/EGRESS.md EG-3); any other
#: address is refused with BIND_REFUSED_LOCAL before a socket exists. A bind
#: rule for ISOLATED is the operator's decision and is not written here.
BIND_HOSTS = ("127.0.0.1",)


def environment() -> str:
    """LOCAL unless the deployment says ISOLATED. Any other value reads as LOCAL."""
    value = (os.environ.get(ENV_ENVIRONMENT) or "LOCAL").strip().upper()
    return value if value in ENVIRONMENTS else "LOCAL"


def deployment_humans() -> frozenset[str]:
    """The human identity list for the current environment."""
    if environment() == "ISOLATED":
        raw = os.environ.get(ENV_HUMANS) or ""
        names = frozenset(n.strip() for n in raw.split(",") if n.strip())
        return names
    return LOCAL_HUMANS
