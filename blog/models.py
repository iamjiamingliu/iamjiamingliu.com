from pydantic import BaseModel
from datetime import datetime, timedelta


class ArticleMetadata(BaseModel):
    title: str
    description: str
    img_url: str | None = None
    tags: list[str]
    category: str
    created_at: datetime
    updated_at: datetime
    excludes_from_index: bool = False
    must_read: bool = False
    word_count: int
    estimated_reading_time: timedelta
    is_new: bool = False
    is_recently_updated: bool = False
    language: str = "en"


class ArticleMD(BaseModel):
    metadata: ArticleMetadata
    content: str


class ArticleHTML(BaseModel):
    metadata: ArticleMetadata
    content: str
    table_of_content: str | None


class ArticleIndexEntry(BaseModel):
    metadata: ArticleMetadata
    file_path: str


class ArticlesIndex(BaseModel):
    categories: list[str]
    must_read: list[ArticleIndexEntry]
    latest: list[ArticleIndexEntry]
    per_category: dict[str, list[ArticleIndexEntry]]
    new_count: int
