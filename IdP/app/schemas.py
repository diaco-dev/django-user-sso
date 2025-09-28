# schemas.py - Pydantic models
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserRoleSchema(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"

class UserStatusSchema(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRoleSchema] = UserRoleSchema.USER

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: UserRoleSchema
    status: UserStatusSchema
    created_at: datetime
    last_login: Optional[datetime]

class TokenRequest(BaseModel):
    grant_type: str
    code: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: str
    client_secret: str
    redirect_uri: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"
    scope: str

class UserInfo(BaseModel):
    sub: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    status: str

class ClientRegister(BaseModel):
    client_name: str
    redirect_uris: List[str]
    allowed_scopes: Optional[str] = "openid profile email"

class ClientResponse(BaseModel):
    client_id: str
    client_secret: str
    client_name: str
    redirect_uris: List[str]


class LoginRequest(BaseModel):
    username: str
    password: str
    client_id: Optional[str] = None
    scope: Optional[str] = "openid profile email"

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"
    user: dict
    scope: str

class AuthorizeRequest(BaseModel):
    client_id: str
    redirect_uri: str
    scope: str = "openid profile email"
    response_type: str = "code"
    state: Optional[str] = None

class AuthorizeResponse(BaseModel):
    client_valid: bool
    client_name: Optional[str] = None
    requested_scopes: list
    state: Optional[str] = None
    message: str