## PART 1 — WHAT THE TWO ARTIFACTS ACTUALLY DO (measured, not inferred)

Files read in full:
- `<wave-0-scratchpad>\plainsight.html` (47.5 KB, ~5,400 words of prose, 6 tables, 5 callouts, 3 pull quotes, 4 `<pre>`, 14 `<h2>`)
- `<wave-0-scratchpad>\sherlock-field-manual.html` (62.1 KB, ~6,300 words, 9 tables, 10 callouts, 0 pull quotes, 15 `<pre>`, 19 `<h2>`, 22 inline chips)

The two documents share **no font, no hue, no device inventory, and no masthead shape**. They share a skeleton and a set of rules. That divergence is the proof that what exists here is a standard and not a template — and it is the most important empirical finding of this survey.

### 1. Structural devices, and the job each one holds

| Device | Where | The job it does | What earns it | What abuse looks like |
|---|---|---|---|---|
| **Headline-verdict banner** | plainsight `.verdict-banner`, `border-top: 2px solid var(--ink)`, `.big` at `clamp(1.3rem, 3.4vw, 2rem)`, `max-width: 22ch` | States the finding before any evidence exists to support it. `<em>` inside it is redefined `font-style: normal; color: var(--signal)` — the emphasis is *hue*, not italic | A document with **one** finding that changes what the reader does. "Zero of the six are adoptable." | A banner containing a topic ("An audit of six tools") instead of a verdict. If you can't fill 22ch with a claim someone could disagree with, you haven't got a banner |
| **Tally strip** | plainsight `.tallies` (5 cells); sherlock `.stats` (5 cells, `grid-template-columns: repeat(auto-fit, minmax(148px,1fr))`) | Makes the verdict *countable* immediately below the verdict. `font-variant-numeric: tabular-nums` on every value. Exactly one cell is allowed the signal colour (`.tally.bad`, `.stat.hot`) | Numbers that are the *substance* of the finding: `4 / 1 / 1 / 0 / 40`; `481 / 414 / 462 / 20 / 78.8%` | A dashboard. Six cells of vanity metrics ("12 sections, 47 sources"). If a number isn't load-bearing in an argument later in the document, it doesn't go in the strip |
| **Verdict table** | plainsight `#verdicts` (Tool / What it is / Licence / Auth / Works? / Verdict); sherlock `errorType` and CLI-flag tables | One row per thing being judged, with the **verdict as the last column** so the eye lands there. `td.dead` colours only that cell | A finite, enumerable set (6 tools, 3 errorTypes, 19 flags) where the reader's real question is "which ones?" | Using a table for prose that has no columnar structure. A two-column table whose second column is a paragraph is a definition list wearing a costume |
| **Callout** | `.call` — `border-left: 3px solid`, `.lbl` mono uppercase `letter-spacing: .14em`. plainsight has 2 variants (signal / `.n` neutral); sherlock has 3 (`accent` / `.trap` red / `.warn` amber) | Holds the *one idea the document turns on*, or a trap the reader will otherwise walk into. Note `.call p { max-width: none }` — the box takes over measure-setting from the paragraph | plainsight: "Adjudication happens at the moment of citation, not the moment of arrival." sherlock: "The URL you are shown is not the URL that was tested" | Ten callouts per screen. In plainsight there are 5 callouts across 14 sections — most sections have none. A callout that only restates the paragraph above it has stolen the device's meaning |
| **Pull quote** | plainsight `.pull` only — sans, 1.32rem, `max-width: 44ch`, `border-left: 3px solid var(--ink)` — **ink, deliberately not signal** | Compresses a whole section into one line the reader can carry away. Used **3 times in 5,400 words** | A sentence that is the section's thesis and survives being read alone: "You are not adopting a toolchain. You are writing six adapters and a system to make their disagreements legible." | Any use in a reference document — sherlock has **zero**, correctly. A manual has no thesis to compress. Also: pull-quoting a sentence that appears verbatim in the body two inches away |
| **Sticky nav rail** | both — `position: sticky; top: 0; max-height: 100vh`, 190px / 232px, grouped by `.grp` mono kickers ("Part 1 · Audit", "Part B — Operating") | Turns a long scroll into a map. The `.grp` groupings *are* the document's argument structure exposed as furniture | Documents over ~2,500 words with more than ~8 sections, that will be **returned to** rather than read once | A rail on a 900-word memo. Also: rail labels that don't match the h2 text, so the reader can't tell where they landed |
| **ASCII wireframe** | plainsight `pre.wire` — 11px, `background: var(--sunken)`, with `<span class="r">` for signal-red inside the block | Shows a UI's *information hierarchy* without implying visual design is settled. Colour used inside it only for the alarm state | A screen whose layout is the argument (DOSSIER's STATE-above-OBSERVATION stacking; COLLECTION's SUSPECT-above-DOWN sort order) | A wireframe of a screen nobody is arguing about. Using it as decoration for "here is a UI" rather than "here is why this arrangement and not the other one" |
| **Open items / footer honesty stamp** | plainsight `#open` section + `<footer>`; sherlock `<footer>` | Names what the document does **not** establish, and when the document expires. plainsight: "Assume dead until proven in a lab against a consenting, owned account." sherlock: "the exclusions list regenerates daily, so re-measure before relying on the numbers in any report" | Every document that asserts anything measured or time-sensitive. This is **not optional** | Omitting it. Or writing a soft disclaimer ("this may change over time") instead of a specific, actionable expiry condition |
| **Inline semantic chip** | sherlock `.chip` × 22, mono 11.5px, five classes; plainsight `.flag` × 3, two classes | Lets the document speak the subject's own vocabulary in running prose: "LinkedIn → `Available` `999`" | A subject with a **closed, named vocabulary** you'd otherwise be re-explaining every paragraph | Inventing chip classes for concepts the subject doesn't actually name. plainsight uses two, because the subject only had two states worth flagging |
| **Funnel / quantity bars** | sherlock `.funnel` (481 → 429 → 414) | Encodes a *reduction* where the shrinkage is the point | Sequential filtering with real numbers | A bar chart with three bars that a sentence would have handled |
| **Lineage chain** | plainsight `.chain` — mono, `line-height: 2`, box-drawing indent | Shows containment/derivation where the nesting is the claim | RUN → ITEM → CLAIM | Any hierarchy you could have expressed as a nested list |

