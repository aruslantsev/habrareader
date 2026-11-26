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

from habrareader.data.columns import (
    ID,
    AUTHOR_ID,
    HUB_ID,
    FLOW_ID,
    COMMENT_ID,
)
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


async def save_download(session: AsyncSession, article_data: ArticleData, comments_data: CommentsData | None = None) -> None:
    dto = article_data.article
    article = await session.get(ORMArticle, dto.id_)
    if article is None:
        article = ORMArticle(id=dto.id_)

    article.state = ArticleState(
        id=dto.id_,
        published_at=dto.time_published,
        updated_at=dto.time_downloaded,
        is_success=dto.is_success == 1,
    )

    if dto.is_success == 1:
        contents = article_data.article_contents
        author = article_data.author
        orm_author = await session.get(ORMAuthor, author.author_id)
        if orm_author is None:
            orm_author = ORMAuthor(id=author.author_id)
        orm_author.alias = author.alias
        orm_author.full_name = author.full_name
        session.add(orm_author)

        article.language = contents.lang
        article.title = contents.title
        article.text_html = contents.text_html
        article.lead_data = contents.lead_data
        article.is_corporative = contents.is_corporative == 1
        article.is_translation = getattr(contents, "is_translation", False)
        article.original_url = contents.original_url
        article.author = orm_author

        statistics = article_data.article_statistics
        article.statistics = ORMArticleStatistics(
            id=statistics.id_,
            num_comments=statistics.num_comments,
            num_readings=statistics.num_readings,
            score=statistics.score,
            votes=statistics.votes,
            votes_positive=statistics.votes_positive,
            votes_negative=statistics.votes_negative,
        )

        hubs = []
        for hub_data in article_data.hubs:
            hub = await session.get(Hub, hub_data.hub_id)
            if hub is None:
                hub = Hub(id=hub_data.hub_id)
            hub.alias = hub_data.hub_alias
            hub.type = hub_data.hub_type
            hub.title = hub_data.hub_title
            hub.title_html = hub_data.hub_title_html
            hubs.append(hub)
        article.hubs = hubs

        flows = []
        for flow_data in article_data.flows:
            flow = await session.get(Flow, flow_data.flow_id)
            if flow is None:
                flow = Flow(id=flow_data.flow_id)
            flow.alias = flow_data.flow_alias
            flow.title = flow_data.flow_title
            flow.title_html = flow_data.flow_title_html
            flows.append(flow)
        article.flows = flows

        tags = []
        for tag_data in article_data.article_tags:
            result = await session.execute(select(Tag).where(Tag.title_html == tag_data.tag_title_html))
            tag = result.scalar_one_or_none()
            if tag is None:
                tag = Tag(title_html=tag_data.tag_title_html)
            tags.append(tag)
        article.tags = tags

    session.add(article)
    await session.flush()

    if dto.is_success == 1 and comments_data is not None:
        await session.execute(delete(ORMArticleComment).where(ORMArticleComment.article_id == dto.id_))

        for author in comments_data.authors:
            orm_author = await session.get(ORMAuthor, author.author_id)
            if orm_author is None:
                orm_author = ORMAuthor(id=author.author_id)
            orm_author.alias = author.alias
            orm_author.full_name = author.full_name
            session.add(orm_author)

        for comment in comments_data.comments:
            orm_comment = ORMArticleComment(id=comment.comment_id, article_id=dto.id_, time_published=comment.time_published)
            session.add(orm_comment)

        await session.flush()

        for contents in comments_data.comments_contents:
            session.add(CommentContents(
                comment_id=contents.comment_id,
                score=int(contents.score),
                votes_count=int(contents.votes_count),
                message=contents.message,
                author_id=contents.author_id,
            ))

        for child in comments_data.comments_children:
            session.add(CommentChild(comment_id=child.comment_id, child_comment_id=child.child_comment_id))

    await session.commit()
