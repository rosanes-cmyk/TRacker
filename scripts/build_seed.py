#!/usr/bin/env python3
"""Turn the assigned-leads CSV into one JSON document per lead.

Each file is written to .seedtmp/<Contact_ID>.json and loaded into the
artifact's database as leads/<Contact_ID>. Re-run this whenever a new
batch of leads is assigned, then seed with the Artifact write_db batch op.

    python3 scripts/build_seed.py data/400_Leads_assigned_2026-09-11.csv
"""
import csv, json, os, re, sys

SEED_DIR = ".seedtmp"
ID_RE = re.compile(r"[A-Za-z0-9_\-.~:@+]{1,200}$")


def main(src):
    os.makedirs(SEED_DIR, exist_ok=True)
    ids = []
    with open(src, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            contact_id = row["Contact_ID"].strip()
            if not ID_RE.fullmatch(contact_id):
                raise SystemExit("Contact_ID %r is not a valid document id" % contact_id)
            # REI BlackBook exports carry stray tabs inside some names, and
            # "(no name)" where the contact has none. Names otherwise stay
            # verbatim so reps can cross-reference them in BlackBook.
            name = re.sub(r"\s+", " ", row["Name"]).strip()
            if name == "(no name)":
                name = ""
            doc = {
                "owner": row["Owner"].strip(),
                "ownerId": row["Owner_ID"].strip(),
                "rank": int(row["Rank"]),
                "name": name,
                "phone": row["Phone"].strip(),
                "bucket": row["Bucket"].strip(),
                "reiLink": row["REI_Link"].strip(),
                "task": row["Task"].strip(),
                "assignedDate": row["Assigned_Date"].strip(),
                "calls": 0, "answered": 0, "vmLeft": 0, "noVm": 0,
                "textSent": False, "emailSent": False,
                "responded": "no", "notes": "",
                "updatedAt": "", "updatedBy": "",
            }
            with open(os.path.join(SEED_DIR, contact_id + ".json"), "w", encoding="utf-8") as out:
                json.dump(doc, out, ensure_ascii=False)
            ids.append(contact_id)

    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate Contact_IDs in %s" % src)

    # Batch payloads, 50 writes per call (the write_db batch ceiling).
    with open(os.path.join(SEED_DIR, "_batches.txt"), "w", encoding="utf-8") as out:
        for i in range(0, len(ids), 50):
            entries = [
                {"op": "set", "collection": "leads", "doc_id": c,
                 "file_path": "%s/%s.json" % (SEED_DIR, c)}
                for c in ids[i:i + 50]
            ]
            out.write(json.dumps(entries, separators=(",", ":")) + "\n")

    print("%d leads -> %s/ (%d batches)" % (len(ids), SEED_DIR, (len(ids) + 49) // 50))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/400_Leads_assigned_2026-09-11.csv")
