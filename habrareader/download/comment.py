import datetime

from habrareader.data import ArticleComment, CommentContents, CommentChild, Author, CommentsData
from habrareader.data.author import default_author
from habrareader.download.client import HabrClient


async def get_article_comments(id_: int, client: HabrClient) -> CommentsData:
    response = await client.request(f"https://habr.com/kek/v2/articles/{id_}/comments")
    if response.status_code != 200:
        return CommentsData()

    data = response.json()
    comments: list[ArticleComment] = []
    contents: list[CommentContents] = []
    authors: dict[int, Author] = {}
    children: list[CommentChild] = []

    for comment_id, comment_data in data["comments"].items():
        author_data = comment_data["author"] or default_author
        author_id = int(author_data["id"])
        authors[author_id] = Author(
            author_id=author_id,
            alias=author_data["alias"],
            full_name=author_data["fullname"],
        )
        numeric_comment_id = int(comment_id)
        comments.append(ArticleComment(
            id_=id_,
            comment_id=numeric_comment_id,
            time_published=int(datetime.datetime.fromisoformat(comment_data["timePublished"]).timestamp()),
        ))
        contents.append(CommentContents(
            comment_id=numeric_comment_id,
            score=str(comment_data["score"]),
            votes_count=str(comment_data["votesCount"]),
            message=comment_data["message"] or "",
            author_id=author_id,
        ))
        children.extend(
            CommentChild(comment_id=numeric_comment_id, child_comment_id=int(child_id))
            for child_id in comment_data["children"]
        )

    return CommentsData(
        comments=comments,
        comments_contents=contents,
        authors=list(authors.values()),
        comments_children=children,
    )
