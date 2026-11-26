from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from habrareader.data.model import Article, ArticleComment


async def save_download(
    session: AsyncSession,
    article: Article,
    comments: list[ArticleComment] | None = None,
) -> None:
    merged = await session.merge(article)

    if comments is not None:
        await session.execute(
            delete(ArticleComment).where(ArticleComment.article_id == merged.id)
        )
        await session.flush()

        for comment in comments:
            comment.article_id = merged.id
            await session.merge(comment)

    await session.commit()
