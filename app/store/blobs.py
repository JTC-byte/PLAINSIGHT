"""Raw bytes, addressed by sha256 at <root>/blobs/<case_id>/<aa>/<sha256>.

put() refuses unless all three conditions hold (BLOB_WRITE_REFUSED):

- the environment is ISOLATED;
- an Encryptor holding a per-case key is configured (doctrine/RETENTION.md RT-4);
- the pin of record reports both EG-2 and RT-4 stamped, read through
  tools/pin_of_record.py, whose trigger for both is the first blob.

On LOCAL no blob is ever written. No stdlib or home-built cipher stands in for
RT-4: which AEAD library the VM image carries is the operator's decision, so
this module defines the Encryptor protocol and ships no implementation of it.

get() verifies the digest of the decrypted bytes and refuses a mismatch
(BLOB_DIGEST_MISMATCH). A digest the store does not hold reads as "raw bytes
not held" (BLOB_NOT_HELD), which is how the corpus's fixture digest renders.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Protocol

from app import config
from app.refusals import Refusal
from app.store import db, envelope

PIN_TOOL = config.REPO_ROOT / "tools" / "pin_of_record.py"

#: The criteria whose stamps a blob write needs.
REQUIRED_STAMPS = ("EG-2", "RT-4")

#: The absent-raw consequence on a synthetic store, where the corpus names a
#: fixture digest that was never captured.
NOT_HELD_LINE = "raw bytes not held · synthetic fixture names a digest with no capture"

#: The absent-raw consequence on any other store: the digest was real, and the
#: bytes were swept or never written.
NOT_HELD_LINE_CASE = (
    "raw bytes not held · swept by retention, or never captured: the claim stands on its item record only"
)


def not_held_line(synthetic) -> str:
    """The absent-raw line for a case, read from its registry's synthetic flag."""
    return NOT_HELD_LINE if synthetic else NOT_HELD_LINE_CASE


class Encryptor(Protocol):
    """A per-case AEAD. Destroying the case key is the shred of every blob (RT-3, RT-4)."""

    def encrypt(self, case_id: str, plaintext: bytes) -> bytes: ...

    def decrypt(self, case_id: str, ciphertext: bytes) -> bytes: ...


def stamped(criteria=REQUIRED_STAMPS) -> dict[str, bool]:
    """Each criterion's stamp as the pin of record reads it. Unreadable reads as unstamped."""
    try:
        pin = envelope.load_tool("plainsight_tools_pin_of_record", PIN_TOOL).read(config.REPO_ROOT)
        return {c: bool(pin.criterion_stamped(c)) for c in criteria}
    except Exception:  # noqa: BLE001 - an unreadable pin permits nothing
        return {c: False for c in criteria}


class BlobStore:
    def __init__(self, root: Path, case_id: str, environment: str | None = None, encryptor: Encryptor | None = None):
        db.case_path(root, case_id)  # refuses a non-uuid case id before any path is built
        self.root = Path(root)
        self.case_id = case_id
        self.environment = environment or config.environment()
        self.encryptor = encryptor

    def path(self, sha: str) -> Path:
        if not (isinstance(sha, str) and len(sha) == 64 and all(ch in "0123456789abcdef" for ch in sha)):
            raise Refusal("BLOB_NOT_HELD", "the digest is not a lowercase sha256")
        return self.root / db.BLOBS_DIR / self.case_id / sha[:2] / sha

    def refusals(self) -> list[str]:
        """The unmet conditions for a write, each rendered as its consequence."""
        out = []
        if self.environment != "ISOLATED":
            out.append("the environment is not ISOLATED, so no blob is written here")
        if self.encryptor is None:
            out.append("no per-case Encryptor is configured, so a blob would be plaintext (RT-4)")
        stamps = stamped()
        for crit in REQUIRED_STAMPS:
            if not stamps.get(crit):
                out.append(f"{crit} is not stamped in doctrine/DOCTRINE_STATUS.md")
        return out

    def put(self, data: bytes) -> str:
        unmet = self.refusals()
        if unmet:
            raise Refusal("BLOB_WRITE_REFUSED", "unmet: " + "; ".join(unmet))
        sha = hashlib.sha256(data).hexdigest()
        target = self.path(sha)
        if not target.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(self.encryptor.encrypt(self.case_id, data))
        return sha

    def get(self, sha: str) -> bytes:
        target = self.path(sha)
        if not target.is_file():
            raise Refusal("BLOB_NOT_HELD")
        stored = target.read_bytes()
        try:
            data = self.encryptor.decrypt(self.case_id, stored) if self.encryptor is not None else stored
        except Exception:  # noqa: BLE001 - a failed decrypt is a failed digest
            raise Refusal("BLOB_DIGEST_MISMATCH", "the stored bytes did not decrypt") from None
        if hashlib.sha256(data).hexdigest() != sha:
            raise Refusal("BLOB_DIGEST_MISMATCH")
        return data