### 2. The typographic system

**Three roles, never four.** Both documents assign exactly three faces to three jobs, and never let a face do a second job:

| Role | plainsight | sherlock | Used for |
|---|---|---|---|
| **Display / interface** | Archivo 500/600/700 | IBM Plex Sans 400–700 | h1–h4, every table (13px / 13.6px), stat and tally values, pull quotes, nav rail, footer |
| **Body** | Newsreader (serif) 17.5px / 1.6 | IBM Plex Serif 16.5px / 1.62 | Running prose only |
| **Machine** | JetBrains Mono | IBM Plex Mono | Code, kickers, chips, labels, wireframes, provenance |

**Why serif body.** The serif is doing register work, not decoration. These documents are long-form argument that expects to be *read*, not scanned — plainsight's h3s are full sentences, its paragraphs run 60–100 words. The serif signals "this is prose, slow down," while the sans in tables and the mono in chips signal "this is data, scan it." Because tables are set in the *sans* inside a *serif* document, a table announces itself as a different mode of reading before you parse a single cell. That contrast is the whole reason for the split, and it collapses if the body is also sans.

**The measure is tiered by type size, not global.** plainsight defines three:
- `--measure: 66ch` — `p, ul, ol.b`, `.call`, `.lede`, `footer`
- `44ch` — `.pull` (1.32rem)
- `22ch` — `.verdict-banner .big` (up to 2rem)

Rule: **the larger the type, the shorter the line.** sherlock uses one measure (`--maxw: 68ch`) because it has no display-scale prose.

**Measure binds prose, never evidence.** Tables live in `.tw` / `.tablewrap` (`overflow-x: auto`) and `<pre>` blocks are full column width with their own scroll. Prose is constrained for readability; evidence is allowed to be as wide as it actually is. And `.call p { max-width: none }` — inside a box, the box owns the measure.

**Scale.** Not a modular ratio — a *functional* one. plainsight: h1 `clamp(3rem, 11vw, 6.6rem)` at `line-height: .86, letter-spacing: -.045em` (poster); h2 2rem; h3 1.18rem; body 1.0; table 13px; chip/kicker 9.5–11.5px. sherlock's h1 tops out at 3rem — a manual doesn't need a poster. Both apply `text-wrap: balance` to **every element that can wrap at display size** (h1, h2, h3, `.big`, `.pull`) and `font-variant-numeric: tabular-nums` to **every place numbers are compared** (`.tally .n`, `.stat .v`, `td.num`).

### 3. Colour discipline — the rule that transfers

