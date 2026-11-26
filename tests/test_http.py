import asyncio

import httpx
import pytest

from habrareader.download.article import get_article, get_latest_id
from habrareader.download.client import HabrClient, RateLimiter
from habrareader.download.comment import get_article_comments


ARTICLE_PAYLOAD = {
    "timePublished": "2025-01-02T03:04:05+00:00",
    "postLabels": [],
    "author": {
        "id": "42",
        "alias": "author",
        "fullname": "Test Author",
    },
    "lang": "ru",
    "titleHtml": "Test article",
    "textHtml": "<p>Text</p>",
    "leadData": {"textHtml": "Lead"},
    "isCorporative": False,
    "statistics": {
        "commentsCount": 1,
        "readingCount": 10,
        "score": 5,
        "votesCount": 7,
        "votesCountPlus": 6,
        "votesCountMinus": 1,
    },
    "hubs": [],
    "tags": [{"titleHtml": "Python"}],
    "flows": [],
}


async def replace_transport(client, handler):
    await client.client.aclose()
    client.client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        timeout=20,
        follow_redirects=True,
    )


@pytest.mark.asyncio
async def test_article_parser_builds_orm_graph():
    client = HabrClient(requests_per_second=1000)

    async def handler(request):
        return httpx.Response(200, json=ARTICLE_PAYLOAD)

    await replace_transport(client, handler)
    try:
        article = await get_article(123, client)

        assert article.id == 123
        assert article.title == "Test article"
        assert article.author is not None
        assert article.author.id == 42
        assert article.state is not None
        assert article.state.is_success is True
        assert article.statistics is not None
        assert article.tags[0].title_html == "Python"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_missing_article_is_marked_failed():
    client = HabrClient(requests_per_second=1000)

    async def handler(request):
        return httpx.Response(404, json={"message": "Not found"})

    await replace_transport(client, handler)
    try:
        article = await get_article(999999999, client)

        assert article.id == 999999999
        assert article.state is not None
        assert article.state.is_success is False
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_comment_parser_builds_comment_graph():
    client = HabrClient(requests_per_second=1000)
    payload = {
        "comments": {
            "654": {
                "timePublished": "2025-01-02T03:04:05+00:00",
                "score": 2,
                "votesCount": 3,
                "message": "A comment",
                "author": {
                    "id": "42",
                    "alias": "author",
                    "fullname": "Test Author",
                },
                "children": ["655"],
            }
        }
    }

    async def handler(request):
        return httpx.Response(200, json=payload)

    await replace_transport(client, handler)
    try:
        comments = await get_article_comments(123, client)

        assert len(comments) == 1
        assert comments[0].id == 654
        assert comments[0].contents is not None
        assert comments[0].contents.message == "A comment"
        assert len(comments[0].children) == 1
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_latest_id_is_read_from_rss():
    client = HabrClient(requests_per_second=1000)
    rss = """<?xml version="1.0"?>
<rss><channel>
<item><link>https://habr.com/ru/articles/1112592/</link></item>
<item><link>https://habr.com/ru/articles/1112586/</link></item>
</channel></rss>
"""

    async def handler(request):
        return httpx.Response(200, text=rss)

    await replace_transport(client, handler)
    try:
        assert await get_latest_id(client) == 1112592
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_retry_after_transient_server_error(monkeypatch):
    client = HabrClient(
        requests_per_second=1000,
        retries=1,
    )
    attempts = 0

    async def handler(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={"ok": True})

    async def no_sleep(delay):
        return None

    await replace_transport(client, handler)
    monkeypatch.setattr(asyncio, "sleep", no_sleep)
    try:
        response = await client.request("https://example.com/test")

        assert response.status_code == 200
        assert attempts == 2
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_rate_limiter_requires_positive_rate():
    with pytest.raises(ValueError):
        RateLimiter(0)

    limiter = RateLimiter(100)
    await limiter.acquire()
    await limiter.acquire()
