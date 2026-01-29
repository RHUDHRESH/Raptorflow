import ast
import os

ROOT = r"c:\Users\hp\OneDrive\Desktop\Raptorflow\backend"
EXCLUDE_DIRS = {
    "tests",
    "docs",
    "__pycache__",
    "node_modules",
    "playwright-report",
    "test-results",
    "migrations",
}


def collect_imports(root: str) -> tuple[int, set[str]]:
    imports: set[str] = set()
    files_scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")
        ]
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            path = os.path.join(dirpath, filename)
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    source = handle.read()
            except UnicodeDecodeError:
                with open(path, "r", encoding="utf-8-sig", errors="ignore") as handle:
                    source = handle.read()
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            files_scanned += 1
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
    return files_scanned, imports


def main() -> None:
    files_scanned, imports = collect_imports(ROOT)
    output_path = r"c:\Users\hp\OneDrive\Desktop\Raptorflow\.logs\backend_imports.txt"
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(f"Files scanned: {files_scanned}\n")
        for name in sorted(imports):
            handle.write(f"{name}\n")


if __name__ == "__main__":
    main()
