import asyncio
from argparse import ArgumentParser

from sqlalchemy import select

from habrareader.data.database import (
    create_database_engine,
    create_session_factory,
    initialize_database,
)
from habrareader.data.model import Article, ArticleState
from habrareader.download.article import get_article, get_latest_id
from habrareader.download.client import HabrClient
from habrareader.download.comment import get_article_comments
from habrareader.download.database_helpers import save_download


async def fetch_one(
    article_id: int,
    client: HabrClient,
):
    article = await get_article(article_id, client)
    comments = None
    if article.state is not None and article.state.is_success:
        comments = await get_article_comments(article_id, client)
    return article, comments


async def run(
    only_missing: bool,
    start_id: int | None,
    end_id: int | None,
    reverse: bool,
    *,
    requests_per_second: float = 5.0,
    concurrency: int = 10,
):
    engine = create_database_engine()
    await initialize_database(engine)
    session_factory = create_session_factory(engine)

    async with session_factory() as session:
        if start_id is None:
            if only_missing:
                start_id = 1
            else:
                result = await session.execute(
                    select(Article.id)
                    .order_by(Article.id.desc())
                    .limit(1)
                )
                latest = result.scalar_one_or_none()
                start_id = (latest or 0) + 1

        client = HabrClient(
            requests_per_second=requests_per_second,
            concurrency=concurrency,
        )
        try:
            if end_id is None:
                if only_missing:
                    result = await session.execute(
                        select(Article.id)
                        .order_by(Article.id.desc())
                        .limit(1)
                    )
                    end_id = result.scalar_one_or_none() or 0
                else:
                    end_id = await get_latest_id(client)
            print(f"Start ID: {start_id}. End ID: {end_id}")

            if only_missing:
                result = await session.execute(
                    select(Article.id)
                    .join(ArticleState)
                    .where(ArticleState.is_success.is_(False))
                    .where(Article.id >= start_id)
                    .where(Article.id <= end_id)
                )
                ids = sorted(row[0] for row in result.all())
            else:
                ids = list(range(start_id, end_id + 1))

            if reverse:
                ids.reverse()

            batch_size = max(concurrency * 2, 1)
            for offset in range(0, len(ids), batch_size):
                batch = ids[offset:offset + batch_size]
                labels = ", ".join(f"#{article_id}" for article_id in batch)
                print("Downloading:", labels)
                tasks = (
                    fetch_one(article_id, client)
                    for article_id in batch
                )
                results = await asyncio.gather(*tasks)

                for article, comments in results:
                    article_id = article.id
                    if (
                        article.state is not None
                        and article.state.is_success
                    ):
                        print(f"#{article_id}: Success")
                    else:
                        print(f"#{article_id}: Failed")
                    async with session_factory() as write_session:
                        await save_download(
                            write_session,
                            article,
                            comments,
                        )
        finally:
            await client.close()

    await engine.dispose()


def main():
    parser = ArgumentParser()
    parser.add_argument("--start-id", type=int, default=None)
    parser.add_argument("--end-id", type=int, default=None)
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--only-missing", action="store_true")
    parser.add_argument("--requests-per-second", type=float, default=5.0)
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()

    asyncio.run(run(
        only_missing=args.only_missing,
        start_id=args.start_id,
        end_id=args.end_id,
        reverse=args.reverse,
        requests_per_second=args.requests_per_second,
        concurrency=args.concurrency,
    ))


if __name__ == "__main__":
    main()
