#!/usr/bin/env python3
"""since_last_record.py: the closeout's delta file, so a resumer reads it instead of the transcript.

Writes, from one Claude Code session transcript (a .jsonl under ~/.claude/projects/<project key>/),
everything a resumer needs that a closeout record can miss, from a given moment to the end of the file:

  - the maintainer's own lines in the span, each marked by how it arrived: TYPED; CLICK ON OFFERED
    ACTION when the text equals, word for word, the `message` of an action the session offered in the
    most recent wrap-up tool call before that line (the app delivers a clicked message cut at 300
    characters, so a 300-character prefix of such a message is the same click, cut, and is marked so),
    or equals that action's `label`, which is what the app delivers for some clicks (marked "by its
    label"; a line he typed that equals a label of that same latest call carries the same record
    fields as the click and reads the same, which the mark says, and a line equal to a label of any
    earlier call stays TYPED); or SELECTION ON OFFERED QUESTION when the maintainer answered an
    AskUserQuestion call, printed with the tool's result text, which carries each question and the
    chosen option verbatim;
  - the harness's own records in the user role, by stamp and kind only: a context-compaction summary
    (the record carries isCompactSummary) and a harness notice such as a classifier stop (the record
    carries isMeta). Neither is a line of his, and before 2026-11-02 each was marked TYPED;
  - every cross-session message the session sent (the SendMessage tool inputs, verbatim);
  - every cross-session message it received (the `<cross-session-message>` user entries, verbatim);
  - its last N assistant texts.

Other tool results, the harness's task notifications (skipped by their tag) and thinking are left out.
Each timestamp is printed in the machine's local zone with the offset in force at that instant and
that offset written after it, as 2026-10-28 17:45:23 -0400, so a stamp from before a daylight-time
change prints as the clock read then and says so (before 2026-11-02 every stamp was converted with the
offset of the day the tool ran and carried no offset, and a stamp from the other side of the change
printed one hour off). The file is data, not a record: it is
filed beside the closeout record, outside the tree, and read once before the records are written, so that
a line marked as a click or a selection is never written as "typed". That is the error the records of
2026-10-18 carried and the commit of 2026-10-24 corrected, and the reason the detection compares against
the offered actions: in this harness a click arrives as an ordinary user entry, with no attachment that
names it a click, and a question's answer arrives as a tool result.

The file copies the maintainer's lines and every message verbatim, so it is a store no retention
mechanism in this repository reaches. The tool refuses an output path inside the repository, and a
closeout does not run it over a span in which case material was discussed until doctrine/RETENTION.md
says how such a copy is held.

Usage:
  python tools/since_last_record.py <transcript.jsonl> <since> <out.md> [last_assistant_n=3]
  python tools/since_last_record.py --self-test

<since> is an ISO-8601 moment with a zone (2026-10-24T18:36:00Z, or an offset such as
2026-10-24T14:36:00-04:00) or the word all. A moment without a zone is refused rather than read as
local time, because a wrong zone silently empties the span.

Exit 0 on success; 1 on a bad argument, a since without a zone, an output path inside the repository, or
a self-test failure; 2 when the input cannot be read or holds no transcript record (the negative control
for a file that is not a transcript); 3 when the output file cannot be written.

The self-test writes a small synthetic transcript under a temporary directory and asserts that a typed
line, a click, a click cut at 300 characters, a click delivered as its button's label, a selection on an
offered question, a sent message, a received message and an assistant text are each classified as what
they are; that a compaction summary and a harness notice in the user role are listed as harness records
and never as typed lines; that a typed line equal to an offer from an earlier, superseded wrap-up call
stays TYPED, and so does a line equal to an offer made after it and a line equal to a superseded call's
label; that both text blocks of an unflagged record typed in two blocks are his lines and neither is a
harness record; that two stamps on either side of the local zone's daylight-time change each print with the
offset the operating system gives for that instant, read independently of the conversion under test;
then it runs the controls: a since later than the last entry yields zero entries and a file whose every
section says "none in the span", a file that is not a transcript is refused, a since without a zone is
refused, and an output path inside the repository is refused. Removing the offered-action comparison fails
the click checks; removing the label comparison fails the label-click check; removing the harness-flag
branch fails the harness checks; converting with one fixed offset fails the zone check on a machine whose
zone observes daylight time; removing the tool-result branch fails the selection check; widening the
comparison past the most recent wrap-up call fails the superseded-offer check; removing the since filter,
the record check, the zone check or the path check fails its control. The tool is a copy of the parent folder's
toolkit playbook of 2026-10-24 under this repository's own process, adapted after that playbook's click
test was found never to fire here (it looked for an attachment this harness does not write); nothing
here is imported from the parent folder.
"""
import io
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime

