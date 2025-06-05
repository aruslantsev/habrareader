from dataclasses import dataclass
from typing import Optional, List, Iterable


@dataclass(eq=True, frozen=True)
class Article:
    id_: int
    time_downloaded: int
    time_published: Optional[int]
    is_success: int


@dataclass(eq=True, frozen=True)
class ArticleContents:
    id_: int
    lang: str
    title: str
    author_id: int
    text_html: str
    lead_data: str
    is_corporative: int
    original_url: Optional[str]  # if translation


@dataclass(eq=True, frozen=True)
class Author:
    author_id: int
    alias: str
    full_name: str


@dataclass(eq=True, frozen=True)
class ArticleStatistics:
    id_: int
    num_comments: int
    num_readings: int
    score: int
    votes: int
    votes_positive: int
    votes_negative: int


@dataclass(eq=True, frozen=True)
class ArticleHub:
    id_: int
    hub_id: int


@dataclass(eq=True, frozen=True)
class ArticleTag:
    id_: int
    tag_title_html: str


@dataclass(eq=True, frozen=True)
class ArticleFlow:
    id_: int
    flow_id: int


@dataclass(eq=True, frozen=True)
class Hub:
    hub_id: int
    hub_alias: str
    hub_type: str
    hub_title: str
    hub_title_html: str


@dataclass(eq=True, frozen=True)
class Flow:
    flow_id: int
    flow_alias: str
    flow_title: str
    flow_title_html: str


@dataclass(eq=True, frozen=True)
class ArticleComment:
    id_: int
    comment_id: int
    time_published: int


@dataclass(eq=True, frozen=True)
class CommentContents:
    comment_id: int
    score: str
    votes_count: str
    message: str
    author_id: int


@dataclass(eq=True, frozen=True)
class CommentChild:
    comment_id: int
    child_comment_id: int


@dataclass
class ArticleData:
    article: Article
    article_contents: ArticleContents = None
    author: Author = None
    article_statistics: Optional[ArticleStatistics] = ()
    article_hubs: Optional[Iterable[ArticleHub]] = ()
    article_tags: Optional[Iterable[ArticleTag]] = ()
    article_flows: Optional[Iterable[ArticleFlow]] = ()
    hubs: Optional[Iterable[Hub]] = ()
    flows: Optional[Iterable[Flow]] = ()


@dataclass
class CommentsData:
    comments: Iterable[ArticleComment] = ()
    comments_contents: Iterable[CommentContents] = ()
    authors: Iterable[Author] = ()
    comments_children: Iterable[CommentChild] = ()