**plainsight uses one hue.** `--signal: #A82A1B` (light) / `#FF6E5B` (dark), plus `--signal-bg`. Every other token is achromatic warm grey: ground `#EDEBE7`, surface `#FAF9F7`, ink `#16171A`, rule `#D4D1CB`. And the document *states its own rule in its own prose*:

> "**One colour.** Red means exactly one thing: *the system does not vouch for this*. Everything else is achromatic, textural, or literal text."

That is not a stylistic preference — it is the PLAINSIGHT design's own doctrine (no computed confidence, provenance facts only) rendered as CSS. The document is styled *by the thing it argues for*.

**sherlock uses six hues, and is equally disciplined.** `--accent: #0F6E8C` plus five semantic pairs: `--claimed` green, `--available` grey, `--waf` amber, `--unknown` purple, `--illegal` red. Six hues instead of one — because the subject *is* a five-valued enum. Sherlock's `QueryStatus` has exactly five members, and the document's palette has exactly five status colours, mapped one-to-one, then reused inside `<pre>` blocks (`.ok`, `.bad`, `.warnc`) and callout variants (`.call.trap` = illegal, `.call.warn` = waf) so a red callout and a red chip mean the same thing.

**The transferable rule:**

> **Derive the palette from the subject's own vocabulary, then spend nothing beyond it.** Count the states the subject genuinely distinguishes and let that number set your hue count. If the subject distinguishes one thing worth flagging, you get one hue. If it names five states, you get five — and each must be bound to that state everywhere it appears, including inside code blocks and callout borders. Everything the subject does not name is achromatic. A hue with no referent in the subject matter is decoration, and decoration in an analytic document reads as a claim you did not make.

Corollary: **never encode a variable in hue that is already redundantly encoded.** plainsight says so explicitly — platform identity gets a two-character mono chip, not a colour, "because platform is type, type is the least interesting variable, and it's already redundantly encoded in handle format and URL."

### 4. The theme token contract, and why it is shaped that way

Both files use the identical three-block structure:

```css
:root { /* complete light palette, every token */ }

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { /* dark values, same token names */ }
}

:root[data-theme="dark"] { /* dark values again, verbatim */ }
```

The reasoning, which is why this must not be "simplified":

1. **Three states, not two.** An explicit light choice, an explicit dark choice, and the default (nothing stamped) where only `prefers-color-scheme` speaks.
2. **The bare `:root` is the base.** No colour has its *only* definition inside a conditional. If both conditionals fail to match, the page is still fully painted. `body` gets an explicit `background: var(--ground)` — a transparent body borrows the host's ground and the page breaks.
3. **The media block is guarded** by `:not([data-theme="light"])` so a reader who explicitly chose light is not overridden by their OS being dark.
4. **The attribute block is duplicated verbatim** so an explicit dark choice wins on a light system. CSS cannot OR a media query with an attribute selector; duplication is the correct cost.
5. **Dark is not an inversion.** `--signal` goes `#A82A1B → #FF6E5B` — deeper and more saturated on light, lighter and softer on dark, because contrast is measured against the ground, not against white. Backgrounds move from near-white tints (`--signal-bg: #F4E2DE`) to near-black shades (`#2E1512`). Every one of sherlock's five status pairs moves the same way. **Tokens hold roles, not colours** — that is what makes the whole palette swappable per document while the structure stays fixed.
6. `@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }` is present in both, unconditionally.

### 5. Editorial rules visible in the prose

