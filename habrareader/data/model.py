from typing import Optional

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


article_hub_table = Table(
    "article_hub",
    Base.metadata,
    Column(
        "article_id",
        ForeignKey("article.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "hub_id",
        ForeignKey("hub.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

article_flow_table = Table(
    "article_flow",
    Base.metadata,
    Column(
        "article_id",
        ForeignKey("article.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "flow_id",
        ForeignKey("flow.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

article_tag_table = Table(
    "article_tag",
    Base.metadata,
    Column(
        "article_id",
        ForeignKey("article.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Author(Base):
    __tablename__ = "author"

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[Optional[str]]
    full_name: Mapped[Optional[str]]

    articles: Mapped[list["Article"]] = relationship(
        back_populates="author",
    )
    comments: Mapped[list["CommentContents"]] = relationship(
        back_populates="author",
    )


class Article(Base):
    __tablename__ = "article"

    id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[Optional[str]]
    title: Mapped[Optional[str]]
    text_html: Mapped[Optional[str]]
    lead_data: Mapped[Optional[str]]
    is_corporative: Mapped[Optional[bool]]
    is_translation: Mapped[Optional[bool]]
    original_url: Mapped[Optional[str]]
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("author.id"),
        nullable=True,
    )

    author: Mapped[Optional[Author]] = relationship(
        back_populates="articles",
    )
    state: Mapped[Optional["ArticleState"]] = relationship(
        back_populates="article",
        uselist=False,
    )
    statistics: Mapped[Optional["ArticleStatistics"]] = relationship(
        back_populates="article",
        uselist=False,
    )
    hubs: Mapped[list["Hub"]] = relationship(
        secondary=article_hub_table,
        back_populates="articles",
    )
    flows: Mapped[list["Flow"]] = relationship(
        secondary=article_flow_table,
        back_populates="articles",
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary=article_tag_table,
        back_populates="articles",
    )
    comments: Mapped[list["ArticleComment"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )


class ArticleState(Base):
    __tablename__ = "article_state"

    id: Mapped[int] = mapped_column(
        ForeignKey("article.id", ondelete="CASCADE"),
        primary_key=True,
    )
    published_at: Mapped[Optional[int]]
    updated_at: Mapped[int]
    is_success: Mapped[bool]

    article: Mapped[Article] = relationship(back_populates="state")


class ArticleStatistics(Base):
    __tablename__ = "article_statistics"

    id: Mapped[int] = mapped_column(
        ForeignKey("article.id", ondelete="CASCADE"),
        primary_key=True,
    )
    num_comments: Mapped[int]
    num_readings: Mapped[int]
    score: Mapped[int]
    votes: Mapped[int]
    votes_positive: Mapped[int]
    votes_negative: Mapped[int]

    article: Mapped[Article] = relationship(back_populates="statistics")


class Hub(Base):
    __tablename__ = "hub"

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str]
    type: Mapped[str]
    title: Mapped[str]
    title_html: Mapped[str]

    articles: Mapped[list[Article]] = relationship(
        secondary=article_hub_table,
        back_populates="hubs",
    )


class Flow(Base):
    __tablename__ = "flow"

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str]
    title: Mapped[str]
    title_html: Mapped[str]

    articles: Mapped[list[Article]] = relationship(
        secondary=article_flow_table,
        back_populates="flows",
    )


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title_html: Mapped[str] = mapped_column(unique=True)

    articles: Mapped[list[Article]] = relationship(
        secondary=article_tag_table,
        back_populates="tags",
    )


class ArticleComment(Base):
    __tablename__ = "article_comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("article.id", ondelete="CASCADE"),
        index=True,
    )
    time_published: Mapped[int]

    article: Mapped[Article] = relationship(back_populates="comments")
    contents: Mapped[Optional["CommentContents"]] = relationship(
        back_populates="comment",
        uselist=False,
        cascade="all, delete-orphan",
    )
    children: Mapped[list["CommentChild"]] = relationship(
        back_populates="comment",
        cascade="all, delete-orphan",
    )


class CommentContents(Base):
    __tablename__ = "comment_contents"

    comment_id: Mapped[int] = mapped_column(
        ForeignKey("article_comment.id", ondelete="CASCADE"),
        primary_key=True,
    )
    score: Mapped[int]
    votes_count: Mapped[int]
    message: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))

    comment: Mapped[ArticleComment] = relationship(back_populates="contents")
    author: Mapped[Author] = relationship(back_populates="comments")


class CommentChild(Base):
    __tablename__ = "comment_child"

    comment_id: Mapped[int] = mapped_column(
        ForeignKey("article_comment.id", ondelete="CASCADE"),
        primary_key=True,
    )
    child_comment_id: Mapped[int] = mapped_column(primary_key=True)

    comment: Mapped[ArticleComment] = relationship(
        back_populates="children",
    )
