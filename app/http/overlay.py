"""The showcase's display overlay: fictional stand-ins for the test corpus's placeholders.

`python -m app serve --ui showcase --overlay PATH` reads one JSON file at launch
and serves it as /static/overlay.json. The showcase draws its values over the
placeholders the store holds, at display time only. Nothing enters the store,
the log or the repository, and every request the page makes is still a GET.

The file must sit outside every git working tree and outside the store root.
AGENTS.md section 4 keeps every value, synthetic ones included, out of a
tracked file, and a file in another repository's working tree can be committed
there, where no gate of this repository runs. The store holds only what passed
the door. Its shape is closed, and its values are fictional by construction,
which this reader enforces rather than trusts:

- only a placeholder in the corpus's form, such as <synthetic-handle-1>, can be
  replaced, so no value the store holds as a value is ever drawn over;
- an email names only a reserved domain (example.com, example.org or
  example.net, RFC 2606) or a masked one;
- a run of digits long enough to be a phone number (seven characters or more,
  separators included) must hold a 555-0100 to 555-0199 number, the range
  reserved for fiction, so a date in a note is refused the same way;
- the subject's display name is the only addition, and it is a label: it carries
  no claim, no link and no review state;
- a handle is never the subject's first and last name joined plainly, which is
  how a real account is often named;
- a case pack, when present, answers every API request for one fictional case;
  in its every string an email names only a reserved domain, and a phone number
  holds a 555-01xx number when it is written in the North American shape, led
  by a plus sign, or as a bare run of ten or eleven digits; no string holds a
  link, no key is a coordinate key, and the file stays under a size cap;
- presentation is marked, the default, where the page labels the person as
  invented, or live, where the page drops its own test and placeholder labels
  for a presenter's screen. The rules above hold either way.

A refusal names the rule and the move, and never echoes a value.

What the reader does not read, so that a pass is not taken for more than it is.
A name or a handle cannot be told from a real person's, so the author of the
file answers for every one in it. In a case pack, a phone number in a shape other than the
three above, or written as a JSON number, is not read.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.store import db

KEYS = {"case", "label", "note", "presentation", "subject", "values"}
SUBJECT_KEYS = {"name"}
PLACEHOLDER = re.compile(r"^<synthetic-[a-z0-9-]+>$")
RESERVED = ("example.com", "example.org", "example.net")
EMAIL_DOMAIN = re.compile(r"@([^\s@]+)")
DIGIT_RUN = re.compile(r"\d[\d\s().-]{5,}\d")
FICTION_PHONE = re.compile(r"555[-. ]?01\d\d")
MAX_TEXT = 200
HANDLE = re.compile(r"^<synthetic-handle-[a-z0-9-]+>$")
PRESENTATIONS = ("marked", "live")
CASE_KEYS = {"responses", "labels"}
CASE_KEY_PREFIX = "/api/cases"
MAX_FILE_BYTES = 12_000_000
# An email in a case pack ends in a letter TLD, so a version stamp such as tool@0.1.0 is not one.
CASE_EMAIL = re.compile(r"[\w.+-]+@((?:[\w-]+\.)+[A-Za-z]{2,})(?![\w-])")
PHONE_SHAPE = re.compile(r"(?<![\w-])(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?![\w-])")
# A number led by a plus sign, in any country's grouping, and a bare run of ten or eleven digits. A time
# zone offset is too short to be the first, and a digit run inside an id, a hash or a timestamp is not the second.
PLUS_RUN = re.compile(r"(?<![\w-])\+\d[\d\s().-]{6,}\d")
BARE_RUN = re.compile(r"(?<![\w.:-])\d{10,11}(?![\w.:-])")
LINK = re.compile(r"://|\bwww\.", re.IGNORECASE)
GEO_KEYS = {"lat", "lon", "lng", "latitude", "longitude", "coordinate", "coordinates", "geometry", "geo_point"}


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _plain_name(handle: str, name: str) -> bool:
    """A handle that is the subject's first and last name joined plainly, in either order."""
    parts = [p.lower() for p in re.findall(r"[A-Za-z]+", name)]
    if len(parts) < 2:
        return False
    first, last = parts[0], parts[-1]
    joined = {a + sep + b for a, b in ((first, last), (last, first)) for sep in ("", ".", "_", "-")}
    return handle.lower().lstrip("@") in joined


def _fictional(text: str, where: str) -> None:
    for m in EMAIL_DOMAIN.finditer(text):
        domain = m.group(1).lower().rstrip(".,;:")
        if domain not in RESERVED and not any(ch in domain for ch in "•*"):
            raise ValueError(f"{where} names an email domain that is not reserved: use example.com, example.org or example.net, or mask it")
    for m in DIGIT_RUN.finditer(text):
        if not FICTION_PHONE.search(m.group(0)):
            raise ValueError(f"{where} holds a number that is not in the 555-0100 to 555-0199 range reserved for fiction")