1. **Lead with the decisive fact, in the first sentence of the unit.** "The decisive fact is in one line." / "That last number is the one to internalise." / "Zero of the six are adoptable."
2. **Headings carry verdicts, not topics.** Every plainsight h3 is a finding: "toutatis — the crown jewel is unproven, and the CLI never reaches it"; "SoIG — dead since mid-2022, and the give-away is a magic number"; "DiscordOSINT — a bibliography, not a component." Compare a topic heading ("toutatis overview") — it defers the answer for no reason.
3. **Cite the artifact, not the impression.** `core.py:125`, `search.py:44`, `search.py:164`, `api.py:76`, commit `9100f9d`, image `sherlock-local:0.16.1`. sherlock's masthead `.provenance` block states the method in mono before the argument starts: "every command below was executed and its output observed."
4. **Quantify or drop the claim.** 78.8%, 41 of 52, 0.24%, 121× overcount, 13.25s, ~40 lines, 6–8 engineer-weeks, 38,400 requests/day.
5. **Mark unverified in place, as prose, at the point of use.** "Verified directly in the cloned source." · "Presumed dead — endpoint TLS-dead since 2025-04." · "Assume dead until proven in a lab against a consenting, owned account." · "Treat anything above 100 as unmeasured against real hosts." Then collect the residue in a named section: "**Open items — carry these, don't resolve them from memory.**"
6. **Refuse to pad a weak finding.** DiscordOSINT gets four sentences and is dismissed. SoIG gets one paragraph ending "Cut it; it is strictly dominated by toutatis." Length is proportional to consequence, never to effort spent.
7. **Kill the reader's strongest objection before they raise it.** "The strongest possible finding here would have been 'SpiderFoot already *is* 80% of what you want.' That was tested against source and it's false."
8. **Record what was cut and what the cut bought.** "All of it was cut... Cutting it also saved 6–8 engineer-weeks." A design document that shows no deletions has not been designed.
9. **Bold marks the load-bearing clause; italic marks the twist.** 78 / 105 uses of `<b>` — always mid-sentence on the operative words, never on keywords for lookup. `<em>` on the qualifier: "the highest-value selector in the set — *if it still works*"; "*when were we blind?*"
10. **Voice follows intent.** sherlock (operating manual) is second-person imperative: "Pass `--print-all` on every single run." plainsight (design argument) is third-person declarative: "The system never asserts identity."
11. **Both footers state an expiry condition, not a disclaimer.** "Tool liveness reflects 2026-08-26 and rots quickly — re-probe before relying on any verdict here."

---

## PART 2 — THE STANDARD

**Proposed name: LEDE.** Four things every document must have, in order: **L**ede (the verdict, before the evidence) · **E**vidence (rendered in the shape it actually has) · **D**oubt (marked in place, collected at the end) · **E**xpiry (when this stops being true). Everything else is a decision, not a requirement.

### A. The seven principles

1. **The document's job is a sentence, and you write it before you write anything else.** Form: *"After reading this, the reader must be able to ___."* Decide / operate / trust / build. That verb selects every device below. If you can't write the sentence, you have notes, not a document.

2. **The verdict precedes the evidence, at every scale.** Document opens with the finding. Section heading states the finding. Paragraph's first sentence states the finding. A reader who stops after the banner should be wrong about nothing, only less equipped.

3. **The palette is derived from the subject and spends nothing beyond it.** Count the states the subject genuinely names. That is your hue count. Bind each hue to its state everywhere — chips, callout borders, code spans, table cells. Everything unnamed is achromatic. One hue is a complete palette when the subject has one thing worth flagging.

4. **Three type roles, never four.** Display/interface, body, machine. Body is serif when the document expects to be read rather than scanned; the sans-in-tables contrast is what makes evidence announce itself. Measure tiers with size (≈66–68ch prose, ≈44ch pull, ≈22ch banner headline). Prose is bound by measure; tables and code are not — they scroll inside their own container.

5. **Every device earns its place by content type, or it isn't used.** No pull quotes in a reference manual. No banner without a real verdict. No stat strip whose numbers aren't argued later. The count is diagnostic: 3 pull quotes and 5 callouts in 5,400 words; 0 pull quotes and 10 traps in 6,300 words. Devices are load-bearing or absent.

6. **Doubt is content with the same typographic weight as findings.** Mark it inline where the reader would otherwise over-trust ("*Presumed dead*", "*unmeasured*", "*Verified directly in source*"), and collect the irreducible residue into a named section the reader is told to carry, not resolve.

7. **Theme tokens hold roles, not colours** — bare `:root` complete, media-query dark guarded by `:not([data-theme="light"])`, `[data-theme="dark"]` duplicated verbatim, `body` background explicit, reduced-motion honoured. This block is fixed across every document. Only the values change.

### B. The decision procedure

**Step 0 — Does this earn a document?** Answer *no* and stop if any of these is true (see section D).

**Step 1 — Write the job sentence.** Then name the document's one finding in ≤22 characters of headline plus one qualifying clause. If it doesn't exist, the document is a reference, not a memo — skip the banner.

**Step 2 — Enumerate the subject's named states.** That count sets the palette. Zero named states → one hue for "do not trust this" plus neutrals. Five named states → five bound hues.

**Step 3 — Choose the entry apparatus by intent:**

