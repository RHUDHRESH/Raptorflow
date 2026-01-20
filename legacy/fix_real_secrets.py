#!/usr/bin/env python3
"""
Fix only REAL hardcoded secrets (not variable names)
Targets actual API keys, not just words like "token" or "key"
"""

import os
import re
from typing import List, Tuple


class RealSecretFixer:
    def __init__(self):
        self.backend_path = "c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\backend"
        self.fixed_files = []

    def find_real_hardcoded_secrets(self, file_path: str) -> List[Tuple[int, str, str]]:
        """Find only REAL hardcoded secrets in a file"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Skip comments and imports
                if (
                    line.strip().startswith("#")
                    or line.strip().startswith("import")
                    or line.strip().startswith("from")
                ):
                    continue

                # Pattern 1: "api_key": "sk-1234567890abcdef" (starts with sk-)
                api_key_pattern = r'["\']([a-zA-Z0-9_-]+)["\']\s*:\s*["\'](sk-[a-zA-Z0-9_-]{20,})["\']'
                matches = re.finditer(api_key_pattern, line)
                for match in matches:
                    key_name = match.group(1)
                    api_key = match.group(2)
                    env_var = self.generate_env_var_name(key_name)
                    issues.append((line_num, f"{key_name}: {api_key}", env_var))

                # Pattern 2: "api_key": "AIzaSy..." (Google API key pattern)
                google_api_pattern = r'["\']([a-zA-Z0-9_-]+)["\']\s*:\s*["\'](AIzaSy[A-Za-z0-9_-]{20,})["\']'
                matches = re.finditer(google_api_pattern, line)
                for match in matches:
                    key_name = match.group(1)
                    api_key = match.group(2)
                    env_var = self.generate_env_var_name(key_name)
                    issues.append((line_num, f"{key_name}: {api_key}", env_var))

                # Pattern 3: variable = "sk-1234567890abcdef"
                var_api_pattern = (
                    r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*["\'](sk-[a-zA-Z0-9_-]{20,})["\']'
                )
                matches = re.finditer(var_api_pattern, line)
                for match in matches:
                    var_name = match.group(1)
                    api_key = match.group(2)
                    if not self.is_common_var_name(var_name):
                        env_var = self.generate_env_var_name(var_name)
                        issues.append((line_num, f"{var_name} = {api_key}", env_var))

                # Pattern 4: variable = "AIzaSy..."
                var_google_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*["\'](AIzaSy[A-Za-z0-9_-]{20,})["\']'
                matches = re.finditer(var_google_pattern, line)
                for match in matches:
                    var_name = match.group(1)
                    api_key = match.group(2)
                    if not self.is_common_var_name(var_name):
                        env_var = self.generate_env_var_name(var_name)
                        issues.append((line_num, f"{var_name} = {api_key}", env_var))

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return issues

    def is_common_var_name(self, var_name: str) -> bool:
        """Check if variable name is commonly used for non-secret values"""
        common_vars = [
            "id",
            "name",
            "type",
            "value",
            "data",
            "content",
            "text",
            "url",
            "path",
            "file",
            "config",
            "settings",
            "options",
            "params",
            "result",
            "response",
            "request",
            "error",
            "message",
            "status",
            "user",
            "workspace",
            "table",
            "column",
            "field",
            "index",
            "token",
            "key",
            "secret",
            "password",  # These are variable names, not actual secrets
        ]

        return var_name.lower() in common_vars

    def generate_env_var_name(self, key_name: str) -> str:
        """Generate environment variable name from key name"""
        # Convert to uppercase and replace common patterns
        env_name = key_name.upper()

        # Common mappings
        mappings = {
            "API_KEY": "API_KEY",
            "SECRET": "SECRET",
            "TOKEN": "TOKEN",
            "PASSWORD": "PASSWORD",
            "GEMINI_API_KEY": "GEMINI_API_KEY",
            "GOOGLE_TRANSLATE_API_KEY": "GOOGLE_TRANSLATE_API_KEY",
            "SUPABASE_KEY": "SUPABASE_ANON_KEY",
            "SUPABASE_URL": "SUPABASE_URL",
        }

        return mappings.get(env_name, env_name)

    def fix_file(self, file_path: str) -> bool:
        """Fix only real hardcoded secrets in a file"""
        issues = self.find_real_hardcoded_secrets(file_path)

        if not issues:
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix each issue
            for line_num, issue_desc, env_var in issues:
                # Pattern 1: "key": "sk-..."
                content = re.sub(
                    r'(["\'][a-zA-Z0-9_-]+["\']\s*:\s*["\']sk-[a-zA-Z0-9_-]{20,}["\'])',
                    lambda m: self.replace_with_env_var(m.group(), env_var),
                    content,
                )

                # Pattern 2: "key": "AIzaSy..."
                content = re.sub(
                    r'(["\'][a-zA-Z0-9_-]+["\']\s*:\s*["\']AIzaSy[A-Za-z0-9_-]{20,}["\'])',
                    lambda m: self.replace_with_env_var(m.group(), env_var),
                    content,
                )

                # Pattern 3: variable = "sk-..."
                content = re.sub(
                    r'([a-zA-Z_][a-zA-Z0-9_]*\s*=\s*["\']sk-[a-zA-Z0-9_-]{20,}["\'])',
                    lambda m: self.replace_var_assignment(m.group(), env_var),
                    content,
                )

                # Pattern 4: variable = "AIzaSy..."
                content = re.sub(
                    r'([a-zA-Z_][a-zA-Z0-9_]*\s*=\s*["\']AIzaSy[A-Za-z0-9_-]{20,}["\'])',
                    lambda m: self.replace_var_assignment(m.group(), env_var),
                    content,
                )

            # Only write if content changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.fixed_files.append(file_path)
                print(f"Fixed {len(issues)} real API keys in {file_path}")
                return True

        except Exception as e:
            print(f"Error fixing {file_path}: {e}")

        return False

    def replace_with_env_var(self, match: str, env_var: str) -> str:
        """Replace hardcoded value with environment variable"""
        # Extract the key name and keep the structure
        parts = match.split(":")
        if len(parts) == 2:
            key_part = parts[0].strip()
            return f"{key_part}: os.getenv('{env_var}')"
        return match

    def replace_var_assignment(self, match: str, env_var: str) -> str:
        """Replace variable assignment with environment variable"""
        parts = match.split("=")
        if len(parts) == 2:
            var_part = parts[0].strip()
            return f"{var_part} = os.getenv('{env_var}')"
        return match

    def add_os_import(self, file_path: str) -> bool:
        """Add os import if needed"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if os is already imported
            if "import os" in content or "from os import" in content:
                return False

            # Find the best place to add the import
            lines = content.split("\n")
            import_index = -1

            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith(
                    "from "
                ):
                    import_index = i
                elif line.strip() == "" and import_index >= 0:
                    break

            if import_index >= 0:
                lines.insert(import_index + 1, "import os")
            else:
                lines.insert(0, "import os")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            return True

        except Exception as e:
            print(f"Error adding os import to {file_path}: {e}")
            return False

    def scan_and_fix_real_secrets(self):
        """Scan and fix only real hardcoded secrets"""
        print("🔧 Scanning for REAL hardcoded API keys...")

        fixed_count = 0
        total_issues = 0

        for root, dirs, files in os.walk(self.backend_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)

                    # Check if file has real issues
                    issues = self.find_real_hardcoded_secrets(file_path)
                    if issues:
                        total_issues += len(issues)

                        # Add os import if needed
                        self.add_os_import(file_path)

                        # Fix the file
                        if self.fix_file(file_path):
                            fixed_count += 1

        print(f"\n📊 SUMMARY:")
        print(f"Files fixed: {fixed_count}")
        print(f"Real API keys found: {total_issues}")

        return fixed_count > 0


if __name__ == "__main__":
    fixer = RealSecretFixer()

    print("🔍 Fixing REAL hardcoded API keys in Raptorflow backend...")
    print("=" * 60)

    # Scan and fix real secrets
    files_fixed = fixer.scan_and_fix_real_secrets()

    if files_fixed > 0:
        print(f"\n✅ SUCCESS: Fixed real API keys in {files_fixed} files")
    else:
        print("\n✅ No real API keys found - all good!")
