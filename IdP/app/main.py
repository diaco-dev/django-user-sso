# main.py - FastAPI application
from fastapi import FastAPI, Depends, HTTPException, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
import json
from uuid import UUID
from .database import get_db, engine
from .models import Base, User, OAuth2Client, AuthorizationCode, Token
from .schemas import *
from .auth import *
from .config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OAuth Identity Provider",
    description="Production-ready OAuth 2.0 Identity Provider with Role-based Access Control",
    version="1.0.0"
)
from app.integrated_login import router as auth_router  # وارد کردن router از فایل دیگر
app.include_router(auth_router)
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# User Registration Endpoint
@app.post("/register", response_model=UserResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# Client Registration Endpoint
@app.post("/register-client", response_model=ClientResponse)
async def register_client(client_data: ClientRegister, db: Session = Depends(get_db)):
    """Register a new OAuth client"""
    client_id = f"client_{secrets.token_urlsafe(16)}"
    client_secret = secrets.token_urlsafe(32)

    client = OAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        client_name=client_data.client_name,
        redirect_uris=json.dumps(client_data.redirect_uris),
        allowed_scopes=client_data.allowed_scopes
    )

    db.add(client)
    db.commit()

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "client_name": client_data.client_name,
        "redirect_uris": client_data.redirect_uris
    }


# OAuth Authorization Endpoint
# @app.get("/authorize")
# async def authorize(
#         client_id: str,
#         redirect_uri: str,
#         scope: str,
#         state: str,
#         response_type: str,
#         db: Session = Depends(get_db),
# ):
#     if response_type != "code":
#         raise HTTPException(status_code=400, detail="Invalid response_type")
#
#     client = db.query(OAuth2Client).filter(
#         OAuth2Client.client_id == client_id,
#         OAuth2Client.is_active == True
#     ).first()
#
#     if not client:
#         raise HTTPException(status_code=400, detail="Invalid client")
#
#     redirect_uris = json.loads(client.redirect_uris)
#     if redirect_uri not in redirect_uris:
#         raise HTTPException(status_code=400, detail="Invalid redirect URI")
#
#     return RedirectResponse(
#         url=f"/login?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"
#     )

# Replace the existing /authorize endpoint with this:
@app.post("/authorize", response_model=AuthorizeResponse)
async def authorize(request: AuthorizeRequest, db: Session = Depends(get_db)):
    """Validate OAuth client and return client info for frontend"""
    if request.response_type != "code":
        raise HTTPException(status_code=400, detail="Invalid response_type. Only 'code' is supported")

    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == request.client_id,
        OAuth2Client.is_active == True
    ).first()

    if not client:
        return AuthorizeResponse(
            client_valid=False,
            requested_scopes=[],
            state=request.state,
            message="Invalid client_id"
        )

    redirect_uris = json.loads(client.redirect_uris)
    if request.redirect_uri not in redirect_uris:
        return AuthorizeResponse(
            client_valid=False,
            client_name=client.client_name,
            requested_scopes=[],
            state=request.state,
            message="Invalid redirect_uri"
        )

    requested_scopes = request.scope.split(" ") if request.scope else []

    return AuthorizeResponse(
        client_valid=True,
        client_name=client.client_name,
        requested_scopes=requested_scopes,
        state=request.state,
        message="Client validation successful. Proceed with login."
    )
# Login endpoints (same as before but with role support)
# @app.get("/login", response_class=HTMLResponse)
# async def login_form(request: Request, client_id: str, redirect_uri: str, scope: str, state: str):
#     return templates.TemplateResponse(
#         "login.html",
#         {"request": request, "client_id": client_id, "redirect_uri": redirect_uri, "scope": scope, "state": state},
#     )
#
#
# @app.post("/login")
# async def login(
#         username: str = Form(...),
#         password: str = Form(...),
#         client_id: str = Form(...),
#         redirect_uri: str = Form(...),
#         scope: str = Form(...),
#         state: str = Form(...),
#         db: Session = Depends(get_db),
# ):
#     user = authenticate_user(db, username, password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#
#     # Update last login
#     user.last_login = datetime.utcnow()
#     db.commit()
#
#     code = generate_authorization_code(db, client_id, user.id, scope)
#
#     import urllib.parse
#     params = {'code': code, 'state': state}
#     query_string = urllib.parse.urlencode(params)
#     redirect_url = f"{redirect_uri}?{query_string}"
#
#     return RedirectResponse(url=redirect_url, status_code=302)
#

