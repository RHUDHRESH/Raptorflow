import json
from collections import Counter


def analyze():
    try:
        with open("audit_report.json", "r") as f:
            data = json.load(f)

        findings = data.get("findings", [])

        # Group by file
        files_score = Counter()
        files_details = {}

        for f in findings:
            fname = f["file"]
            if "tests" in fname or "test_" in fname:
                continue

            cat = f["category"]

            # Weighted score?
            weight = 1
            if cat == "POTENTIAL_SECRET":
                weight = 10
            if cat == "MOCK_DATA":
                weight = 5
            if cat == "TODO_FIXME":
                weight = 3

            files_score[fname] += weight

            if fname not in files_details:
                files_details[fname] = {"categories": Counter()}
            files_details[fname]["categories"][cat] += 1

        print("TOP 20 OFFENDERS (Weighted by severity):")
        print("-" * 60)
        for fname, score in files_score.most_common(20):
            print(f"{score} pts - {fname}")
            details = files_details[fname]["categories"]
            for cat, count in details.items():
                print(f"    {cat}: {count}")
            print()

        print("\nPOTENTIAL SECRETS FOUND:")
        print("-" * 60)
        secrets = [f for f in findings if f["category"] == "POTENTIAL_SECRET"]
        for s in secrets:
            print(f"{s['file']}:{s['line']} - {s['content'].strip()[:100]}...")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    analyze()
