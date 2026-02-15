import os
import traceback
from pathlib import Path
from typing import Iterable, Sequence

from .render import render_to_markdown
from .models import ArticlesIndex, ArticleIndexEntry

_DEFAULT_EXTS = {".md", ".markdown", ".mdx"}


def _iter_article_files(
    blogs_root: Path,
    *,
    exts: set[str] = _DEFAULT_EXTS,
    followlinks: bool = True,
    include_hidden: bool = False,
) -> Iterable[Path]:
    """
    Yields article file paths under blogs_root, filtered by extension and (optionally) hidden files/dirs.
    """
    root = blogs_root.resolve()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=followlinks):
        dpath = Path(dirpath)

        if not include_hidden:
            # mutate in-place so os.walk doesn't descend into hidden dirs
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for fname in filenames:
            if not include_hidden and fname.startswith("."):
                continue
            fpath = dpath / fname
            if fpath.suffix.lower() in exts:
                yield fpath


def _relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        # if for some reason relative_to fails, fall back to absolute posix
        return path.resolve().as_posix()


def _sort_entries_desc(entries: Sequence[ArticleIndexEntry]) -> list[ArticleIndexEntry]:
    """
    Sort newest first. Tie-breakers keep ordering deterministic.
    """
    return sorted(
        entries,
        key=lambda e: (
            e.metadata.updated_at,
            e.metadata.created_at,
            e.metadata.title.lower(),
            e.file_path,
        ),
        reverse=True,
    )


# ---- main API ----


def ensure_articles_are_valid(
    blogs_root: Path,
    *,
    exts: set[str] = _DEFAULT_EXTS,
    followlinks: bool = True,
    include_hidden: bool = False,
    stop_on_first_error: bool = True,
) -> None:
    """
    Validates every article under blogs_root by attempting to render/parse it.

    If stop_on_first_error=False, collects all failures and raises one ValueError at the end.
    """
    blogs_root = Path(blogs_root)
    failures: list[str] = []

    for fpath in _iter_article_files(
        blogs_root, exts=exts, followlinks=followlinks, include_hidden=include_hidden
    ):
        try:
            render_to_markdown(fpath.as_posix())
        except Exception:
            msg = f"Could not render article {fpath.as_posix()}:\n{traceback.format_exc()}"
            if stop_on_first_error:
                raise ValueError(msg)
            failures.append(msg)

    if failures:
        raise ValueError("Some articles failed validation:\n\n" + "\n\n".join(failures))


def load_articles_index(
    blogs_root: Path,
    *,
    latest_n: int = 12,
    exts: set[str] = _DEFAULT_EXTS,
    followlinks: bool = True,
    include_hidden: bool = False,
    store_relative_paths: bool = True,
    skip_bad_articles: bool = False,
) -> ArticlesIndex:
    """
    Builds an index for all articles under blogs_root.

    - Filters by extension (default: .md/.markdown/.mdx)
    - Stable sorting for reproducible output
    - Per-category lists are sorted newest-first
    - categories is a sorted list[str] (not a set)
    - file_path can be stored relative to blogs_root for cleaner URLs/links
    """
    blogs_root = Path(blogs_root)
    root_resolved = blogs_root.resolve()

    all_entries: list[ArticleIndexEntry] = []
    per_category: dict[str, list[ArticleIndexEntry]] = {}

    for fpath in _iter_article_files(
        blogs_root, exts=exts, followlinks=followlinks, include_hidden=include_hidden
    ):
        try:
            md = render_to_markdown(fpath.as_posix())
            metadata = md.metadata
        except Exception:
            if skip_bad_articles:
                continue
            raise ValueError(
                f"Could not render article {fpath.as_posix()}:\n{traceback.format_exc()}"
            )

        file_path = (
            _relpath(fpath, root_resolved) if store_relative_paths else fpath.as_posix()
        )
        entry = ArticleIndexEntry(metadata=metadata, file_path=file_path)
        all_entries.append(entry)

        cat = (metadata.category or "").strip() or "Uncategorized"
        per_category.setdefault(cat, []).append(entry)

    # Sort globally + per-category
    all_sorted = _sort_entries_desc(all_entries)
    for cat, entries in per_category.items():
        per_category[cat] = _sort_entries_desc(entries)

    # Nice deterministic category ordering:
    # 1) by number of posts desc
    # 2) then alphabetically
    categories = sorted(
        per_category.keys(),
        key=lambda c: (-len(per_category[c]), c.lower()),
    )

    return ArticlesIndex(
        categories=categories,
        latest=all_sorted[:latest_n],
        per_category=per_category,
    )
