import re

file_path = r'C:\Users\hp\OneDrive\Desktop\Raptorflow\conductor\tracks\massive_build_20251223\plan.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

phases = re.findall(r'Phase (\d+)', content)
phase_nums = [int(p) for p in phases]

expected = 1
gaps = []
for p in sorted(phase_nums):
    while expected < p:
        gaps.append(expected)
        expected += 1
    expected = p + 1

if gaps:
    print(f"Gaps found: {gaps[:20]}... (Total gaps: {len(gaps)})")
else:
    print("No gaps found up to the last number.")

print(f"Last phase found: {phase_nums[-1] if phase_nums else 'None'}")

