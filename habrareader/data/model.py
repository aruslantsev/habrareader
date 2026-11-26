from typing import Optional

from sqlalchemy import ForeignKey, Table, Column, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from habrareader.data.tables import (
    ARTICLE_TBL,
    ARTICLE_STATE_TBL,
    AUTHOR_TBL,
    ARTICLE_STATISTICS_TBL,
    ARTICLE_HUB_TBL,
    HUB_TBL,
    ARTICLE_TAG_TBL,
    TAG_TBL,
    ARTICLE_FLOW_TBL,
    FLOW_TBL,
    ARTICLE_COMMENT_TBL,
    COMMENT_CONTENTS_TBL,
    COMMENT_CHILD_TBL,
)


def sanitize(value: str) -> str:
    return value.encode("utf-16-le", errors="replace").decode("utf-16-le")


class Base(DeclarativeBase):
    pass


article_hub_table = Table(
    ARTICLE_HUB_TBL,
    Base.metadata,
    Column("article_id", ForeignKey(f"{ARTICLE_TBL}.id", ondelete="CASCADE"), primary_key=True),
    Column("hub_id", ForeignKey(f"{HUB_TBL}.id", ondelete="CASCADE"), primary_key=True),
)

article_flow_table = Table(
    ARTICLE_FLOW_TBL,
    Base.metadata,
    Column("article_id", ForeignKey(f"{ARTICLE_TBL}.id", ondelete="CASCADE"), primary_key=True),
    Column("flow_id", ForeignKey(f"{FLOW_TBL}.id", ondelete="CASCADE"), primary_key=True),
)

article_tag_table = Table(
    ARTICLE_TAG_TBL,
    Base.metadata,
    Column("article_id", ForeignKey(f"{ARTICLE_TBL}.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey(f"{TAG_TBL}.id", ondelete="CASCADE"), primary_key=True),
)


class Author(Base):
    __tablename__ = AUTHOR_TBL

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str]
    full_name: Mapped[str]

    articles: Mapped[list["Article"]] = relationship(back_populates="author")
    comments: Mapped[list["CommentContents"]] = relationship(back_populates="author")


class Article(Base):
    __tablename__ = ARTICLE_TBL

    id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[Optional[str]]
    title: Mapped[Optional[str]]
    text_html: Mapped[Optional[str]]
    lead_data: Mapped[Optional[str]]
    is_corporative: Mapped[Optional[bool]]
    is_translation: Mapped[Optional[bool]]
    original_url: Mapped[Optional[str]]
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{AUTHOR_TBL}.id"), nullable=True)

    author: Mapped[Optional[Author]] = relationship(back_populates="articles")
    state: Mapped[Optional["ArticleState"]] = relationship(back_populates="article", uselist=False)
    statistics: Mapped[Optional["ArticleStatistics"]] = relationship(back_populates="article", uselist=False)
    hubs: Mapped[list["Hub"]] = relationship(secondary=article_hub_table, back_populates="articles")
    flows: Mapped[list["Flow"]] = relationship(secondary=article_flow_table, back_populates="articles")
    tags: Mapped[list["Tag"]] = relationship(secondary=article_tag_table, back_populates="articles")
    comments: Mapped[list["ArticleComment"]] = relationship(back_populates="article", cascade="all, delete-orphan")

    def __post_init__(self) -> None:
        self.title = sanitize(self.title)
        self.text_html = sanitize(self.text_html)
        self.lead_data = sanitize(self.lead_data)


class ArticleState(Base):
    __tablename__ = ARTICLE_STATE_TBL

    id: Mapped[int] = mapped_column(ForeignKey(f"{ARTICLE_TBL}.id", ondelete="CASCADE"), primary_key=True)
    published_at: Mapped[Optional[int]]
    updated_at: Mapped[int]
    is_success: Mapped[bool]

    article: Mapped[Article] = relationship(back_populates="state")


class ArticleStatistics(Base):
    __tablename__ = ARTICLE_STATISTICS_TBL

    id: Mapped[int] = mapped_column(ForeignKey(f"{ARTICLE_TBL}.id", ondelete="CASCADE"), primary_key=True)
    num_comments: Mapped[int]
    num_readings: Mapped[int]
    score: Mapped[int]
    votes: Mapped[int]
    votes_positive: Mapped[int]
    votes_negative: Mapped[int]

    article: Mapped[Article] = relationship(back_populates="statistics")


class Hub(Base):
    __tablename__ = HUB_TBL

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str]
    type: Mapped[str]
    title: Mapped[str]
    title_html: Mapped[str]

    articles: Mapped[list[Article]] = relationship(secondary=article_hub_table, back_populates="hubs")


class Flow(Base):
    __tablename__ = FLOW_TBL

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str]
    title: Mapped[str]
    title_html: Mapped[str]

    articles: Mapped[list[Article]] = relationship(secondary=article_flow_table, back_populates="flows")


class Tag(Base):
    __tablename__ = TAG_TBL

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title_html: Mapped[str] = mapped_column(unique=True)

    articles: Mapped[list[Article]] = relationship(secondary=article_tag_table, back_populates="tags")


class ArticleComment(Base):
    __tablename__ = ARTICLE_COMMENT_TBL

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey(f"{ARTICLE_TBL}.id", ondelete="CASCADE"), index=True)
    time_published: Mapped[int]

    article: Mapped[Article] = relationship(back_populates="comments")
    contents: Mapped[Optional["CommentContents"]] = relationship(back_populates="comment", uselist=False, cascade="all, delete-orphan")
    children: Mapped[list["CommentChild"]] = relationship(back_populates="comment", cascade="all, delete-orphan")


class CommentContents(Base):
    __tablename__ = COMMENT_CONTENTS_TBL

    comment_id: Mapped[int] = mapped_column(ForeignKey(f"{ARTICLE_COMMENT_TBL}.id", ondelete="CASCADE"), primary_key=True)
    score: Mapped[int]
    votes_count: Mapped[int]
    message: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey(f"{AUTHOR_TBL}.id"))

    comment: Mapped[ArticleComment] = relationship(back_populates="contents")
    author: Mapped[Author] = relationship(back_populates="comments")

    def __post_init__(self) -> None:
        self.message = sanitize(self.message)


class CommentChild(Base):
    __tablename__ = COMMENT_CHILD_TBL

    comment_id: Mapped[int] = mapped_column(ForeignKey(f"{ARTICLE_COMMENT_TBL}.id", ondelete="CASCADE"), primary_key=True)
    child_comment_id: Mapped[int] = mapped_column(primary_key=True)

    comment: Mapped[ArticleComment] = relationship(back_populates="children")

