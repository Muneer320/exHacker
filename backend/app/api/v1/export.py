"""Export API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.export import export_markdown, export_json, get_export_filename
from app.services.blueprint.coordinator import generate_blueprint
from app.services.project import get_project

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
                {"format": "markdown", "label": "README.md", "description": "Complete project blueprint as Markdown", "content_type": "text/markdown"},
                {"format": "json", "label": "blueprint.json", "description": "Raw blueprint data as JSON", "content_type": "application/json"},
            ],
        },
        "message": "Operation successful",
    }


@router.get("/download", response_class=PlainTextResponse)
async def download_export(
    project_id: str,
    format: str = Query("markdown", regex="^(markdown|json)$"),
    db: AsyncSession = Depends(get_db),
):
    """Download project blueprint in the specified format."""
    project = await get_project(db, project_id)
    blueprint = await generate_blueprint(idea=project.idea, enrich_architecture=False)

    content_type = "text/markdown"
    filename = get_export_filename(project.name, "md")

    if format == "json":
        content = export_json(blueprint)
        content_type = "application/json"
        filename = get_export_filename(project.name, "json")
    else:
        content = export_markdown(project.idea, blueprint, project.name)

    return PlainTextResponse(
        content=content,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": content_type,
        },
    )