SKIP = ("<", "[Image", "# Workflow", "[Usage", "[Earlier", "[Request", "Another Claude", "<command-name>")
WRAP_UP_SUFFIX = "wrap_up"
ASK_TOOL = "AskUserQuestion"
SEND_TOOLS = ("SendMessage", "mcp__ccd_session_mgmt__send_message")
CUT = 300
REPO_ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


class Refusal(Exception):
    """A refusal the caller reports with exit 1: the message names the rule and the legal move."""


def _local_zone():
    return datetime.now().astimezone().tzinfo


def _local(ts, zone=None):
    """The stamp in the machine's local zone, with the offset in force at that instant.

    astimezone() with no argument asks the operating system for the local offset of that moment, so a
    stamp from before a daylight-time change prints as the clock read then. The zone the header prints
    is still the one in force when the tool runs; `zone` is accepted and unused so callers need not change.
    """
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    except Exception:
        return ts


HARNESS_FLAGS = (("isCompactSummary", "context-compaction summary"), ("isMeta", "harness notice"))


def _harness_kind(o):
    """The kind of a harness record in the user role, or None for a record that may be his."""
    for flag, kind in HARNESS_FLAGS:
        if o.get(flag) is True:
            return kind
    return None


def _clean(t):
    t = t.strip()
    cut = t.find("<command-name>")
    return t[:cut].strip() if cut > 0 else t


def _norm(t):
    return re.sub(r"\s+", " ", t).strip()


def parse_since(since):
    """'all' -> None; otherwise an aware datetime, or a Refusal when the moment has no zone."""
    if since == "all":
        return None
    try:
        dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
    except ValueError:
        raise Refusal("since %r is not an ISO-8601 moment; moves: give 2026-10-24T18:36:00Z, or the word all" % since)
    if dt.tzinfo is None:
        raise Refusal("since %r has no zone, and a zone guessed wrong empties the span silently; "
                      "moves: append Z for UTC, or an offset such as -04:00 for EDT" % since)
    return dt


def check_out_path(out):
    """Refuse an output path that resolves inside the repository."""
    real = os.path.realpath(out)
    if real == REPO_ROOT or real.startswith(REPO_ROOT + os.sep):
        raise Refusal("the output path %s is inside the repository, and the file copies the maintainer's lines and "
                      "messages verbatim into a store no retention mechanism reaches; moves: write it beside the "
                      "closeout record under Z-ISR/_session-artifacts/, outside the tree" % out)


def _tool_result_text(block):
    c = block.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(p.get("text", "") for p in c if isinstance(p, dict) and p.get("type") == "text")
    return ""


