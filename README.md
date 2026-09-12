# Twin Home Buyer — Live Lead Tracker

A live acquisitions tracker for the 400 leads assigned 09.11.26, split 100 each
across Era, Barbie, David, and Diego. Built from `lead-tracker-spec-for-jonathan.docx`.

**Live tracker:** https://claude.ai/code/artifact/0cf8866b-19ab-4283-8979-d9a5c6bb0bfa
**User handbook:** https://claude.ai/code/artifact/6a9471fd-92ef-4959-abfe-2e990b63da69

## What's here

| Path | What it is |
| --- | --- |
| `index.html` | The whole app — one page, no build step. This is what gets published. |
| `data/400_Leads_assigned_2026-09-11.csv` | The assignment export from REI BlackBook, as received. |
| `scripts/build_seed.py` | Turns that CSV into one JSON document per lead for loading into the database. |
| `guide.html` | The plain-language handbook for reps and ops. Published as its own artifact, separate from the tracker. |

## How it's stored

Every lead is one document at `leads/<REI Contact_ID>` in the artifact's database,
shared by everyone who opens the page. 400 documents today; the store holds 5,000,
so roughly eleven more assignment rounds fit before old rounds need archiving.

| Field | Type | Notes |
| --- | --- | --- |
| `owner`, `ownerId` | string | The assigned rep and their REI BlackBook user id. |
| `rank` | number | Priority order within that rep's list. |
| `name`, `phone` | string | Verbatim from BlackBook so reps can cross-reference. Empty name = the export's `(no name)`. |
| `bucket` | string | `HOT` or `Distress`. |
| `reiLink` | string | Deep link to the contact in REI BlackBook. |
| `calls` | number | Cumulative dial attempts. |
| `answered`, `vmLeft`, `noVm`, `vmFull` | number | Cumulative outcomes; they sum to `calls`. `vmFull` is a blocked attempt — the rep wanted to leave a voicemail and the box was full — kept apart from `noVm`, which is a choice. |
| `leadStatus` | `""` \| `wrongNumber` \| `invalid` \| `optedOut` \| `doNotCall` \| `notOwner` \| `outOfBuyBox` \| `skipped` | Empty means working. `wrongNumber` and `invalid` park the lead as needing a new number; the other three close it. A parked lead leaves the call list and every rate denominator, and is reported separately so a file of dud numbers never reads as a rep not calling. `outOfBuyBox` is the exception: it leaves the call list but stays in contacted and in the rates, because the contact really happened and the rep qualified it correctly. `skipped` is deferred rather than finished: it leaves the call list but stays in the rep's own count, so skipping can never flatter a rep's numbers. |
| `skipReason` | string | Why a lead was skipped. Required — the status will not apply without one — and cleared when the lead goes back on the call list. |
| `textSent`, `emailSent` | boolean | Outreach checkboxes. |
| `responded` | `no` \| `call` \| `text` \| `email` \| `both` | Which channel the lead came back on. `call` is a callback or an engaged pickup; `both` means text and email, the value the field carried before `call` existed. |
| `notes` | string | Free text per lead. |
| `updatedAt`, `updatedBy` | string | ISO timestamp and rep name of the last edit. |

Counters are written as absolute values, not increments, so a retried save can't
double-count a dial.

## Loading a new batch of leads

1. Drop the new export in `data/`.
2. `python3 scripts/build_seed.py data/<new-file>.csv` — writes `.seedtmp/<id>.json`
   per lead plus `.seedtmp/_batches.txt`, one line per 50-write batch.
3. Feed each line to the Artifact `write_db` tool with `db_op: "batch"`, passing the
   artifact URL above. Re-seeding a lead that already exists resets its counters,
   so only seed ids that are actually new.

Reps can also paste names straight into their own tab ("Add leads to your list"),
which is the faster path for a handful of leads.

## Access

The page is organization-internal — every viewer is a signed-in member of the
Twin Home Buyer workspace. Inside it, who sees which board follows one rule
(`canOpen` in `index.html`):

| Logged in as | Boards | CSV export |
| --- | --- | --- |
| A rep | Dashboard + their own board only; the other three tabs are not rendered | Their own 100 leads |
| Cherry / ops | Dashboard + all four boards, read-only | All 400 leads |
| Nobody yet | Dashboard only | Disabled |

The dashboard rollup and the name search still span all 400 leads for everyone,
since the point of the search is to find a lead without knowing whose list it is
on. A lead that belongs to someone else shows its status but offers no way to
open it.

This is a **soft gate**, not authentication: anyone who can open the page can
pick a different name from the dropdown and get that rep's board. It stops the
accidental cross-editing the shared spreadsheet allowed, which is the problem
the spec set out to solve, but it does not stop someone who means to. Real
per-rep locks need per-rep accounts — the open question flagged for Cherry in
§6 of the spec.
