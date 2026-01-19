from pydantic import BaseModel
from datetime import datetime


class ArticleMetadata(BaseModel):
    title: str
    img_url: str
    tags: list[str]
    category: str
    created_at: datetime
    updated_at: datetime


class ArticleMD(BaseModel):
    metadata: ArticleMetadata
    content: str


class ArticleHTML(BaseModel):
    metadata: ArticleMetadata
    content: str
    table_of_content: str | None
