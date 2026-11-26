import datetime
import re
import xml.etree.ElementTree as ET

from habrareader.data.model import (
    Article,
    ArticleState,
    ArticleStatistics,
    Author,
    Flow,
    Hub,
    Tag,
)
from habrareader.download.client import HabrClient


async def get_article(id_: int, client: HabrClient) -> Article:
    response = await client.request(f"https://habr.com/kek/v2/articles/{id_}")
    downloaded_at = int(datetime.datetime.now().timestamp())

    if response.status_code != 200:
        article = Article(id=id_) 
        article.state = ArticleState(
            id=id_,
            published_at=None,
            updated_at=downloaded_at,
            is_success=False,
        )
        return article

    data = response.json()
    published_at = int(datetime.datetime.fromisoformat(data["timePublished"]).timestamp())

    author_data = data["author"]
    if author_data is None:
        author = Author(id=0, alias="", full_name="")
    else:
        author = Author(
            id=int(author_data["id"]),
            alias=author_data.get("alias") or "",
            full_name=author_data.get("fullname") or "",
        )

    original_url = None
    is_translation = False
    for post_label in data["postLabels"]:
        if post_label["type"] == "translation":
            is_translation = True
            original_url = post_label["data"].get("originalUrl")

    statistics = data["statistics"]
    hubs = [
        Hub(
            id=int(hub["id"]),
            alias=hub["alias"],
            type=hub["type"],
            title=hub["title"],
            title_html=hub["titleHtml"],
        )
        for hub in data["hubs"]
    ]
    flows = [
        Flow(
            id=int(flow["id"]),
            alias=flow["alias"],
            title=flow["title"],
            title_html=flow["titleHtml"],
        )
        for flow in data["flows"]
    ]
    tags = [Tag(title_html=tag["titleHtml"]) for tag in data["tags"]]

    article = Article(
        id=id_,
        language=data["lang"],
        title=data["titleHtml"],
        text_html=data["textHtml"] or "",
        lead_data=(data["leadData"] or {}).get("textHtml") or "",
        is_corporative=bool(data["isCorporative"]),
        is_translation=is_translation,
        original_url=original_url,
        author=author,
        hubs=hubs,
        flows=flows,
        tags=tags,
    )
    article.state = ArticleState(
        id=id_,
        published_at=published_at,
        updated_at=downloaded_at,
        is_success=True,
    )
    article.statistics = ArticleStatistics(
        id=id_,
        num_comments=statistics["commentsCount"],
        num_readings=statistics["readingCount"],
        score=statistics["score"],
        votes=statistics["votesCount"],
        votes_positive=statistics["votesCountPlus"],
        votes_negative=statistics["votesCountMinus"],
    )
    return article


async def get_latest_id(client: HabrClient) -> int:
    response = await client.request("https://habr.com/ru/rss/articles/")
    response.raise_for_status()

    article_ids: list[int] = []
    try:
        root = ET.fromstring(response.text)
        for link in root.findall(".//item/link"):
            if link.text:
                article_ids.extend(int(value) for value in re.findall(r"/articles/(\d+)", link.text))
    except ET.ParseError:
        article_ids.extend(int(value) for value in re.findall(r"/articles/(\d+)", response.text))

    if not article_ids:
        raise RuntimeError("Could not determine the latest Habr article ID")
    return max(article_ids)
