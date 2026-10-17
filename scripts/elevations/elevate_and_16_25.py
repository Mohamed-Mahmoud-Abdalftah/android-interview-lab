#!/usr/bin/env python3
"""Elevate AND-16 through AND-25 for bilingual parity and senior spoken answers."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.elevations import elevation_engine as ee
from scripts.elevations.data_and_16_20 import CANONICAL_DATA as CD_1, ARABIC_METADATA as AM_1
from scripts.elevations.data_and_21_25 import CANONICAL_DATA as CD_2, ARABIC_METADATA as AM_2

ALL_CANONICAL = {**CD_1, **CD_2}
ALL_ARABIC = {**AM_1, **AM_2}

def main():
    print("=== Elevating AND-16 through AND-25 ===")
    
    # 1. Update canonical question markdown files
    for qid, cdata in ALL_CANONICAL.items():
        print(f"Updating canonical question: {qid}...")
        ee.update_canonical_question(
            qid=qid,
            concept_en=cdata["concept_en"],
            walkthrough_en=cdata["walkthrough_en"],
            structured_en=cdata["structured_en"],
            deep_senior_en=cdata["deep_senior_en"],
            short_en=cdata["short_en"],
        )

    # 2. Save metadata to metadata_and_16_25.json
    out_meta_path = ee.DATA_DIR / "metadata_and_16_25.json"
    print(f"Saving Arabic metadata to {out_meta_path}...")
    out_meta_path.write_text(
        json.dumps(ALL_ARABIC, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    # 3. Merge metadata
    print("Merging metadata into arabic_lab_metadata.json...")
    ee.merge_all_metadata()

    # 4. Validate each question
    print("\n=== Validating AND-16 through AND-25 ===")
    total_errors = 0
    for i in range(16, 26):
        qid = f"AND-{i:02d}"
        errs = ee.validate_question(qid)
        if errs:
            print(f"❌ {qid}: {len(errs)} errors")
            for e in errs:
                print(f"    - {e}")
            total_errors += len(errs)
        else:
            print(f"✅ {qid}: 0 errors (PASSED)")

    if total_errors > 0:
        print(f"\nTotal validation errors: {total_errors}")
        sys.exit(1)
    else:
        print("\nAll 10 questions passed validation with 0 errors!")

if __name__ == "__main__":
    main()
