import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import Table, Column
from typing import Optional, List
from habrareader.data.tables import (
    ARTICLE_TBL,
    ARTICLE_CONTENTS_TBL,
    AUTHOR_TBL,
    ARTICLE_STATISTICS_TBL,
    ARTICLE_HUB_TBL,
    HUB_TBL,
    ARTICLE_TAG_TBL,
    ARTICLE_FLOW_TBL,
    FLOW_TBL,
    ARTICLE_COMMENT_TBL,
    COMMENT_CONTENTS_TBL,
    COMMENT_CHILD_TBL,
)


def sanitize(string):
    return string.encode("utf-16-le", errors="replace").decode("utf-16-le")


class Base(DeclarativeBase):
    pass


article_hub_table = Table(
    ARTICLE_HUB_TBL,
    Base.metadata,
    Column("article_id", sqlalchemy.schema.ForeignKey(f"{ARTICLE_TBL}.id"), primary_key=True),
    Column("hub_id", sqlalchemy.schema.ForeignKey(f"{HUB_TBL}.id"), primary_key=True),
)


class ArticleBase(Base):
    __tablename__ = ARTICLE_TBL
    id: Mapped[int] = mapped_column(primary_key=True)
    time_downloaded: Mapped[int]
    time_published: Mapped[Optional[int]]
    is_success: Mapped[int]
    author_id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey(f"{AUTHOR_TBL}.id"))

    contents: Mapped["ArticleContentsBase"] = relationship(back_populates="article", uselist=False,)
    author: Mapped["AuthorBase"] = relationship(back_populates="articles")
    statistics: Mapped["ArticleStatisticsBase"] = relationship(back_populates="article", uselist=False,)
    hubs: Mapped[List["HubBase"]] = relationship(secondary=article_hub_table, back_populates="articles")


class ArticleContentsBase(Base):
    __tablename__ = ARTICLE_CONTENTS_TBL
    id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey(f"{ARTICLE_TBL}.id"), primary_key=True)
    lang: Mapped[str]
    title: Mapped[str]
    text_html: Mapped[str]
    lead_data: Mapped[str]
    is_corporative: Mapped[int]
    original_url: Mapped[Optional[str]]
    article: Mapped["ArticleBase"] = relationship(back_populates="contents", uselist=False)

    def __post_init__(self):
        self.text_html = sanitize(self.text_html)
        self.lead_data = sanitize(self.lead_data)


class AuthorBase(Base):
    __tablename__ = AUTHOR_TBL
    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str]
    full_name: Mapped[str]

    articles: Mapped[List["ArticleBase"]] = relationship(back_populates="author")


class ArticleStatisticsBase(Base):
    __tablename__ = ARTICLE_STATISTICS_TBL
    id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey(f"{ARTICLE_TBL}.id"), primary_key=True)
    num_comments: Mapped[int]
    num_readings: Mapped[int]
    score: Mapped[int]
    votes: Mapped[int]
    votes_positive: Mapped[int]
    votes_negative: Mapped[int]

    article: Mapped["ArticleBase"] = relationship(back_populates="statistics", uselist=False)


class HubBase(Base):
    __tablename__ = HUB_TBL
    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str]
    type: Mapped[str]
    title: Mapped[str]
    title_html: Mapped[str]

    articles: Mapped[List["ArticleBase"]] = relationship(secondary=article_hub_table, back_populates="hubs")


from dataclasses import dataclass
from typing import Iterable

#
# @dataclass(frozen=True)
# class ArticleTag:
#     id_: int
#     tag_title_html: str
#
#
# @dataclass(frozen=True)
# class ArticleFlow:
#     id_: int
#     flow_id: int
#
#
# @dataclass(frozen=True)
# class Flow:
#     flow_id: int
#     flow_alias: str
#     flow_title: str
#     flow_title_html: str
#
#
# @dataclass(frozen=True)
# class ArticleComment:
#     id_: int
#     comment_id: int
#     time_published: int
#
#
# @dataclass
# class CommentContents:
#     comment_id: int
#     score: str
#     votes_count: str
#     message: str
#     author_id: int
#
#     def __post_init__(self):
#         self.message = sanitize(self.message)
#
#
# @dataclass(frozen=True)
# class CommentChild:
#     comment_id: int
#     child_comment_id: int


# @dataclass
# class ArticleData:
#     article: Article
#     article_contents: ArticleContents = None
#     author: Author = None
#     article_statistics: Optional[ArticleStatistics] = ()
#     article_hubs: Optional[Iterable[ArticleHub]] = ()
#     article_tags: Optional[Iterable[ArticleTag]] = ()
#     article_flows: Optional[Iterable[ArticleFlow]] = ()
#     hubs: Optional[Iterable[Hub]] = ()
#     flows: Optional[Iterable[Flow]] = ()


# @dataclass
# class CommentsData:
#     comments: Iterable[ArticleComment] = ()
#     comments_contents: Iterable[CommentContents] = ()
#     authors: Iterable[Author] = ()
#     comments_children: Iterable[CommentChild] = ()
