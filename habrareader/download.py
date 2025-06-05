import sqlite3
from argparse import ArgumentParser

from habrareader.data.tables import ARTICLE_TBL
from habrareader.data.tddl import create_tables
from habrareader.download.article import get_article, get_latest_id
from habrareader.download.comment import get_article_comments
from habrareader.download.database_helpers import (
    save_article,
    save_article_contents,
    save_author,
    save_article_statistics,
    save_article_hubs,
    save_article_tags,
    save_article_flows,
    save_hub,
    save_flow,
    save_article_comments,
    save_comment_contents,
    save_comment_child,
    clean_comments,
)

SQLITE_CONNECTION = "database.sqlite"


def run(
    only_missing: bool,
    start_id: int,
    end_id: int,
):
    with sqlite3.connect(SQLITE_CONNECTION) as connection:
        create_tables(connection=connection)
        connection.commit()

        cursor = connection.cursor()

        if start_id is None:
            if only_missing:
                start_id = 1
            else:
                cursor.execute(f"SELECT max(id) FROM {ARTICLE_TBL}")
                start_id = cursor.fetchall()[0][0]
                if start_id is None:
                    start_id = 0
                start_id += 1

        if end_id is None:
            if only_missing:
                cursor.execute(f"SELECT max(id) FROM {ARTICLE_TBL}")
                end_id = cursor.fetchall()[0][0]
                if end_id is None:
                    end_id = 0
            else:
                end_id = get_latest_id()
        print(f"Start ID: {start_id}. End ID: {end_id}")

        if only_missing:
            query = f"SELECT id FROM {ARTICLE_TBL} WHERE is_success = 0 AND id >= {start_id} AND id <= {end_id}"
            cursor.execute(query)
            ids = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute(f"SELECT id FROM {ARTICLE_TBL} WHERE is_success = 0")
            ids = list(range(start_id, end_id + 1))
        try:
            for id_ in ids:
                print(f"Downloading article #{id_}...")
                article_data = get_article(id_)
                cursor.execute(f"SELECT is_success FROM {ARTICLE_TBL} WHERE id = {id_}")
                was_success = cursor.fetchall()
                if len(was_success) == 0:
                    was_success = 0
                else:
                    was_success = was_success[0][0]
                if article_data.article.is_success != 0:
                    comments_data = get_article_comments(id_)
                    print("Success")
                    save_article(article_data.article, cursor=cursor)
                    save_article_contents(article_data.article_contents, cursor=cursor)
                    save_author(article_data.author, cursor=cursor)
                    save_article_statistics(article_data.article_statistics, cursor=cursor)
                    save_article_hubs(article_data.article_hubs, cursor=cursor)
                    save_article_tags(article_data.article_tags, cursor=cursor)
                    save_article_flows(article_data.article_flows, cursor=cursor)

                    for hub in article_data.hubs:
                        save_hub(hub, cursor=cursor)

                    for flow in article_data.flows:
                        save_flow(flow, cursor=cursor)

                    clean_comments(comments_data.comments, cursor=cursor)
                    save_article_comments(comments_data.comments, cursor=cursor)

                    for comment_contents in comments_data.comments_contents:
                        save_comment_contents(comment_contents, cursor=cursor)

                    for comment_child in comments_data.comments_children:
                        save_comment_child(comment_child, cursor=cursor)

                    for comment_author in comments_data.authors:
                        save_author(comment_author, cursor=cursor)
                else:
                    print("Failed")
                    if not was_success:
                        save_article(article_data.article, cursor=cursor)
                    else:
                        print(f"Article {id_} was downloaded earlier. Skipping update.")
                connection.commit()
        except Exception as e:
            connection.rollback()
            print(e)
            print(article_data)
            raise e
        return


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--start-id",
        type=int,
        default=None,
        help=(
            "First article id. If not specified, will be last_downloaded + 1, "
            "if not set --only-missing, else 1"
        )
    )
    parser.add_argument(
        "--end-id",
        type=int,
        default=None,
        help=(
            "Last article id. If not specified, will be last available article on the website "
            "if not set --only-missing, else last downloaded article"
        )
    )
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="Download only articles that were not downloaded due to errors"
    )
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    only_missing = args.only_missing
    run(
        only_missing=only_missing,
        start_id=start_id,
        end_id=end_id,
    )


if __name__ == "__main__":
    main()
