# Twin Home Buyer — Live Lead Tracker

A live acquisitions tracker for the 400 leads assigned 09.11.26, split 100 each
across Era, Barbie, David, and Diego. Built from `lead-tracker-spec-for-jonathan.docx`.

**Live artifact:** https://claude.ai/code/artifact/0cf8866b-19ab-4283-8979-d9a5c6bb0bfa

## What's here

| Path | What it is |
| --- | --- |
| `index.html` | The whole app — one page, no build step. This is what gets published. |
| `data/400_Leads_assigned_2026-09-11.csv` | The assignment export from REI BlackBook, as received. |
| `scripts/build_seed.py` | Turns that CSV into one JSON document per lead for loading into the database. |

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
| `answered`, `vmLeft`, `noVm` | number | Cumulative outcomes; they sum to `calls`. |
| `textSent`, `emailSent` | boolean | Outreach checkboxes. |
| `responded` | `no` \| `text` \| `email` \| `both` | Response channel. |
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
Twin Home Buyer workspace. Inside it, the rep gate is a **soft gate**: you pick
your name, and the page then makes every other rep's list read-only for you. It
stops the accidental edits that the shared spreadsheet allowed, which is the
problem the spec set out to solve. It is not authentication: anyone who can open
the page can pick a different name and edit that rep's list. Real per-rep edit
locks need per-rep accounts, which is the open question flagged for Cherry in
§6 of the spec.
