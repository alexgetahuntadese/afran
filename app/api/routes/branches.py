from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models import Branch, User
from app.schemas.branches import BranchRead, BranchUpdate

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("", response_model=list[BranchRead])
async def list_branches(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[BranchRead]:
    result = await session.execute(select(Branch).where(Branch.organization_id == user.organization_id))
    return list(result.scalars().all())


@router.patch("/{branch_id}", response_model=BranchRead)
async def update_branch(
    branch_id: UUID,
    data: BranchUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> BranchRead:
    branch = await session.get(Branch, branch_id)
    if branch is None or branch.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Branch not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(branch, key, value)
    await session.commit()
    return branch
