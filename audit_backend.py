import os
import re
import json
from typing import List, Dict, Any

# Configuration
SEARCH_DIR = "backend"
OUTPUT_FILE = "audit_report.json"

# Patterns to search for
PATTERNS = {
    "MOCK_DATA": r"(?i)(mock|dummy|fake|placeholder|stub)",
    "TODO_FIXME": r"(?i)(TODO|FIXME|HACK|XXX|REVIEW)",
    "HARDCODED_RETURN": r"return\s*(\[.*\]|\{.*\})\s*$",  # Suspicious simple returns
    "PRINT_STMT": r"print\(",
    "BARE_EXCEPT": r"except\s*:|except\s+Exception\s*:",
    "SWALLOWED_ERROR": r"except.*:\s*pass",
    "POTENTIAL_SECRET": r"(?i)(api_key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]"
}

IGNORE_DIRS = {
    "__pycache__", ".venv", "venv", ".git", ".idea", ".vscode", "node_modules", 
    "backend-clean", # User mentioned this is messy/old, but maybe we should scan it to know? 
                     # The prompt said "stress test the entire fcking thing", so we SCAN IT but note it.
                     # Actually, the user goal is production readiness of the ACTIVE backend. 
                     # backend-clean might be confusing. I'll scan it but tag it.
                     # For now, let's focus on the active backend to not get noise. 
                     # But wait, user said "verify every single file". I will scan everything but separate by folder.
}
IGNORE_DIRS = {"__pycache__", ".venv", "venv", ".git", ".idea", ".vscode", "node_modules"}

IGNORE_FILES = {"audit_backend.py", "production_readiness_check.py"}

def scan_file(filepath: str) -> List[Dict[str, Any]]:
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            line_num = i + 1
            content = line.strip()
            
            # Check each pattern
            for category, pattern in PATTERNS.items():
                if re.search(pattern, content):
                    # Filter out common false positives
                    if category == "PRINT_STMT" and "logger" in content: continue # accidental match? no, print( is specific.
                    
                    findings.append({
                        "category": category,
                        "line": line_num,
                        "content": content,
                        "file": filepath
                    })
                    
    except UnicodeDecodeError:
        pass # Skip binary files
    except Exception as e:
        print(f"Error scanning {filepath}: {e}")
        
    return findings

def main():
    print(f"Starting audit of {SEARCH_DIR}...")
    all_findings = []
    
    file_count = 0
    
    for root, dirs, files in os.walk(SEARCH_DIR):
        # Modify dirs in-place to skip ignored
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file in IGNORE_FILES: continue
            if not file.endswith(('.py', '.sql', '.md', '.txt')): continue # Focus on code/config
            
            filepath = os.path.join(root, file)
            file_findings = scan_file(filepath)
            all_findings.extend(file_findings)
            file_count += 1

    # Analysis
    summary = {
        "files_scanned": file_count,
        "total_issues": len(all_findings),
        "breakdown": {},
        "findings": all_findings
    }
    
    for f in all_findings:
        cat = f["category"]
        summary["breakdown"][cat] = summary["breakdown"].get(cat, 0) + 1
        
    print(f"Scan complete. Scanned {file_count} files. Found {len(all_findings)} issues.")
    print("Breakdown:")
    for cat, count in summary["breakdown"].items():
        print(f"  {cat}: {count}")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
