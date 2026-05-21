from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/bootstrap", response_model=TokenResponse)
async def bootstrap(data: UserCreate, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    return await AuthService(session).bootstrap_owner(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    return await AuthService(session).login(data.email, data.password)
