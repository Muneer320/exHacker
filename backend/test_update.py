import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.project import Project

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Project).where(Project.id == '89dc6048-9fc7-480e-af77-ab6c40d920f2'))
        proj = result.scalar_one_or_none()
        print(f"Before: {proj.status}")
        proj.status = "researching"
        await session.commit()
        
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Project).where(Project.id == '89dc6048-9fc7-480e-af77-ab6c40d920f2'))
        proj = result.scalar_one_or_none()
        print(f"After: {proj.status}")

if __name__ == "__main__":
    asyncio.run(main())
