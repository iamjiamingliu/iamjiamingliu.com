from . import models
from pathlib import Path
import frontmatter
import markdown2
import math
from datetime import timedelta
import re


def count_words(text: str) -> int:
    words = re.findall(r"\b\w+\b", text)
    return len(words)


def estimate_reading_time(word_count: int, wpm=150) -> timedelta:
    minutes = word_count / wpm
    return timedelta(minutes=math.ceil(minutes))


def render_to_markdown(file_path: Path | str) -> models.ArticleMD:
    if isinstance(file_path, str):
        file_path = Path(file_path)
    payload = frontmatter.load(str(file_path))
    word_count = count_words(payload.content)
    estimated_reading_time = estimate_reading_time(word_count)
    metadata = models.ArticleMetadata(
        **payload.to_dict(),
        word_count=word_count,
        estimated_reading_time=estimated_reading_time
    )
    return models.ArticleMD(metadata=metadata, content=payload.content)


def render_to_html(file_path: Path | str) -> models.ArticleHTML:
    md = render_to_markdown(file_path)
    html = markdown2.markdown(
        md.content, extras=["toc", "fenced-code-blocks", "tables"]
    )
    return models.ArticleHTML(
        metadata=md.metadata, content=str(html), table_of_content=html.toc_html
    )
