from typing import Iterable

from habrareader.data.tables import (
    ARTICLE_TBL,
    ARTICLE_CONTENTS_TBL,
    AUTHOR_TBL,
    ARTICLE_STATISTICS_TBL,
    ARTICLE_HUB_TBL,
    ARTICLE_TAG_TBL,
    ARTICLE_FLOW_TBL,
    HUB_TBL,
    FLOW_TBL,
    ARTICLE_COMMENT_TBL,
    COMMENT_CONTENTS_TBL,
    COMMENT_CHILD_TBL,
)
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
    ArticleComment,
    CommentContents,
    CommentChild,
)
from sqlite3 import Cursor


def save_article(article: Article, cursor: Cursor):
    data = [(
        article.id_,
        article.time_downloaded,
        article.time_published,
        article.is_success,
    )]
    cursor.execute(f"DELETE FROM {ARTICLE_TBL} WHERE id = {article.id_}")
    cursor.executemany(f"INSERT INTO {ARTICLE_TBL} VALUES (?, ?, ?, ?)", data)


def save_article_contents(article_contents: ArticleContents, cursor: Cursor):
    data = [(
        article_contents.id_,
        article_contents.lang,
        article_contents.title,
        article_contents.author_id,
        article_contents.text_html,
        article_contents.lead_data,
        article_contents.is_corporative,
        article_contents.original_url,
    )]
    cursor.execute(f"DELETE FROM {ARTICLE_CONTENTS_TBL} WHERE id = {article_contents.id_}")
    cursor.executemany(f"INSERT INTO {ARTICLE_CONTENTS_TBL} VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)


def save_author(author: Author, cursor: Cursor):
    data = [(
        author.author_id,
        author.alias,
        author.full_name,
    )]
    cursor.execute(f"DELETE FROM {AUTHOR_TBL} WHERE author_id = {author.author_id}")
    cursor.executemany(f"INSERT INTO {AUTHOR_TBL} VALUES (?, ?, ?)", data)


def save_article_statistics(article_statistics: ArticleStatistics, cursor: Cursor):
    data = [(
        article_statistics.id_,
        article_statistics.num_comments,
        article_statistics.num_readings,
        article_statistics.score,
        article_statistics.votes,
        article_statistics.votes_positive,
        article_statistics.votes_negative,
    )]
    cursor.execute(f"DELETE FROM {ARTICLE_STATISTICS_TBL} WHERE id = {article_statistics.id_}")
    cursor.executemany(f"INSERT INTO {ARTICLE_STATISTICS_TBL} VALUES (?, ?, ?, ?, ?, ?, ?)", data)


def save_article_hubs(article_hubs: Iterable[ArticleHub], cursor: Cursor):
    data = [(hub.id_, hub.hub_id) for hub in article_hubs]
    article_id = set(hub.id_ for hub in article_hubs)
    if len(article_id) != 1:
        raise ValueError(f"Multiple article ids: {article_id}")
    article_id = article_id.pop()
    cursor.execute(f"DELETE FROM {ARTICLE_HUB_TBL} WHERE id = {article_id}")
    cursor.executemany(f"INSERT INTO {ARTICLE_HUB_TBL} VALUES (?, ?)", data)


def save_article_tags(article_tags: Iterable[ArticleTag], cursor: Cursor):
    data = [(tag.id_, tag.tag_title_html) for tag in article_tags]
    article_id = set(tag.id_ for tag in article_tags)
    if len(article_id) != 1:
        raise ValueError(f"Multiple article ids: {article_id}")
    article_id = article_id.pop()
    cursor.execute(f"DELETE FROM {ARTICLE_TAG_TBL} WHERE id = {article_id}")
    cursor.executemany(f"INSERT INTO {ARTICLE_TAG_TBL} VALUES (?, ?)", data)


def save_article_flows(article_flows: Iterable[ArticleFlow], cursor: Cursor):
    data = [(flow.id_, flow.flow_id) for flow in article_flows]
    article_id = set(flow.id_ for flow in article_flows)
    if len(article_id) != 1:
        raise ValueError(f"Multiple article ids: {article_id}")
    article_id = article_id.pop()
    cursor.execute(f"DELETE FROM {ARTICLE_FLOW_TBL} WHERE id = {article_id}")
    cursor.executemany(f"INSERT INTO {ARTICLE_FLOW_TBL} VALUES (?, ?)", data)


def save_hub(hub: Hub, cursor: Cursor):
    data = [(
        hub.hub_id,
        hub.hub_alias,
        hub.hub_type,
        hub.hub_title,
        hub.hub_title_html,
    )]
    cursor.execute(f"DELETE FROM {HUB_TBL} WHERE hub_id = {hub.hub_id}")
    cursor.executemany(f"INSERT INTO {HUB_TBL} VALUES (?, ?, ?, ?, ?)", data)


def save_flow(flow: Flow, cursor: Cursor):
    data = [(
        flow.flow_id,
        flow.flow_alias,
        flow.flow_title,
        flow.flow_title_html,
    )]
    cursor.execute(f"DELETE FROM {FLOW_TBL} WHERE flow_id = {flow.flow_id}")
    cursor.executemany(f"INSERT INTO {FLOW_TBL} VALUES (?, ?, ?, ?)", data)


def save_article_comments(article_comments: Iterable[ArticleComment], cursor: Cursor):
    data = [(
        comment.id_,
        comment.comment_id,
        comment.time_published,
    ) for comment in article_comments]
    article_id = set(comment.id_ for comment in article_comments)
    if len(article_id) == 0:
        return
    if len(article_id) != 1:
        raise ValueError(f"Multiple article ids: {article_id}")
    article_id = article_id.pop()
    cursor.execute(f"DELETE FROM {ARTICLE_COMMENT_TBL} WHERE id = {article_id}")
    cursor.executemany(f"INSERT INTO {ARTICLE_COMMENT_TBL} VALUES (?, ?, ?)", data)


def save_comment_contents(comment_contents: CommentContents, cursor: Cursor):
    data = [(
        comment_contents.comment_id,
        comment_contents.score,
        comment_contents.votes_count,
        comment_contents.message,
        comment_contents.author_id,
    )]
    cursor.execute(
        f"DELETE FROM {COMMENT_CONTENTS_TBL} WHERE comment_id = {comment_contents.comment_id}"
    )
    cursor.executemany(f"INSERT INTO {COMMENT_CONTENTS_TBL} VALUES (?, ?, ?, ?, ?)", data)


def save_comment_child(comment_child: CommentChild, cursor: Cursor):
    data = [(
        comment_child.comment_id, comment_child.child_comment_id
    )]
    cursor.execute(
        f"DELETE FROM {COMMENT_CHILD_TBL} WHERE comment_id = {comment_child.comment_id}"
    )
    cursor.executemany(f"INSERT INTO {COMMENT_CHILD_TBL} VALUES (?, ?)", data)


def clean_comments(article_comments: Iterable[ArticleComment], cursor: Cursor):
    article_id = set(comment.id_ for comment in article_comments)
    if len(article_id) == 0:
        # already clean
        return
    if len(article_id) != 1:
        raise ValueError(f"Multiple article ids: {article_id}")
    article_id = article_id.pop()
    query = f"SELECT comment_id FROM {ARTICLE_COMMENT_TBL} WHERE id = {article_id}"
    cursor.execute(query)
    old_ids = [row[0] for row in cursor.fetchall()]
    for comment_id in old_ids:
        cursor.execute(f"DELETE from {COMMENT_CONTENTS_TBL} WHERE comment_id = {comment_id}")
        cursor.execute(f"DELETE FROM {COMMENT_CHILD_TBL} WHERE comment_id = {comment_id}")
