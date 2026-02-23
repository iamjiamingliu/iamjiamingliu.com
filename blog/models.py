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
    word_count: int
    estimated_reading_time: timedelta


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
    latest: list[ArticleIndexEntry]
    per_category: dict[str, list[ArticleIndexEntry]]
