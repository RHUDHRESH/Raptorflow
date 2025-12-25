from backend.core.discovery import parse_sitemap, score_url


def test_parse_sitemap_index():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <sitemap>
            <loc>https://example.com/sitemap-products.xml</loc>
        </sitemap>
        <sitemap>
            <loc>https://example.com/sitemap-docs.xml</loc>
        </sitemap>
    </sitemapindex>
    """
    urls, sitemaps = parse_sitemap(xml)

    assert urls == []
    assert sitemaps == [
        "https://example.com/sitemap-products.xml",
        "https://example.com/sitemap-docs.xml",
    ]


def test_parse_sitemap_urlset():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/pricing</loc>
        </url>
        <url>
            <loc>https://example.com/docs/getting-started</loc>
        </url>
    </urlset>
    """
    urls, sitemaps = parse_sitemap(xml)

    assert urls == [
        "https://example.com/pricing",
        "https://example.com/docs/getting-started",
    ]
    assert sitemaps == []


def test_score_url_prioritizes_keywords():
    scored = sorted(
        [
            "https://example.com/blog/hello",
            "https://example.com/pricing",
            "https://example.com/docs/security",
        ],
        key=score_url,
        reverse=True,
    )

    assert scored[0] == "https://example.com/docs/security"
    assert scored[1] == "https://example.com/pricing"
