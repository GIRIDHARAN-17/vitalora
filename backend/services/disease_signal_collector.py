from __future__ import annotations

import asyncio
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup
from googlesearch import search
from backend.core.config import settings


async def search_disease_outbreak(condition: str, location: str) -> list[str]:
    """
    Search Google for disease outbreak news and return URLs.

    Args:
        condition: Disease name (e.g., "covid-19", "flu")
        location: Location (e.g., "Chennai", "Tamil Nadu")

    Returns:
        List of up to 10 article URLs
    """
    query = f"{condition} outbreak {location} hospital cases"

    # Run Google search in executor (it's synchronous)
    loop = asyncio.get_event_loop()
    urls = await loop.run_in_executor(
        None,
        lambda: list(
            search(query, num_results=settings.search_results, sleep_interval=1)),
    )

    return urls[:settings.search_results]


async def scrape_article_text(url: str) -> str:
    """
    Scrape article text from a URL using BeautifulSoup.

    Args:
        url: Article URL

    Returns:
        Extracted text (truncated to max_article_chars)
    """
    try:
        timeout = aiohttp.ClientTimeout(total=settings.scrape_timeout_seconds)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                if response.status != 200:
                    return ""
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()

        # Try to find main article content
        article = soup.find("article") or soup.find(
            "main") or soup.find("body")
        if article:
            text = article.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)

        # Clean up whitespace
        text = " ".join(text.split())

        # Truncate
        if len(text) > settings.max_article_chars:
            text = text[:settings.max_article_chars] + "..."

        return text

    except Exception:
        return ""


async def collect_disease_signals(condition: str, location: str) -> str:
    """
    Search for disease outbreak news and scrape article text.

    Args:
        condition: Disease name
        location: Location

    Returns:
        Combined article text from all scraped articles
    """
    urls = await search_disease_outbreak(condition, location)

    # Scrape all URLs concurrently
    tasks = [scrape_article_text(url) for url in urls]
    texts = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out empty strings and exceptions
    valid_texts = [
        t for t in texts
        if isinstance(t, str) and t.strip()
    ]

    return "\n\n---\n\n".join(valid_texts)
