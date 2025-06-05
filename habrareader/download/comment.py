import datetime

import requests

from habrareader.data import ArticleComment, CommentContents, CommentChild, Author, CommentsData

DEFAULT_AUTHOR = {"id": "0", "alias": "", "fullname": ""}


def get_article_comments(id_: int) -> CommentsData:
    with requests.get(f"https://habr.com/kek/v2/articles/{id_}/comments", ) as req:
        req.raise_for_status()
        data = req.json()
        comments = []
        comments_contents = []
        authors = []
        comments_children = []
        for comment_id, comment_data in data["comments"].items():
            if comment_data["author"] is None:
                comment_data["author"] = DEFAULT_AUTHOR
            comment = ArticleComment(
                id_=int(id_),
                comment_id=int(comment_id),
                time_published=int(
                    datetime.datetime.fromisoformat(comment_data["timePublished"]).timestamp()
                ),
            )
            comment_contents = CommentContents(
                comment_id=int(comment_id),
                score=comment_data["score"],
                votes_count=comment_data["votesCount"],
                message=comment_data["message"],
                author_id=int(comment_data["author"]["id"]),
            )
            author = Author(
                author_id=int(comment_data["author"]["id"]),
                alias=comment_data["author"]["alias"],
                full_name=comment_data["author"]["fullname"],
            )
            comment_children = [
                CommentChild(
                    comment_id=int(comment_id), child_comment_id=int(child_id)
                ) for child_id in comment_data["children"]
            ]
            comments.append(comment)
            comments_contents.append(comment_contents)
            authors.append(author)
            comments_children.extend(comment_children)
        return CommentsData(
            comments=comments,
            comments_contents=comments_contents,
            authors=list(set(authors)),
            comments_children=comments_children,
        )
