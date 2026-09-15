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
shared by everyone who opens the page. 700 documents today; the store holds 5,000,
and the page reads up to 1,000, so the read limit binds first — raise the
`limit(1000)` on the `leads` subscription before the next 300-lead round.

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
| `assignedDate` | string | The day the lead was handed out, `YYYY-MM-DD`. Doubles as the batch key: each distinct date is one batch, numbered in date order, and the Showing switch filters every counted figure by it. |
| `notes` | string | Free text per lead. |
| `updatedAt`, `updatedBy` | string | ISO timestamp and rep name of the last edit. |

Counters are written as absolute values, not increments, so a retried save can't
double-count a dial.

### Batches

A rep's list grows in rounds. Folding a finished round in with a fresh one turns a
hand-out into what reads as a collapse — 100% becomes 40% overnight with nobody
having done less — so the dashboard and every rep board carry a **Showing** switch:
All batches / Batch 1 / Batch 2 / … built from the distinct `assignedDate` values.
The pick drives every counted figure, the tab counts and the CSV export; searching
and the Days worked panel deliberately ignore it, since neither is about one round.
On All batches the hint line spells out each batch's own percentage, so the mixed
figure can't be misread.

## Loading a new batch of leads

1. Drop the new export in `data/`.
2. `python3 scripts/build_seed.py data/<new-file>.csv` — writes `.seedtmp/<id>.json`
   per lead plus `.seedtmp/_batches.txt`, one line per 50-write batch.
3. Back up first: `ArtifactData action:list`, collection `leads`, with `out_dir` set.
   It is the only way back if a write goes wrong.
4. Check for collisions before writing anything. A `set` on an existing id replaces
   that lead and wipes its calls, notes and status. Compare the export's
   `Contact_ID`s against the backup and refuse to write any id already there.
5. Continue the rank numbering rather than restarting it — a new export numbers
   each rep 1..N again, and two leads sharing `owner` + `rank` scramble the list
   order. Add the rep's current maximum rank to each new one.
6. Feed each batch to `ArtifactData action:"batch"` with the artifact URL above.
   Every entry should come back at **version 1**; any higher version means that
   write landed on an existing lead.
7. Verify: re-list the collection and diff the pre-write ids against the backup.
   Expect zero missing, zero changed, and exactly the new ids added.

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
