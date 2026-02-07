"""
Documentation Testing with Link Validation and Content Accuracy Checking

Comprehensive documentation testing for RaptorFlow backend:
- Link validation and broken link detection
- Content accuracy verification
- Code example validation
- Documentation coverage analysis
- Consistency checking
"""

import pytest

pytest.skip(
    "Archived manual test script; use explicit run if needed.", allow_module_level=True
)

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import aiohttp
import markdown
import yaml
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class IssueType(Enum):
    """Documentation issue types."""

    BROKEN_LINK = "broken_link"
    MISSING_LINK = "missing_link"
    OUTDATED_CONTENT = "outdated_content"
    INCORRECT_CODE = "incorrect_code"
    MISSING_DOCUMENTATION = "missing_documentation"
    INCONSISTENT_FORMAT = "inconsistent_format"
    MISSING_EXAMPLE = "missing_example"
    INVALID_SYNTAX = "invalid_syntax"


class SeverityLevel(Enum):
    """Issue severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DocumentationIssue:
    """Documentation issue."""

    type: IssueType
    severity: SeverityLevel
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    context: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class LinkCheckResult:
    """Link validation result."""

    url: str
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_time: Optional[float] = None
    is_valid: bool = False
    is_internal: bool = False


@dataclass
class DocumentationTestResult:
    """Documentation test result."""

    file_path: str
    total_links: int = 0
    valid_links: int = 0
    broken_links: int = 0
    total_issues: int = 0
    issues: List[DocumentationIssue] = field(default_factory=list)
    link_results: List[LinkCheckResult] = field(default_factory=list)
    execution_time: float = 0.0


class DocumentationTestConfig(BaseModel):
    """Documentation test configuration."""

    docs_dir: str = "docs"
    output_dir: str = "doc_test_results"
    base_url: str = "https://api.raptorflow.com"
    check_external_links: bool = True
    check_code_examples: bool = True
    check_content_accuracy: bool = True
    timeout: int = 10
    max_concurrent_requests: int = 10
    exclude_patterns: List[str] = Field(
        default_factory=lambda: ["http://localhost", "http://127.0.0.1", "example.com"]
    )


class DocumentationTester:
    """Comprehensive documentation tester."""

    def __init__(self, config: DocumentationTestConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.openapi_spec: Dict[str, Any] = {}

        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

        # Load OpenAPI specification for validation
        self._load_openapi_spec()

    async def __aenter__(self):
        """Async context manager entry."""
        await self._setup_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _setup_session(self) -> None:
        """Setup HTTP session."""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        connector = aiohttp.TCPConnector(limit=self.config.max_concurrent_requests)

        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={"User-Agent": "RaptorFlow-Doc-Test/1.0"},
        )

    def _load_openapi_spec(self) -> None:
        """Load OpenAPI specification."""
        spec_path = Path(self.config.docs_dir) / "openapi_comprehensive.yaml"
        if spec_path.exists():
            try:
                with open(spec_path, "r") as f:
                    self.openapi_spec = yaml.safe_load(f)
                logger.info(f"Loaded OpenAPI spec: {spec_path}")
            except Exception as e:
                logger.error(f"Failed to load OpenAPI spec: {e}")

    async def test_documentation_file(self, file_path: Path) -> DocumentationTestResult:
        """Test a single documentation file."""
        start_time = time.time()
        result = DocumentationTestResult(file_path=str(file_path))

        try:
            content = file_path.read_text(encoding="utf-8")

            # Extract and validate links
            if file_path.suffix.lower() in [".md", ".html"]:
                await self._validate_links(content, result)

            # Check code examples
            if self.config.check_code_examples:
                self._check_code_examples(content, result)

            # Check content accuracy
            if self.config.check_content_accuracy:
                self._check_content_accuracy(content, result)

            # Check formatting consistency
            self._check_formatting(content, result)

        except Exception as e:
            result.issues.append(
                DocumentationIssue(
                    type=IssueType.INVALID_SYNTAX,
                    severity=SeverityLevel.HIGH,
                    title="File Processing Error",
                    description=f"Failed to process file: {str(e)}",
                    file_path=str(file_path),
                )
            )

        result.execution_time = time.time() - start_time
        return result

    async def _validate_links(
        self, content: str, result: DocumentationTestResult
    ) -> None:
        """Validate links in documentation."""
        # Extract links based on file type
        if result.file_path.endswith(".md"):
            links = self._extract_markdown_links(content)
        elif result.file_path.endswith(".html"):
            links = self._extract_html_links(content)
        else:
            return

        result.total_links = len(links)

        # Check links concurrently
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        tasks = []

        for link in links:
            task = self._check_single_link(link, semaphore, result)
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        # Update statistics
        result.valid_links = len([r for r in result.link_results if r.is_valid])
        result.broken_links = len([r for r in result.link_results if not r.is_valid])

    def _extract_markdown_links(self, content: str) -> List[str]:
        """Extract links from markdown content."""
        # Markdown link pattern: [text](url)
        pattern = r"\[([^\]]*)\]\(([^)]+)\)"
        matches = re.findall(pattern, content)

        links = []
        for text, url in matches:
            # Skip anchor links and email links
            if not url.startswith("#") and not url.startswith("mailto:"):
                links.append(url)

        return links

    def _extract_html_links(self, content: str) -> List[str]:
        """Extract links from HTML content."""
        soup = BeautifulSoup(content, "html.parser")
        links = []

        for link in soup.find_all("a", href=True):
            href = link["href"]
            # Skip anchor links and email links
            if not href.startswith("#") and not href.startswith("mailto:"):
                links.append(href)

        return links

    async def _check_single_link(
        self, url: str, semaphore: asyncio.Semaphore, result: DocumentationTestResult
    ) -> None:
        """Check a single link."""
        async with semaphore:
            link_result = LinkCheckResult(url=url)

            # Determine if internal link
            link_result.is_internal = url.startswith(
                self.config.base_url
            ) or not url.startswith(("http://", "https://"))

            # Skip external links if disabled
            if not self.config.check_external_links and not link_result.is_internal:
                link_result.is_valid = True
                result.link_results.append(link_result)
                return

            # Skip excluded patterns
            if any(pattern in url for pattern in self.config.exclude_patterns):
                link_result.is_valid = True
                result.link_results.append(link_result)
                return

            try:
                start_time = time.time()

                # Handle relative URLs
                if url.startswith("/"):
                    full_url = self.config.base_url + url
                elif not url.startswith(("http://", "https://")):
                    # Relative link - assume it's valid for now
                    link_result.is_valid = True
                    result.link_results.append(link_result)
                    return
                else:
                    full_url = url

                async with self.session.head(
                    full_url, allow_redirects=True
                ) as response:
                    link_result.status_code = response.status
                    link_result.response_time = time.time() - start_time
                    link_result.is_valid = response.status < 400

                if not link_result.is_valid:
                    # Find line number for the link
                    line_number = self._find_link_line_number(result.file_path, url)

                    severity = (
                        SeverityLevel.HIGH
                        if link_result.status_code >= 500
                        else SeverityLevel.MEDIUM
                    )

                    result.issues.append(
                        DocumentationIssue(
                            type=IssueType.BROKEN_LINK,
                            severity=severity,
                            title=f"Broken Link: {url}",
                            description=f"Link returned status {link_result.status_code}",
                            file_path=result.file_path,
                            line_number=line_number,
                            context=url,
                            suggestion="Check if the URL is correct and the resource is available",
                        )
                    )

            except asyncio.TimeoutError:
                link_result.error_message = "Timeout"
                result.issues.append(
                    DocumentationIssue(
                        type=IssueType.BROKEN_LINK,
                        severity=SeverityLevel.MEDIUM,
                        title=f"Link Timeout: {url}",
                        description="Link request timed out",
                        file_path=result.file_path,
                        context=url,
                        suggestion="Check if the server is responsive",
                    )
                )
            except Exception as e:
                link_result.error_message = str(e)
                result.issues.append(
                    DocumentationIssue(
                        type=IssueType.BROKEN_LINK,
                        severity=SeverityLevel.MEDIUM,
                        title=f"Link Error: {url}",
                        description=f"Error checking link: {str(e)}",
                        file_path=result.file_path,
                        context=url,
                        suggestion="Verify the link format and accessibility",
                    )
                )

            result.link_results.append(link_result)

    def _find_link_line_number(self, file_path: str, url: str) -> Optional[int]:
        """Find line number for a link in file."""
        try:
            content = Path(file_path).read_text(encoding="utf-8")
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                if url in line:
                    return i
        except Exception:
            pass

        return None

    def _check_code_examples(
        self, content: str, result: DocumentationTestResult
    ) -> None:
        """Check code examples in documentation."""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for code blocks
            if line.strip().startswith("```"):
                language = line.strip()[3:].strip()
                if language:
                    # Validate code block language
                    valid_languages = [
                        "python",
                        "javascript",
                        "bash",
                        "curl",
                        "json",
                        "yaml",
                    ]
                    if language not in valid_languages:
                        result.issues.append(
                            DocumentationIssue(
                                type=IssueType.INCORRECT_CODE,
                                severity=SeverityLevel.LOW,
                                title=f"Invalid Code Language: {language}",
                                description=f"Code language '{language}' is not in the supported list",
                                file_path=result.file_path,
                                line_number=i,
                                context=line.strip(),
                                suggestion=f"Use one of: {', '.join(valid_languages)}",
                            )
                        )

            # Check for common code issues
            if "http://localhost" in line or "http://127.0.0.1" in line:
                result.issues.append(
                    DocumentationIssue(
                        type=IssueType.INCORRECT_CODE,
                        severity=SeverityLevel.MEDIUM,
                        title="Localhost URL in Code Example",
                        description="Code example contains localhost URL",
                        file_path=result.file_path,
                        line_number=i,
                        context=line.strip(),
                        suggestion="Replace localhost with the actual API base URL",
                    )
                )

            # Check for placeholder values
            placeholders = ["YOUR_API_KEY", "YOUR_TOKEN", "REPLACE_ME", "FIXME"]
            for placeholder in placeholders:
                if placeholder in line.upper():
                    result.issues.append(
                        DocumentationIssue(
                            type=IssueType.INCORRECT_CODE,
                            severity=SeverityLevel.LOW,
                            title=f"Placeholder Found: {placeholder}",
                            description="Code example contains placeholder value",
                            file_path=result.file_path,
                            line_number=i,
                            context=line.strip(),
                            suggestion="Replace placeholder with actual example values",
                        )
                    )

    def _check_content_accuracy(
        self, content: str, result: DocumentationTestResult
    ) -> None:
        """Check content accuracy against OpenAPI spec."""
        if not self.openapi_spec:
            return

        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check endpoint references
            endpoint_pattern = r"/(api/v\d+/[a-zA-Z0-9/_-]+)"
            matches = re.findall(endpoint_pattern, line)

            for endpoint in matches:
                if not self._endpoint_exists_in_spec(endpoint):
                    result.issues.append(
                        DocumentationIssue(
                            type=IssueType.OUTDATED_CONTENT,
                            severity=SeverityLevel.HIGH,
                            title=f"Invalid Endpoint: {endpoint}",
                            description=f"Endpoint '{endpoint}' not found in OpenAPI specification",
                            file_path=result.file_path,
                            line_number=i,
                            context=line.strip(),
                            suggestion="Update the endpoint to match the current API specification",
                        )
                    )

            # Check method references
            methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
            for method in methods:
                if f"{method} /" in line:
                    # Extract full endpoint
                    endpoint_match = re.search(f"{method} (/[^\\s]+)", line)
                    if endpoint_match:
                        endpoint = endpoint_match.group(1)
                        if not self._method_endpoint_exists_in_spec(
                            method.lower(), endpoint
                        ):
                            result.issues.append(
                                DocumentationIssue(
                                    type=IssueType.OUTDATED_CONTENT,
                                    severity=SeverityLevel.HIGH,
                                    title=f"Invalid Method-Endpoint: {method} {endpoint}",
                                    description=f"Method {method} for endpoint {endpoint} not found in OpenAPI specification",
                                    file_path=result.file_path,
                                    line_number=i,
                                    context=line.strip(),
                                    suggestion="Verify the method and endpoint combination",
                                )
                            )

    def _endpoint_exists_in_spec(self, endpoint: str) -> bool:
        """Check if endpoint exists in OpenAPI spec."""
        paths = self.openapi_spec.get("paths", {})
        return endpoint in paths

    def _method_endpoint_exists_in_spec(self, method: str, endpoint: str) -> bool:
        """Check if method-endpoint combination exists in OpenAPI spec."""
        paths = self.openapi_spec.get("paths", {})
        endpoint_data = paths.get(endpoint, {})
        return method in endpoint_data

    def _check_formatting(self, content: str, result: DocumentationTestResult) -> None:
        """Check formatting consistency."""
        lines = content.split("\n")

        # Check for common formatting issues
        for i, line in enumerate(lines, 1):
            # Check for trailing whitespace
            if line.endswith(" "):
                result.issues.append(
                    DocumentationIssue(
                        type=IssueType.INCONSISTENT_FORMAT,
                        severity=SeverityLevel.LOW,
                        title="Trailing Whitespace",
                        description="Line contains trailing whitespace",
                        file_path=result.file_path,
                        line_number=i,
                        context=line.rstrip(),
                        suggestion="Remove trailing whitespace",
                    )
                )

            # Check for mixed line endings (basic check)
            if "\r" in line:
                result.issues.append(
                    DocumentationIssue(
                        type=IssueType.INCONSISTENT_FORMAT,
                        severity=SeverityLevel.LOW,
                        title="Mixed Line Endings",
                        description="Line contains carriage return character",
                        file_path=result.file_path,
                        line_number=i,
                        context=line.rstrip(),
                        suggestion="Use consistent line endings (LF)",
                    )
                )

            # Check for very long lines
            if len(line) > 120:
                result.issues.append(
                    DocumentationIssue(
                        type=IssueType.INCONSISTENT_FORMAT,
                        severity=SeverityLevel.LOW,
                        title="Long Line",
                        description=f"Line is {len(line)} characters long (recommended: <120)",
                        file_path=result.file_path,
                        line_number=i,
                        context=line[:100] + "..." if len(line) > 100 else line,
                        suggestion="Break long lines for better readability",
                    )
                )

    async def test_all_documentation(self) -> List[DocumentationTestResult]:
        """Test all documentation files."""
        logger.info("Starting comprehensive documentation testing")

        docs_path = Path(self.config.docs_dir)
        if not docs_path.exists():
            raise FileNotFoundError(f"Documentation directory not found: {docs_path}")

        # Find all documentation files
        doc_files = []
        for pattern in ["**/*.md", "**/*.html", "**/*.txt"]:
            doc_files.extend(docs_path.glob(pattern))

        if not doc_files:
            logger.warning("No documentation files found")
            return []

        # Test files concurrently
        semaphore = asyncio.Semaphore(5)  # Limit concurrent file processing
        tasks = []

        for file_path in doc_files:
            task = self._test_file_with_semaphore(file_path, semaphore)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, DocumentationTestResult):
                valid_results.append(result)
            else:
                logger.error(f"Error testing file: {result}")

        logger.info(
            f"Documentation testing completed: {len(valid_results)} files tested"
        )
        return valid_results

    async def _test_file_with_semaphore(
        self, file_path: Path, semaphore: asyncio.Semaphore
    ) -> DocumentationTestResult:
        """Test file with semaphore control."""
        async with semaphore:
            return await self.test_documentation_file(file_path)

    def generate_test_report(
        self, results: List[DocumentationTestResult]
    ) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_files = len(results)
        total_links = sum(r.total_links for r in results)
        valid_links = sum(r.valid_links for r in results)
        broken_links = sum(r.broken_links for r in results)
        total_issues = sum(len(r.issues) for r in results)

        # Group issues by type and severity
        issues_by_type = {}
        issues_by_severity = {}

        for result in results:
            for issue in result.issues:
                issue_type = issue.type.value
                severity = issue.severity.value

                if issue_type not in issues_by_type:
                    issues_by_type[issue_type] = 0
                issues_by_type[issue_type] += 1

                if severity not in issues_by_severity:
                    issues_by_severity[severity] = 0
                issues_by_severity[severity] += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": total_files,
                "total_links": total_links,
                "valid_links": valid_links,
                "broken_links": broken_links,
                "link_success_rate": (
                    (valid_links / total_links * 100) if total_links > 0 else 0
                ),
                "total_issues": total_issues,
                "issues_by_type": issues_by_type,
                "issues_by_severity": issues_by_severity,
            },
            "file_results": [
                {
                    "file_path": result.file_path,
                    "total_links": result.total_links,
                    "valid_links": result.valid_links,
                    "broken_links": result.broken_links,
                    "total_issues": len(result.issues),
                    "execution_time": result.execution_time,
                    "issues": [
                        {
                            "type": issue.type.value,
                            "severity": issue.severity.value,
                            "title": issue.title,
                            "description": issue.description,
                            "line_number": issue.line_number,
                            "context": issue.context,
                            "suggestion": issue.suggestion,
                        }
                        for issue in result.issues
                    ],
                }
                for result in results
            ],
            "recommendations": self._generate_recommendations(
                issues_by_type, issues_by_severity
            ),
        }

    def _generate_recommendations(
        self, issues_by_type: Dict[str, int], issues_by_severity: Dict[str, int]
    ) -> List[str]:
        """Generate recommendations based on issues found."""
        recommendations = []

        if issues_by_type.get("broken_link", 0) > 0:
            recommendations.append(
                f"Fix {issues_by_type['broken_link']} broken links to improve user experience"
            )

        if issues_by_type.get("outdated_content", 0) > 0:
            recommendations.append(
                f"Update {issues_by_type['outdated_content']} outdated content references"
            )

        if issues_by_type.get("incorrect_code", 0) > 0:
            recommendations.append(
                f"Review and fix {issues_by_type['incorrect_code']} code examples"
            )

        if issues_by_type.get("inconsistent_format", 0) > 5:
            recommendations.append("Standardize formatting across documentation")

        if issues_by_severity.get("critical", 0) > 0:
            recommendations.append("Address critical issues immediately")

        if issues_by_severity.get("high", 0) > 0:
            recommendations.append("Prioritize high-severity issues for next release")

        return recommendations

    def save_report(self, results: List[DocumentationTestResult]) -> None:
        """Save documentation test report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate report
        report_data = self.generate_test_report(results)

        # Save JSON report
        json_file = Path(self.config.output_dir) / f"doc_test_report_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Documentation test report saved: {json_file}")

        # Save HTML report
        html_file = Path(self.config.output_dir) / f"doc_test_report_{timestamp}.html"
        html_content = self._generate_html_report(report_data)
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Documentation test HTML report saved: {html_file}")

        # Print summary
        summary = report_data["summary"]
        print(f"\nDocumentation Testing Summary:")
        print(f"Files Tested: {summary['total_files']}")
        print(f"Total Links: {summary['total_links']}")
        print(f"Valid Links: {summary['valid_links']}")
        print(f"Broken Links: {summary['broken_links']}")
        print(f"Link Success Rate: {summary['link_success_rate']:.1f}%")
        print(f"Total Issues: {summary['total_issues']}")

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report."""
        summary = report_data["summary"]

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Test Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8">Documentation Test Report</h1>

        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Summary</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600">{summary['total_files']}</div>
                    <div class="text-sm text-gray-600">Files Tested</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-green-600">{summary['valid_links']}</div>
                    <div class="text-sm text-gray-600">Valid Links</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-red-600">{summary['broken_links']}</div>
                    <div class="text-sm text-gray-600">Broken Links</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-orange-600">{summary['total_issues']}</div>
                    <div class="text-sm text-gray-600">Total Issues</div>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Issues by Type</h2>
            <div class="space-y-2">
                {self._generate_issue_chart(summary['issues_by_type'])}
            </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold mb-4">File Results</h2>
            <div class="space-y-4">
                {self._generate_file_results(report_data['file_results'])}
            </div>
        </div>
    </div>
</body>
</html>
        """

        return html

    def _generate_issue_chart(self, issues_by_type: Dict[str, int]) -> str:
        """Generate issue chart HTML."""
        if not issues_by_type:
            return '<p class="text-gray-600">No issues found!</p>'

        items = []
        for issue_type, count in issues_by_type.items():
            items.append(
                f"""
            <div class="flex justify-between items-center">
                <span class="text-sm font-medium">{issue_type.replace('_', ' ').title()}</span>
                <span class="text-sm bg-red-100 text-red-800 px-2 py-1 rounded">{count}</span>
            </div>
            """
            )

        return "".join(items)

    def _generate_file_results(self, file_results: List[Dict[str, Any]]) -> str:
        """Generate file results HTML."""
        items = []

        for result in file_results:
            if result["total_issues"] > 0:
                items.append(
                    f"""
                <div class="border rounded-lg p-4">
                    <div class="flex justify-between items-center mb-2">
                        <h3 class="font-medium">{result['file_path']}</h3>
                        <span class="text-sm bg-red-100 text-red-800 px-2 py-1 rounded">
                            {result['total_issues']} issues
                        </span>
                    </div>
                    <div class="text-sm text-gray-600">
                        Links: {result['valid_links']}/{result['total_links']} valid
                    </div>
                </div>
                """
                )

        if not items:
            return '<p class="text-gray-600">All files passed!</p>'

        return "".join(items)


# CLI usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test documentation")
    parser.add_argument("--docs-dir", default="docs", help="Documentation directory")
    parser.add_argument(
        "--output-dir", default="doc_test_results", help="Output directory"
    )
    parser.add_argument(
        "--base-url", default="https://api.raptorflow.com", help="Base API URL"
    )
    parser.add_argument(
        "--no-external-links", action="store_true", help="Skip external link checking"
    )
    parser.add_argument(
        "--no-code-checks", action="store_true", help="Skip code example validation"
    )
    parser.add_argument(
        "--no-accuracy-checks",
        action="store_true",
        help="Skip content accuracy checking",
    )
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout")

    args = parser.parse_args()

    # Create configuration
    config = DocumentationTestConfig(
        docs_dir=args.docs_dir,
        output_dir=args.output_dir,
        base_url=args.base_url,
        check_external_links=not args.no_external_links,
        check_code_examples=not args.no_code_checks,
        check_content_accuracy=not args.no_accuracy_checks,
        timeout=args.timeout,
    )

    # Run documentation tests
    async def main():
        async with DocumentationTester(config) as tester:
            results = await tester.test_all_documentation()
            tester.save_report(results)

    asyncio.run(main())
