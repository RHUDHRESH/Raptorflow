#!/usr/bin/env python3
"""
Fix hardcoded secrets in the codebase
Replaces hardcoded API keys, tokens, and secrets with environment variables
"""

import os
import re
from typing import List, Tuple


class SecretFixer:
    def __init__(self):
        self.backend_path = "c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\backend"
        self.fixed_files = []
        self.issues_found = []

    def find_hardcoded_secrets(self, file_path: str) -> List[Tuple[int, str, str]]:
        """Find hardcoded secrets in a file"""
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

                # Pattern 1: "key": "value" where value looks like an API key
                key_pattern = (
                    r'["\']([a-zA-Z0-9_-]+)["\']\s*:\s*["\']([a-zA-Z0-9_-]{15,})["\']'
                )
                matches = re.finditer(key_pattern, line)
                for match in matches:
                    key_name = match.group(1)
                    value = match.group(2)

                    # Check if it looks like a real API key (not a placeholder)
                    if self.is_real_api_key(value):
                        env_var = self.generate_env_var_name(key_name)
                        issues.append((line_num, f"{key_name}: {value}", env_var))

                # Pattern 2: variable = "value" where value looks like an API key
                var_pattern = (
                    r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*["\']([a-zA-Z0-9_-]{15,})["\']'
                )
                matches = re.finditer(var_pattern, line)
                for match in matches:
                    var_name = match.group(1)
                    value = match.group(2)

                    # Skip common variable names that aren't secrets
                    if self.is_real_api_key(value) and not self.is_common_var_name(
                        var_name
                    ):
                        env_var = self.generate_env_var_name(var_name)
                        issues.append((line_num, f"{var_name} = {value}", env_var))

                # Pattern 3: os.getenv("key", "default_value") where default looks like API key
                getenv_pattern = (
                    r'os\.getenv\(["\']([^"\']+)["\'],\s*["\']([a-zA-Z0-9_-]{15,})["\']'
                )
                matches = re.finditer(getenv_pattern, line)
                for match in matches:
                    env_name = match.group(1)
                    default_value = match.group(2)

                    if self.is_real_api_key(default_value):
                        issues.append(
                            (
                                line_num,
                                f"os.getenv({env_name}, {default_value})",
                                env_name,
                            )
                        )

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return issues

    def is_real_api_key(self, value: str) -> bool:
        """Check if a value looks like a real API key"""
        # Skip placeholder values
        placeholders = [
            "your-",
            "YOUR-",
            "example-",
            "test-",
            "demo-",
            "sample-",
            "api_key",
            "secret",
            "token",
            "password",
            "key",
            "xxx",
            "yyy",
            "zzz",
            "abc",
            "def",
            "123",
            "456",
            "your-gemini-api-key",
            "your-google-translate-api-key",
        ]

        value_lower = value.lower()
        for placeholder in placeholders:
            if placeholder in value_lower:
                return False

        # Check if it looks like a real key (mix of letters, numbers, underscores, dashes)
        if len(value) < 15:
            return False

        # Should contain at least some numbers or special characters
        has_numbers = any(c.isdigit() for c in value)
        has_special = any(c in "-_" for c in value)

        return has_numbers or has_special

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
        """Fix hardcoded secrets in a file"""
        issues = self.find_hardcoded_secrets(file_path)

        if not issues:
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix each issue
            for line_num, issue_desc, env_var in issues:
                # Pattern 1: "key": "value"
                content = re.sub(
                    r'(["\'][a-zA-Z0-9_-]+["\']\s*:\s*["\'][a-zA-Z0-9_-]{15,}["\'])',
                    lambda m: self.replace_with_env_var(m.group(), env_var),
                    content,
                )

                # Pattern 2: variable = "value"
                content = re.sub(
                    r'([a-zA-Z_][a-zA-Z0-9_]*\s*=\s*["\'][a-zA-Z0-9_-]{15,}["\'])',
                    lambda m: self.replace_var_assignment(m.group(), env_var),
                    content,
                )

                # Pattern 3: os.getenv("key", "default_value")
                content = re.sub(
                    r'os\.getenv\(["\'][^"\']+["\'],\s*["\'][a-zA-Z0-9_-]{15,}["\']\)',
                    lambda m: self.replace_getenv_default(m.group(), env_var),
                    content,
                )

            # Only write if content changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.fixed_files.append(file_path)
                self.issues_found.extend(issues)
                print(f"Fixed {len(issues)} issues in {file_path}")
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

    def replace_getenv_default(self, match: str, env_var: str) -> str:
        """Replace os.getenv default with just os.getenv"""
        # Extract the environment variable name
        env_match = re.search(r'os\.getenv\(["\']([^"\']+)["\']', match)
        if env_match:
            env_name = env_match.group(1)
            return f"os.getenv('{env_name}')"
        return match

    def add_os_import(self, file_path: str) -> bool:
        """Add os import if needed"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if os is already imported
            if "import os" in content or "from os import" in content:
                return False

            # Find the best place to add the import (after other imports)
            lines = content.split("\n")
            import_index = -1

            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith(
                    "from "
                ):
                    import_index = i
                elif line.strip() == "" and import_index >= 0:
                    # Found end of imports
                    break

            if import_index >= 0:
                # Insert after the last import
                lines.insert(import_index + 1, "import os")
            else:
                # Insert at the beginning
                lines.insert(0, "import os")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            return True

        except Exception as e:
            print(f"Error adding os import to {file_path}: {e}")
            return False

    def scan_and_fix_all_files(self):
        """Scan and fix all Python files"""
        print("🔧 Scanning for hardcoded secrets...")

        fixed_count = 0
        total_issues = 0

        for root, dirs, files in os.walk(self.backend_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)

                    # Check if file has issues
                    issues = self.find_hardcoded_secrets(file_path)
                    if issues:
                        total_issues += len(issues)

                        # Add os import if needed
                        self.add_os_import(file_path)

                        # Fix the file
                        if self.fix_file(file_path):
                            fixed_count += 1

        print(f"\n📊 SUMMARY:")
        print(f"Files fixed: {fixed_count}")
        print(f"Total issues found: {total_issues}")
        print(f"Files with issues: {len(self.fixed_files)}")

        return fixed_count > 0

    def create_env_example(self):
        """Create .env.example file with all required environment variables"""
        env_vars = set()

        for _, _, env_var in self.issues_found:
            env_vars.add(env_var)

        # Add common environment variables
        common_vars = [
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "SUPABASE_JWT_SECRET",
            "GEMINI_API_KEY",
            "GOOGLE_TRANSLATE_API_KEY",
        ]

        env_vars.update(common_vars)

        env_example_path = os.path.join(self.backend_path, ".env.example")

        with open(env_example_path, "w") as f:
            f.write("# Raptorflow Environment Variables\n")
            f.write("# Copy this file to .env and fill in your actual values\n\n")

            for var in sorted(env_vars):
                f.write(f"{var}=your_{var.lower()}_here\n")

        print(f"Created .env.example at {env_example_path}")

    def update_gitignore(self):
        """Update .gitignore to exclude .env files"""
        gitignore_path = os.path.join(self.backend_path, "..", ".gitignore")

        try:
            with open(gitignore_path, "r") as f:
                content = f.read()

            # Add .env patterns if not present
            env_patterns = [".env", ".env.local", ".env.production", ".env.development"]

            added_patterns = []
            for pattern in env_patterns:
                if pattern not in content:
                    content += f"\n{pattern}\n"
                    added_patterns.append(pattern)

            if added_patterns:
                with open(gitignore_path, "w") as f:
                    f.write(content)

                print(f"Added to .gitignore: {', '.join(added_patterns)}")

        except Exception as e:
            print(f"Error updating .gitignore: {e}")


if __name__ == "__main__":
    fixer = SecretFixer()

    print("🔍 Fixing hardcoded secrets in Raptorflow backend...")
    print("=" * 60)

    # Scan and fix all files
    files_fixed = fixer.scan_and_fix_all_files()

    if files_fixed > 0:
        # Create .env.example
        fixer.create_env_example()

        # Update .gitignore
        fixer.update_gitignore()

        print(f"\n✅ SUCCESS: Fixed hardcoded secrets in {files_fixed} files")
        print("\n📋 NEXT STEPS:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your actual API keys and secrets")
        print("3. Run the red team assessment again to verify fixes")
    else:
        print("\n✅ No hardcoded secrets found - all good!")
