# connectors/sherlock

DRAFT, written by an agent at Step 12 on 2026-10-28, UNRATIFIED. Nothing here
has run against a platform, an account or a person, and nothing here may.

## What it does

Sherlock 0.16.1, at sherlock-project commit `9100f9d`, takes one username
string and sends one unauthenticated HTTP request to each site in its manifest,
414 sites on a default run at the capability audit. Each site is scored by one
rule, its `errorType`, and the tool reports one of five statuses per site:
Claimed, Available, Unknown, Illegal or WAF. This connector runs it as the
local Docker image `sherlock-local:0.16.1` with `--csv --print-all --no-color
--timeout 20`, reads the CSV export and stdout, and emits PSE events: a
PROBE_EVENT RUN_START, one ITEM per probed site, a RUN_END, and one EXTRACT_EVENT
CLAIM of selector type `handle` per site whose row is a hit, whose value carries
that site's platform token (SH-R18).

Every fact below about the tool comes from the capability audit of that commit,
which sits outside this repository beside the Sherlock clone, and from its
`data.json`, which `site_facts.json` summarizes: per site, the `errorType`, the
`errorCode`, the verb, and the host `urlProbe` sends the username to where it
differs from the displayed one. `site_facts.json` also carries the 52-name
upstream false-positive exclusion list as the audit read it, and the three
sites whose `url` has no username slot (SH-R15). It holds no username:
`username_claimed` was never read.

| File | What it is |
|---|---|
| `manifest.yaml` | The declarations. It passes the manifest gate since the move SH-R5 names was built on 2026-10-28; the maintainer decides whether that move stands. |
| `adapter.py` | `parse`, `emit` and `invoke`, plus `read_cassette` and `cassette_values` for the harness. |
| `site_facts.json` | Per-site quality and exposure facts at the pinned commit. |
| `cassettes/` | Three runs, hand-built in Sherlock's recorded shape and never captured. |
| `fixtures.jsonl` | Six harness fixtures: three events fixtures and three refusals. |
| `tests/` | Rung 1 under pytest, replay only. |

`known_positive/` is the golden fixture: 12 sites, 3 hits, and one row of every
shape the parser has to classify without a hit, including an Illegal row with
empty cells, a WAF row, an Unknown row with the `?` status, a Claimed row at HTTP
429, an Available row at HTTP 429, an Available row at HTTP 999, an Available
row on the site's own `errorCode`, and a Claimed row on Discord, whose `url_user`
is its bare host. `known_negative/` is the canary's zero-hit shape, with a
Discord row as well. `argparse_error/` is an exit 2 with no CSV. The CSVs are CRLF-terminated
and an Unknown line in stdout ends in a space, because Sherlock writes both, so
`git diff --check` reports those bytes and the parser is tested against them.

## What it cannot say

- **That an account belongs to anyone.** A hit means one site's rule scored one
  response as Claimed. It is the same string, never the same person, and the
  adapter's `inference_hint` only proposes `same_entity` by identical string.
- **That an account does not exist.** `zero_means` is `inconclusive` (SH-R1).
  Available is reported for a rate-limited or blocked probe as readily as for a
  missing account, 131 removed sites and Facebook are never probed, and three
  sites' own comments say results depend on the egress geography.
- **Anything about WAF or Unknown rows.** Neither status is an answer, so each
  is an `error` item with no `negative_class`. 303 of 481 sites are probed with
  HEAD and carry no body, so a WAF block there cannot be fingerprinted at all and
  reaches the CSV as Available or Claimed. A run whose every row is Unknown is
  adapter state `error`, an egress or connection failure, and not `blocked`.
- **The site's own answer, on a site with a `probe_host`.** On the 21 sites whose
  `urlProbe` names another host, a hit is that third party's answer, not the
  site's: Instagram's is `imginn.com`'s and Twitter's is a public Nitter
  instance's. The adapter still emits the claim at the displayed site, and
  `probe_host` on the parsed item says whose answer it was. Whether such a hit
  should be held as `ambiguous` is the operator's decision.
- **That a profile exists, on a site whose url has no username slot.** A Claimed
  row on Discord, Diskusjon.no or Kvinneguiden means the name is taken in a
  registration check (A1.5), so it is `ambiguous` and emits no claim (SH-R15).
- **The same site set twice.** The exclusion list is fetched live and changes
  daily, so two runs on different days can probe different sets. The parser
  records the sites that ran, and a Claimed row from a site on the audit's
  exclusion list is held as ambiguous (SH-R7).
- **Latency.** `response_time_s` includes queue wait in Sherlock's 20-worker
  pool, so the adapter carries it on the parsed item and ranks nothing by it.

