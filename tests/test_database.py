import pytest

from habrareader.data.database import (
    create_database_engine,
    create_session_factory,
    initialize_database,
)
from habrareader.data.model import Article, ArticleState


@pytest.mark.asyncio
async def test_failed_article_is_saved():
    engine = create_database_engine("sqlite+aiosqlite:///:memory:")
    await initialize_database(engine)
    factory = create_session_factory(engine)

    article = Article(id=123)
    article.state = ArticleState(
        id=123,
        published_at=None,
        updated_at=100,
        is_success=False,
    )

    async with factory() as session:
        from habrareader.download.database_helpers import save_download
        await save_download(session, article)

    async with factory() as session:
        stored_article = await session.get(Article, 123)
        state = await session.get(ArticleState, 123)
        assert stored_article is not None
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
