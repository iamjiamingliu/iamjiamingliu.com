import traceback
from pathlib import Path
import os
from .render import render_to_markdown
from .models import ArticlesIndex, ArticleIndexEntry


def ensure_articles_are_valid(blogs_root: Path):
    for dirpath, dirnames, filenames in os.walk(blogs_root, followlinks=True):
        for fname in filenames:
            path = os.path.join(dirpath, fname)
            try:
                render_to_markdown(path)
            except Exception:
                raise ValueError(
                    f"Could not render article {path}: {traceback.format_exc()}"
                )


def load_articles_index(blogs_root: Path) -> ArticlesIndex:
    all_entries = []
    for dirpath, dirnames, filenames in os.walk(blogs_root, followlinks=True):
        for fname in filenames:
            path = os.path.join(dirpath, fname)
            metadata = render_to_markdown(path).metadata
            all_entries.append(ArticleIndexEntry(metadata=metadata, file_path=path))

    per_category = {}
    for i in all_entries:
        if i.metadata.category not in per_category:
            per_category[i.metadata.category] = []
        per_category[i.metadata.category].append(i)

    return ArticlesIndex(
        latest=sorted(all_entries, key=lambda e: e.metadata.updated_at, reverse=True)[
            :12
        ],
        categories={i.metadata.category for i in all_entries},
        per_category=per_category,
    )