## How Sherlock goes wrong, and what the adapter does about it

| Mode | Evidence in the audit | What the adapter does |
|---|---|---|
| status_code sites score any 2xx as Claimed | 327 sites, 6 with an `errorCode` | A soft-404 hit stays a hit; the `fp_mode` says so and the per-endpoint known-negative canary is what catches it |
| A HEAD probe cannot see a WAF | 303 sites; a 403 challenge scored Available in a controlled test | Available at 403, 503, 999 or any status outside 200, 404, 410, 3xx and the site's own `errorCode` is `ambiguous`, never a negative |
| A rate-limit page scores Claimed on a message site | Steam Community (User), Claimed at HTTP 429 | Claimed at 429 is `throttled` and emits no claim |
| A rate limit scores Available | HackerNews at 429, LinkedIn at 999 | `throttled` and `ambiguous`, never a negative |
| A stable false positive | Trakt, Claimed for a random string across runs, 1 of 414 | A hit with a claim; at onboarding Trakt fails its known negative and renders SUSPECT |
| The exclusions fetch fails silently | 41 of the 52 excluded sites claim a random 18-character string | Claimed on a site from the audit's list is `ambiguous` and `exclusions_applied` is false |
| The username goes to a third party | 21 cross-host probes, among them Instagram to `imginn.com` and Twitter to `nitter.privacydev.net` | `probe_host` on the parsed item, and the manifest's `exposure.detail`, `fp_mode` and `observation_statement` |
| A raw errorMsg substring misses a reformatted not-found text | The GitHub API's `message` field | Nothing the adapter can see: the row is Claimed; the `fp_mode` says so and the known-negative canary is what catches it |
| The url carries no username slot | Discord, Diskusjon.no, Kvinneguiden; Discord is in every default run | The url_user containment check is skipped for those sites, and a Claimed row there is `ambiguous` |

## What the operator does at onboarding

1. Decide whether the SH-R5 move built on 2026-10-28 stands: the manifest
   schema's `platform_from_item` (MF-R17), amendment 9.14 of
   `docs/PLAINSIGHT-design.md`, and the token rule SH-R18. Reverting it returns
   the manifest to a refusal under `MANIFEST_SELECTOR_PLATFORM`, and with it
   `make validate-manifest`, `make validate-connector`, the pre-commit hook and
   the kernel gate.
2. Build `sherlock-local:0.16.1` from the clone at `9100f9d`, outside this tree.
3. Ratify what SS-14 item 6 lists and a re-measured dispatch allowlist (DA-R1),
   so `runner.subject_guard.evaluate()` can permit. This connector adds no
   allowlist entry: `--dispatch-paths` finds its three sites, the type check,
   `build_argv` and `subprocess.run`, all behind the permits check in `invoke`.
4. Resolve `<institutional_handle>` outside the tree to an institutional account,
   an upstream project's own handle and never a person's. The known-negative
   input is a fresh random string made at run time.
5. Run both canaries live from ISOLATED, which is design section 6.5's Prove It.
   Expect Trakt to fail the known negative. That endpoint renders SUSPECT, which
   is the canary working.
6. Replace `cassettes/known_positive/` with the capture, after replacing the
   institutional handle with `<institutional_handle>` in every cell. The harness
   refuses a cassette cell that is not a placeholder, and git history is the one
   store a crypto-shred cannot reach.

## Readings

Each is an agent reading awaiting the operator.

- **SH-R1, zero_means.** `inconclusive`. Available is confidently wrong under
  rate limits and blocks (LinkedIn at 999, HackerNews at 429), every HEAD-probed
  site turns a 403 into Available, 24 of 414 sites gave no verdict on the
  audit's real sweep, and the unprobed sites are many. `absence_evidence` would
  read a negative the tool did not observe. `never_conclusive` would discard the
  1-in-414 false-hit rate the audit measured on a nonexistent string, which is
  what makes a zero-hit run informative at all.
- **SH-R2, exposure.** `logged`. No account is used, and every probed site logs
  the request against the egress identity with a fixed Firefox 129 user agent;
  21 sites send the username to another host. `none` would describe the absence
  of an account rather than the absence of a record. The alternative is `none`,
  on the reading that the field is about an account the platform can attribute.
- **SH-R3, auth.** No block. The schema does not require one and Sherlock never
  authenticates, so `interaction_class` is `passive_unauthenticated`.
