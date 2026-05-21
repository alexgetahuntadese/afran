from uuid import UUID

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    organization_id: UUID


class UserCreate(BaseModel):
    organization_name: str
    branch_name: str = "Main Branch"
    email: EmailStr
    full_name: str
    password: str
