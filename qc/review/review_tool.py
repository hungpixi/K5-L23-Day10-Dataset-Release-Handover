#!/usr/bin/env python3
"""Interactive and validation helper for Phase 2 Human Visual Review.

Reads candidates.json, assists reviewer in logging visual findings, validates note length >= 20,
and produces clean review_log.csv conforming to check_handover criteria (H3).

Usage:
  python qc/review/review_tool.py --candidates <candidates.json> --out <review_log.csv>
  python qc/review/review_tool.py --validate-only --out <review_log.csv>
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def load_candidates(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    doc = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(doc, dict):
        return doc.get("candidates", [])
    if isinstance(doc, list):
        return doc
    return []


def load_existing_log(path: Path) -> dict[tuple[str, str], dict]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return {(row.get("type", "").strip(), row.get("image", "").strip()): row for row in reader}


def save_log(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "type", "verdict", "note"])
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "image": row.get("image", "").strip(),
                "type": row.get("type", "").strip(),
                "verdict": row.get("verdict", "").strip(),
                "note": row.get("note", "").strip(),
            })


def main() -> int:
    ap = argparse.ArgumentParser(description="P2 Visual Review Assistant Tool")
    ap.add_argument("--candidates", help="Path to candidates.json")
    ap.add_argument("--out", required=True, help="Path to output review_log.csv")
    ap.add_argument("--validate-only", action="store_true", help="Validate existing review_log.csv against rubric")
    args = ap.parse_args()

    out_path = Path(args.out)

    if args.validate_only:
        if not out_path.is_file():
            print(f"Error: {out_path} does not exist.")
            return 1
        with out_path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        print(f"Checking {out_path}: {len(rows)} entries found.")
        notes = [(r.get("note") or "").strip() for r in rows]
        short_notes = [n for n in notes if len(n) < 20]
        if short_notes:
            print(f"[FAIL] Found {len(short_notes)} notes with length < 20 chars:")
            for sn in short_notes[:3]:
                print(f"  - '{sn}' ({len(sn)} chars)")
            return 1
        uniq_ratio = len(set(notes)) / max(1, len(notes))
        if uniq_ratio < 0.7:
            print(f"[FAIL] Note diversity ratio {uniq_ratio:.1%} is below 70% threshold (too many duplicate notes).")
            return 1
        bad_verdicts = [r.get("verdict") for r in rows if r.get("verdict") not in ("confirmed", "rejected")]
        if bad_verdicts:
            print(f"[FAIL] Invalid verdicts found: {bad_verdicts[:3]}. Allowed: confirmed, rejected.")
            return 1
        print(f"[PASS] All {len(rows)} rows strictly adhere to H3 review criteria!")
        return 0

    if not args.candidates:
        print("Error: --candidates argument is required for interactive review mode.")
        return 1

    cand_path = Path(args.candidates)
    cands = load_candidates(cand_path)
    print(f"Loaded {len(cands)} candidates from {cand_path}.")
    existing = load_existing_log(out_path)
    print(f"Existing review entries in {out_path}: {len(existing)}")

    rows = list(existing.values())
    for idx, c in enumerate(cands, 1):
        key = (c.get("type", "").strip(), c.get("image", "").strip())
        if key in existing:
            continue
        print(f"\n[{idx}/{len(cands)}] Candidate: {c.get('image')} | Type: {c.get('type')}")
        if "details" in c:
            print(f"  Details: {c['details']}")
        while True:
            v_input = input("  Verdict [c=confirmed / r=rejected / s=skip / q=quit]: ").strip().lower()
            if v_input in ("q", "quit"):
                save_log(out_path, rows)
                print(f"Saved {len(rows)} entries. Exiting.")
                return 0
            if v_input in ("s", "skip"):
                break
            if v_input in ("c", "confirmed"):
                verdict = "confirmed"
            elif v_input in ("r", "rejected"):
                verdict = "rejected"
            else:
                print("  Invalid choice. Please enter 'c', 'r', 's', or 'q'.")
                continue

            note = input("  Note (what human eyes see, >= 20 chars): ").strip()
            if len(note) < 20:
                print(f"  Note is too short ({len(note)} chars). Must be >= 20 chars.")
                continue

            rows.append({
                "image": c.get("image", "").strip(),
                "type": c.get("type", "").strip(),
                "verdict": verdict,
                "note": note,
            })
            save_log(out_path, rows)
            print(f"  Recorded ({verdict}).")
            break

    save_log(out_path, rows)
    print(f"\nDone! Total review rows saved: {len(rows)} -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