def extract(src, since, out, last_n=3):
    """Run the extraction. Returns a dict of counts.

    Raises Refusal for a since without a zone or an output path inside the repository, OSError when the
    input cannot be read, ValueError("not a transcript") when no line parses as a transcript record, and
    OSError from the write (the caller tells the two apart by order).
    """
    since_dt = parse_since(since)
    check_out_path(out)
    zone = _local_zone()
    with open(src, encoding="utf-8") as f:
        raw = f.read().splitlines()
    all_entries = []
    for line in raw:
        try:
            o = json.loads(line)
        except Exception:
            continue
        if isinstance(o, dict) and "type" in o:
            all_entries.append(o)
    if not all_entries:
        raise ValueError("not a transcript")

    # Pass 1, the whole file: every wrap-up call with its offered actions, and every AskUserQuestion
    # call by id, so a line in the span can be matched against an offer made before the span began.
    wrapups = []  # (timestamp, [(label, normalized message, normalized label)])
    asks = {}     # tool_use id -> timestamp
    for o in all_entries:
        if o.get("type") != "assistant":
            continue
        for b in o.get("message", {}).get("content", []) or []:
            if b.get("type") != "tool_use":
                continue
            name = str(b.get("name", ""))
            if name.endswith(WRAP_UP_SUFFIX):
                acts = []
                for a in (b.get("input", {}) or {}).get("actions", []) or []:
                    label = a.get("label") or ""
                    msg = a.get("message") or label
                    if msg:
                        acts.append((label, _norm(msg), _norm(label)))
                wrapups.append((o.get("timestamp", ""), acts))
            elif name == ASK_TOOL:
                asks[b.get("id", "")] = o.get("timestamp", "")

    def offered_before(ts, text):
        """Match only against the most recent wrap-up call at or before ts: the action's message, a
        300-character prefix of it, or the action's label, which is what the app delivers for some clicks."""
        latest = None
        for wts, acts in wrapups:
            if wts and ts and wts > ts:
                break
            latest = (wts, acts)
        if latest is None:
            return None
        n = _norm(text)
        rawt = text.strip()
        for label, msg, lab in latest[1]:
            if msg == n:
                return (latest[0], label, "")
            if len(rawt) == CUT and msg.startswith(_norm(rawt)):
                return (latest[0], label, ", cut at %d characters by the app" % CUT)
            if lab and lab == n:
                return (latest[0], label, ", by its label: the app delivered the button's label rather than its "
                                          "message, and a line typed equal to that label would read the same")
        return None

    entries = []
    for o in all_entries:
        ts = o.get("timestamp") or ""
        if since_dt is not None:
            try:
                ets = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                continue
            if ets < since_dt:
                continue
        entries.append(o)

    lines, queued, sent, received, assistant, harness = [], [], [], [], [], []
    seen = set()
    for o in entries:
        ts, t = o.get("timestamp", ""), o.get("type")
        if t == "user":
            harness_kind = _harness_kind(o)
            c = o.get("message", {}).get("content")
            blocks = [{"type": "text", "text": c}] if isinstance(c, str) else [b for b in (c or []) if isinstance(b, dict)]
            for b in blocks:
                if b.get("type") == "tool_result":
                    # A tool result is read whatever the record's flags say, so a flagged record
                    # can never hide an answer to an offered question.
                    if b.get("tool_use_id") in asks:
                        tx = _tool_result_text(b).strip()
                        if tx:
                            lines.append((ts, "SELECTION ON OFFERED QUESTION (asked at %s)" % _local(asks[b["tool_use_id"]], zone), tx))
                    continue
                if b.get("type") != "text":
                    continue
                if harness_kind:
                    # A text the harness wrote in the user role: a compaction summary or a notice. Not
                    # his, so it is counted and listed by stamp and kind, and its text is not copied.
                    # The name is the record's, never the line kind below, which a later text block
                    # of the same record must not inherit (the self-test plants a two-block record).
                    harness.append((ts, harness_kind))
                    break
                tx = _clean(b.get("text", ""))
                if not tx:
                    continue
                if tx.startswith("Another Claude session sent a message") or "<cross-session-message" in tx[:200]:
                    received.append((ts, tx))
                elif not tx.startswith(SKIP):
                    hit = offered_before(ts, tx)
                    kind = ("CLICK ON OFFERED ACTION (button %r offered at %s%s)" % (hit[1], _local(hit[0], zone), hit[2])) if hit else "TYPED"
                    lines.append((ts, kind, tx))
                    seen.add(_norm(tx))
        elif t == "attachment":
            a = o.get("attachment", {})
            if a.get("type") == "queued_command" and a.get("prompt"):
                tx = _clean(a["prompt"])
                if tx.startswith(SKIP) or "<cross-session-message" in tx[:200]:
                    continue
                if _norm(tx) not in seen:
                    hit = offered_before(ts, tx)
                    kind = ("CLICK ON OFFERED ACTION, queued (button %r)" % hit[1]) if hit else "QUEUED (queued_command, no user entry)"
                    queued.append((ts, kind, tx))
        elif t == "queue-operation":
            tx = _clean(o.get("content") or "")
            if tx and o.get("operation") == "enqueue" and not tx.startswith(SKIP) and "<cross-session-message" not in tx[:200]:
                if _norm(tx) not in seen and _norm(tx) not in {_norm(q[2]) for q in queued}:
                    queued.append((ts, "QUEUED (queue-operation enqueue, no user entry)", tx))
        elif t == "assistant":
            for b in o.get("message", {}).get("content", []) or []:
                if b.get("type") == "text" and b.get("text", "").strip():
                    assistant.append((ts, b["text"]))
                elif b.get("type") == "tool_use" and b.get("name") in SEND_TOOLS:
                    inp = b.get("input", {}) or {}
                    sent.append((ts, str(inp.get("to") or inp.get("session_id") or ""), inp.get("message") or ""))
    queued = [q for q in queued if _norm(q[2]) not in seen]

    with open(out, "w", encoding="utf-8") as g:
        g.write("# Since-last-record extraction of %s\n\n" % src.replace("\\", "/").split("/")[-1])
        g.write("Status: data, not a record; produced by tools/since_last_record.py from the transcript, entries at or after %s; "
                "%d entries read; %d wrap-up calls and %d question calls seen in the whole file; written %s.\n\n"
                % (since, len(entries), len(wrapups), len(asks), datetime.now(zone).strftime("%Y-%m-%d %H:%M:%S %Z")))
        g.write("## The maintainer's lines\n\n")
        for ts, kind, tx in lines:
            g.write("- [%s] %s: %s\n" % (_local(ts, zone), kind, tx))
        for ts, kind, tx in queued:
            g.write("- [%s] %s: %s\n" % (_local(ts, zone), kind, tx))
        if not (lines or queued):
            g.write("- none in the span\n")
        g.write("\n## Harness records in the user role (not his; stamp and kind only)\n\n")
        for ts, kind in harness:
            g.write("- [%s] %s\n" % (_local(ts, zone), kind))
        if not harness:
            g.write("- none in the span\n")
        g.write("\n## Messages sent to other sessions\n\n")
        for ts, to, msg in sent:
            g.write("### [%s] to %s\n\n%s\n\n" % (_local(ts, zone), to, msg))
        if not sent:
            g.write("- none in the span\n\n")
        g.write("## Messages received from other sessions\n\n")
        for ts, tx in received:
            body = re.sub(r"^Another Claude session sent a message:\s*", "", tx)
            g.write("### [%s]\n\n%s\n\n" % (_local(ts, zone), body))
        if not received:
            g.write("- none in the span\n\n")
        g.write("## Last %d assistant texts\n\n" % last_n)
        for ts, tx in assistant[-last_n:]:
            g.write("### [%s]\n\n%s\n\n" % (_local(ts, zone), tx))
        if not assistant:
            g.write("- none in the span\n")
    clicks = sum(1 for l in lines if l[1].startswith("CLICK"))
    selections = sum(1 for l in lines if l[1].startswith("SELECTION"))
    return {"entries": len(entries), "typed": len(lines) - clicks - selections, "clicks": clicks,
            "cut_clicks": sum(1 for l in lines if "cut at" in l[1]),
            "label_clicks": sum(1 for l in lines if "by its label" in l[1]), "selections": selections,
            "harness": len(harness),
            "queued": len(queued), "sent": len(sent), "received": len(received), "assistant": len(assistant),
            "wrapups": len(wrapups), "asks": len(asks)}


