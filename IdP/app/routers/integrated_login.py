from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
import json
import secrets

from app.core.authentication import authenticate_user, generate_authorization_code, generate_tokens, generate_tokens_role
from app.core.database import get_db
from app.models import OAuth2Client, AuthorizationCode
from app.schemas import LoginResponse, LoginRequest
from app.core.config import settings
router = APIRouter()


class IntegratedLoginRequest(BaseModel):
    username: str
    password: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: Optional[str] = None
    state: Optional[str] = None


CLIENT_ID = settings.oauth_client_id
CLIENT_SECRET = settings.oauth_client_secret
REDIRECT_URI = settings.oauth_redirect_uri
@router.post("/integrated_login", response_model=LoginResponse)
async def integrated_login(payload: LoginRequest, db: Session = Depends(get_db)):
    username = payload.username
    password = payload.password
    scope = payload.scope
    """Integrated login endpoint that authenticates user, validates client, and returns tokens"""

    # Generate state for CSRF protection
    generated_state = secrets.token_urlsafe(32)

    # Validate client (from env, not frontend)
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == CLIENT_ID,
        OAuth2Client.is_active == True
    ).first()

    if not client:
        raise HTTPException(status_code=400, detail="Invalid client_id")

    if client.client_secret != CLIENT_SECRET:
        raise HTTPException(status_code=401, detail="Invalid server client_secret")

    redirect_uris = json.loads(client.redirect_uris)
    if REDIRECT_URI not in redirect_uris:
        raise HTTPException(status_code=400, detail="Invalid server redirect_uri")

    # Authenticate user
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if user.status != "active":
        raise HTTPException(status_code=401, detail="User not active")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Generate authorization code internally
    auth_code = generate_authorization_code(db, CLIENT_ID, user.id, scope)


    # Exchange code for tokens internally
    tokens = generate_tokens(db, CLIENT_ID, user.id, scope, user.role.value)

    # Mark code as used
    code_obj = db.query(AuthorizationCode).filter(
        AuthorizationCode.code == auth_code
    ).first()
    if code_obj:
        code_obj.used = True
        db.commit()

    # Prepare user info
    user_info = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.value,
        "status": user.status.value
    }

    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
        token_type=tokens["token_type"],
        user=user_info,
        scope=tokens["scope"],
        state=generated_state
    )


ROLE_REDIRECTS = {
    "admin": "http://localhost:3000/admin-dashboard",
    "staff": "http://localhost:3000/staff-dashboard",
    "user": "http://localhost:8001/home/",
}
@router.post("/role_login", response_model=LoginResponse)
async def role_login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint with role-based redirect and audience in token"""

    # Authenticate user
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if user.status != "active":
        raise HTTPException(status_code=403, detail="User not active")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Role & redirect
    role = user.role.value
    redirect_url = ROLE_REDIRECTS.get(role)
    if not redirect_url:
        raise HTTPException(status_code=400, detail="No panel defined for this role")

    # Generate authorization code internally (optional, keep for SSO flow)
    auth_code = generate_authorization_code(db, settings.oauth_client_id, user.id, payload.scope)

    # Generate tokens with audience = role/panel
    tokens = generate_tokens_role(
        db=db,
        client_id=settings.oauth_client_id,
        user_id=user.id,
        scope=payload.scope,
        role=role,
        audience=role
    )

    # Mark code as used
    code_obj = db.query(AuthorizationCode).filter(
        AuthorizationCode.code == auth_code
    ).first()
    if code_obj:
        code_obj.used = True
        db.commit()

    # Prepare user info
    user_info = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": role,
        "status": user.status.value
    }

    # Generate CSRF state if not provided
    state = payload.state or secrets.token_urlsafe(32)

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_in": tokens["expires_in"],
        "token_type": "Bearer",
        "user": user_info,
        "scope": tokens["scope"],
        "state": state,
        "redirect_url": redirect_url,   # <-- SPA می‌تونه مستقیم redirect کنه
    }