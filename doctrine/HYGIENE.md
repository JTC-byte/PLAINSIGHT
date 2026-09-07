# Hygiene doctrine: housekeeping, and adjudicating the gates themselves

**Status: DRAFTED 2026-08-27. ALL CONCLUSIONS RECORDED. Landed in commit `4c5cd25` on 2026-08-27.**

Advisory, Class A, and the only doctrine file that is not rank 1. It governs how
this repository keeps itself honest over time rather than what may be collected.

The 2026-08-26 draft of the `docs/THE-GAMEPLAN.md` §2.1 register said the
absence of this file would show up at month four as drift in both directions;
the row now reads that gate drift in both directions is silent. The operator
asked on 2026-08-27 for gate firings and gate failures to be recorded so that
keeping, improving or retiring a check becomes an adjudicated decision. That
request is the reason this file exists now rather than at month four.

---

## 1. Why the gates need their own pattern of life

A gate has two failure modes and both are silent.

A check that **never fires** looks exactly like a check that is working. There is
no observable difference between a guard nobody has tripped and a guard whose
condition can never be true, and the second one is a comfort rather than a
control. `zisr-recon`'s `guard.py` is the measured case: `scope` was declared,
required, and printed, and `check()` never read it, so the guard reported a scope
it did not enforce and nothing in the system could tell.

A check that **always fires** gets routed around rather than fixed. Every author
learns the flag that skips it, and after a month the refusal is noise carrying no
information.

Neither is visible from a single run. Both are obvious from a pattern.

**HY-1. Every gate run is recorded, and the record never carries the offending
value.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

`tools/gate_log.py` appends one line per gate run: timestamp, gate token,
outcome, violation code, and the location. **It records the file and the line. It
never records the string that matched.**

That rule is the whole safety of this mechanism. A `--repo-scan` refusal exists
because a selector-shaped string was found in a tracked file, and a telemetry
record quoting that string would place the value into a durable local log,
turning the gate's own evidence into the surface the gate exists to prevent. The
allowed field list in `gate_log.py` is a fixed tuple rather than a convention, so
a caller cannot widen the record by accident.

Telemetry never blocks a gate. Every failure path in the recorder is swallowed,
because a gap in the pattern of life costs a decision later and a crashed gate
costs enforcement now.

**HY-2. Both directions are adjudicated, against stated thresholds.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

`make gate-telemetry` renders per-gate run counts, refusal counts, and the
violation codes behind them over the retained window.

| Observed | Reading | Move |
|---|---|---|
| Zero refusals over a full window, and the condition was reachable | The check may be unfalsifiable | Break the corpus deliberately and confirm it refuses. If it cannot be made to refuse, it is not a check |
| Refuses on nearly every run | The refusal carries no information and will be routed around | Narrow the rule, or accept the pattern and exempt the class explicitly with a reason |
| One violation code dominates every other | The rule is probably two rules | Split it, so the frequent one can be tuned without loosening the rare one |
| A code that fired once and never again | Nothing. A rare catch is the point | Keep |

**The thresholds are deliberately not numeric.** A count means nothing without
knowing how many commits the window covers, and this repository has one
contributor, so a rate is not a statistic. The judgment is the operator's and the
telemetry exists to inform it rather than to make it.

**HY-3. Retiring or loosening a gate is a decision with a written reason.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Recorded in the worklog, naming the gate, the pattern that justified the change,
and what is no longer checked. Deleting a check quietly is the drift this file
exists to prevent, and it is the easiest thing in the repository to do.

**The reason a gate was added survives with it.** The module docstring of
`tools/validate_doctrine.py` lists the defects its checks were written against,
and most check blocks name their defect id in place; the two corpus-shape
checks, `DOCTRINE_FILE_EMPTY` and `DOCTRINE_CRITERION_DUPLICATE`, are attached
to D-04 and D-02 in the docstring only. A check whose origin is forgotten looks
arbitrary and gets removed.

**HY-4. A gate that was adjudicated and kept is recorded too, not only the ones
that changed.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

`docs/THE-GAMEPLAN.md` §5.9 gives the reason, and it applies to gates as directly
as to doctrine: recording only the failures removes the baseline that makes an
outlier recognizable. A review that examined six gates and changed none is a
result, and writing it down is what makes the seventh review's change meaningful.

---

## 2. Cadence

- **Per commit:** the pre-commit battery runs. That is not a review.
- **Per wave:** `make gate-telemetry`, adjudicate against HY-2, record the
  outcome per HY-3 and HY-4.
- **Per doctrine change:** the documentation matrix in `AGENTS.md` §6 names the
  surfaces that move together. The gates check some of it and not all of it.
- **When a check is written:** break the corpus deliberately and confirm the
  check refuses. A gate nobody has watched fail is an assumption, and design
  gate 1 asks for a test that fails when the constraint is removed.

---

## 3. What is explicitly NOT gated

- How often the operator reviews telemetry. The cadence above is a
  recommendation, and a missed review costs a delayed decision rather than a
  violation.
- Adding a gate. New checks are free and are expected to be routine, on the same
  reasoning as design gate 8's cheap additions.
- The content of the telemetry log, which is untracked, local, and carries no
  subject-derived value by construction.

---

## 4. Ratification table

| Item | Subject | Related |
|---|---|---|
| HY-1 | Every gate run recorded, never the offending value | RT-19 |
| HY-2 | Both failure directions adjudicated against stated thresholds | none |
| HY-3 | Retiring or loosening a gate needs a written reason | none |
| HY-4 | Gates adjudicated and kept are recorded too | none |