- **SH-R4, bystanders.** `named_selector_only`. SS-10's populations are reached
  beyond the named selector: a channel's members, an account's followers, an
  organization's staff. Sherlock's argv carries one string and its output names
  only that string, per site. The holders of the same string on other sites are
  whoever registered it, which is the false-positive mode the registry records on
  `username_string`. The alternative is that those holders are a population
  reached by construction; no class in the schema's closed set fits them, so
  that reading refuses this connector until the operator adds a class, which is
  Class F.
- **SH-R5, the handle's platform. The first move below was built on
  2026-10-28 on the maintainer's instruction, and he decides whether it
  stands.** The paragraph that follows is the reading as it stood before the
  build: the manifest refused on it until the schema gained
  `platform_from_item` (MF-R17 in `tools/validate_manifest.py`), the handle emit
  declared it, and the adapter began writing each claim's platform by SH-R18.
  A handle's
  registry form binds one platform, and `tools/validate_manifest.py` requires a
  `platform` beside every handle emit. Sherlock's claims land on whichever site
  answered, a different platform per item, and the manifest schema takes one
  platform per emit. A token such as `sherlock_site` would pass and would name a
  platform that does not exist, which the handle matcher would later read as a
  character set. The legal moves, each the operator's: a schema and validator
  change that lets an emit say its platform is the one the ITEM locator names,
  which is a rank-3 change; or a fixed `--site` list with one handle emit per
  site and a real platform token each, which changes the site set, un-excludes
  any excluded site it names, and makes the canary set the operator's choice; or
  a ratified token that the matcher is told to resolve per item.
- **SH-R6, outcomes.** The table in `adapter.py`'s docstring. Only a hit becomes
  a claim. `negative_state` is an EXTRACT_EVENT field, so a non-claimed row emits
  no claim and carries its class as the ITEM's `negative_class`. An
  `attempted_and_absent` claim would fire `ABSENCE_CLAIMED_WITHOUT_CANARY` until a
  canary proves the field. WAF and Unknown rows are outcome `error` and carry no
  class, because `spec/layer-model.yaml` draws `negative_class` from the
  manifest's `distinguishable_negatives` only when the outcome is miss, and a
  request that returned no answer is not a negative. The first draft carried
  both as negatives, as the brief asked; the review of 2026-10-28 removed them,
  and the WAF-versus-Unknown distinction stays on the parsed item's `exists` and
  `unknown_context`. Carrying it on the wire is a layer-model change. Available
  counts as a negative only at 200, 404, 410, a 3xx or the site's own
  `errorCode`, the rule `docs/OSINT-COP-tool-review.md` states for mirror and
  rate-limit probes, widened by the codes a status_code or response_url site
  uses for not-found.
- **SH-R7, the exclusion list.** A Claimed row from a site on the audit's
  52-name list is held as `ambiguous`, because its presence means the exclusions
  fetch failed and 41 of those 52 claim a random string. The list dates from the
  audit and the upstream list changes daily, so a site removed upstream since
  then is held too, and a site added since then is not.
- **SH-R8, what invoke can check.** A Decision carries the connector and the
  selector type and never the value, by design, so `invoke` refuses a permit for
  another connector or type and cannot compare the input value with the selector
  the gate evaluated. The runner builds the Request and the inputs from one case
  record and owns their equality.
- **SH-R9, facts the wire cannot carry.** The ITEM payload admits no field for a
  site's `errorType`, verb or probe host. They live on the parsed item and in
  `site_facts.json`, keyed by the site the ITEM locator names, and the case's
  pinned connector version recovers them. Carrying them on the wire is a
  layer-model change.
- **SH-R10, the dispatch scan and the type check.** `--dispatch-paths` reads any
  reference to `runner.subject_guard.Decision` outside a permitted region as a
  forgery, including an `isinstance` check. `invoke` therefore checks for a
  missing decision, then `permits`, then the type, and an object that says
  `permits` True and is not the gate's Decision is refused at the third check.
  The scan was not edited.
- **SH-R11, refusal codes.** A missing or null input refuses under
  `PAYLOAD_FIELD_MISSING`, the nearest declared code (MF-R10). A capture whose
  username differs from the input refuses under `SUBJECT_NOT_AUTHORIZED`, because
  its claims would be about a string the gate never evaluated.
- **SH-R12, two subject classes.** The manifest declares `institutional`, which
  is what the live canaries and the golden capture will be taken against. The
  fixtures declare `synthetic`, because their cassettes were built by hand and
  captured against nobody.
- **SH-R13, the command template.** `--json` pins the manifest to `9100f9d`
  through raw.githubusercontent.com, where a default run fetches the moving
  master. `-v ./out:/sherlock` assumes a Docker that accepts a relative bind
  path, run from a fresh scratch directory, and `--` stops a username from being
  read as a flag. The template has never been executed.
