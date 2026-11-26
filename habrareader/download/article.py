import datetime

from habrareader.data import (
    Article,
    ArticleContents,
    Author,
    ArticleStatistics,
    ArticleHub,
    ArticleTag,
    ArticleFlow,
    Hub,
    Flow,
    ArticleData,
)
from habrareader.data.author import default_author
from habrareader.download.client import HabrClient


async def get_article(id_: int, client: HabrClient) -> ArticleData:
    current_time = int(datetime.datetime.now().timestamp())
    response = await client.request(f"https://habr.com/kek/v2/articles/{id_}")
    if response.status_code != 200:
        return ArticleData(
            article=Article(id_=id_, time_downloaded=current_time, time_published=None, is_success=0)
        )

    data = response.json()
    published = int(datetime.datetime.fromisoformat(data["timePublished"]).timestamp())
    article = Article(id_=id_, time_downloaded=current_time, time_published=published, is_success=1)

    original_url = None
    is_translation = False
    for post_label in data["postLabels"]:
        if post_label["type"] == "translation":
            is_translation = True
            original_url = post_label["data"].get("originalUrl")

    author_data = data["author"] or default_author
    article_contents = ArticleContents(
        id_=id_,
        lang=data["lang"],
        title=data["titleHtml"],
        author_id=int(author_data["id"]),
        text_html=data["textHtml"] or "",
        lead_data=(data["leadData"] or {}).get("textHtml") or "",
        is_corporative=1 if data["isCorporative"] else 0,
        original_url=original_url,
    )
    author = Author(author_id=int(author_data["id"]), alias=author_data["alias"], full_name=author_data["fullname"])
    statistics = data["statistics"]
    article_statistics = ArticleStatistics(
        id_=id_,
        num_comments=statistics["commentsCount"],
        num_readings=statistics["readingCount"],
        score=statistics["score"],
        votes=statistics["votesCount"],
        votes_positive=statistics["votesCountPlus"],
        votes_negative=statistics["votesCountMinus"],
    )

    article_hubs = [ArticleHub(id_=id_, hub_id=int(hub["id"])) for hub in data["hubs"]]
    hubs = [Hub(hub_id=int(hub["id"]), hub_alias=hub["alias"], hub_type=hub["type"], hub_title=hub["title"], hub_title_html=hub["titleHtml"]) for hub in data["hubs"]]
    article_tags = [ArticleTag(id_=id_, tag_title_html=tag["titleHtml"]) for tag in data["tags"]]
    article_flows = [ArticleFlow(id_=id_, flow_id=int(flow["id"])) for flow in data["flows"]]
    flows = [Flow(flow_id=int(flow["id"]), flow_alias=flow["alias"], flow_title=flow["title"], flow_title_html=flow["titleHtml"]) for flow in data["flows"]]

    # Attach translation metadata to a transient attribute consumed by the ORM mapper.
    setattr(article_contents, "is_translation", is_translation)

    return ArticleData(
        article=article,
        article_contents=article_contents,
        author=author,
        article_statistics=article_statistics,
        article_hubs=article_hubs,
        article_tags=article_tags,
        article_flows=article_flows,
        hubs=hubs,
        flows=flows,
    )


async def get_latest_id(client: HabrClient) -> int:
    response = await client.request("https://habr.com/kek/v2/articles/?period=daily&sort=date&page=1")
    response.raise_for_status()
    data = response.json()
    return max(int(article_id) for article_id in data["publicationIds"])
