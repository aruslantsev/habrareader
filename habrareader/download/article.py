import datetime

import requests

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


def get_article(id_: int) -> ArticleData:
    current_time = int(datetime.datetime.now().timestamp())
    with (requests.get(f"https://habr.com/kek/v2/articles/{id_}") as req):
        if req.status_code != 200:
            article = Article(
                id_=int(id_),
                time_downloaded=current_time,
                time_published=None,
                is_success=0,
            )
            return ArticleData(article=article)
        data = req.json()
        article = Article(
            id_=int(id_),
            time_downloaded=current_time,
            time_published=int(datetime.datetime.fromisoformat(data["timePublished"]).timestamp()),
            is_success=1,
        )
        original_url = None
        for post_label in data["postLabels"]:
            if post_label["type"] == "translation":
                original_url = post_label["data"]["originalUrl"]
        article_contents = ArticleContents(
            id_=int(id_),
            lang=data["lang"],
            title=data["titleHtml"],
            author_id=int(data["author"]["id"]),
            text_html=data["textHtml"],
            lead_data=data["leadData"]["textHtml"],
            is_corporative=1 if data["isCorporative"] else 0,
            original_url=original_url,
        )
        author = Author(
            author_id=int(data["author"]["id"]),
            alias=data["author"]["alias"],
            full_name=data["author"]["fullname"],
        )
        article_statistics = ArticleStatistics(
            id_=int(id_),
            num_comments=data["statistics"]["commentsCount"],
            num_readings=data["statistics"]["readingCount"],
            score=data["statistics"]["score"],
            votes=data["statistics"]["votesCount"],
            votes_positive=data["statistics"]["votesCountPlus"],
            votes_negative=data["statistics"]["votesCountMinus"],
        )
        article_hubs = []
        hubs = []
        for hub in data["hubs"]:
            article_hubs.append(
                ArticleHub(
                    id_=int(id_),
                    hub_id=int(hub["id"]),
                )
            )
            hubs.append(
                Hub(
                    hub_id=int(hub["id"]),
                    hub_alias=hub["alias"],
                    hub_type=hub["type"],
                    hub_title=hub["title"],
                    hub_title_html=hub["titleHtml"],
                )
            )
        article_tags = [
            ArticleTag(id_=int(id_), tag_title_html=tag["titleHtml"]) for tag in data["tags"]
        ]
        article_flows = []
        flows = []
        for flow in data["flows"]:
            article_flows.append(
                ArticleFlow(
                    id_=int(id_),
                    flow_id=int(flow["id"]),
                )
            )
            flows.append(
                Flow(
                    flow_id=int(flow["id"]),
                    flow_alias=flow["alias"],
                    flow_title=flow["title"],
                    flow_title_html=flow["titleHtml"],
                )
            )
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


def get_latest_id():
    with requests.get(
        "https://habr.com/kek/v2/articles/?period=daily&sort=date&page=1",
        headers={"Accept-Language": "ru,en-US;q=0.7,en;q=0.3",}
    ) as req:
        req.raise_for_status()
        data = req.json()
        return max([int(id_) for id_ in data["publicationIds"]])