| Intent | Job sentence verb | Entry apparatus | Devices that earn their place | Devices to refuse | Voice |
|---|---|---|---|---|---|
| **Decision memo** | *decide* | Poster h1 + **verdict banner** + tally strip. Sticky rail only if >8 sections | Verdict table (verdict in last column), 1–2 pull quotes, ≤1 callout per 3 sections, decision table with "cost of deferring" | Gotcha index, legend, funnel, long code | Third-person declarative |
| **Reference manual** | *operate* | Modest h1 + standfirst + **mono provenance block** (version, commit, method) + stat strip. Rail mandatory, grouped | Chips for the subject's vocabulary, trap/warn callouts (many), `pre.cmd` vs plain `pre` split, per-flag tables, **gotcha index as last section** | Verdict banner, pull quotes, poster h1 | Second-person imperative |
| **Audit** | *trust* | Verdict banner + tally strip + **explicit method line as `.lede` under the first h2** ("Static review only — no tool was executed…") | Per-subject verdict table, one h3 per subject whose heading *is* the verdict, quoted source lines with `file:line`, salvage/what-survives table | Wireframes, funnels, roadmaps | Third-person, past tense on method |
| **Design spec** | *build* | Thesis pull quote near the top; banner only if there's a build-vs-adopt verdict | ASCII wireframes (only where layout is the argument), object-model table, lineage chain, callouts for the one organizing idea and for each cut-and-why, phase table, "must be right on day one" ordered list | Stat strips of vanity metrics, chips for concepts the design doesn't name | Third-person declarative; imperative only in the doctrine section |

**Step 4 — Choose evidence devices by what the evidence *is*:** enumerable set → table · closed vocabulary → chips · sequential reduction → funnel · containment/derivation → chain · layout-as-argument → wireframe · a runnable thing → `pre.cmd` with accent border, its output in a plain `pre` · one turning idea or one trap → callout · a section compressible to one line → pull quote. Nothing else.

**Step 5 — Set the scale to the document's ambition.** A memo that must land in five seconds gets a 6.6rem h1. A manual someone opens forty times gets 3rem and spends the room on the rail.

**Step 6 — Write the footer before the body.** State the method and the expiry condition specifically ("re-probe before relying on any verdict here"; "re-measure before relying on these numbers"). Writing it first disciplines every claim above it, because you now know exactly what you're on the hook for.

**Step 7 — Audit the device counts.** More than one callout per ~1,000 words, or a pull quote in a reference doc, or a stat whose number never reappears in the argument: cut it. The devices' authority comes from their scarcity.

### C. What stays fixed vs. what must change per document

**Fixed (copy verbatim):** the three-block theme token contract · `body` explicit background · `* { box-sizing: border-box }` · reduced-motion block · `overflow-x: auto` wrapper on every table and `<pre>` · sticky rail collapsing to a horizontal chip row at ~880–900px with `.grp { display: none }` · `text-wrap: balance` on all display-size headings · `tabular-nums` wherever numbers are compared · `.call > :last-child { margin-bottom: 0 }` and `.call p { max-width: none }` · h2 with top rule + mono kicker · footer with top rule + method/expiry.

**Must change (deriving them is the design work):** the three font families · body size and measure · hue count and hue values · h1 scale · which devices exist at all · the `.grp` groupings, which are the argument's structure made visible.

### D. What this standard is NOT for

Use a plain terminal answer when:
- The answer is a fact, a number, a yes/no, or a fix the user will act on **alone, now, in the code in front of them**. There is no audience.
- The user asked a question, not for a document. Answer it. Offer the page in one line if it would help.
- The finding is one sentence. A one-sentence finding wrapped in a masthead, a rail, and a stat strip reads as padding, and it *devalues the devices* for the next document that needs them.
- It's in-progress reasoning, an option sketch, or a working note. These documents are for settled positions with evidence behind them; styling an unsettled position gives it unearned authority.

Use a plain `.md` file when:
- The artifact is **input to a tool or a repo**: CLAUDE.md, a README, a spec that must diff cleanly in git, anything another agent will parse.
- The content will be edited by several people over time. HTML is a publication, not a working copy. Both source documents here (`OSINT-COP-tool-review.md`, `PLAINSIGHT-design.md`) correctly stayed markdown; the HTML is the *rendering for a reader*, not the record.
- Fidelity of raw content matters more than legibility of argument — long code listings, data dumps, transcripts.

**The gate, in one line:** this standard applies when a document has *a reader who is not the author*, *a finding worth leading with*, and *enough consequence that being skimmed wrong would cost something*. Absent any one of the three, write less and style none of it.