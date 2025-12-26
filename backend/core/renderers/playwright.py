from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Optional

from bs4 import BeautifulSoup

APP_SHELL_MARKERS: tuple[str, ...] = (
    'id="root"',
    "id='root'",
    'id="app"',
    "id='app'",
    'id="__next"',
    "id='__next'",
    'id="__nuxt"',
    "id='__nuxt'",
    "data-reactroot",
    "ng-app",
)


def _text_density(html: str) -> float:
    if not html:
        return 0.0
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    text = soup.get_text(separator=" ", strip=True)
    html_length = max(len(html), 1)
    return len(text) / html_length


def _has_app_shell_marker(
    html: str, markers: Iterable[str] = APP_SHELL_MARKERS
) -> bool:
    if not html:
        return False
    lowered = html.lower()
    return any(marker in lowered for marker in markers)


def should_render(html: str, min_text_density: float = 0.02) -> bool:
    if _has_app_shell_marker(html):
        return True
    if _text_density(html) < min_text_density:
        return True
    if not re.search(r"<body[^>]*>.*</body>", html, re.DOTALL | re.IGNORECASE):
        return True
    return False


@dataclass
class PlaywrightRenderer:
    timeout_s: int = 20
    user_agent: Optional[str] = None

    async def render(self, url: str) -> str:
        from playwright.async_api import async_playwright

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.user_agent)
            page = await context.new_page()
            await page.goto(
                url, wait_until="networkidle", timeout=self.timeout_s * 1000
            )
            await page.wait_for_timeout(1000)
            html = await page.content()
            await context.close()
            await browser.close()
            return html
