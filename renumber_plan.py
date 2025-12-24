import os
import re

file_path = r"C:\Users\hp\OneDrive\Desktop\Raptorflow\conductor\tracks\massive_build_20251223\plan.md"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
phase_counter = 1

for line in lines:
    # Match "- [ ] Phase XXXX: "
    match = re.match(r"^(\s*-\s*\[\s*\]\s*Phase\s+)(\d+)(:.*)$", line)
    if match:
        prefix = match.group(1)
        suffix = match.group(3)
        new_phase_str = f"{phase_counter:04d}"
        new_lines.append(f"{prefix}{new_phase_str}{suffix}\n")
        phase_counter += 1
    else:
        # Clean up encoding artifacts if any
        line = line.replace("", "-")
        new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Renumbering complete. Total phases: {phase_counter - 1}")
