import re
from datetime import datetime, timedelta
from pathlib import Path

import frontmatter
import markdown2

from . import models

NEW_THRESHOLD = timedelta(days=7)


def count_words(text: str) -> int:
    words = re.findall(r"\b\w+\b", text)
    return len(words)


def estimate_reading_time(word_count: int, wpm=200) -> timedelta:
    minutes = word_count / wpm
    return timedelta(seconds=minutes * 60)


def _is_recent(timestamp: datetime) -> bool:
    return (datetime.now(tz=timestamp.tzinfo) - timestamp) < NEW_THRESHOLD


def render_to_markdown(file_path: Path | str) -> models.ArticleMD:
    if isinstance(file_path, str):
        file_path = Path(file_path)
    payload = frontmatter.load(str(file_path))
    if payload.get("language") == "zh":
        word_count = len(payload.content)
        estimated_reading_time = estimate_reading_time(
            word_count, wpm=500
        )  # Chinese WPM
    else:
        word_count = count_words(payload.content)
        estimated_reading_time = estimate_reading_time(word_count)
    metadata = models.ArticleMetadata(
        **payload.to_dict(),
        word_count=word_count,
        estimated_reading_time=estimated_reading_time,
    )
    metadata.is_new = _is_recent(metadata.created_at)
    metadata.is_recently_updated = _is_recent(metadata.updated_at)
    return models.ArticleMD(metadata=metadata, content=payload.content)


def render_to_html(file_path: Path | str) -> models.ArticleHTML:
    md = render_to_markdown(file_path)
    html = markdown2.markdown(
        md.content, extras=["toc", "fenced-code-blocks", "tables", "footnotes"]
    )
    return models.ArticleHTML(
        metadata=md.metadata, content=str(html), table_of_content=html.toc_html
    )
