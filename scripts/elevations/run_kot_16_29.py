#!/usr/bin/env python3
"""Runner script to elevate KOT-16 through KOT-29, merge metadata, and validate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root and elevations to sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.elevations import elevation_engine as ee
from scripts.elevations.elevate_kot_16_22 import KOT_16_TO_22
from scripts.elevations.elevate_kot_23_29 import KOT_23_TO_29

ALL_KOT = {**KOT_16_TO_22, **KOT_23_TO_29}

def main():
    print(f"Starting elevation for {len(ALL_KOT)} questions: {sorted(ALL_KOT.keys())}")
    
    # 1. Update Canonical Questions in Markdown
    for qid, data in sorted(ALL_KOT.items()):
        print(f"Updating canonical Markdown for {qid}...")
        ee.update_canonical_question(
            qid=qid,
            concept_en=data["concept_en"],
            walkthrough_en=data["walkthrough_en"],
            structured_en=data["structured_en"],
            deep_senior_en=data["deep_senior_en"],
            short_en=data["short_en"],
        )
    print("All 14 canonical Markdown files updated successfully.")

    # 2. Save Arabic metadata dictionary to metadata_kot_16_29.json
    metadata_out = {qid: data["arabic"] for qid, data in sorted(ALL_KOT.items())}
    target_json = ee.DATA_DIR / "metadata_kot_16_29.json"
    target_json.write_text(json.dumps(metadata_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved Arabic metadata dictionary to {target_json}")

    # 3. Merge metadata
    print("Merging all metadata into arabic_lab_metadata.json...")
    ee.merge_all_metadata()

    # 4. Validate each question
    print("Validating all 14 questions with ee.validate_question...")
    total_errors = 0
    for i in range(16, 30):
        qid = f"KOT-{i:02d}"
        errors = ee.validate_question(qid)
        if errors:
            print(f"❌ {qid} FAILED with {len(errors)} error(s):")
            for e in errors:
                print(f"   - {e}")
            total_errors += len(errors)
        else:
            print(f"✅ {qid} passed validation with 0 errors.")

    if total_errors > 0:
        print(f"\nElevation FAILED with {total_errors} total errors across KOT-16 through KOT-29.", file=sys.stderr)
        sys.exit(1)

    print("\n🎉 All 14 questions (KOT-16 to KOT-29) passed elevation validation with 0 errors!")

if __name__ == "__main__":
    main()
