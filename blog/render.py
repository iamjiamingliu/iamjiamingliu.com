from . import models
from pathlib import Path
import frontmatter
import markdown2


def render_to_markdown(file_path: Path | str) -> models.ArticleMD:
    if isinstance(file_path, str):
        file_path = Path(file_path)
    payload = frontmatter.load(str(file_path))
    metadata = models.ArticleMetadata(**payload.to_dict())
    return models.ArticleMD(metadata=metadata, content=payload.content)


def render_to_html(file_path: Path | str) -> models.ArticleHTML:
    md = render_to_markdown(file_path)
    html = markdown2.markdown(md.content)
    return models.ArticleHTML(
        metadata=md.metadata, content=str(html), table_of_content=html.toc_html
    )
