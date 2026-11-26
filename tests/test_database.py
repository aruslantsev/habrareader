import pytest

from sqlalchemy import select

from habrareader.data.database import create_database_engine, initialize_database, create_session_factory
from habrareader.data.model import Article, ArticleState
from habrareader.data import Article as DTOArticle, ArticleData, CommentsData


@pytest.mark.asyncio
async def test_failed_article_is_saved():
    engine = create_database_engine("sqlite+aiosqlite:///:memory:")
    await initialize_database(engine)
    factory = create_session_factory(engine)

    async with factory() as session:
        from habrareader.download.database_helpers import save_download
        await save_download(
            session,
            ArticleData(article=DTOArticle(
                id_=123,
                time_downloaded=100,
                time_published=None,
                is_success=0,
            ),),
            CommentsData(),
        )

    async with factory() as session:
        article = await session.get(Article, 123)
        state = await session.get(ArticleState, 123)
        assert article is not None
        assert state is not None
        assert state.is_success is False

    await engine.dispose()


@pytest.mark.asyncio
async def test_fresh_schema_contains_canonical_tables():
    engine = create_database_engine("sqlite+aiosqlite:///:memory:")
    await initialize_database(engine)

    async with engine.connect() as connection:
        rows = await connection.run_sync(
            lambda sync_connection: sorted(sync_connection.dialect.get_table_names(sync_connection))
        )

    assert "article" in rows
    assert "article_comment" in rows
    assert "article_flow" in rows
    assert "article_hub" in rows
    assert "article_tag" in rows
    await engine.dispose()
