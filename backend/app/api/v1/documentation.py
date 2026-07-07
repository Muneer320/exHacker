"""Documentation API endpoints — S13 Documentation Writer (Bible §6.2 S13)."""
# pyright: reportGeneralTypeIssues=false

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.specialists import documentation_writer

router = APIRouter(prefix="/projects/{project_id}/docs", tags=["documentation"])


@router.post("", response_model=dict)
async def generate_docs(project_id: str, db: AsyncSession = Depends(get_db)):
    """Generate the complete documentation package (S13)."""
    result = await documentation_writer.generate_documentation(db, project_id)
    return {"success": True, "data": result, "message": "Documentation generated."}


@router.get("", response_model=dict)
async def get_docs(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get existing documentation."""
    result = await documentation_writer.get_documentation(db, project_id)
    return {"success": True, "data": result, "message": "Operation successful"}


@router.get("/{filename}")
async def get_doc_file(
    project_id: str,
    filename: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single documentation file as markdown."""
    result = await documentation_writer.get_documentation(db, project_id)
    for doc in result.get("documents", []):
        if doc.get("filename") == filename:
            return PlainTextResponse(doc.get("content", ""), media_type="text/markdown")
    return PlainTextResponse("# Not found\n\nDocument not found.", status_code=404, media_type="text/markdown")


@router.get("/download/all")
async def download_all(project_id: str, db: AsyncSession = Depends(get_db)):
    """Download all documentation as a combined markdown file."""
    result = await documentation_writer.get_documentation(db, project_id)
    parts = []
    for doc in result.get("documents", []):
        parts.append(f"---\n# {doc.get('title', '')}\n---\n")
        parts.append(doc.get("content", ""))
        parts.append("\n\n")
    content = "\n".join(parts)
    return PlainTextResponse(content, media_type="text/markdown", headers={
        "Content-Disposition": f"attachment; filename=exhacker-docs-{project_id[:8]}.md"
    })