@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Direct login endpoint that returns tokens and user info"""

    # Authenticate user
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Generate tokens
    tokens = generate_tokens(db, request.client_id or "direct", user.id, request.scope, user.role.value)

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
        scope=tokens["scope"]
    )


# Add a new OAuth code generation endpoint:
@app.post("/oauth/authorize")
async def oauth_authorize(
        username: str = Form(...),
        password: str = Form(...),
        client_id: str = Form(...),
        redirect_uri: str = Form(...),
        scope: str = Form(...),
        state: str = Form(None),
        db: Session = Depends(get_db)
):
    """Generate authorization code for OAuth flow (for compatibility with existing OAuth clients)"""

    # Validate client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id,
        OAuth2Client.is_active == True
    ).first()

    if not client:
        raise HTTPException(status_code=400, detail="Invalid client")

    redirect_uris = json.loads(client.redirect_uris)
    if redirect_uri not in redirect_uris:
        raise HTTPException(status_code=400, detail="Invalid redirect URI")

    # Authenticate user
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Generate authorization code
    code = generate_authorization_code(db, client_id, user.id, scope)

    # Return JSON instead of redirect
    return {
        "code": code,
        "state": state,
        "redirect_uri": redirect_uri,
        "message": "Authorization code generated successfully"
    }


# Add refresh token endpoint:
@app.post("/refresh")
async def refresh_token(
        refresh_token: str = Form(...),
        client_id: str = Form(None),
        client_secret: str = Form(None),
        db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""

    token_obj = db.query(Token).filter(Token.refresh_token == refresh_token).first()
    if not token_obj or token_obj.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired refresh token")

    # Validate client if provided
    if client_id and client_secret:
        if not validate_client(db, client_id, client_secret):
            raise HTTPException(status_code=401, detail="Invalid client credentials")

    user = db.query(User).filter(User.id == token_obj.user_id).first()
    if not user or user.status != "active":
        raise HTTPException(status_code=401, detail="User not active")

    # Generate new tokens
    new_tokens = generate_tokens(db, token_obj.client_id, token_obj.user_id, token_obj.scope, user.role.value)

    # Delete old refresh token
    db.delete(token_obj)
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

    return {
        "access_token": new_tokens["access_token"],
        "refresh_token": new_tokens["refresh_token"],
        "expires_in": new_tokens["expires_in"],
        "token_type": new_tokens["token_type"],
        "scope": new_tokens["scope"],
        "user": user_info
    }



# Token endpoint with role support
# @app.post("/token", response_model=TokenResponse)
# async def token(
#         request: Request,
#         db: Session = Depends(get_db),
#         grant_type: str = Form(None),
#         code: str = Form(None),
#         refresh_token: str = Form(None),
#         client_id: str = Form(None),
#         client_secret: str = Form(None),
#         redirect_uri: str = Form(None),
# ):
#     # Handle JSON requests
#     if not grant_type:
#         try:
#             json_data = await request.json()
#             grant_type = json_data.get("grant_type")
#             code = json_data.get("code")
#             refresh_token = json_data.get("refresh_token")
#             client_id = json_data.get("client_id")
#             client_secret = json_data.get("client_secret")
#             redirect_uri = json_data.get("redirect_uri")
#         except:
#             pass
#
#     if not grant_type:
#         raise HTTPException(status_code=400, detail="Missing grant_type")
#
#     if grant_type == "authorization_code":
#         if not code or not client_id or not client_secret:
#             raise HTTPException(status_code=400, detail="Missing required parameters")
#
#         auth_code = db.query(AuthorizationCode).filter(
#             AuthorizationCode.code == code,
#             AuthorizationCode.used == False
#         ).first()
#
#         if not auth_code or auth_code.expires_at < datetime.utcnow():
#             raise HTTPException(status_code=400, detail="Invalid or expired code")
#
#         if not validate_client(db, client_id, client_secret):
#             raise HTTPException(status_code=401, detail="Invalid client credentials")
#
#         user = db.query(User).filter(User.id == auth_code.user_id).first()
#         tokens = generate_tokens(db, client_id, auth_code.user_id, auth_code.scope, user.role.value)
#
#         # Mark code as used
#         auth_code.used = True
#         db.commit()
#
#         return tokens
#
#     elif grant_type == "refresh_token":
#         if not refresh_token or not client_id or not client_secret:
#             raise HTTPException(status_code=400, detail="Missing required parameters")
#
#         token_obj = db.query(Token).filter(Token.refresh_token == refresh_token).first()
#         if not token_obj or token_obj.expires_at < datetime.utcnow():
#             raise HTTPException(status_code=400, detail="Invalid or expired refresh token")
#
#         if not validate_client(db, client_id, client_secret):
#             raise HTTPException(status_code=401, detail="Invalid client credentials")
#
#         user = db.query(User).filter(User.id == token_obj.user_id).first()
#         tokens = generate_tokens(db, client_id, token_obj.user_id, token_obj.scope, user.role.value)
#
#         db.delete(token_obj)
#         db.commit()
#
#         return tokens
#
#     raise HTTPException(status_code=400, detail="Unsupported grant type")


# Update the existing token endpoint to also return user info:
@app.post("/token", response_model=LoginResponse)  # Changed response model
async def token(
        request: Request,
        db: Session = Depends(get_db),
        grant_type: str = Form(None),
        code: str = Form(None),
        refresh_token: str = Form(None),
        client_id: str = Form(None),
        client_secret: str = Form(None),
        redirect_uri: str = Form(None),
):
    """Enhanced token endpoint that returns user info along with tokens"""

    # Handle JSON requests
    if not grant_type:
        try:
            json_data = await request.json()
            grant_type = json_data.get("grant_type")
            code = json_data.get("code")
            refresh_token = json_data.get("refresh_token")
            client_id = json_data.get("client_id")
            client_secret = json_data.get("client_secret")
            redirect_uri = json_data.get("redirect_uri")
        except:
            pass

    if not grant_type:
        raise HTTPException(status_code=400, detail="Missing grant_type")

    if grant_type == "authorization_code":
        if not code or not client_id or not client_secret:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        auth_code = db.query(AuthorizationCode).filter(
            AuthorizationCode.code == code,
            AuthorizationCode.used == False
        ).first()

        if not auth_code or auth_code.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Invalid or expired code")

        if not validate_client(db, client_id, client_secret):
            raise HTTPException(status_code=401, detail="Invalid client credentials")

        user = db.query(User).filter(User.id == auth_code.user_id).first()
        tokens = generate_tokens(db, client_id, auth_code.user_id, auth_code.scope, user.role.value)

        # Mark code as used
        auth_code.used = True
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
            scope=tokens["scope"]
        )

    elif grant_type == "refresh_token":
        if not refresh_token or not client_id or not client_secret:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        token_obj = db.query(Token).filter(Token.refresh_token == refresh_token).first()
        if not token_obj or token_obj.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Invalid or expired refresh token")

        if not validate_client(db, client_id, client_secret):
            raise HTTPException(status_code=401, detail="Invalid client credentials")

        user = db.query(User).filter(User.id == token_obj.user_id).first()
        tokens = generate_tokens(db, client_id, token_obj.user_id, token_obj.scope, user.role.value)

        db.delete(token_obj)
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
            scope=tokens["scope"]
        )

# UserInfo endpoint with role information
@app.get("/userinfo", response_model=UserInfo)
async def userinfo(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, public_key, algorithms=[settings.ALGORITHM])
        user = db.query(User).filter(User.id == UUID(payload["sub"])).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return UserInfo(
            sub=str(user.id),
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            status=user.status.value
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# JWKS endpoint
@app.get("/.well-known/jwks.json")
async def jwks():
    public_numbers = public_key.public_numbers()

    # Convert integers to base64url
    import base64

    def int_to_base64url(val):
        byte_length = (val.bit_length() + 7) // 8
        bytes_val = val.to_bytes(byte_length, 'big')
        return base64.urlsafe_b64encode(bytes_val).decode('ascii').rstrip('=')

    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "n": int_to_base64url(public_numbers.n),
                "e": int_to_base64url(public_numbers.e),
            }
        ]
    }


# Admin endpoints for user management
@app.get("/admin/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    """Admin endpoint to list all users"""
    users = db.query(User).all()
    return users


@app.put("/admin/users/{user_id}/role")
async def update_user_role(user_id: int, role: UserRoleSchema, db: Session = Depends(get_db)):
    """Admin endpoint to update user role"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "User role updated successfully"}


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}