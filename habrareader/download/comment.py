import datetime

from habrareader.data.model import (
    ArticleComment,
    Author,
    CommentChild,
    CommentContents,
)
from habrareader.download.client import HabrClient


async def get_article_comments(
    article_id: int,
    client: HabrClient,
) -> list[ArticleComment]:
    url = f"https://habr.com/kek/v2/articles/{article_id}/comments"
    response = await client.request(url)
    if response.status_code != 200:
        return []

    data = response.json()
    comments: list[ArticleComment] = []

    for comment_id, comment_data in data["comments"].items():
        author_data = comment_data["author"]
        if author_data is None:
            author = Author(id=0, alias="", full_name="")
        else:
            author = Author(
                id=int(author_data["id"]),
                alias=author_data.get("alias") or "",
                full_name=author_data.get("fullname") or "",
            )

        numeric_comment_id = int(comment_id)
        published_at = datetime.datetime.fromisoformat(
            comment_data["timePublished"]
        ).timestamp()
        comment = ArticleComment(
            id=numeric_comment_id,
            article_id=article_id,
            time_published=int(published_at),
        )
        comment.contents = CommentContents(
            comment_id=numeric_comment_id,
            score=int(comment_data["score"]),
            votes_count=int(comment_data["votesCount"]),
            message=comment_data["message"] or "",
            author_id=author.id,
            author=author,
        )
        comment.children = [
            CommentChild(
                comment_id=numeric_comment_id,
                child_comment_id=int(child_id),
            )
            for child_id in comment_data["children"]
        ]
        comments.append(comment)

    return comments
