from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Branch, Organization, Role, Subscription, User
from app.schemas.auth import TokenResponse, UserCreate


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bootstrap_owner(self, data: UserCreate) -> TokenResponse:
        existing = await self.session.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        settings = get_settings()
        organization = Organization(name=data.organization_name, industry="healthcare_office")
        role = Role(
            name=f"{data.organization_name}:owner",
            permissions={
                "devices": ["read", "write"],
                "printers": ["read", "write", "admin"],
                "remote_support": ["start", "control"],
                "subscriptions": ["read", "write"],
                "alerts": ["read", "acknowledge", "resolve"],
            },
        )
        self.session.add_all([organization, role])
        await self.session.flush()

        branch = Branch(
            organization_id=organization.id,
            name=data.branch_name,
            subnet_cidr=None,
        )
        user = User(
            organization_id=organization.id,
            role_id=role.id,
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
        )
        subscription = Subscription(
            organization_id=organization.id,
            trial_ends_at=datetime.now(UTC) + timedelta(days=settings.trial_days),
            device_limit=settings.trial_max_devices,
            feature_flags={
                "cloud_sync": False,
                "automation_scripts": False,
                "remote_support_minutes": settings.trial_remote_session_minutes,
                "label": "Trial Version",
            },
        )
        self.session.add_all([branch, user, subscription])
        await self.session.commit()
        return self._token_for_user(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        result = await self.session.execute(select(User).where(User.email == email, User.is_active.is_(True)))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return self._token_for_user(user)

    def _token_for_user(self, user: User) -> TokenResponse:
        token = create_access_token(
            str(user.id),
            {"organization_id": str(user.organization_id), "role_id": str(user.role_id) if user.role_id else None},
        )
        return TokenResponse(access_token=token, user_id=user.id, organization_id=user.organization_id)