- **SH-R14, the version.** `version` is `0.16.1`, the tool's own, as the design's
  example manifest pins its tool's version. An adapter change at the same tool
  version needs its own number, which is the operator's convention to set.
- **SH-R15, sites whose url has no username slot.** At `9100f9d` three sites'
  `url` carries no `{}`: Discord, Diskusjon.no and Kvinneguiden. Sherlock writes
  that bare url as `url_user` on every non-Illegal row, so the parser's check
  that `url_user` contains the username would refuse every default run, since
  Discord is in every one. `site_facts.json` lists the three under
  `url_without_username_slot`, the parser skips the containment check for them,
  and a Claimed row on one of them is `ambiguous` with no claim, because Discord's
  probe asks whether the name can be registered and not whether a profile
  exists. The alternative is a hit with a claim and the caveat in `fp_mode`.
- **SH-R16, invoke() is an argv builder under SS-19.** SS-19 refuses, at argv
  construction, a value that does not match its registered matcher.
  `invoke()` builds argv from the manifest's command template, and
  `shape.username.v1` in `ontology/selectors.yaml` carries no grammar, so no
  matcher can be run. `check_argv_value` is the interim shape gate: it refuses a
  placeholder, a leading hyphen, a brace, whitespace or a control character, a
  value over 256 characters, a path separator, a colon, and a bare `.` or `..`,
  the last three because Sherlock names its CSV export after the username and
  `invoke()` reads that file back. Supplying the matcher's grammar is the
  operator's decision, and `runner/subject_guard.py` SG-R14 names this site.
- **SH-R17, the scratch directory.** `invoke()` given no `workdir` makes a
  scratch directory and removes it before it returns, on every path, because
  the CSV inside it is stratum-0 raw capture (RT-1) carrying the selector in its
  name and its rows. The capture leaves `invoke()` only as returned text, which
  the runner writes inside the case boundary. A directory the caller passes is
  the caller's to remove. On a Linux host, a container that writes as root can
  leave files `shutil.rmtree` cannot delete, and the removal ignores that error;
  the Docker user is the operator's to set at onboarding.
- **SH-R18, the platform token a handle claim carries.** Since 2026-10-28 the
  manifest's handle emit declares `platform_from_item` (MF-R17), so each claim
  names the platform of the site its ITEM locator names, and `emit()` writes the
  claim value as that platform token, a slash, and the CSV's username cell. The
  token is derived from the site name and nothing else, by `platform_token()` in
  `adapter.py`: the name lower-cased, each run of characters outside a to z and 0
  to 9 replaced by one underscore, and leading and trailing underscores removed,
  so `Diskusjon.no` gives `diskusjon_no` and `GitHub` gives `github`. A result
  that does not match the manifest schema's platform pattern `^[a-z][a-z0-9_]*$`
  is no token. At `9100f9d` that is four sites, 1337x, 2Dimensions, 7Cups and
  9GAG, each a name beginning with a digit. A name carrying a parenthesised
  qualifier is also no token, which at `9100f9d` is five sites on three
  platforms: Genius (Artists), Genius (Users), HackenProof (Hackers), Steam
  Community (Group) and Steam Community (User). The qualifier names an endpoint
  of a platform rather than the platform, so the plain rule would give Steam
  and Genius two tokens each and would record a hit on a group or artist
  directory as a person's handle on a platform named after that directory; the
  registry files a group under `channel`, not `handle`. A Claimed 2xx row on
  any of the nine sites is `ambiguous` with no claim, because a token not taken
  from the platform's name would be a platform that does not exist, which is
  laundering. No two of the 481 sites give the same token. The adapter tests
  hold these facts against `site_facts.json`, and `emit()` refuses a hit on a
  site with no token rather than inventing one. The qualifier rule was added on
  2026-10-28 by the review of the build, as amendment 9.15 of
  `docs/PLAINSIGHT-design.md` records. The token is the site's name in
  Sherlock's manifest and not a name a registry of platforms has confirmed, so
  two sources that spell one platform differently produce two tokens, and four
  pairs of unqualified names at `9100f9d` give tokens where one extends the
  other (chaos and chaos_social, cracked and cracked_forum, discord and
  discord_bio, eintracht and eintracht_frankfurt_forum), which no rule here
  judges. Two alternatives are the maintainer's to choose: a fixed prefix such
  as `site_` for the four digit names, and a written mapping from each
  qualified endpoint to its platform's single token, with the group and artist
  endpoints held ambiguous.
  `tools/validate_connector_conformance.py` holds the part of the value after
  the slash to the placeholder rule, and checks nothing about the token beyond
  its pattern.
