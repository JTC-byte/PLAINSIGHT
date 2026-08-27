# OSINT COP — Tool Review, System Architecture, and Doctrine Backlog

**Date:** 2026-08-26 · **Scope:** six person-centric OSINT tools evaluated as candidate components for a consolidating "OSINT COP" · **Method:** static review only — source read from local clones, licence files read on disk, upstream trackers and package indices queried. No tool was executed against any platform, account, or person. No credential or session material was supplied, requested, or fabricated.

**Headline: zero of the six are adoptable as dependencies.** Four are functionally dead. One is not software. One works only as a reference design. That is not a reason to abandon the program — it is the strongest possible argument for the build-vs-adopt decision in Part 2, and it tells you exactly where to spend the first sprint.

---

# PART 1 — THE REVIEW

## Verdict table

| Tool | What it is | Licence (SPDX) | Auth required | Works today? | Verdict |
|---|---|---|---|---|---|
| **toutatis** `megadose/toutatis` | 171-line IG CLI: username → numeric PK → profile record → account-recovery endpoint for obfuscated email/phone hints | **GPL-3.0-only** (unfilled copyright notice — chain-of-title defect) | **Instagram `sessionid` cookie from a real logged-in account** (burnable, phone-backed) | **CLI: NO.** Crashes at `core.py:125` on the removed `total_igtv_videos` field before printing any contact field. Crown-jewel path: **NOT VERIFIED, trending dead** | **Reject as dependency. Rebuild two primitives clean-room.** |
| **DiscordOSINT** `husseinmuhaisen/DiscordOSINT` | A README. 52 unique third-party links, Discord in-app search operators, Google dorks | MIT — **covers the prose only**, confers nothing on what it links | None (the document); the two useful techniques need a Discord account in the target guild | N/A — **not software.** 8 of 52 links dead (~15%), including both links that teach how to obtain a user ID | **Not a tool. Harvest once as a bibliography, cite in an appendix, do not list as a component.** |
| **informer** `paulpierre/informer` | 2019 Telethon userbot: joins channels from CSV, regex-matches messages, alerts to a private channel + MySQL | MIT (clean) | **Telegram api_id/api_hash + a full user session bound to a real phone number** | **NO — four independently verified blockers**, incl. compose file that fails `docker compose config`, and an `AttributeError` on the pinned Telethon before a single DB row is written | **Reject. Read the schema, lift the FloodWait pacing, write ~300 lines of Telethon yourself.** |
| **snapmap** `nemec/snapchat-map-scraper` | 406-line CLI: POSTs lat/lon to Snapchat's undocumented `ms.sc-jpl.com/web/getPlaylist`, downloads public Snaps into SQLite | MIT (clean) | **NONE** — genuinely zero credentials, zero ban surface | **Presumed dead.** Endpoint TLS-dead since at least **2025-04-13** (archiver maintainer's own `openssl s_client` reproduction); the better sibling implementation was archived 2025-10-31 rather than fixed | **Probe once (30 seconds). If it answers, rebuild ~80 lines as a geo adapter. If not, the capability is gone from the web endpoint.** |
| **CrossLinked** `m8sec/CrossLinked` | company name → LinkedIn employee roster, by scraping Google/Bing SERPs; synthesizes email/username candidates from a format string | **GPL-3.0** (ambiguous -only/-or-later; strong copyleft either way) | **NONE** — never touches linkedin.com | **NO.** Seven independent reporters over 16 months: Google 429, Bing CAPTCHA. `&num=100` dead since Sept 2025 and untouched | **Disqualified. But the *capability* is the only org→person fan-out in the set — rebuild it against a paid SERP API.** |
| **SoIG** `yezz123/SoIG` | 283-line IG profile scraper; re-badged derivative of the now-archived `sc1341/InstagramOSINT` | MIT — **but upstream attribution stripped**, and the repo was relicensed Apache-2.0→MIT in 2020 | NONE | **NO.** Parses `window._sharedData`, which Instagram removed in **mid-2022**. Fails in the constructor. Three open issues report the exact line; most recent "same" comment 2026-05-13 | **Disqualified outright. Nothing to salvage. Cut it.** |

---

## Per-tool, blunt

### toutatis — the crown jewel is unproven and the CLI never reaches it

**It is GPL-3.0-only, it requires a live Instagram `sessionid` from a real phone-backed account, and its CLI provably crashes before printing a single item of OSINT value.** `main()` prints IGTV at `core.py:125` via a bare subscript `infos["total_igtv_videos"]`. Instagram removed the field. That line executes *before* public email (133), *before* public phone (145), and *before* `advanced_lookup()` is even called (147). Ordering verified in source; corroborated by real tracebacks in issues #389 (2026-05-02) and #202.

The tool has **two auth planes with different consumables**, and the README says so nowhere. The profile fetch carries your `sessionid` — structured `<accountPK>%3A<token>%3A<n>`, so the collecting account's own numeric PK travels in cleartext on every request, and issue #486 (2026-08-10) documents a browser-valid session getting `checkpoint_required`. The obfuscated-hint call (`advanced_lookup`, defined at `core.py:66`, POST at 74–88) sends **no cookies at all** — it is an anonymous, IP-attributed abuse of the password-recovery endpoint via the legacy `signed_body=SIGNATURE.` unsigned-request bypass. Those are different legal animals and must never share a permission tier.

The client fingerprint guarantees flagging: `getUserId` sends the literal string `"iphone_ua"` as its User-Agent, `getInfo` sends `Instagram 64.0.0.14.96`, `advanced_lookup` sends `Instagram 101.0.0.15.120`. Three requests, three mutually inconsistent client identities, one IP, no rotation, no proxy support, **no timeouts on any of the three requests** (grep-verified).

