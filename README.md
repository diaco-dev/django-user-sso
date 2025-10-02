# SSO Authentication Gateway

The SSO Authentication Gateway is a production-ready authentication solution designed to provide secure Single Sign-On (SSO) functionality across multiple subdomains. Built with **FastAPI**, it leverages **JWT (RS256)** and **cookie-based authentication** to support role-based redirects, token management, and robust security practices, ensuring a seamless and secure user experience.

## Features

- **Role-Based Authentication and Redirection**  
  Redirects users to role-specific subdomains (e.g., `staff.yourdomain.com`, `admin.yourdomain.com`) upon successful login.
- **JWT Access Tokens**  
  Short-lived tokens signed with the **RS256** algorithm using public/private key pairs for enhanced security.
- **Refresh Tokens**  
  Long-lived tokens stored as SHA-256 hashes in the database, supporting rotation and revocation to prevent replay attacks.
- **HttpOnly Cookies**  
  Tokens are stored in cookies with the following attributes:  
  - `HttpOnly` to prevent client-side script access  
  - `Secure` to ensure transmission over HTTPS  
  - `SameSite=None` to enable cross-subdomain functionality  
  - `Domain=.yourdomain.com` for seamless subdomain sharing  
- **Logout Functionality**  
  Revokes refresh tokens and clears cookies to terminate user sessions securely.
- **CSRF Protection**  
  Optional CSRF tokens for state-changing requests to mitigate cross-site request forgery attacks.
- **Rate Limiting**  
  Protects the login endpoint against brute-force attacks.
- **JWKS Endpoint**  
  Exposes public keys for token verification across services.
- **Production-Ready Security**  
  Enforces HTTPS, implements HTTP Strict Transport Security (HSTS), includes secure headers, and maintains audit logs.

## Technology Stack

- **FastAPI**: High-performance Python framework for building the API.  
- **PostgreSQL**: Relational database for storing user and token data.  
- **Redis**: Optional in-memory store for token blacklisting and session revocation.  
- **SQLAlchemy**: Object-Relational Mapping (ORM) for database interactions.  
- **Python-Jose**: Library for JWT signing and validation.  
- **Nginx**: Configured for TLS termination and reverse proxy functionality.

## Project Structure

```
sso-auth-gateway/
│
├── app/
│   ├── main.py             # FastAPI application entry point
│   ├── auth.py            # JWT and token management utilities
│   ├── routes/
│   │   ├── auth.py        # Endpoints for login, refresh, and logout
│   │   └── jwks.py        # JWKS endpoint for public key exposure
│   ├── models.py          # SQLAlchemy models (User, RefreshToken)
│   ├── deps.py            # Authentication dependencies
│   └── config.py          # Configuration settings loaded from .env
│
├── migrations/            # Alembic database migration scripts
├── .env.example           # Example environment variable configuration
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Environment Variables

The project relies on environment variables for configuration. Below is an example configuration based on `.env.example`:

```env
# JWT Configuration
JWT_PRIVATE_KEY_PATH=/run/secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=/run/secrets/jwt_public.pem
JWT_ALGORITHM=RS256

# Token Expiry
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Cookie Settings
COOKIE_DOMAIN=.yourdomain.com
COOKIE_SECURE=true

# Database and Redis Connections
DATABASE_URL=postgresql://user:pass@localhost:5432/sso_db
REDIS_URL=redis://localhost:6379/0
```

## Authentication Flow

1. **Login**  
   - **Request**: `POST /api/login` with username and password.  
   - **Process**: The backend verifies credentials and determines the user's role.  
   - **Response**: Generates access and refresh tokens, sets them in HttpOnly cookies, and returns a redirect URL for the role-specific panel.  

2. **Accessing Protected Routes**  
   - The browser automatically sends the access token cookie with each request.  
   - The backend validates the JWT for every protected endpoint.  

3. **Token Refresh**  
   - **Request**: `POST /api/refresh` when the access token expires.  
   - **Process**: The refresh token is validated, rotated, and new access and refresh tokens are issued.  

4. **Logout**  
   - **Request**: `POST /api/logout`.  
   - **Process**: Revokes the refresh token and clears cookies to terminate the session.

## Running the Project Locally

Follow these steps to set up and run the project on a local development environment:

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-org/sso-auth-gateway.git
   cd sso-auth-gateway
   ```

2. **Create a Virtual Environment**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Database Migrations**  
   ```bash
   alembic upgrade head
   ```

5. **Start the Development Server**  
   ```bash
   uvicorn app.main:app --reload
   ```

## Security Checklist

The following security measures are implemented to ensure a robust and secure system:

- ✅ **HTTPS Enforcement**: TLS is mandatory in production environments.  
- ✅ **HSTS Headers**: Enforces secure connections over time.  
- ✅ **Rate Limiting**: Protects the login endpoint from brute-force attacks.  
- ✅ **Refresh Token Rotation and Revocation**: Prevents token reuse and ensures session invalidation.  
- ✅ **Secure Cookies**: Configured with `HttpOnly`, `Secure`, `SameSite=None`, and `Domain=.yourdomain.com`.  
- ✅ **Key Management**: Cryptographic keys are stored securely in a secret manager, not in version control.
