# PURPOSE: Crawl Doctors of Doom content and extract readable text.
# DEPENDENCIES: httpx, bs4, urllib.parse, app.utils.text
# MODIFICATION NOTES: MVP crawler with domain scoping and page limits.

from collections import deque
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.utils.text import normalize_text


@dataclass
class CrawledPage:
    # PURPOSE: Represent a crawled page payload.
    # DEPENDENCIES: dataclasses
    # MODIFICATION NOTES: MVP crawl result container.

    url: str
    title: str
    raw_html: str
    text: str


def _is_allowed_url(url: str, base_netloc: str) -> bool:
    # PURPOSE: Ensure URLs stay within the allowed domain.
    # DEPENDENCIES: urllib.parse
    # MODIFICATION NOTES: MVP domain guard.
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and parsed.netloc == base_netloc


def _extract_text(html: str) -> str:
    # PURPOSE: Extract readable text from HTML content.
    # DEPENDENCIES: BeautifulSoup
    # MODIFICATION NOTES: MVP extraction using body/main/article.
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    main = soup.find("main") or soup.find("article") or soup.body
    text = main.get_text(" ", strip=True) if main else ""
    return normalize_text(text)


def crawl_doctors_of_doom(
    base_url: str,
    max_pages: int,
    timeout_seconds: float,
    user_agent: str,
) -> Iterable[CrawledPage]:
    # PURPOSE: Crawl the Doctors of Doom site with BFS and page limits.
    # DEPENDENCIES: httpx, BeautifulSoup
    # MODIFICATION NOTES: MVP crawl that yields normalized text per page.
    parsed_base = urlparse(base_url)
    base_netloc = parsed_base.netloc
    queue = deque([base_url])
    visited: set[str] = set()

    headers = {"User-Agent": user_agent}
    with httpx.Client(timeout=timeout_seconds, headers=headers, follow_redirects=True) as client:
        while queue and len(visited) < max_pages:
            current = queue.popleft()
            if current in visited:
                continue
            if not _is_allowed_url(current, base_netloc):
                continue
            try:
                response = client.get(current)
                if response.status_code != 200:
                    continue
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    continue
                html = response.text
            except httpx.RequestError:
                continue

            visited.add(current)

            soup = BeautifulSoup(html, "html.parser")
            title = (soup.title.string.strip() if soup.title and soup.title.string else current)
            text = _extract_text(html)
            if text:
                yield CrawledPage(url=current, title=title, raw_html=html, text=text)

            for link in soup.find_all("a", href=True):
                href = urljoin(current, link["href"])
                if _is_allowed_url(href, base_netloc) and href not in visited:
                    queue.append(href)