The error model lies to you. `core.py:28-29` converts any non-JSON reply in `getUserId` into the literal string `"Rate limit"` — so an HTML login wall, a challenge page, an IP block and a genuine 429 collapse into one value. (`getInfo` at `core.py:50-51` *does* have a real `status_code == 429` branch, which makes the point sharper: the tracker's flood of "rate limit" reports is mostly misdiagnosed auth failure.)

Maintenance: last commit **2024-12-05**, and it is a merge of someone else's PR. 285 open issues + 52 open PRs. Nine open PRs are byte-trivial duplicates of the same one-line IGTV fix; none merged in a year. PR #180 — a competent library refactor — has sat with zero reviews since 2025-09-20. The maintainer has pushed nothing to *any* of his 20 repos in ~20 months. The tracker is a doxxing request board, not a support channel; associating a program with it carries real reputational baggage.

**The one thing that must survive into your planning:** issue #148 (2025-07-30, "Instagram API Changed", zero maintainer response) states plainly *"This output was received using the id of the user as getUserId does not work anymore."* That is the specific GET this review otherwise recommends rebuilding as your cheapest primitive. Treat it as at-risk. The same issue is also the **only** non-placeholder evidence anywhere in the tracker of the crown-jewel path returning live data — a populated `obfuscated_phone` alongside `has_valid_phone`, `can_email_reset`, `can_sms_reset`. Every other "working output" pasted in the tracker (#390, #429, #370, #434, #481) is a verbatim copy of the README placeholder `me********s@examplemail.com`.

Also note: `pip install toutatis` gives you **1.31 (2024-06-26)**, which is materially worse than git master — no `raise_for_status()`, no 429 handling, a bare `.json()["user"]` subscript. That PyPI artifact is the origin of the `KeyError: 'user'` in issue #486. And PyPI's `info.license` and `info.license_expression` are both `null`, so automated SBOM scanners will report UNKNOWN.

**Do:** reimplement `username → numeric PK` and the obfuscated-hint **verifier** clean-room. At the library layer `getInfo()` returns the entire raw Instagram `user` object — which carries `fbid_v2` (a Facebook cross-platform join key) and `encrypted_user_ids`, neither of which the CLI prints. That's the correlation value.

### DiscordOSINT — not software, and it rots exactly where it matters

**It is a two-file repository: `README.md` and `LICENSE`. Across all 54 commits, no source file has ever existed at any commit** (`git log --all --name-only` returns exactly two paths). There is no runtime, no I/O, no exit code, no structured output. It consumes no selector and emits no selector, so it cannot be a node in a correlation graph — which is the entire point of the system you are building.

It is 2 years stale (pushed 2024-08-08), single maintainer (`/contributors` returns one login; the two noreply addresses share GitHub user ID 59100756 — one account renamed). 8 of 52 unique links are dead (~15%), and the dead ones are the wrong ones: `hugo.moe` — the README's **#1 listed tool**, the Discord creation-date decoder — is NXDOMAIN with no NS delegation at all, and **both** `techswift.org` links are HTTP **410 Gone** (the whole domain is tombstoned). Those two are the entirety of the section explaining how to obtain a user ID — the highest-value selector Discord offers and the only one usable offline. So the document's decoder link is gone and its ID-acquisition instructions are gone.

Be precise about what survives: the snowflake formula `(id >> 22) + 1420070400000` is **not in this README**. `grep -inE 'snowflake|1420070400000|epoch|>> ?22'` returns zero matches across all 104 lines. The genuinely durable first-party content is one block — lines 84–90, the in-app search operators `from: mentions: has: before: during: after: in:`. Lift those into operator documentation. The `Name#0773` discriminator dorks are obsolete since Discord's 2023 handle migration and are still taught as primary.

The MIT badge blesses the prose only. Downstream: `discordlookup` is **AGPL-3.0 and archived**; `WhatsMyName`, `DevSpen/scam-links` and `undiscord` are NOASSERTION; `Discord-AntiScam/scam-links`, `Gobutsu/Disserv` and `nashwik/All-Discord-Exploits` have **no licence file at all** (all rights reserved). Exploits items 4 and 6 are the same repo (`aletheialab/ZeroDiscord`) listed twice under two stale owner names — and it is MIT and **archived**.

The Exploits/Pentesting section links a group-flood spammer and `undiscord` (mass message deletion). That is abuse and counter-forensic capability. A collection platform should be structurally incapable of reaching it.

**Do:** implement snowflake→timestamp natively (eight lines, offline, zero ToS exposure). Integrate `dfir-unfurl` properly (`pip install dfir-unfurl`, v20260405, Apache-2.0, actively developed, importable API + JSON graph output — the single cleanest integration target the README pointed at). Note the canonical repo is now **`RyanDFIR/unfurl`**, not `obsidianforensics/unfurl`; any citation you carry forward should use the new path.

### informer — a Telegram userbot that needs a burnable phone-backed account, and does not run

**It requires a real Telegram user session — api_id/api_hash plus a phone number and an SMS login code — and the README says the choice of a userbot over the Bot API is deliberate: "Uses REAL accounts avoiding bot detection."** The `.session` file *is* the account; anyone holding it can send as that identity. The author documents burner-number tradecraft as the mitigation and notes Twilio-class VoIP numbers are blocked from receiving Telegram's shortcode SMS, so number acquisition is a manual recurring cost.

Four blockers, each independently verified:

1. **`docker compose -f docker-compose.yml config` fails.** Reproduced: `service "app_informer" refers to undefined volume app/: invalid compose project`. `./start.sh` — the README's primary deployment step — cannot start. (This defect dates to 2021-08-23 and Compose v1 tolerated it; v2+ rejects it.)
2. **The image cannot build.** `FROM python:3.7-alpine`, but `gspread 6.1.4`, `python-dotenv 1.0.1` and `mysql-connector-python 8.4.0` all declare `requires_python >=3.8` (checked against PyPI). Three hard `==` pins are unsatisfiable.
3. **The notification path `AttributeError`s on the pinned Telethon.** `informer.py:219` calls `GetFullUserRequest` and `:224-230` read `user.user.username`. In Telethon 1.23.0 that attribute existed. In 1.36.0 — the version the repo pins **now** — `GetFullUserRequest` returns `telethon/tl/types/users.py::UserFull(full_user, chats, users)`. There is no `.user`. Verified by reading the generated types out of both sdists. Every keyword hit hits this and raises, so **no `chat_user` row, no `message` row, no `notification` row is ever written** — the database, the tool's only structured output, stays empty.
4. **Seeding never creates any monitors.** `build_database.py:197-198` loops `if account_index in accounts:` where `account_index` is the integer `0` and `accounts` is a list of ORM objects with no `__eq__`. Always `False`. Zero `Monitor` rows → `informer.py:286` returns empty → `self.channel_list` is empty → nothing is ever joined or matched.

Blocker 3 was **introduced by the only maintenance the repo has seen since 2021** — an October 2025 AI-generated pass that bumped Telethon four minor versions without reviewing a single call site, claimed to close issues #10/#13/#16, and left all three open. Master has **no commits at all** between 2023-03-06 and 2025-10-20.

Blocker 4 has been reported in the wild: issue #14 contains a user's own container log, `INFO:root:init_monitor_channels: Monitoring channels: []`, with the keyword loader working correctly two lines above. So people *have* run this; it has simply never worked out of the box.

Correction worth carrying: there **is** a designed push output path. On every keyword match, `informer.py:535` sends a formatted alert into an operator-controlled Telegram channel, and that fires 29 lines *before* the `AttributeError` at 564. The valid criticism is that the payload is an unschematised human-readable f-string, not that no delivery path exists.

Two schema defects to inherit as lessons, not as code: `message_tcreate = datetime.now()` stores the **ingest** time, never the Telegram message timestamp, and Telegram's message ID is never persisted — so the corpus cannot be deduplicated or linked to source. And `chat_user_id`/`channel_id` are SQLAlchemy `Integer` → signed MySQL INT (max 2,147,483,647), while Telegram moved to 64-bit IDs in v1.24. Even a repaired write path throws out-of-range on modern accounts.

**Do:** read `app/models.py` as a schema sketch and `init_monitor_channels`' join-with-jitter loop as a reference for join pacing. Then write it yourself: `client.start`, `iter_dialogs`, `JoinChannelRequest` with real backoff, an `events.NewMessage` handler, an NDJSON writer. ~300 lines. MIT makes that lift clean. Note also that informer only persists on a regex hit — it is a tripwire, not a corpus collector, and its recall is whatever your regex list is.

### snapmap — the only zero-auth, only geospatial tool in the set, and its endpoint has been dropping connections since April 2025

**No account, no phone number, no session, no ban surface — verified by grep, both requests set exactly one header (`Content-Type: application/json`) and media is fetched by bare `requests.get` with no headers at all.** That property is genuinely rare and is the thing worth preserving. All attribution collapses onto the source IP and a default `python-requests/2.25.1` User-Agent, which is a bright, trivially-classifiable beacon.

Liveness: the maintainer's last positive test is **2024-05-25** (not 2025 — off by a year, and it therefore *predates* the July 2024 certificate rotation rather than surviving it). The better-engineered sibling `king-millez/snapmap-archiver` carries issue #25 in which its own maintainer reproduced the failure on **2025-04-13** with both `curl` and `openssl s_client`: `error:0A000126:SSL routines::unexpected eof while reading`, `no peer certificate available`, concluding *"the endpoint is dropping the connection without sending the close_notify alert."* Issue #26 (2025-10-19) was closed as a duplicate on 2025-10-30 with *"I don't have time to debug the Snap mobile app to find an updated API endpoint at the moment."* That repo was archived the next day. **The most capable independent implementation of this exact capability was abandoned because the shared endpoint stopped answering.**

Correct the operator framing: **this is geo-QUERIED, not geo-TAGGED.** The API returns no per-snap coordinates — only a place-name string. `sql/media.sql` has no lat/lon column; `media.location_id` is an FK to *your own query point*. Verified against three independent implementations. Every Snap is locatable to nothing better than your query disc.

And the uncertainty is worse than 500 m whenever `--randomize` is used. `scrape_location` randomizes lat/lon at line 139 with radius **1609.0 m** *after* the row is read, and the randomized point is **never persisted** — so the recorded provenance is affirmatively wrong by up to 1609 m, giving ~2109 m real uncertainty against a database that claims the stored coordinate. Compounding it, `randomize_location` divides by `cos(longitude)` instead of `cos(latitude)` **and** applies the east-west correction to the latitude component, so the displacement distribution is distorted unpredictably and the 1609 m figure itself is not trustworthy.

The defect that matters most for an evidentiary system is not a crash — it's silent archive corruption. `download_media` assigns `media_file = media/<id>.mp4` *before* calling `download_file`, and returns it unconditionally. `download_file`'s retry guard is dead (`if tries == 0: raise` is checked while `tries` is still 3/2/1 — decremented after), so three failed attempts return normally and **a path for a file that was never written is INSERTed into the media table as if archived.** `export()` then dies with `FileNotFoundError`. The DB asserts custody of media that does not exist on disk.

Also: `review` issues `FROM media m JOIN locations l WHERE ...` with no `ON` clause — a cartesian product. In the labelled variant the label predicate filters the *locations* side, so `review <label>` silently returns media from **all** locations. PR #3 has been open and unmerged since 2022-06-14.

Two unmerged CVE-fix PRs sit there: #8 (requests 2.25.1 → 2.31.0, CVE-2023-32681 Proxy-Authorization leak on cross-host redirect — and this tool *follows redirects to CDN hosts*) and #9 (certifi → 2023.7.22, against an endpoint whose certificate is known to have been rotated).

**Do this first, it costs 30 seconds and de-risks the whole geo question:**

```bash
curl -sS -m 10 -w '\nHTTP %{http_code} in %{time_total}s\n' \
  -X POST https://ms.sc-jpl.com/web/getLatestTileSet \
  -H 'Content-Type: application/json' -d '{}'
```

That is a tileset-metadata call with an empty body — no person selector, no coordinate, no target. If it answers, reimplement the two calls as a geo adapter emitting NDJSON with a mandatory `geo_uncertainty_m` derived from the **true** query point. If it does not, the capability must be re-derived from the mobile app, which is a separately-scoped effort.

**One caveat on reference implementations:** `snapmap-archiver` is **GPL-3.0-or-later** and has **no tests** (recursive find for any test file returns zero; `.github/` contains only an image; `[tool.poetry.dev-dependencies]` is empty). Do not clean-room from its source. Work from the wire schema.

One concrete lead if you scope a better geo adapter: archiver's `SNAP_PATTERN` parses share URLs of the form `https://map.snapchat.com/ttp/snap/W7_<56 chars>/@<lat>,<lon>,<zoom>z`. **Snaps are geo-tagged platform-side; `getPlaylist` simply does not surface it.** Whether that coordinate is a snap fix or the map-view centre at share time is **NOT VERIFIED**.

### CrossLinked — the only org→person tool in the set, and both of its engines are blocked

**It is credential-free in a way that genuinely matters — it never contacts linkedin.com, only Google and Bing SERPs — and it is dead against both.** Verified by grep: the entire package contains no credential store, no config read, no env var, no code path that could accept one. The only "auth"-shaped code is a hardcoded `cookies={'CONSENT':'YES'}` dismissing Google's EU interstitial.

Seven independent reporters on issue #44 across 16 months, zero maintainer responses (every comment `author_association: NONE`). The concrete failure, with screenshot, 2025-09-09: *"Google return specifically 429 too many requests and Bing fails because of captcha."* On 2026-07-02 a third party declared it "fully dead," forked it, added Yahoo, and reported that **even after modernization Google and Bing still do not work.**

Independent of bot detection, there is a structural break: the Google URL template hardcodes `&num=100` at `search.py:43`. Google removed that parameter 8–10 September 2025; Danny Sullivan confirmed it was intentionally disabled and that it was "not an officially supported feature." Nobody has touched the line. (Note: the pagination offset was *never* correct — `len(self.results)` counts deduplicated LinkedIn profiles, not SERP results, so overlap and skip predate Sept 2025. The change altered the magnitude of a pre-existing bug.)

Three code decisions burn the IP faster than necessary. The offset never advances when a page yields zero parseable profiles, so at defaults (`-t 15 -j 1`) the tool re-requests the identical URL ~15 times in rapid succession — **it manufactures the 429 users report.** `search.py:147` is missing a trailing comma, so Python implicitly concatenates the two Firefox UAs into one 163-character string containing two `Mozilla/5.0` tokens; AST-verified, 1 request in 8 carries an unambiguous bot signature and **no valid Firefox UA is ever sent.** The remaining pool is 5 × Chrome 108/109 and 2 × Safari 16.1 — January 2023 vintage, itself now a detection signal.

**Collection-integrity finding, worse than first assessed:** `verify=False` is hardcoded at `search.py:164` with no flag to re-enable it, `InsecureRequestWarning` is suppressed at line 13, **and the Bing endpoint is plaintext `http://`** while Google is `https://`. On the default engine list `google,bing`, roughly half your SERP traffic has no transport security at all. The documented workflow routes this through third-party proxies. A hostile proxy can inject fabricated employees into a targeting list undetectably, and against the Bing half it needs no certificate trickery whatsoever.

Maintenance: last code change to the package **2024-01-30** (by an outside contributor); `search.py` itself untouched since **2023-08-22**. PyPI 0.3.0 (2023-06-19) is *behind* master, so the README's first install instruction hands you older code. The maintainer is still active — pushing to `taser` on 2026-07-28 and `Dispatch` on 2026-03-13 — while his most-starred repo (1,582 stars) sits broken. That is deliberate deprioritization, not an author who vanished. Do not plan on an upstream fix.

`-f` is `required=True`, so the CLI cannot be used as a pure collector — you must assert an email naming convention just to get raw names out. `names.csv` rows are hand-built with `'"{}","{}",...'.format(...)` through a *logging FileHandler*, not the `csv` module: no quote escaping, and a trailing comma on every row producing a phantom 7th column.

**Do:** reimplement the technique against a paid SERP API (SerpAPI, Bright Data, Zenserp). That single decision converts the fatal weakness into a strength — you keep the credential-free-against-LinkedIn property that makes the legal posture clean, you exit the CAPTCHA arms race upstream spent five years losing, and the API key authenticates you to the *SERP vendor*, not to LinkedIn, so nothing about the LinkedIn-side posture changes. Read `search.py:87-130` for the anchor-shape heuristics (~40 lines, real hard-won knowledge) and the fork's `<h3>/<h2>` extraction and `/url?q=` redirect decoding as the correct modern refinements. **Cite as prior art; do not copy verbatim — GPL-3.0 follows the code.**

### SoIG — dead since mid-2022, derivative of an archived upstream, and it leaks your target list to TinyURL

**Its single collection path parses `window._sharedData`, an artifact Instagram removed around June 2022.** `get_profile()` does `soup.find_all("script", attrs={"type": "text/javascript"})`, hard-indexes `more_data[3]`, slices `[21:]` off the front — exactly `len("window._sharedData = ")` — and walks `data["entry_data"]["ProfilePage"][0]["graphql"]["user"]`. All three assumptions (script type, ordinal position, byte prefix) are independently false today. Modern Instagram carries data in `type="application/json"` RelayPrefetchedStreamCache blobs that this selector can never match, and anonymous profile requests get a login wall.

Three open issues report the identical traceback terminating at `api/api.py, line 76 ... IndexError: list index out of range` — #8 (2022-08-22), #10 (2023-01-24), #13 (2024-05-17). Issue #13 has six "same" comments running through **2026-05-13**, three months ago. Zero maintainer replies on any of them. `__init__` calls `get_profile()`, so failure is in the constructor: **no degraded mode, no partial capability, no subset of fields that still returns.**

It is not original work. It is a re-badge of `sc1341/InstagramOSINT` — the README's opening sentence is verbatim identical and the load-bearing parse line was byte-identical at time of copy (commit `e67a84f`, 2020-06-08). The banner was changed to read "Coded By : Yezz123", and `grep -rniE "sc1341|InstagramOSINT"` returns **zero hits** in the worktree and `git log --all -S "sc1341"` returns zero commits. MIT clause 2 requires retaining the original copyright notice. **The upstream author has since archived his own repo.** When the person who wrote the mechanism has formally given up, adopting a downstream copy whose maintainer stopped answering in 2022 is indefensible.

Undeclared third-party disclosure: `extra.tiny_url()` pushes every target's profile-picture CDN URL and every post thumbnail to `http://tinyurl.com/api-create.php` over **plaintext HTTP**, with no timeout and no error handling — and it is reached on the profile-only path, so egress happens even without `-s`. Your target set is disclosed to a US third party, logged there against your IP, in cleartext. It also destroys evidentiary value: the signed CDN URL is discarded and replaced with a redirector, so the artifact you retain is not the artifact you collected.

Even granting a working endpoint, it is disqualified for a multi-target system: `raw_tags` and `tag_lis` are **module-level mutable globals** appended to and never reset, so two targets in one process cross-contaminate hashtag data — wrong-but-plausible intelligence, the worst failure mode available. `from api.api import *` with no `__all__` injects `re` into the caller **bound to the ANSI string `"\033[1;31m"`**, shadowing the regex module. `make_dir()` does `os.chdir(self.user)` on an unvalidated argv-derived path and never returns. Output is ANSI-coloured `print()` with a per-character `time.sleep(0.1)` typewriter affectation. Not on PyPI (404). No packaging, no tests, no CI. `beautifulsoup4==4.6.0` is a **2017** pin requiring a `collections.Callable` monkeypatch to survive Python 3.10+.

Two silent-data defects beyond the three above: captions are **never** written to `posts_data.txt` (`api.py:241` writes into the per-edge dict `post` instead of `posts[index]`, and the `KeyError` is swallowed), and `tags.txt` receives the flat repeated list, not the `Counter` — frequency counts exist only on stdout.

**Decisively for a correlation platform: it never emits Instagram's numeric user ID.** The graphql payload contains `id`; the code does not extract it. Issue #3 ("Suggestion: ID profile", 2020-12-29) asked for exactly this and was closed without implementing it. The only join key it produces is the mutable, re-assignable handle.

Correct one narrative point: the owner is not entirely absent — he merged PR #15 himself on 2026-06-28 and opened issue #16 himself on 2026-07-06 (an empty-bodied "Huge refactor and enhancements" intent note; it is an **issue by the owner**, not a farmed PR). Nothing has happened in the seven weeks since, and PR #15 was a one-line README edit that inserted a stray `ls -la venv/bin/` into the middle of the install block, making the docs actively wrong. So `pushed_at: 2026-06-28` is a worse freshness signal than it looks — the owner personally merged a change he evidently did not read.

**Carry forward exactly two things:** the pivots `connected_fb_page` (IG→Facebook) and `external_url` (IG→domain) are worth designing for, and the confirmation that the unauthenticated-collection posture is what you want and is **no longer available on this platform**.

---

## What the six collectively do not give you

| Capability the COP needs | Provided by any of the six? |
|---|---|
| Immutable platform ID as a primary key | **toutatis only** (IG PK, plus `fbid_v2` at the library layer). informer emits Telegram `chat_user_id` but on a 32-bit column. |
| Structured machine output on stdout | **None.** SQLite (snapmap), MySQL (informer), CSV/TXT (CrossLinked), console + mislabelled files (SoIG, toutatis). |
| Avatar fetch + perceptual hash | **None.** toutatis returns `hd_profile_pic_url_info.url`; nobody fetches or hashes it. |
| Bio / `external_url` link extraction | **None.** toutatis returns the raw strings; nobody parses them. |
| Per-result confidence or provenance | **None.** Zero of six. |
| Working code today | **Zero of six.** |

---

# PART 2 — THE COP

## 2.0 Is a single plane of glass the right shape for *this* set?

**The shape is right. The set is not, and you should not let the set define the shape.**

A consolidating COP is the correct architecture for person-centric OSINT because the actual analytic job — *"is this the same person, and how sure am I?"* — is a resolution problem over evidence from multiple sources, and it cannot be done in six terminal windows. That is a real requirement and it does not evaporate because these six particular repos rotted.

But be honest about what these six would contribute to it *today*: **nothing.** Four are dead, one is a README, one runs only after you fix four bugs. If you build a COP and wire these six in, you have built a plane of glass over an empty room.

So invert the plan. **Build the plane of glass around a data model and an adapter contract, and populate it with collectors you control** — two or three reimplemented from this set's tradecraft, plus live third-party libraries (Maigret, Sherlock, WhatsMyName) that are MIT and actually maintained. The six deliver their value as a **specification**, not as dependencies. That is the honest deliverable from this review.

## 2.1 Build vs adopt — lead with this, it is the highest-leverage decision

**Recommendation: BUILD the COP core. Do not adopt IntelOwl. Do not adopt SpiderFoot as a running system — vendor its ontology, which is MIT and is the best prior art in this space.**

The tempting counter-argument — "IntelOwl or SpiderFoot is already 80% of this" — is **false**, and the two candidates fail on *orthogonal* axes. Neither gap closes by writing plugins.

### IntelOwl is alive and has the wrong entity model

`api_app/choices.py:105`:

```python
class Classification(models.TextChoices):
    IP = "ip"; URL = "url"; DOMAIN = "domain"
    HASH = "hash"; GENERIC = "generic"; FILE = "file"
```

No person, username, email, phone, or name type. Tracing `calculate_observable()` (same file, 113–156): a username matches no branch → `GENERIC`. An email fails the DOMAIN regex (`@` is not in the character class) → `GENERIC`. A phone → `GENERIC`. The fallback logs *"Couldn't detect observable classification."*

Then `Classification.get_data_model_class()` — the enrichment layer that would carry correlation — **raises `NotImplementedError` for `GENERIC`.** Every selector your six tools consume and emit lands in `GENERIC`. You would be wrapping six person-centric tools into a platform whose entity-resolution layer structurally refuses to represent people. That is a core-model fork of an **AGPL-3.0** Django app, not a plugin gap.

Integration cost, measured: IntelOwl registers every plugin via a **Django data migration** — `api_app/analyzers_manager/migrations/` holds **289** of them. Wrapping six tools is six analyzer classes *plus* six numbered data migrations carried as a permanent fork delta against an upstream that ships new migrations continuously. Migration-number collisions on every rebase. Under AGPL-3.0.

IntelOwl's "correlation" is also not correlation. `pivots_manager/pivots/` is five files. Reading `pivots_manager/classes.py`, a Pivot is `get_value_to_pivot_to()` → `get_playbook_to_execute()`: take a value from report A, start a job with playbook B. One-directional job chaining, scoped to a job. It never merges entities, never detects that two investigations share a selector, builds no graph. **It orchestrates; it does not correlate.**

### SpiderFoot has the right model and is dead

`spiderfoot/db.py` defines 172 event types in a four-tier ontology (57 `ENTITY`, 79 `DESCRIPTOR`, 5 `SUBENTITY`, 30 `DATA`):

```
['USERNAME',                'Username',                        0, 'ENTITY']
['HUMAN_NAME',              'Human Name',                      0, 'ENTITY']
['EMAILADDR',               'Email Address',                   0, 'ENTITY']
['PHONE_NUMBER',            'Phone Number',                    0, 'ENTITY']
['ACCOUNT_EXTERNAL_OWNED',  'Account on External Site',        0, 'ENTITY']
['SOCIAL_MEDIA',            'Social Media Presence',           0, 'ENTITY']
['SIMILAR_ACCOUNT_EXTERNAL','Similar Account on External Site',0, 'ENTITY']
```

The `ENTITY` vs `DESCRIPTOR` split is the abstraction you will otherwise reinvent: `EMAILADDR` is a thing that exists; `EMAILADDR_COMPROMISED` is an assertion *about* that thing. That is what makes correlation tractable and provenance auditable. It is genuinely good design work and it is MIT.

**The liveness trap will burn a casual assessment.** GitHub reports `pushed_at: 2026-04-13` and LFX Insights reports "active 364 of the last 365 days." Both are artifacts. Branches are only `master`, `fix-install-error`, and `dependabot/pip/test/pytest-9.0.3` — the 2026 push is **the dependabot branch**. `master` HEAD is `0f815a20`, committer date **2023-11-05**, *"sfwebui: Update jQuery 3.6.0 to 3.7.1"*. Last release **v4.0, 2022-04-07**. The "activity" LFX counts is an unmoderated spam issue tracker. Steve Micallef joined Intel 471 on its acquisition (2022-11-02) as VP of Attack Surface Technology; the OSS repo was left running. **Upstream is dead ~2 years 9 months.**

SpiderFoot's correlation engine is real but narrower than advertised: 37 rules in a genuine declarative DSL (`collections` → `aggregation` → `analysis`, with `threshold`/`outlier` methods) — e.g. `email_in_multiple_breaches.yaml` collects `EMAILADDR_COMPROMISED`, aggregates on `source.data`, fires at `minimum: 2`. That is within-**one-scan** anomaly detection over a flat event table, not persistent cross-investigation entity resolution. **Good pattern to copy, insufficient engine to inherit.**

**NOT VERIFIED:** the exact release at which SpiderFoot relicensed GPL-2.0 → MIT (commonly cited as v3.3, 2021-01-24). Current licence is unambiguously MIT (`LICENSE`, module headers, `spdx_id: MIT`). **If you vendor code, verify the relicensing commit covers the specific files you take.** I did not confirm it.

The live fork `poppopjmp/spiderfoot` ("Codename Mirage") is a real continuation — MIT, monthly releases, v6.1.0 2026-06-02 — but its README describes a **23-container Docker Compose stack** (Traefik, FastAPI+GraphQL, React SPA, Celery + beat + Flower, Tika, Qdrant, MinIO, LiteLLM, "7 AI Agents") to run a username lookup, with contributor stats of `poppopjmp` 1495 commits and **`claude` 104 commits**, 191 stars, effectively single-maintainer. Viable fallback; enormous footprint; **does not remove your need for your own entity model.**

### The rest, briefly

| Candidate | SPDX | Liveness (default branch) | Correlation? | Verdict |
|---|---|---|---|---|
| SpiderFoot (smicallef) | MIT | **dead** — HEAD 2023-11-05 | within-scan YAML rules | **Mine the ontology, don't run it** |
| SpiderFoot (poppopjmp) | MIT | active, v6.1.0 2026-06-02 | inherited | Fallback, high footprint |
| **IntelOwl** | **AGPL-3.0** | healthy, v6.8.0 2026-08-17 | **no** | **Reject: wrong entity model** |
| recon-ng | GPL-3.0 | dormant — 2024-11-01, zero releases | no | Reject |
| Maltego CE | proprietary | vendor-controlled | yes (graph) | Reject as platform; steal the transform model |
| **Maigret** | MIT | **active today** | no (collector) | **Wrap as library** |
| theHarvester | **GPL-2.0-only** | active | no (collector) | Wrap at arm's length; note licence |
| Blackbird | **no LICENSE file at all** | stale — 2025-07-13 | no (collector) | **Cannot vendor. Use WhatsMyName directly.** |

Two licence traps, because GitHub reports `license: null` for both: **theHarvester** is `GPL-2.0-only`, declared only in `pyproject.toml` with no root `LICENSE`; **Blackbird** has no licence file anywhere (default: all rights reserved), vendors WhatsMyName (CC BY-SA 4.0) and a GPLv3 permute module, and is not on PyPI — the PyPI package named `blackbird` is unrelated software by a different author, a live typosquat hazard. **Drop Blackbird and consume WhatsMyName directly** (CC BY-SA 4.0, maintained, a single pinned JSON file with a published schema).

### Why build wins on the merits

Your collectors are already library-integrable, which removes the main reason to adopt a framework:

```python
# Maigret (MIT) — maigret/checking.py:1206
async def maigret(username: str, site_dict: Dict[str, MaigretSite], logger,
                  ..., id_type="username", ...) -> Dict[str, SiteResult]

# Sherlock (MIT) — sherlock_project/sherlock.py:173
def sherlock(username: str, site_data: dict, query_notify: QueryNotify,
             ...) -> dict[str, dict[str, str | QueryResult]]
```

Both return structured objects, not console text. Maigret even parameterises `id_type` and accepts 12 typed IDs (`gaia_id`, `vk_id`, `steam_id`, `orcid`, `yandex_public_id`, `qq_id`, …). A framework buys you a scheduler, a UI, and a data model — you need the first two and must reject the third from **both** candidates. Writing a task queue and a web UI against a correct entity model is far less work than retrofitting a person ontology into IntelOwl's `Classification` enum or resurrecting a codebase that predates Python 3.12.

**Build order:** (1) entity/assertion model, seeded from SpiderFoot's `ENTITY`/`DESCRIPTOR`/`SUBENTITY`/`DATA` vocabulary — MIT, copy verbatim and extend; (2) the adapter contract declaring each collector's *consumed* and *emitted* selectors — this is the only thing that makes cross-tool correlation possible; (3) normalise collectors into the model; (4) correlation over the persistent store; (5) UI last.

---

## 2.2 Entity and selector model

### The three-layer split the whole design rests on

Every person-centric OSINT tool conflates three things. The COP must not.

```
Selector   a typed string. A join key. An immutable value.
           "torvalds" is a Selector, not an account.

Account    a platform-scoped principal, identified by a PLATFORM-ISSUED
           IMMUTABLE ID. Its username is a time-bounded ATTRIBUTE,
           not its identity.

Person     an analyst-asserted CLUSTER HYPOTHESIS over Accounts.
           NEVER created by a collector. Only by a resolution decision.
```

Why this is not academic: Instagram, Telegram and Snapchat handles are all **recyclable**. Key an Instagram account on the handle, the handle gets released and re-registered, and your dossier silently fuses two humans — with no signal that it happened. This is precisely why **toutatis emitting the IG numeric PK is the single most valuable output in the entire toolset**: it is the only platform-issued immutable identifier any of the six produces. informer's Telegram `chat_user_id` is the second (on a 32-bit column that overflows).

SoIG, CrossLinked and both Snap Map implementations emit **no immutable platform ID at all.** Everything they produce is handle-keyed or content-keyed, and therefore structurally fragile.

### Node types

| Node | Identity | Created by |
|---|---|---|
| `Person` | COP-issued UUID | **analyst resolution decision only** |
| `Account` | `(platform, platform_uid)` if known; else `(platform, normalized_handle)` with `provisional = true` | collector |
| `Selector` | `(selector_type, value_norm, norm_rule)` | collector |
| `Organization` | COP-issued UUID | collector/analyst |
| `Place` | UUID + geometry **with mandatory accuracy** | collector/geocoder |
| `Media` | content SHA-256 (pHash is an attribute, **never** identity) | collector |
| `Observation` | UUID — **the only node a collector may assert freely** | collector |
| `CollectionTask` | UUID | tasking layer |
| `Tool` | `(name, version, config_hash)` | registry |

Selector types in scope for this set: `username`, `email`, `email_obfuscated`, `phone_e164`, `phone_obfuscated`, `real_name`, `platform_uid`, `profile_url`, `url`, `org_name`, `domain`, `snap_id`, `telegram_channel`, `geo_point`, `image_phash`, `discord_snowflake`.

### The edge rule

**There are no bare edges.** Every edge is a *view* over one or more `Observation` rows. An edge with no surviving observation does not exist. This is what makes provenance structural rather than an add-on — the graph is literally reconstructed from the evidence table.

```
Account      --HAS_HANDLE(valid_from, valid_to)-->  Selector(username)
Account      --HAS_UID-->                           Selector(platform_uid)
Account      --DECLARES_CONTACT-->                  Selector(email|phone_e164)
Account      --DECLARES_CONTACT_MASKED-->           Selector(email_obfuscated|phone_obfuscated)
Account      --HAS_AVATAR-->                        Media
Account      --SELF_LINKS_TO-->                     Selector(url) | Account
Account      --AUTHORED-->                          Observation(message|post|snap)
Account      --MEMBER_OF-->                         Organization | Venue(telegram_channel)
Person       --IS(score_db, decision_id)-->         Account   <-- the ONLY resolution edge
Observation  --OCCURRED_AT-->                       Place (accuracy_m NOT NULL)
Observation  --OCCURRED_ON-->                       observed_at (NOT collected_at)
Media        --DEPICTS(conf)-->                     Person | Place   <-- exploitation output
```

`Person --IS--> Account` carries the confidence and a decision ID. **Confidence lives on the resolution edge, not on the Person.** A `Person` with a `confidence` field is the classic laundering bug: it lets a 0.55 link and a 0.99 link both become "this person."

### Schema (PostgreSQL 16)

```sql
-- ============ EVIDENCE SUBSTRATE ============

CREATE TABLE tool (
  tool_id        uuid PRIMARY KEY,
  name           text NOT NULL,
  version        text NOT NULL,
  image_digest   text NOT NULL,          -- sha256:… NOT a version string. Versions lie.
  vcs_commit     text,
  config_hash    text NOT NULL,          -- manifest/site-list hash
  spdx_licence   text NOT NULL,
  UNIQUE (name, version, config_hash)
);

CREATE TABLE collection_task (
  task_id        uuid PRIMARY KEY,
  case_id        uuid NOT NULL REFERENCES investigation_case,
  tool_id        uuid NOT NULL REFERENCES tool,
  method_class   text NOT NULL,          -- see §Doctrine D7
  requested_by   text NOT NULL,
  justification  text NOT NULL,
  authority_ref  text NOT NULL,          -- controlled vocab; NOT NULL is the point
  input_selector jsonb NOT NULL,         -- {"type":"username","value":"…"} or AOI geometry
  credential_ref text,                   -- opaque vault handle. NEVER the secret.
  persona_id     uuid,                   -- which sock performed it -> blast-radius query
  egress_ip      inet,                   -- RESULT-AFFECTING. Not ops trivia.
  corpus_version text,
  corpus_site_count int,
  started_at     timestamptz NOT NULL,
  finished_at    timestamptz,
  exit_class     text                    -- 'ok' | 'degraded' | 'failed'
);

CREATE TABLE raw_evidence (
  sha256         bytea PRIMARY KEY,      -- content-addressed; blob in MinIO
  media_type     text NOT NULL,
  byte_len       bigint NOT NULL,
  uri            text NOT NULL,
  task_id        uuid NOT NULL REFERENCES collection_task,
  tombstoned_at  timestamptz             -- purge sets this; assertions survive, degraded
);

CREATE TYPE evidence_class AS ENUM (
  'observed',       -- the collector saw it on the platform
  'proxy_mirror',   -- seen via a third-party mirror -- hard confidence cap
  'derived',        -- computed from other assertions by a named rule
  'synthesized',    -- template-generated (CrossLinked names.txt) -- NEVER a join key
  'analyst'         -- a human asserted it
);

CREATE TABLE assertion (
  assertion_id     uuid PRIMARY KEY,
  subject_kind     text NOT NULL,
  subject_id       uuid NOT NULL,
  predicate        text NOT NULL,
  object_kind      text,
  object_id        uuid,
  object_literal   jsonb,

  -- PROVENANCE. All NOT NULL by design.
  task_id          uuid NOT NULL REFERENCES collection_task,
  tool_id          uuid NOT NULL REFERENCES tool,
  evidence_sha256  bytea REFERENCES raw_evidence,
  evidence_pointer jsonb,        -- {"json_path":"$.user.public_email"} | {"csv_row":42}
  probed_host      text,         -- differs from displayed host on mirror sites
  displayed_url    text,

  -- BITEMPORAL. Three clocks. Never collapse them.
  observed_at      timestamptz,            -- true on-platform (nullable)
  collected_at     timestamptz NOT NULL,   -- when the collector saw it
  ingested_at      timestamptz NOT NULL DEFAULT now(),
  valid_from       timestamptz,            -- for time-bounded attrs (handles!)
  valid_to         timestamptz,

  -- CONFIDENCE
  ev_class         evidence_class NOT NULL,
  confidence_db    numeric(6,2) NOT NULL,      -- DECIBANS
  confidence_basis text NOT NULL,              -- rule id / calibration ref
  collector_health text NOT NULL,              -- 'healthy'|'degraded'|'unknown' AT COLLECTION
  derivation_rule  text,                       -- non-null iff ev_class='derived'
  derived_from     uuid[] NOT NULL DEFAULT '{}',  -- FULL input closure

  retracted_at     timestamptz,
  retraction_reason text
);

CREATE INDEX ON assertion (subject_kind, subject_id, predicate) WHERE retracted_at IS NULL;
CREATE INDEX ON assertion USING gin (derived_from);

-- ============ ENTITIES ============

CREATE TABLE selector (
  selector_id    uuid PRIMARY KEY,
  selector_type  text NOT NULL,
  value_raw      text NOT NULL,     -- NEVER destroyed (CrossLinked unidecodes; don't)
  value_norm     text NOT NULL,
  norm_rule      text NOT NULL,     -- 'username/casefold/v1', 'email/gmail_dots/v2'
  rarity_bits    numeric(5,2),
  rarity_source  text,              -- 'proxy_v1' | 'sherlock_availability' | 'corpus_v3'
  is_pii         boolean NOT NULL,
  UNIQUE (selector_type, value_norm, norm_rule)
);

CREATE TABLE account (
  account_id     uuid PRIMARY KEY,
  platform       text NOT NULL,
  platform_uid   text,              -- IG PK, fbid_v2, TG chat_user_id -- the durable key
  provisional    boolean NOT NULL DEFAULT true,   -- true while keyed only on a handle
  first_seen     timestamptz NOT NULL,
  UNIQUE (platform, platform_uid)
);

CREATE TABLE person (
  person_id      uuid PRIMARY KEY,
  created_by     text NOT NULL,
  created_at     timestamptz NOT NULL,
  case_id        uuid NOT NULL REFERENCES investigation_case
);

-- The resolution edge. Confidence lives HERE.
CREATE TABLE resolution_decision (
  decision_id      uuid PRIMARY KEY,
  person_id        uuid NOT NULL REFERENCES person,
  account_id       uuid NOT NULL REFERENCES account,
  score_db         numeric(6,2) NOT NULL,
  family_breakdown jsonb NOT NULL,     -- {"F1":15,"F2":6,"F4":25,"F7":-3}
  evidence_closure uuid[] NOT NULL,    -- every assertion that fed the score
  decided_by       text NOT NULL,      -- a human. always.
  decided_at       timestamptz NOT NULL,
  confirmed_by     text,               -- second analyst; required above 35 dB
  reversed_at      timestamptz,
  reversal_reason  text
);

CREATE TABLE place (
  place_id       uuid PRIMARY KEY,
  geom           geography(Point,4326),
  accuracy_m     numeric NOT NULL,     -- NOT NULL ON PURPOSE. No accuracy, no point.
  accuracy_basis text NOT NULL,        -- 'snap_url_suffix'|'query_radius'|'geocoded_name'
  name_raw       text
);
```

### The four invariants

1. **Monotonic confidence.** For `ev_class='derived'`, `confidence_db ≤ min(confidence_db of derived_from)` **unless** `derivation_rule` is registered as a corroboration rule *and* its inputs come from ≥2 distinct evidence families. Enforce as a constraint trigger, not a code convention.
2. **Full closure.** Every derived assertion records its complete input set. This is what makes transitive-exclusion computable (§2.4) and retraction cascade correctly.
3. **Immutable content-addressed raw evidence.** Purge sets `tombstoned_at`; dependent assertions are marked `evidence_unavailable` and their confidence is **floored**, never silently kept at full strength.
4. **`synthesized` is never a join key.** CrossLinked's `names.txt` output must be *barred by the schema* from participating in selector equality joins. It may only be **tested against a mask** (§2.5) or confirmed by an independent observation, creating a new `observed` assertion. This is the single rule that prevents *"we generated an email, then found the email in our graph, therefore it's real."*

---

## 2.3 The pivot chain — which tool actually feeds which

```
 org_name ──CrossLinked──► real_name + linkedin_url + job_title
                              │
                              ├──(template)──► email@corp.com  [SYNTHESIZED. Not evidence.]
                              │
                              └──(analyst guess)──► username ──┐
                                                               ▼
                                                    Sherlock / Maigret / WMN
                                                               │
                                    ┌──────────────────────────┼──────────────────┐
                                    ▼                          ▼                  ▼
                            "Instagram: Claimed"      "Telegram: Claimed"   ~400 other verdicts
                                    │                          │            (analyst-only)
                                    ▼                          ▼
                          toutatis-equivalent          DEAD END — nothing in the
                          (needs IG sessionid)         set consumes a TG handle
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
  IG numeric PK              obfuscated_email/phone       external_url + bio
  + fbid_v2 (IMMUTABLE)              │                           │
        │                            ▼                           ▼
        │                 ══► VERIFY / REFUTE the ◄══     domain, other handles
        │                    CrossLinked hypothesis        (SELF-ASSERTION —
        │                                                   strongest class available)
        ▼
  profile_pic_url ──► [YOU MUST BUILD] avatar fetch + pHash


 telegram_channel ──informer-equivalent──► chat_user_id + username + message corpus
        ▲
     analyst picks venues. NOT reachable from any person selector.
     VENUE-IN, PERSON-OUT.


 lat/lon ──snapmap──► snap_id + media + timestamp + place STRING
                          │
                          └──► NO PERSON SELECTOR. EVER.
                               Joins to a Person only via media exploitation:
                               [YOU MUST BUILD] OCR of overlay text, face match,
                               visible handles.
```

### The honest count

Of the six, exactly **two machine-automatable edges** exist with real confidence gain:

1. **`Sherlock "Instagram: Claimed"` → IG collector (username).** Handle passes directly. The one clean programmatic pivot.
2. **`obfuscated_email` → verify/refute the CrossLinked synthesized email.** The highest-value fusion available. Build it first (§2.5).

Everything else is analyst-mediated or absent:

- **`Person name → username` is a generator, not a pivot.** CrossLinked gives you "jordan voss"; Sherlock needs a handle. Producing `jvoss`, `jordanvoss`, `jmvoss`, `vossj` is **enumeration**, and each candidate is an independent hypothesis whose hits carry near-zero weight until corroborated. The COP must not present these as findings.
- **Telegram is a dead end in this set.** Nothing consumes a Telegram handle; informer only ingests channels.
- **Snap Map has no person selector on either side.** No author field in the `getPlaylist` response.
- **DiscordOSINT contributes zero.** The one automatable thing it points at is `(snowflake >> 22) + 1420070400000` — eight lines, deterministic, offline, no ToS exposure. Implement natively and retire the repo as a "tool."
- **SoIG is redundant with toutatis and dead.** Cut it.

### Three integration landmines that will corrupt the graph if not handled at the adapter

**(a) Mirror probes.** Sherlock's Instagram entry probes `imginn.com` while *displaying* `instagram.com`:
```json
"Instagram": { "errorType": "status_code",
               "url": "https://instagram.com/{}",
               "urlProbe": "https://imginn.com/{}" }
```
A "Claimed" verdict is evidence about a scraper's cache, and every lookup leaks your target list to that third party. 52 of 482 manifest entries carry a `urlProbe`. **Adapter rule:** record `probed_host` separately from `displayed_url`; any assertion where they differ gets `ev_class = 'proxy_mirror'` and a hard confidence cap.

**(b) Rate-limits scored as confident negatives.** Sherlock's Discord entry lists `"The resource is being rate limited"` in `errorMsg`. Under the `message` strategy, presence of the `errorMsg` string means **AVAILABLE** — a 429 becomes "this person is not on Discord." **Adapter rule:** `Available` is never ingested as negative evidence unless `http_status == 200` and no WAF fingerprint fired. Otherwise map to `Unknown`.

**(c) Wrong timestamps and truncated IDs.** informer stores `datetime.now()` — ingest time — and never persists Telegram's message ID or message date. Its `chat_user_id`/`channel_id` are 32-bit signed. Both are adapter-blocking. Fix in your own collector.

**(d) Discarded geometry.** Neither Snap Map implementation stores coordinates. The archiver's `SNAP_PATTERN` *captures* `@lat,lon,zoom` from the share URL and throws it away. **The one geospatial tool in the set discards geometry.** Your adapter must re-derive lat/lon from the snap URL suffix where present, and where absent record the query point + `radiusMeters` as **accuracy**, not as a position.

---

## 2.4 Confidence and provenance

### Same username on two platforms is weak, and the reason is quantifiable

The evidentiary weight of a handle match is not a property of "handle matching." It is a property of **that specific string's population frequency**. `mjohnson` is held by thousands of humans. A 14-character non-dictionary string functions as a shared secret. Treating both as "+1 link" is the single most common way OSINT graphs become fiction.

**A free rarity estimator hides in the negative results.** Run a full site sweep and compute `n_available / n_probed`. A handle available on ~400 of 414 sites and claimed on 3 is rare, and those 3 claims are strong evidence of a common owner. A handle claimed on 380 of 414 is a common word everybody grabs. This monetizes the otherwise-noisy half of the output at zero extra cost. Store as `selector.rarity_bits` with `rarity_source = 'sherlock_availability'`.

Until you have a corpus, back it with dictionary-token decomposition + digit runs → `-log10(P_generative)`, and **label it a proxy in the schema** (`rarity_source = 'proxy_v1'`). Do not let a proxy silently become a measurement.

### Store confidence as decibans

`dB = 10 · log10(LR)`. Combination is addition, there is no 0–1 ceiling to saturate against, and refutation is just a negative number. A 0–1 "score" invites averaging, and averaging is how confidence gets laundered.

**Be honest about what this is:** absolute posteriors are not computable — you do not have the base rates. The deciban sum is a **ranking and thresholding instrument** that must be calibrated against a labelled set you build. **Every number below is a design default for calibration, not a measurement.**

### Evidence families, with caps

Group by *generating cause*, because within a family items are correlated, not independent.

| Family | Evidence | Default dB | Family cap |
|---|---|---|---|
| **F1 HANDLE** | high-rarity handle match (>20 bits) | +15 | **+15** |
| | medium rarity | +7 | |
| | dictionary/common handle | +1 | |
| **F2 CONTACT** | identical verified email on both accounts | +30 | **+30** |
| | identical E.164 phone | +28 | |
| | masked value *consistent* with candidate | +6 | |
| | masked value *inconsistent* | **−20** | |
| **F3 IMAGE** | avatar pHash Hamming ≤6, non-stock | +18 | **+18** |
| | pHash match on a platform-default avatar | **0** | |
| **F4 SELF-ASSERTION** | A's bio/`external_url` links to B | +25 | **+30** |
| | mutual A↔B links | +30 | |
| **F5 NAME** | rare full-name match | +10 | **+10** |
| | common full-name match | +2 | |
| **F6 TEMPORAL** | sustained co-activity / creation-time proximity | +3 | **+3** |
| **F7 NEGATIVE** | platform-verified conflicting legal names | −10 | uncapped |
| | temporal impossibility | −25 | |
| | clean `Available` (200, no WAF) where B is claimed | −3 | |

**The rule that stops transitive laundering:**

> A link's score is `Σ over families of min(family_sum, family_cap)`. Two links A–B (18 dB) and B–C (18 dB) do **not** produce A–C at 36 dB. A–C must be scored **from its own evidence**, with any evidence item already appearing in A–B or B–C **excluded** from the A–C computation. Every derived assertion stores its full input closure precisely so this exclusion is computable.

Three platforms showing the same handle is **one** piece of evidence (one generating cause: the human picked one handle), not three — hence the F1 cap. This is the failure mode that turns a 6-node graph into a 60-node fiction.

### Resolution is an event, not a state

- **No automatic Person merges. Ever.** Above threshold the COP *proposes*; a human decides; the decision is a row.
- Merges must be **reversible** — store the decision and its evidence closure, do not mutate the graph in place.
- Thresholds (defaults): `<10 dB` unlinked · `10–20` candidate · `20–35` probable, analyst review · `>35` assertable, second-analyst confirmation.
- **Per-site reliability priors, not a global one.** Maintain `tool_site_reliability(tool, site, tp, fp, measured_at)` as a first-class, versioned COP artifact and feed it into F1.

---

## 2.5 The one high-value fusion in this toolset — build it first

CrossLinked emits `jvoss@acme.com` — **synthesized**, zero evidentiary value alone. toutatis emits `obfuscated_email` as `j***s@a***.com` and `obfuscated_phone` as a masked trailing-digit string. These are **not selectors — they cannot join** — but they are **constraints that verify or refute a candidate.**

```python
def match_masked(candidate: str, mask: str) -> tuple[str, float]:
    """Returns (REFUTE|CONSISTENT|UNDETERMINED, weight_db).
    Reveals: first char, last char, local-part length, domain shape.
    A mismatch is a HARD refutation. That asymmetry is the whole value."""
    revealed = parse_mask(mask)            # positions + lengths that survive masking
    if any(disagree(candidate, revealed)):
        return ("REFUTE", -20.0)
    return ("CONSISTENT", revealed_entropy_bits(revealed))   # ~6-10 dB, corporate domain
```

Honest calibration: first-char + last-char + local-length + domain-shape agreement on a corporate domain is roughly **6–10 bits** — meaningfully positive, **not proof**. Its real power is asymmetric: **a mismatch is a hard refutation, and refutations are what keep candidate sets from exploding.** ~150 lines, and it is the only place in the six where two independent sources actually constrain each other.

An entire separate tool (`0x0be/yesitsme`) exists solely to perform this match, which validates the pattern as established tradecraft.

**Format caveat, NOT VERIFIED:** toutatis's own README shows `me********s@examplemail.com` and `+00 0xx xxx xx 00`; the widely-documented Instagram shapes are `j*****e@gmail.com` and `+39 *** *** **09`. Current mask width and whether the domain survives intact is unverified — every "sample output" in the tracker is a copy of the README placeholder. **Determine the real mask shape in a lab against a consenting, owned account before calibrating the matcher.**

---

## 2.6 UI shape — and an honest answer on map vs graph

### The data audit

| Data class | Volume | Has coordinates? |
|---|---|---|
| Site-enumeration verdicts | ~414/target | No |
| IG profile facts | ~20 fields/target | No |
| CrossLinked names | 10s–100s/org | No (org HQ is geocodable — that's the *org*, not the person) |
| Telegram messages | high | No (Telegram strips geo from ordinary posts) |
| IG post metadata | moderate | Rarely — a `location` object when present |
| **Snap Map snaps** | high | **Yes — and both implementations discard it** |

**One of six sources is geospatial, and the two implementations of it throw the geometry away.** A map built from this toolset today is a map of one source, rendered at the wrong accuracy.

### Recommendation

**Primary: the entity dossier. Secondary: the link graph. Tertiary: the timeline. The map is a layer and a tasking surface, not the home screen.**

This is task-analytic, not aesthetic. The analyst's actual job is *"is this the same person, and how sure am I?"* — a resolution question over attributes and evidence, answered by putting candidate accounts side by side with their evidence and the deciban breakdown. That is a **dossier**, and it is the only view where the confidence math is legible.

The link graph is the right *working surface* for the resolution decision (select two nodes → see scored evidence → merge or reject), but a force-directed hairball is a poor primary view: it makes weak and strong links look identical, which is exactly the error this design exists to prevent. **Render edge thickness and opacity keyed to decibans, and do not draw an edge below 10 dB by default.**

The timeline earns third place and matters more than it looks: F6 temporal correlation, message streams, snap timestamps, and account-creation times (including the free Discord snowflake derivation) all live there — and **temporal impossibility is one of your few strong refutations.**

### What the map is actually for — three concrete roles

1. **Collection tasking.** Snap Map genuinely is map-first: draw an AOI, set radius and zoom, and that geometry *becomes* a `collection_task`. This is the one place a map is the correct primary interaction, and it is a tasking surface, not a display surface.
2. **Uncertainty display, never pins.** `place.accuracy_m` is `NOT NULL` on purpose. A snap recovered from a `radiusMeters=10000` query is an annulus, not a point. **Prohibit by doctrine: rendering a pin at the query centroid.** That displays *collection geometry as target geometry* — the map lying about where someone was — and it is the most dangerous single defect available, because a pin looks like truth. With `--randomize` on nemec's tool, the recorded coordinate can be **2109 m** from the actual query centre.
3. **Co-presence.** The one relationship a graph cannot show and a map can: two entities in the same place in the same time window. Thin with this toolset; real the moment you add a geospatially-rich source.

### Name it honestly

**This is an entity COP, not a geospatial COP.** Anyone who hears "COP" in an ISR context expects TAK-style geospatial SA, and this system will not deliver that, because the data is not geospatial. Setting that expectation wrong at the naming stage costs credibility later. If a TAK bridge is ever wanted, bridge **only** the geospatial subset (Snap Map observations with re-derived coordinates and honest accuracy circles). Pushing person-resolution assertions into CoT is a category error — CoT has no representation for the confidence and provenance that make those assertions meaningful.

---

## 2.7 Collection and operations layer

### The collector contract — the load-bearing abstraction

```
stdin:  {"job_id":…, "case_id":…, "selector":{"type":"username","value":"…"},
         "params":{…}, "corpus_version":"…", "deadline_s":600}
stdout: NDJSON, one schema-versioned observation per line
stderr: structured JSON logs
exit:   0  = ran to completion (including zero observations)
        70 = ran but DEGRADED (partial corpus, upstream manifest fetch failed)
        *  = did not run
```

Those exit codes are deliberate because **you cannot borrow the tools' conventions.** Sherlock exits `0` on zero hits, `0` on SIGINT, `0` on a typo'd `--site`, and `1` on an unhandled `FileNotFoundError` raised *after* every probe already ran. toutatis's CLI dies with an unhandled `KeyError`. nemec's snapmap dies with an uncaught `SSLError` traceback (its `sys.exit(1)` branch fires only in the *opposite* case — request succeeded but no HEAT tileset present). The wrapper must translate, and **"ran, but with the wrong corpus" must be distinguishable from both success and failure.** That is what 70 is for.

### Every tool is a container, not an import — and the licence analysis agrees

| Tool | SPDX | In-process import? |
|---|---|---|
| Maigret, Sherlock | MIT | Safe |
| **toutatis, CrossLinked** | **GPL-3.0** | **No — makes the COP a combined work** |
| holehe, PhoneInfoga | GPL-3.0 | No |
| GHunt | **AGPL-3.0** | **No — §13 extends to network users; a web UI is exactly the case AGPL was written for** |
| Blackbird | **none** | **Cannot vendor or redistribute at all** |
| informer, snapmap, SoIG | MIT | Moot — they don't run |

Separate process, separate container, JSON over stdio is standard mere-aggregation and sidesteps all of it. That this is *also* the right answer for dependency isolation, *also* the right answer for egress isolation, and *also* the right answer for blast radius is what makes it a confident recommendation rather than a compromise.

**Program rule to adopt now:** *any GPL collector is shelled out at arm's length or reimplemented — never linked.* Decide it once and it costs nothing; discover it after the COP is built and it is an architectural crisis.

### Named stack

| Layer | Choice | Why |
|---|---|---|
| Runtime | **Podman (rootless)**, BuildKit, base image pinned **by digest**, deps from a lockfile with `--require-hashes` | Unpinned upstream deps make builds non-reproducible (informer, holehe, SoIG all ship unpinned or 2017-era pins). Rootless because collectors parse hostile third-party input. |
| Scheduler | **HashiCorp Nomad** (3 servers, N clients) | Single binary. Native per-task network namespaces + CNI. `template` stanza + OpenBao gives lease-bound per-job secret injection — the exact primitive needed. K3s if the team already runs k8s. **Compose cannot express per-job secrets or per-job egress and is a dead end here.** |
| Secrets | **OpenBao** KV-v2, AppRole per collector class | Versioned KV = free rotation history. Per-persona paths = the blast-radius query. Named over Vault because BUSL is a live procurement question for a distributable program. |
| Queue | **PostgreSQL + Procrastinate** (or `pgmq`) | **Transactional enqueue in the same commit as the case/authorization row.** One consistency domain means the audit trail cannot disagree with what ran. A Redis queue splits that and you will eventually have a job with no audit row. |
| Rate-limit state | **Redis** — ephemeral only, explicitly not a system of record | High-churn counters that must not touch durable storage. |
| Egress | **WireGuard** per persona / tool-class + **Envoy** with the `ratelimit` service; namespace has **no fallback route** | L3 covers tools with no proxy support at all. Envoy is the single chokepoint that throttles *and* observes every request. |
| Object store | **MinIO**, content-addressed by sha256 | Raw bodies, media, canary fixtures. Immutable references for the audit trail. |
| Records | **PostgreSQL 16**, observations partitioned monthly (`pg_partman`) | Volume is dominated by per-site observation rows. |
| Graph | **Apache AGE** on the *same* Postgres, or materialized adjacency tables | **Do not add Neo4j.** A second database is a second backup, a second access-control surface, and a second audit gap. |
| API | **FastAPI** + **Pydantic v2**; observation model exported to JSON Schema, validating collector NDJSON at ingest | One schema definition enforced at the boundary. Off-schema lines fail the job rather than writing garbage into a person's record. |
| UI | **React** + **TanStack Query**; graph in **Cytoscape.js**; timeline as plain SVG | Cytoscape handles thousands of nodes with real layout algorithms; D3 force graphs degrade badly past a few hundred. |
| Observability | **OpenTelemetry** → **Prometheus** + **Loki** + **Grafana** | Canary state and per-host status distributions are metrics; alerting must live where engineers already look. |
| Identity | **Keycloak** (or existing IdP) via OIDC | Every API call carries an authenticated subject. Non-negotiable. |

**Sizing for 3–8 analysts / 2 engineers:** ~5 VMs (3 small Nomad servers co-located with Postgres/OpenBao, 2 larger workers) plus 2–4 tiny egress nodes. Runs on a single beefy host with Nomad in dev mode for the first six months, and **the topology does not change when it grows** — that is the reason to pick Nomad over Compose on day one.

### Why egress must be layer 3, not `--proxy`

Two decisive reasons drawn straight from this tool set:

- **toutatis has no proxy parameter at all** — grep-verified, no `proxies=`, no `--proxy`, no env var. Neither does holehe. If your egress story is "pass `--proxy`," these tools simply egress from wherever the process runs.
- **Sherlock's `--proxy` is incomplete and unfixable by flags.** The update check (`api.github.com`), the `--json <PR#>` lookup, the manifest fetch (`data.sherlockproject.xyz`) and the exclusions fetch all bypass `--proxy` and ignore `--timeout`. The update check is **unsuppressible** — no flag disables it, `--local` included. A `--proxy`-only design leaks your real source IP to GitHub on every invocation.

**Mechanism:** each collector task runs in its own network namespace whose only route is a WireGuard interface (`AllowedIPs = 0.0.0.0/0`) to the persona's egress node. No route on the host bridge. **The tool cannot escape the egress even though it has no idea a proxy exists.**

**Fail closed.** A namespace with no fallback route returns `ENETUNREACH` when the tunnel is down. The job fails loudly instead of silently reverting to corporate egress. Assert "no default route on any other interface" in the job spec and *test it* — this is the control that most commonly rots silently.

**DNS is attribution.** Each namespace gets its own resolver over the tunnel. Otherwise the corporate resolver holds a second, independent, unaudited log of exactly who you investigated.

**Egress selection by class:**
- **Class 2 (platform session — toutatis's IG `sessionid`, informer's Telegram session): stable per-persona egress.** A Google/Meta session authenticating from a rotating pool of unrelated IPs is *more* anomalous, not less.
- **Class 0 (no credentials — snapmap, CrossLinked, Sherlock): per-tool-class egress**, isolated so one tool's reputation damage does not take the others down.
- **Commercial residential/mobile proxy pools: recommend against by default.** The provider sees your CONNECT authority for every request and **retains a log of every person you investigated.** That alone should end the discussion for a person-centric system. If used at all: Class 0 tools only, never on a case with a sensitivity marking.

Note the toutatis-specific wrinkle: the durable community workaround (issue #37) is to tether to a phone hotspot — datacenter egress is heavily penalised by Meta. **Plan residential or mobile egress for any Instagram collector, and budget it.**

### Rate limiting and scheduling

Cost is three different currencies. **They must not share a queue with a shared policy.** A session-bearing collector's cost function is *sessions per day*; a site-sweeper's is *bytes out of one IP*; an email-prober's is *state-changing writes per target*. A single "requests per second" knob is the wrong abstraction for all three.

Enforce at the egress with Envoy, not in the tool: per-`:authority` token buckets backed by Redis, and per-host status-code metrics from one place that sees **every** request from **every** collector — including the ones with no proxy support, which you can throttle in no other way.

**Do not terminate TLS on collection traffic.** You would be storing plaintext third-party content in a proxy you now have to secure, and for session-bearing collectors you would be handling the platform session in a second place. SNI-level buckets are sufficient for both throttling and rot detection.

Queue topology (Postgres + Procrastinate):
- `q.sweep` — site enumeration. Concurrency 4–8.
- `q.probe` — email/phone probes. Concurrency **2** (some tools fire uncapped concurrent requests per invocation; you cap by capping *invocations*).
- `q.authed` — session-bearing collectors. **Concurrency 1 per persona**, via a Postgres advisory lock on `persona_id`, plus a **daily job budget per persona** that hard-fails and surfaces as case-blocking, never a silent skip.
- `q.canary` — health checks. Lowest priority, **own worker pool** — if canaries share a pool with production work they starve exactly when saturation is what you most need to detect.

**Recursion is a budget, not a feature.** Maigret's recursive search extracts new identifiers from found profiles and re-searches them. One common username can consume a day's egress budget in a single job. `--no-recursion` by default; depth ≤ 2 as an explicit logged analyst decision; per-case request budget enforced at enqueue; **recursion-discovered selectors land `pending`, not collected** — this is an authorization boundary, not just a cost control (§Doctrine D1).

**Retry at the job level, not the request level.** Sherlock carries `Retry(total=0, ...)` on both adapters and has no sleep, semaphore, backoff or jitter anywhere. A transient 500 is a permanent wrong answer for that site in that run, invisible without `--print-all`. So: never re-run the whole sweep — re-run the **failed subset** with `--site` for exactly the sites that returned Unknown. That requires per-site status in the observation record, which makes `--csv --print-all` mandatory.

**Don't batch.** A per-case sweep when an analyst opens a case is normal traffic. Forty sweeps at 03:00 is a burst signature. Uniform 0–15 min jitter on all scheduled collection.

---

## 2.8 Tool rot — the problem that quietly ruins this class of system

**State it precisely: in every one of these tools, "collector broken" and "clean negative" produce byte-identical output.** This is the failure mode that turns a COP into a machine for manufacturing confident wrong answers about real people. It is not hypothetical — here are verified instances from the set under review:

- **toutatis** collapses an HTML login wall, a challenge page, an IP block and a genuine 429 into the literal string `"Rate limit"` (`core.py:28-29`). You cannot triage, alert, or drive backoff off it. The tracker's flood of "rate limit" reports is mostly misdiagnosed auth failure — and nobody noticed for two years.
- **SoIG** fails in its constructor with `IndexError` — at least that one is loud. But six users filed "same" comments across four years on an unanswered issue, which means *users could not tell it was the tool and not the target*.
- **holehe/instagram** (representative of this whole class): if CSRF extraction raises — exactly what happens when Instagram changes markup — the module returns `{"rateLimit": True, "exists": False}`. **Tool rot is reported as a rate limit, with `exists = False`.** Read only the `exists` column and a permanently broken module is indistinguishable from "this person has no Instagram."
- **Sherlock, `status_code` strategy — 327 of 481 sites.** Only **6** define an `errorCode`. For the other 321 the entire test is "did the server answer 2xx." A site that starts soft-404ing flips to permanent CLAIMED. A site that starts 403ing flips to permanent AVAILABLE. **Exit code is 0 either way.**
- **Sherlock, `message` strategy.** Raw substring against the whole body — not regex, not JSON parsing, no whitespace normalization. Proven: GitHub's API returns `"message": "Not Found"` (space after colon) while a manifest literal `"message":"Not Found"` never matches → **CLAIMED for a nonexistent user.** One whitespace change in a third party's JSON serializer silently inverts your verdict.
- **Sherlock, WAF detection.** Four hardcoded body substrings tested as `hitMsg in r.text` — but the **303 implicit-HEAD sites have no response body.** Two-thirds of the manifest can never be fingerprinted as WAF-blocked.
- **Maigret ships 691 of 3305 sites already `disabled: true`.** **21% of the corpus already rotted**, from an upstream that commits daily. That is the honest base rate for this entire tool class.

### Layer 1 — per-site control pairs (the ground truth already exists)

**Maigret's site DB carries `usernameClaimed` and `usernameUnclaimed` for 3304 of 3305 sites.** A known-positive and known-negative for every site. Build **one shared control corpus keyed by normalized `urlMain` host**, seeded from Maigret's DB, hand-extended for sites only your collectors cover, reused by every enumeration collector.

A canary asserts **both directions**, because the two failures mean different things:

- **Positive passes, negative fails** → the site is soft-404ing; *everything* is now claimed. **Every prior CLAIMED from that site is suspect.**
- **Negative passes, positive fails** → the site is blocking you; *nothing* is claimed. **Every prior negative from that site is meaningless.**

**Rotate the negative control.** It must be a guaranteed-unregistered string, and any literal published in a repo eventually gets registered. Maigret's shipped `noonewouldeverusethis7` sits in a 37k-star public repo — treat it as already compromised. Generate negatives per canary epoch (`zz` + 12 random chars) and record which epoch a result belongs to.

For the toolset under review, the equivalent canaries are:

| Collector | Positive control | Negative control | What a failure means |
|---|---|---|---|
| IG PK resolver | an owned, consenting account | rotating high-entropy handle | `getUserId` broke — see issue #148, this is already at risk |
| Masked-hint verifier | owned account with known reg. email/phone | — | The recovery-endpoint bypass has been closed |
| Snap Map | `getLatestTileSet` returns a HEAT tileset | — | Endpoint gone (already presumed) |
| SERP-API org expansion | a known org with a known headcount floor | nonsense org string | Vendor changed result shape |

### Layer 2 — aggregate distribution monitoring

Cheap, broad, computed on every production run:

- **`found_rate` per collector per day.** A sweep that historically returns ~90 hits on a common handle and returns 3 today has not found a cleaner person.
- **`unknown_rate` / `error_rate`.** Note Sherlock's UNKNOWN *context string* — the actual reason — lives only in `QueryResult.context` and **is discarded by every export format.** That is a concrete reason to run collectors **as libraries, not CLIs**: the error taxonomy you need for rot detection is only reachable in-process.
- **`zero_result_run_rate`.** Three consecutive zero-result runs across distinct selectors ⇒ presumed dead.
- **Per-host status distribution from Envoy.** A host that flips from a 200/404 mix to 100% 403 is a rot signal that costs nothing extra and is **collector-agnostic** — it catches rot in tools you haven't instrumented.

### Layer 3 — golden-transcript replay

Record raw responses for a fixed site set during a known-healthy canary run. Store as fixtures (`vcrpy`, or record with `mitmproxy` and serve back via `mitmdump --server-replay`). On **every collector image build**, replay them through the parser offline and assert verdicts.

This separates *"the platform changed"* from *"our build changed"* — a distinction you cannot make from production data alone — and it is the only test you can run at high frequency with **zero third-party traffic**.

### Making health load-bearing

- **Cadence:** Layer 1 nightly over a rotating 10% corpus slice (full sweep every 10 days) + on demand for any site an analyst disputes. Layer 2 continuous. Layer 3 per build.
- **Metrics:** `collector_canary_pass{tool,site,direction}`, `collector_found_rate{tool}`, `collector_zero_runs{tool}`, `egress_host_status{host,code}` → Prometheus → Grafana alerts.
- **Health is a field on every observation** (`assertion.collector_health`), frozen at collection time. **A negative result from a `degraded` collector renders in the UI as "not checked," never as "not found."** This is the single most important product decision in the system — it is what stops a dead collector from becoming an exculpatory or inculpatory finding about a real person.
- **Quarantine, don't auto-disable.** Maigret has `--auto-disable`; adopt the mechanism, reject the automation. Silently disabling a site shrinks the corpus and changes the meaning of every subsequent negative. Canary failure → `quarantined` → excluded from runs → surfaced on a maintenance dashboard with the diagnostic → engineer confirms fix-or-remove.
- **Record corpus size with every run.** Sherlock's exclusions fetch failing silently changes the probed set from 414 to 481 and **nothing tells you.** The run's meaning changed.

### Upstream drift is rot, and it is in your runtime path

Sherlock fetches its manifest from `data.sherlockproject.xyz` and its exclusions (regenerated daily 05:00 UTC) on **every run**. Maigret auto-updates its site DB from `raw.githubusercontent.com` every 24h. Blackbird pulls `wmn-data.json` on run. **All three put a third-party GitHub repo in your runtime path and make your results non-reproducible.**

Mirror every manifest into your own artifact store and pin: `--json <pinned-raw-url>` for Sherlock (**do not use `--local` as the "safe offline" option** — it silently sets `honor_exclusions=False`, expanding to 462 sites *including* the 52 known-false-positive targets, and it does not stop the update check anyway), `--no-autoupdate` for Maigret, `--no-update` for Blackbird. Then update the mirror deliberately, on a schedule, **gated by a canary run.** `corpus_version` becomes a recorded parameter of every observation.

**Special case — some tools self-mutate.** holehe's `check_update()` (`core.py:197`) runs `pip3 install --upgrade holehe` as a subprocess whenever PyPI's version differs from `__version__`. **No flag disables it.** It is currently inert only because PyPI hasn't moved since 2022-07-21. Patch out the call (four lines; GPL-3.0 permits a maintained fork) **and** deny PyPI at the egress proxy for runtime namespaces.

---

## 2.9 What the COP must build, because no tool in the set provides it

Ranked by value per unit of effort:

| # | Capability | Effort | Why |
|---|---|---|---|
| 1 | **Masked-contact matcher** | ~150 lines | The only real cross-tool fusion available. Asymmetric refutation keeps candidate sets from exploding. |
| 2 | **IG `username → numeric PK` (+ `fbid_v2`)** | ~1 day clean-room | The only durable join key in the set. Voids the GPL problem, the abandonment risk, the missing timeouts and the broken error taxonomy at once. **At risk — see issue #148; canary it from day one.** |
| 3 | **Avatar fetcher + perceptual hasher** | ~1 day | F3 is worth up to +18 dB and *nothing in the six produces it*. Include a stock/default-avatar blocklist or F3 fires constantly on placeholders. |
| 4 | **Bio / `external_url` link extractor** | ~half day | F4 (self-assertion) is the strongest evidence class available. toutatis returns the raw strings; nobody parses them. |
| 5 | **Handle rarity estimator** off availability ratio | ~half day | Free, and it is the difference between F1 being useful and F1 being noise. |
| 6 | **Org→person expansion on a paid SERP API** | ~2 days | The only org→person fan-out; without it the COP cannot bootstrap from a company name. Keeps the clean LinkedIn-side posture. |
| 7 | **Telegram collector on current Telethon** | ~300 lines | 64-bit IDs, real message timestamps, message IDs, NDJSON out, real FloodWait handling. |
| 8 | **Snap Map geo adapter** — *conditional on the liveness probe* | ~1 day | Re-derive lat/lon from the `@lat,lon,zoom` URL suffix; mandatory `geo_uncertainty_m` from the **true** query point. |
| 9 | **Discord snowflake → creation timestamp** | 8 lines | Offline, deterministic, zero ToS exposure. Retires DiscordOSINT as a "tool." |
| 10 | **`dfir-unfurl` integration** | ~half day | Apache-2.0, maintained, importable, JSON graph out. Repo is now `RyanDFIR/unfurl`. |

---

# PART 3 — DOCTRINE TO WRITE

Framed as engineering requirements. Each is a decision the program owner must make, with the options, a recommendation, and **the specific system control that enforces it**. If a decision has no enforcing control, it is a policy sentence and it will be violated.

---

## D1 — Authorization and case model

**Decision:** what must exist before a collection job may be enqueued, and what expires.

**Options:**
- (a) Free-form — analysts run collectors ad hoc. *Zero friction, zero defensibility, and no way to answer "who did we collect on."*
- (b) Case-bound with a soft policy note.
- (c) **Case-bound with a typed authority reference, an enumerated selector set, and a mandatory expiry, enforced at the API.**

**Recommend (c).**

**Engineering requirements:**
1. `investigation_case` carries: identifier, opening analyst, stated purpose, `authority_ref` (typed, `NOT NULL`, controlled vocabulary — *you* fill the vocabulary; the system enforces that it is non-empty and valid), approver where the authority class demands one, start date, and **mandatory `expires_at`**.
2. **Expired case ⇒ job submission rejected at the API, not warned about.** This is the highest-value control in the entire design: it converts "we should stop collecting on this person" from a policy sentence into a database constraint.
3. **Selectors are scoped to the case.** A case authorizes an enumerated selector set. Adding one is an auditable event with its own justification — not a free-text search box.
4. **Recursion-discovered selectors land `pending` and require analyst promotion.** Unbounded recursive identifier extraction is *the system authorizing its own collection*. Depth-1 auto-promotion is defensible if you decide so — make it a **policy flag**, not a code path.
5. **Deny-by-default on selector type.** A case authorized for username enumeration cannot submit a phone number without a distinct grant.
6. Enqueue happens **in the same Postgres transaction** as the authorization row. The audit trail cannot physically disagree with what ran.

---

## D2 — Method-class tiering (this is the one this tool set most demands)

**Decision:** authorization granularity — per tool, or per *what the tool actually does*?

**Options:** (a) global "OSINT tools allowed"; (b) per-tool allowlist; (c) **per collection-method class.**

**Recommend (c).** The toutatis review makes the case by itself: the same 171-line tool contains a session-authenticated profile read *and* an anonymous probe of a password-recovery endpoint. Those are different legal animals and **must not share a permission.**

| Method class | Examples from this review | Why it is its own tier |
|---|---|---|
| `passive_public_read` | Snap Map `getPlaylist`, SERP-API org expansion, snowflake decode | Reads what any client can reach |
| `third_party_api` | SERP vendor, any AI enrichment | A vendor gets a log of your selector |
| `authenticated_platform_read` | IG profile fetch with `sessionid`; Telegram user session | Collection attributable to a real account you control; burnable |
| **`recovery_probe`** | **toutatis `advanced_lookup` — POST to `users/lookup/`** | **Probes an account-recovery flow to enumerate a stranger's registration contacts. Qualitatively different from reading a profile.** |
| **`target_interactive`** | holehe-class email probes: 102 registration submissions, 13 logins, **4 password-recovery flows** | **Writes to third-party systems about the subject; the recovery probes can cause mail to be sent to the target.** |

**Engineering requirements:**
1. `collection_task.method_class` is `NOT NULL` and drives authorization.
2. `recovery_probe` and `target_interactive` sit behind a **strictly higher approval tier** than `authenticated_platform_read`, with a distinct grant and (recommended) a named approver per case.
3. **Policy-enforced flags, not analyst memory.** If doctrine says no password-recovery probes, the equivalent of holehe's `-NP` is applied by the job template, not remembered by a human. Note the sharp trade: in holehe those same four modules are the *only* ones returning `emailrecovery` and `phoneNumber` — the highest-value correlation data is produced exclusively by the highest-risk method. The system must be able to enforce **either** side of that trade.

---

## D3 — Retention, deletion, and minimization

**Decision:** how long each data class lives, and what happens to bycatch.

**Options:** (a) keep everything; (b) single global clock; (c) **per-data-class clocks with separate case and audit tracks.**

**Recommend (c).** This tool set produces at least four sharply different sensitivity classes:

| Class | Source | Recommended default | Rationale |
|---|---|---|---|
| Site-enumeration verdicts | Sherlock/Maigret/WMN | case clock | Low sensitivity, high volume, cheaply re-collected |
| Profile facts + immutable IDs | IG collector | case clock | The graph substrate |
| **Facial imagery** | avatar fetch, Snap Map media | **shorter clock than text, separate store** | Art. 9 the moment any matching capability touches it |
| **Bulk third-party message content** | Telegram collector, Discord History Tracker output | **shortest clock, restricted store, restricted role** | Sweeps in dozens of people who were never selectors |
| **Bystander media at an AOI** | Snap Map | **shortest clock, delete-on-unreviewed** | Overwhelmingly non-target; Snap Map skews young, so incidental collection of minors is a near-certainty at any populated AOI and cannot be filtered at query time |

**Engineering requirements:**
1. Retention clock is **set at ingest from the data class**, not applied later.
2. **Two separable clocks.** The **case** clock (working data) and the **audit** clock (the record that collection occurred). Deleting a case must not delete the audit trail, and the audit trail must stay meaningful after the case data is gone — which is why the audit row carries a selector **HMAC**, not a foreign key into deleted rows.
3. Purge is `tombstoned_at`, not `DELETE`, on `raw_evidence`. Dependent assertions become `evidence_unavailable` with **floored** confidence — never silently kept at full strength.
4. Per-case **legal hold** that suspends deletion.
5. **Delete-on-unreviewed** for bystander media: nemec's schema already has `reviewed` and `insert_date` and that is the right shape — adopt it, and drive the purge job off it.

---

## D4 — Confidence handling (the anti-laundering rules)

**Decision:** how uncertainty is represented, combined, and displayed.

**Options:** (a) 0–1 score; (b) qualitative labels; (c) **decibans with capped evidence families and no transitive inheritance.**

**Recommend (c).**

**Engineering requirements:**
1. **Confidence lives on the resolution edge**, never on the `Person`. Reject any schema where `person` has a `confidence` column.
2. **Family caps with the transitive-exclusion rule** (§2.4). A–C is scored from A–C's own evidence, with any item already used in A–B or B–C excluded.
3. **`synthesized` values are barred by the schema from equality joins.** CrossLinked's `{first}.{last}@company.com` will otherwise join against breach corpora and produce confident false attributions **against real, wrong human beings.** Masked values (`obfuscated_email`, `obfuscated_phone`, holehe's `masked_email`/`masked_phone`) get a distinct type, a distinct edge class, a mandatory confidence, and **never auto-merge entities.** Get this right on day one; it is nearly impossible to retrofit after analysts have built findings on top of it.
4. **No automatic Person merges.** The COP proposes; a human decides; the decision is a reversible row with an evidence closure. Second-analyst confirmation above 35 dB.
5. **Adapters must not launder tool verdicts into person-level assertions.** Sherlock's own source says the quiet part (`result.py:47-50`): the URL *"may or may not exist: this just indicates what the name would be, if it existed."* A CLAIMED verdict is evidence that **a string is registered on a platform** — not that **a person holds it.** For `torvalds`, a full sweep returns 91 hits spanning Snapchat, Duolingo, geocaching and a dozen national-language forums, all with **identical weight**.
6. **Ship the deciban defaults as `calibration: uncalibrated`.** Build a labelled set. Shipping design defaults as if measured is exactly the laundering this design exists to prevent.

---

## D5 — Audit

**Decision:** what is recorded, how tamper-evident, and whether reads are logged.

**Options:** (a) application logs; (b) an audit table; (c) **append-only hash-chained audit table, written transactionally with the enqueue, covering reads as well as collection.**

**Recommend (c).**

**Engineering requirements:**
1. One append-only row per job, `INSERT`-only, enforced by a `BEFORE UPDATE OR DELETE` trigger that raises, plus a **hash chain** (`prev_hash`/`row_hash`) so tampering is detectable even by a DB superuser. That chain is ~20 lines and is the entire difference between "our logs say" and "our logs are verifiable." Optionally ship chain heads to MinIO with object lock.
2. Fields that are easy to get wrong and must be present:
   - **`tool_image_digest`, not a version string.** Versions lie — toutatis's git master and its PyPI 1.31 are materially different code under the same name; Sherlock's repo says 0.16.1 while PyPI serves 0.16.0. Digests don't.
   - **`corpus_version` + `corpus_site_count`,** mandatory. The corpus determines the answer.
   - **`egress_ip`,** because it is a **result-affecting parameter**. Sherlock's own manifest `__comment__` fields flag namuwiki, YandexMusic and Kick as geo-dependent. A negative from a German egress and a negative from a US egress are different claims about a person.
   - **`persona_id`,** so that when a session is burned the blast-radius query is `SELECT case_id FROM collection_task WHERE persona_id = ? AND started_at > ?` — an exact enumeration, not an inference.
   - **`collector_health_at_submit`,** frozen, so a later canary failure does not retroactively repaint a good run and a degraded run stays flagged forever.
   - **`selector_value_hmac`** (key from OpenBao) alongside ciphertext, so you can answer *"have we ever collected against this person?"* — the query auditors and subject-access requests actually ask — **without the audit index becoming a plaintext roster of everyone you have ever investigated.**
3. **Reads are audited.** In a person-centric system, *viewing* a dossier is an event. The real insider-misuse case is almost never "ran an unauthorized sweep" — it is "looked up someone they knew."
4. **Provenance to the leaf.** Every rendered claim is one click from: the job, the raw artifact hash, the collector digest, the corpus version, and health at collection time.

---

## D6 — Credentials, personas, and attribution

**Decision:** how platform sessions are held, isolated, rotated, and accounted for.

**Options:** (a) config files / env vars; (b) a vault with tool-scoped secrets; (c) **a vault with persona-scoped secrets, one persona per job, egress bound to persona.**

**Recommend (c).** **The unit of isolation is a persona, not a tool** — a persona is one credential principal + one egress identity + one behavioral history.

**Engineering requirements:**
1. Layout:
   ```
   secret/collect/persona/<persona-id>/instagram     # Class 2, versioned
   secret/collect/persona/<persona-id>/telegram      # api_id/api_hash + .session blob
   secret/collect/vendor/serpapi/<key-id>            # Class 1
   secret/collect/hmac/selector-index                # audit index key
   ```
2. **One persona per job, enforced at submit.** A job template binding two personas is rejected before enqueue. This is what stops cascade.
3. **Class 2 secrets are injected as a file into task-private tmpfs, never as env vars.** Env vars surface in `docker inspect`, crash dumps, `/proc/<pid>/environ`, and are inherited by child processes — and some of these tools spawn children. **Never pass a session token as an argv parameter** — toutatis's CLI takes `-s <sessionid>` on the command line, so it leaks into shell history and process listings by default. Your reimplementation reads it from the mounted file.
4. **Concurrency 1 per persona** via a Postgres advisory lock, plus a **daily job budget per persona** that hard-fails and surfaces as case-blocking. (Session files are single-writer resources; concurrent refreshes race and corrupt them.)
5. **Rotation, honestly stated: Class 2 cannot be rotated in the API-key sense.** Rotation means standing up a *new* persona and retiring the old one — and account age is itself a trust signal on the platform side, so a cold spare is worthless the day you need it. **Maintain N+1 personas with a warm spare seeing low, regular, legitimate traffic, and rotate the binding, not the credential.**
6. **Personas are tracked consumable assets** with an owner, a controlling phone number, an acquisition date, and a burn state. Instagram demands SMS verification at signup and near-certainly at checkpoint clearance, so **each persona needs a controllable real number.** Aged, warmed accounts survive materially longer than fresh ones (widely reported operationally; **NOT VERIFIED** by controlled experiment here). Budget them as consumables, not fixtures.
7. **The API/web tier has zero read access to any credential path.** It references personas by opaque ID. Compromise of the web tier yields case data (bad), not credentials (catastrophic).
8. **Third-party disclosure allowlist.** Any host that learns your target set must be explicitly listed. This set contains two undeclared channels: SoIG ships every image URL to `tinyurl.com` over plaintext HTTP, and Sherlock's Instagram probe goes through `imginn.com`. `probed_host` on every assertion makes violations auditable after the fact.
9. **TLS verification is a non-negotiable invariant for every collector.** CrossLinked hardcodes `verify=False` with no override *and* uses a plaintext `http://` Bing endpoint, while its documented workflow routes traffic through third-party proxies. A hostile proxy can inject fabricated people into a targeting list undetectably.
10. **Decide the anti-bot posture explicitly and config-lock it.** Maigret's `search()` accepts `cloudflare_bypass`, `tor_proxy`, `i2p_proxy`; CrossLinked's mitigation is rotating proxies specifically to defeat rate limiting — which is a materially worse framing in a ToS dispute than incidental automated access. Whether the COP may evade bot detection is a doctrine decision with real exposure, and it must be a locked config value, not an adapter default someone flips.

---

## D7 — Scope of targeting

**Decision:** who may be a target, and what the system refuses to do.

**Options:** (a) analyst discretion; (b) written policy; (c) **enumerated target classes with system-enforced gates and an enumerated prohibited-capability list.**

**Recommend (c).**

**Engineering requirements:**
1. **Classify collectors as PASSIVE / SESSION-BEARING / PROHIBITED, and make the third structurally unreachable.** Wire PASSIVE directly in; gate SESSION-BEARING behind named-operator authorization with a registered persona; **the COP must be structurally incapable of mutating a target platform.** DiscordOSINT links a group-flood spammer and `undiscord` (mass message deletion) — abuse and counter-forensic capability that has no place in a collection platform. That is not a policy note; it is an architectural boundary.
2. **Public vs private venue split.** Joining an invite-only Telegram channel under a fabricated persona to harvest members and message content is a materially different act from reading a public channel, and informer distinguishes them only in code path, never in policy. Private-venue collection requires **named approval per venue**.
3. **Bystander minimization is a first-class rule, because these tools do not collect on targets — they collect on populations.** Regex-on-a-channel collects on everyone present. An AOI Snap Map sweep collects on everyone in the disc. Requirements: mandatory AOI justification recorded at task time; a documented incidental-collection-of-minors handling rule (unavoidable at any populated AOI); and **a prohibition on face-matching collected bystander frames against any other dataset** unless separately authorized.
4. **Org→person expansion is pre-attack targeting by design.** CrossLinked's entire downstream product is a credential-spray and phishing target list. Bind every org-expansion run to an engagement/authorization record with an expiry, and **refuse to execute without one.** Cheap to build now; impossible to retrofit credibly.
5. **A documented lawful basis recorded per case**, and for any target who may be an EU/UK data subject, a DPIA **before first use** — particularly for the recovery-probe class, where there is no plausible "manifestly made public" argument, since registration contacts are by definition the ones the person did *not* publish.

---

## D8 — Tool lifecycle and rot governance

**Decision:** how a collector enters service, how it is declared broken, and what happens to results collected while it was broken.

**Options:** (a) informal; (b) a wiki page; (c) **a registry with canary gates, quarantine, and health-stamped observations.**

**Recommend (c).** This is the decision most programs skip and most regret.

**Engineering requirements:**
1. **Entry gate:** no collector enters service without (i) a positive and a negative control pair, (ii) golden-transcript fixtures, (iii) an SPDX record and an integration mode (`import` only if permissive; otherwise `subprocess`), (iv) a declared selectors-in / selectors-out contract, and (v) an honest error taxonomy that distinguishes auth wall / challenge / block / 429 / genuine negative. **A collector that reports every failure as one string does not enter service.**
2. **Quarantine, never auto-disable.** Canary failure removes the site or collector from runs and raises a dashboard item with the diagnostic. An engineer confirms fix-or-remove.
3. **Health is stamped on the observation at collection time and never rewritten.** Negatives from a degraded collector render as **"not checked."**
4. **Corpus is pinned and mirrored.** No third-party GitHub repo in the runtime path. `corpus_version` is a recorded parameter of every observation.
5. **A collector that mutates itself at runtime is patched or rejected.** `pip install --upgrade` inside a collection container is disqualifying; deny the package index at the egress proxy for runtime namespaces as belt and braces.
6. **A documented sunset trigger.** Define it now: e.g. *three consecutive zero-result runs across distinct selectors + a failed positive canary ⇒ quarantine; 30 days quarantined ⇒ removal proposal with an impact list of every case whose findings depended on it.* Four of the six tools in this review would have tripped that trigger years before anyone noticed.

---

## Relevant paths

- Working tree: `<Z-ISR>\Sherlock\`
- Measured Sherlock review (source for the 414/462, 20-worker, 327-`status_code`, 303-bodyless-HEAD, 52-`urlProbe`, 41/52-excluded-FP figures, commit `9100f9d`): `<Z-ISR>\Sherlock\sherlock\CAPABILITIES.md`
- Sherlock source and manifest: `...\Sherlock\sherlock\sherlock_project\sherlock.py`, `...\sherlock_project\resources\data.json`
- Tool clones: `<wave-0-scratchpad>\{toutatis,dosint,informer,snapmap,archiver,crosslinked,crosslinked-fork,soig,holehe}`

## NOT VERIFIED — carry these as open items

- **Whether toutatis's obfuscated-hint path returns live data today.** No credible public evidence since issue #148 (2025-07-30), which *did* show a populated `obfuscated_phone` — but that reporter's two output blocks appear mislabeled, so treat it as one unreplicated community report. Assume dead until proven in a lab against a consenting, owned account.
- **Whether `getUserId` still works.** Issue #148 states it does not. This is the primitive the review recommends rebuilding first. Canary it before you build on it.
- **Snap Map endpoint liveness.** Run the `getLatestTileSet` probe above before authorizing any geo integration effort.
- **Whether the Snap share-URL `@lat,lon,zoom` suffix is a snap fix or the map-view centre at share time.** Decisive for whether a real geo adapter is worth scoping.
- **Whether CrossLinked's fork's Yahoo path returns results today.** Confirming requires live collection against a search engine; not done.
- **SpiderFoot's GPL-2.0 → MIT relicensing commit.** Verify it covers the specific files before vendoring the ontology.
- **All deciban values in §2.4** are design defaults awaiting calibration against a labelled set you build.
- **The exact current shape of Instagram's obfuscation masks** (width, whether the domain survives) — determine in a lab before calibrating the matcher.
- **Nomad / OpenBao / Envoy** are recommended on architectural fit against the specific constraints above (no-proxy-support tools, per-job secrets, per-job egress), not on a bake-off in this environment.
- **No tool was executed against any platform, account, or person during this review.** The only things run were offline validators (`docker compose config`, an AST parse, an offline retry simulation) and metadata reads against GitHub, PyPI and Docker Hub.