def _case_text(text: str, where: str) -> None:
    for m in CASE_EMAIL.finditer(text):
        if m.group(1).lower() not in RESERVED:
            raise ValueError(f"{where} names an email domain that is not reserved: use example.com, example.org or example.net")
    for shape in (PHONE_SHAPE, PLUS_RUN, BARE_RUN):
        for m in shape.finditer(text):
            if not FICTION_PHONE.search(m.group(0)):
                raise ValueError(f"{where} holds a phone number outside the 555-0100 to 555-0199 range reserved for fiction")
    if LINK.search(text):
        raise ValueError(f"{where} holds a link; the case pack is display only and links to nothing")


def _walk_case(x, where: str) -> None:
    if isinstance(x, str):
        _case_text(x, where)
    elif isinstance(x, dict):
        for k, v in x.items():
            if not isinstance(k, str):
                raise ValueError(f"{where} has a key that is not text")
            if k.lower() in GEO_KEYS:
                raise ValueError(f"{where} holds a coordinate key; a case pack names places at city level, never a coordinate")
            _case_text(k, where)
            _walk_case(v, where)
    elif isinstance(x, list):
        for v in x:
            _walk_case(v, where)
    elif x is not None and not isinstance(x, (bool, int, float)):
        raise ValueError(f"{where} holds a value that is not JSON")


def _text(value, where: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TEXT:
        raise ValueError(f"{where} must be text of 1 to {MAX_TEXT} characters")
    _fictional(value, where)
    return value


def read_overlay(path, store_root) -> bytes:
    """The overlay as canonical JSON bytes, or ValueError naming what was refused."""
    p = Path(path).resolve()
    if db.in_git_working_tree(p.parent):
        raise ValueError("the overlay file is inside a git working tree; keep it outside every one, this repository's or another's")
    if _inside(p, Path(store_root).resolve()):
        raise ValueError("the overlay file is inside the store root; the store holds only what passed the door")
    try:
        too_big = p.stat().st_size > MAX_FILE_BYTES
    except OSError:
        too_big = False
    if too_big:
        raise ValueError(f"the overlay file is larger than {MAX_FILE_BYTES} bytes; a case pack stays under that cap")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"the overlay file could not be read as JSON ({type(exc).__name__})") from None
    if not isinstance(data, dict) or not set(data) <= KEYS or not isinstance(data.get("values"), dict) or not data["values"]:
        raise ValueError("the overlay must be an object with values, and may carry only case, label, note, presentation, subject and values")
    out: dict = {"values": {}}
    for key, value in data["values"].items():
        if not isinstance(key, str) or not PLACEHOLDER.fullmatch(key):
            raise ValueError("an overlay key is not a corpus placeholder such as <synthetic-handle-1>; only placeholders are drawn over")
        out["values"][key] = _text(value, "an overlay value")
    for key in ("label", "note"):
        if key in data:
            out[key] = _text(data[key], f"the overlay's {key}")
    if "subject" in data:
        subject = data["subject"]
        if not isinstance(subject, dict) or not set(subject) <= SUBJECT_KEYS:
            raise ValueError("the overlay's subject may carry only a name")
        out["subject"] = {k: _text(v, "the subject's name") for k, v in subject.items()}
    if "case" in data:
        case = data["case"]
        if not isinstance(case, dict) or not set(case) <= CASE_KEYS or not isinstance(case.get("responses"), dict) or not case["responses"]:
            raise ValueError("the overlay's case must be an object of responses, and may carry only responses and labels")
        if not all(isinstance(k, str) and k.startswith(CASE_KEY_PREFIX) for k in case["responses"]):
            raise ValueError("a case-pack key is not a case request such as /api/cases/<case>/header")
        labels = case.get("labels", {})
        if not isinstance(labels, dict) or not all(isinstance(k, str) and isinstance(v, str) and 0 < len(v) <= 60 for k, v in labels.items()):
            raise ValueError("the case pack's labels map a producer to a display name of 1 to 60 characters")
        _walk_case(case, "the case pack")
        out["case"] = case
    if "presentation" in data:
        if data["presentation"] not in PRESENTATIONS:
            raise ValueError("the overlay's presentation is marked or live: marked labels the person as invented, live drops the page's test labels")
        out["presentation"] = data["presentation"]
    name = out.get("subject", {}).get("name", "")
    for key, value in out["values"].items():
        if HANDLE.fullmatch(key) and _plain_name(value, name):
            raise ValueError("an overlay handle is the subject's plain first and last name; use an uncommon handle, such as one with digits, so it stays clear of real accounts")
    return json.dumps(out, ensure_ascii=False, sort_keys=True).encode("utf-8")