def _rec(ts, typ, **kw):
    o = {"type": typ, "timestamp": ts}
    o.update(kw)
    return json.dumps(o)


def _wrapup(ts, actions):
    return _rec(ts, "assistant", message={"content": [{"type": "tool_use", "name": "mcp__ccd_turn__wrap_up",
                                                      "input": {"actions": actions}}]})


def self_test():
    """Plant one line of each kind and the controls; exit 1 on the first failure."""
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))
        print("  %-8s %s" % ("ok" if cond else "FAILED", name))

    long_msg = ("Commit the staged draft now as me with no trailer, push it on a branch, open the pull request and read "
                "every step before any merge; this message is made long on purpose so that the cut at three hundred "
                "characters leaves a strict prefix of it for the test, and it keeps going past that length to be sure "
                "it does so.")
    assert len(long_msg) > CUT
    t = lambda m, s=0: "2026-10-24T12:%02d:%02d.000Z" % (m, s)
    planted = {
        "typed": "Something I typed myself.",
        "click": "Do the thing now.",
        "cut click": long_msg[:CUT],
        "selection": 'Your questions have been answered: "Merge it?"="Merge now (Recommended)". You can now continue.',
        "sent": "A line to a peer.",
        "received": "Another Claude session sent a message:\n<cross-session-message from=\"local_peer\">hello</cross-session-message>",
        "assistant text": "The last thing said.",
        "typed, equal to a superseded offer": "Old offer text.",
        "typed, equal to a later offer": "Future offer text.",
        "label click": "Hold",
        "typed, equal to a superseded call's label": "Old",
        "typed, first text block of a two-block record": "The first block of a record he typed in two blocks.",
        "typed, second text block of a two-block record": "The second block of the same record.",
        "compaction summary": "This session is being continued from a previous conversation that ran out of context. "
                              "The summary below covers the earlier portion of the conversation.",
        "harness notice": "Your response above was stopped by a safety classifier. The rest of it was withheld.",
    }
    recs = [
        _wrapup(t(0), [{"label": "Old", "message": "Old offer text."}]),
        _wrapup(t(1), [{"label": "Do it", "message": "Do the thing now."}, {"label": "Hold", "message": "Hold it."}]),
        _rec(t(2), "user", message={"content": planted["click"]}),
        _rec(t(2, 30), "user", message={"content": planted["label click"]}),
        _rec(t(3), "user", message={"content": planted["typed"]}),
        _rec(t(3, 30), "user", message={"content": planted["typed, equal to a superseded offer"]}),
        _rec(t(3, 40), "user", message={"content": planted["typed, equal to a later offer"]}),
        _rec(t(3, 45), "user", message={"content": planted["typed, equal to a superseded call's label"]}),
        _rec(t(3, 47), "user", message={"content": [
            {"type": "text", "text": planted["typed, first text block of a two-block record"]},
            {"type": "text", "text": planted["typed, second text block of a two-block record"]}]}),
        _rec(t(3, 50), "user", isCompactSummary=True, message={"content": planted["compaction summary"]}),
        _rec(t(3, 55), "user", isMeta=True, message={"content": planted["harness notice"]}),
        _wrapup(t(4), [{"label": "Commit", "message": long_msg}, {"label": "Later", "message": "Future offer text."}]),
        _rec(t(5), "user", message={"content": planted["cut click"]}),
        _rec(t(5, 30), "assistant", message={"content": [{"type": "tool_use", "name": ASK_TOOL, "id": "ask-1",
                                                          "input": {"questions": [{"question": "Merge it?"}]}}]}),
        _rec(t(5, 40), "user", message={"content": [{"type": "tool_result", "tool_use_id": "ask-1", "content": planted["selection"]}]}),
        _rec(t(6), "assistant", message={"content": [{"type": "tool_use", "name": "SendMessage",
                                                      "input": {"to": "local_peer", "message": planted["sent"]}}]}),
        _rec(t(7), "user", message={"content": planted["received"]}),
        _rec(t(8), "assistant", message={"content": [{"type": "text", "text": planted["assistant text"]}]}),
    ]
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "t.jsonl")
        with open(src, "w", encoding="utf-8") as f:
            f.write("\n".join(recs) + "\n")
        out = os.path.join(d, "out.md")
        r = extract(src, "all", out, 3)
        text = open(out, encoding="utf-8").read()
        check("a typed line is TYPED, and so is a line equal to a superseded or a later offer, to a superseded call's "
              "label, and each text block of a record typed in two blocks (6 typed)", r["typed"] == 6)
        check("the superseded call's label is marked TYPED, not CLICK",
              ("TYPED: " + planted["typed, equal to a superseded call's label"]) in text)
        check("the second text block of an unflagged record is his line, not a harness record",
              ("TYPED: " + planted["typed, second text block of a two-block record"]) in text and r["harness"] == 2)
        check("a line equal to the latest offer is a CLICK, a 300-character prefix is a cut CLICK, and the button's "
              "label alone is a CLICK by its label (3 clicks)",
              r["clicks"] == 3 and r["cut_clicks"] == 1 and r["label_clicks"] == 1)
        check("the label click names its button and says the app delivered the label",
              "by its label" in text and ("(button 'Hold' offered at" in text) and (": Hold\n" in text))
        check("a compaction summary and a harness notice in the user role are harness records, not his lines (2)",
              r["harness"] == 2 and "context-compaction summary" in text and "harness notice" in text)
        check("neither harness record's text is copied or marked TYPED",
              planted["compaction summary"] not in text and planted["harness notice"] not in text)
        check("the superseded offer's text is marked TYPED, not CLICK", ("TYPED: " + planted["typed, equal to a superseded offer"]) in text)
        check("the later offer's text is marked TYPED, not CLICK", ("TYPED: " + planted["typed, equal to a later offer"]) in text)
        # The zone: each stamp converts with the operating system's offset for that instant, and the
        # reference is read from time.localtime, not from the conversion under test.
        pair = ("2026-10-28T21:45:23Z", "2026-11-02T22:44:21Z")
        refs = []
        for s in pair:
            lt = time.localtime(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
            off = lt.tm_gmtoff
            refs.append(time.strftime("%Y-%m-%d %H:%M:%S", lt) + " %s%02d%02d" % ("-" if off < 0 else "+", abs(off) // 3600, abs(off) % 3600 // 60))
        check("each stamp prints as the operating system's local clock read at that instant, with that offset",
              [_local(s) for s in pair] == refs)
        fixed = datetime.now().astimezone().tzinfo
        olds = [datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(fixed).strftime("%Y-%m-%d %H:%M:%S %z") for s in pair]
        offsets = {time.localtime(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()).tm_gmtoff for s in pair}
        if len(offsets) > 1:
            check("control: one fixed offset prints one of the two stamps an hour off on this machine", olds != refs)
        else:
            check("control: this machine's zone has one offset across the pair, so the fixed-offset control cannot fire here "
                  "and is reported rather than claimed", olds == refs)
        check("an AskUserQuestion answer is a SELECTION ON OFFERED QUESTION", r["selections"] == 1 and planted["selection"] in text)
        check("the sent message is listed", r["sent"] == 1 and planted["sent"] in text)
        check("the received message is listed", r["received"] == 1 and "hello" in text)
        check("the last assistant text is listed", r["assistant"] == 1 and planted["assistant text"] in text)
        check("no click or selection is written as TYPED", text.count("TYPED:") == 6)
        # Control 1: a since-stamp later than the last entry.
        out2 = os.path.join(d, "out2.md")
        r2 = extract(src, "2026-10-25T00:00:00Z", out2, 3)
        text2 = open(out2, encoding="utf-8").read()
        check("control: a since past the last entry reads zero entries, every section none in the span",
              r2["entries"] == 0 and text2.count("none in the span") == 5)
        # Control 2: a file that is not a transcript.
        notes = os.path.join(d, "notes.txt")
        with open(notes, "w", encoding="utf-8") as f:
            f.write("This is prose, not a transcript.\n")
        refused = False
        try:
            extract(notes, "all", os.path.join(d, "out3.md"), 3)
        except ValueError:
            refused = True
        check("control: a file that is not a transcript is refused", refused)
        # Control 3: a since without a zone.
        refused = False
        try:
            extract(src, "2026-10-24T08:00:00", os.path.join(d, "out4.md"), 3)
        except Refusal:
            refused = True
        check("control: a since without a zone is refused", refused)
        # Control 4: an output path inside the repository.
        refused = False
        try:
            extract(src, "all", os.path.join(REPO_ROOT, "since_last_record_control.md"), 3)
        except Refusal:
            refused = True
        check("control: an output path inside the repository is refused", refused)
        check("control: nothing was written inside the repository", not os.path.exists(os.path.join(REPO_ROOT, "since_last_record_control.md")))
    failed = [n for n, ok in checks if not ok]
    if failed:
        print("since_last_record --self-test FAILED: %d of %d checks" % (len(failed), len(checks)))
        return 1
    print("since_last_record --self-test ok: %d checks, %d planted lines classified, 4 controls seen refusing" % (len(checks), len(planted)))
    return 0


def main(argv):
    if len(argv) >= 2 and argv[1] == "--self-test":
        return self_test()
    if len(argv) < 4:
        print(__doc__)
        return 1
    src, since, out = argv[1], argv[2], argv[3]
    try:
        last_n = int(argv[4]) if len(argv) > 4 else 3
    except ValueError:
        print("bad argument: last_assistant_n must be an integer")
        return 1
    try:
        parse_since(since)
        check_out_path(out)
    except Refusal as e:
        print("REFUSED:", e)
        return 1
    try:
        with open(src, encoding="utf-8"):
            pass
    except OSError as e:
        print("cannot read transcript:", e)
        return 2
    try:
        r = extract(src, since, out, last_n)
    except ValueError:
        print("not a transcript: no line of the file parses as a transcript record")
        return 2
    except OSError as e:
        print("cannot write the output file %s: %s; moves: create its folder beside the closeout record, or name another path outside the tree" % (out, e))
        return 3
    print("%d entries since %s: %d typed, %d clicks on offered actions (%d cut, %d by label), %d selections on offered questions, "
          "%d harness records in the user role, %d queued, %d sent, %d received, %d assistant texts -> %s"
          % (r["entries"], since, r["typed"], r["clicks"], r["cut_clicks"], r["label_clicks"], r["selections"], r["harness"],
             r["queued"], r["sent"], r["received"], r["assistant"], out))
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.exit(main(sys.argv))
