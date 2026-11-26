from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from habrareader.data.model import Article, ArticleComment, Tag


async def save_download(
    session: AsyncSession,
    article: Article,
    comments: list[ArticleComment] | None = None,
) -> None:
    merged_tags = []
    for tag in article.tags:
        result = await session.execute(
            select(Tag).where(Tag.title_html == tag.title_html)
        )
        existing = result.scalar_one_or_none()
        merged_tags.append(existing or tag)
    article.tags = merged_tags

    merged = await session.merge(article)

    if comments is not None:
        delete_statement = delete(ArticleComment).where(
            ArticleComment.article_id == merged.id
        )
        await session.execute(delete_statement)
        await session.flush()

        for comment in comments:
            comment.article_id = merged.id
            await session.merge(comment)

    await session.commit()
