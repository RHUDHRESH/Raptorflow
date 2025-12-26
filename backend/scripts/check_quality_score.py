import glob

import pandas as pd

from agents.vacuum_node import VacuumNode


def verify_quality_scores():
    print("--- Data Quality Score Verification ---")

    # Load ingested content (simulated from Instruction files for this track)
    instruction_files = glob.glob("Instruction/*.md")
    total_records = 0
    valid_records = 0

    required = ["tenant_id", "content"]
    schema = {"tenant_id": str, "content": str}

    for file_path in instruction_files:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                clean_line = line.strip()
                if not clean_line:
                    continue

                total_records += 1
                record = {"tenant_id": "raptor-prod-001", "content": clean_line}

                # Apply VACUUM Valid
                report = VacuumNode.validate_record(record, required, schema)
                if report.is_valid:
                    valid_records += 1

    if total_records == 0:
        print("FAIL: No records found to verify.")
        return

    quality_score = (valid_records / total_records) * 100
    print(f"Total Records: {total_records}")
    print(f"Valid Records: {valid_records}")
    print(f"Quality Score: {quality_score:.2f}%")

    if quality_score >= 95.0:
        print(f"PASS: Quality Score {quality_score:.2f}% is above 95% threshold.")
    else:
        print(f"FAIL: Quality Score {quality_score:.2f}% is below 95% threshold.")


if __name__ == "__main__":
    verify_quality_scores()
