import logging
from typing import Iterable, List, Tuple
from urllib import robotparser, request
from urllib.parse import urlparse
import xml.etree.ElementTree as ElementTree

logger = logging.getLogger("raptorflow.discovery")


KEYWORD_SCORES = {
    "pricing": 8,
    "price": 6,
    "docs": 7,
    "documentation": 7,
    "case-study": 6,
    "case-studies": 6,
    "integration": 6,
    "integrations": 6,
    "security": 6,
    "compliance": 5,
    "privacy": 5,
    "about": 3,
    "customers": 4,
    "product": 5,
    "platform": 5,
}


def _strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def parse_sitemap(xml_text: str) -> Tuple[List[str], List[str]]:
    """Parse a sitemap XML document.

    Returns a tuple of (page_urls, sitemap_urls).
    """
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError:
        return [], []

    root_tag = _strip_namespace(root.tag)
    urls: List[str] = []
    sitemaps: List[str] = []

    for loc in root.findall(".//{*}loc"):
        if loc.text:
            text = loc.text.strip()
            if text:
                if root_tag == "sitemapindex":
                    sitemaps.append(text)
                else:
                    urls.append(text)

    return urls, sitemaps


def score_url(url: str) -> int:
    """Score a URL based on heuristic path keywords."""
    path = urlparse(url).path.lower()
    score = 0
    for keyword, weight in KEYWORD_SCORES.items():
        if keyword in path:
            score += weight
    if path in {"", "/"}:
        score -= 1
    return score


def _normalize_domain(domain: str) -> str:
    if domain.startswith("http://") or domain.startswith("https://"):
        return domain.rstrip("/")
    return f"https://{domain.strip('/')}"


def _fetch_text(url: str, timeout: int = 10) -> str:
    with request.urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="ignore")


def _unique_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    unique_items = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)
    return unique_items


def discover_urls(domain: str) -> List[str]:
    """Discover and prioritize URLs for a domain using robots.txt and sitemaps."""
    base_url = _normalize_domain(domain)
    robots_url = f"{base_url}/robots.txt"

    parser = robotparser.RobotFileParser()
    parser.set_url(robots_url)

    sitemaps: List[str] = []
    try:
        parser.read()
        sitemaps = parser.site_maps() or []
    except Exception as exc:
        logger.warning("Failed to read robots.txt for %s: %s", domain, exc)

    if not sitemaps:
        sitemaps = [f"{base_url}/sitemap.xml"]

    discovered_urls: List[str] = []
    seen_sitemaps = set()

    while sitemaps:
        sitemap_url = sitemaps.pop(0)
        if sitemap_url in seen_sitemaps:
            continue
        seen_sitemaps.add(sitemap_url)

        try:
            xml_text = _fetch_text(sitemap_url)
        except Exception as exc:
            logger.warning("Failed to fetch sitemap %s: %s", sitemap_url, exc)
            continue

        urls, nested_sitemaps = parse_sitemap(xml_text)
        discovered_urls.extend(urls)
        for nested in nested_sitemaps:
            if nested not in seen_sitemaps:
                sitemaps.append(nested)

    unique_urls = _unique_preserve_order(discovered_urls)
    return sorted(unique_urls, key=score_url, reverse=True)
