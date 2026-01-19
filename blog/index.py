import traceback
from pathlib import Path
import os
from .render import render_to_markdown


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
