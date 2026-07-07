"""Export API endpoints — uses documentation package (Bible §6.2 S13)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.export import export_markdown, export_json, get_export_filename
from app.services.specialists.documentation_writer import get_documentation

router = APIRouter(prefix="/projects/{project_id}/export", tags=["export"])


@router.get("", response_model=dict)
async def list_exports(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """List available export formats for a project."""
    return {
        "success": True,
        "data": {
            "formats": [
                {"format": "markdown", "label": "Documentation", "description": "Complete documentation package as Markdown", "content_type": "text/markdown"},
                {"format": "json", "label": "Blueprint JSON", "description": "Project data as JSON", "content_type": "application/json"},
            ],
        },
        "message": "Operation successful",
    }


@router.get("/download", response_class=PlainTextResponse)
async def download_export(
    project_id: str,
    format: str = Query("markdown", pattern="^(markdown|json)$"),
    db: AsyncSession = Depends(get_db),
):
    """Download project in the specified format."""
    docs = await get_documentation(db, project_id)

    if format == "json":
        content = export_json(docs)
        content_type = "application/json"
        filename = get_export_filename(project_id[:8], "json")
    else:
        # Combine all docs into a single markdown file
        parts = []
        for doc in docs.get("documents", []):
            parts.append(f"# {doc.get('title', '')}\n\n")
            parts.append(doc.get("content", ""))
            parts.append("\n\n---\n\n")
        content = "".join(parts)
        content_type = "text/markdown"
        filename = get_export_filename(project_id[:8], "md")

    return PlainTextResponse(
        content=content,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": content_type,
        },
    )
