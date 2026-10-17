#!/usr/bin/env python3
"""Runner to elevate COR-16 through COR-31, merge metadata, and validate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add script directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import elevation_engine as ee
from elevate_cor_16_19 import COR_16_19
from elevate_cor_20_23 import COR_20_23
from elevate_cor_24_27 import COR_24_27
from elevate_cor_28_31 import COR_28_31

ALL_COR = {}
ALL_COR.update(COR_16_19)
ALL_COR.update(COR_20_23)
ALL_COR.update(COR_24_27)
ALL_COR.update(COR_28_31)

def run():
    print(f"Loaded {len(ALL_COR)} questions: {sorted(ALL_COR.keys())}")

    # 1. Update canonical markdown for all 16 questions
    for qid in sorted(ALL_COR.keys()):
        data = ALL_COR[qid]
        ee.update_canonical_question(
            qid=qid,
            concept_en=data["concept_en"],
            walkthrough_en=data["walkthrough_en"],
            structured_en=data["structured_en"],
            deep_senior_en=data["deep_senior_en"],
            short_en=data["short_en"],
        )
        print(f"Updated canonical question {qid}")

    # 2. Save Arabic metadata dictionary to scripts/elevations/data/metadata_cor_16_31.json
    metadata_dict = {qid: ALL_COR[qid]["meta_ar"] for qid in sorted(ALL_COR.keys())}
    meta_file = SCRIPT_DIR / "data" / "metadata_cor_16_31.json"
    meta_file.parent.mkdir(parents=True, exist_ok=True)
    meta_file.write_text(json.dumps(metadata_dict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved Arabic metadata to {meta_file}")

    # 3. Merge all metadata into arabic_lab_metadata.json
    ee.merge_all_metadata()

    # 4. Validate each question using ee.validate_question
    all_passed = True
    total_errors = 0
    for qid in sorted(ALL_COR.keys()):
        errs = ee.validate_question(qid)
        if errs:
            all_passed = False
            total_errors += len(errs)
            print(f"❌ {qid} failed validation with {len(errs)} errors:")
            for e in errs:
                print(f"   - {e}")
        else:
            print(f"✅ {qid} passed validation with 0 errors!")

    if not all_passed:
        print(f"\nTotal validation errors across 16 questions: {total_errors}")
        sys.exit(1)
    else:
        print(f"\n🎉 All {len(ALL_COR)} questions passed ee.validate_question with 0 errors!")

if __name__ == "__main__":
    run()
