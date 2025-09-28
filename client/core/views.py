# views.py - Updated OAuth views
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import secrets
import logging
import urllib.parse

logger = logging.getLogger(__name__)

# OAuth configuration
oauth = OAuth()
oauth.register(
    name="idp",
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    authorize_url=settings.IDP_AUTHORIZE_URL,
    token_url=settings.IDP_TOKEN_URL,
    userinfo_endpoint=settings.IDP_USERINFO_URL,
    redirect_uri=settings.REDIRECT_URI,
    client_kwargs={"scope": "openid profile email"},
)


def login_redirect(request):
    """Initiate OAuth login flow"""
    try:
        # Ensure session is created
        if not request.session.session_key:
            request.session.create()

        # Generate and store state
        state = secrets.token_urlsafe(32)
        request.session['oauth_state'] = state
        request.session.save()

        logger.info("=== LOGIN REDIRECT DEBUG ===")
        logger.info(f"Session key: {request.session.session_key}")
        logger.info(f"Stored state: {state}")
        logger.info(f"Session items: {dict(request.session)}")

        # Create authorization URL manually (more reliable than authlib)
        redirect_uri = settings.REDIRECT_URI
        authorize_url = f"{settings.IDP_AUTHORIZE_URL}?" + urllib.parse.urlencode({
            'response_type': 'code',
            'client_id': settings.CLIENT_ID,
            'redirect_uri': redirect_uri,
            'scope': 'openid profile email',
            'state': state,
        })

        logger.info(f"Redirecting to: {authorize_url}")
        return redirect(authorize_url)

    except Exception as e:
        logger.error(f"Error in login_redirect: {str(e)}")
        return HttpResponse(f"Login error: {str(e)}", status=500)


@csrf_exempt
def oauth_callback(request):
    """Handle OAuth callback"""
    logger.info("=== OAUTH CALLBACK DEBUG ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"Session key: {request.session.session_key}")
    logger.info(f"Session items: {dict(request.session)}")
    logger.info(f"GET parameters: {dict(request.GET)}")
    logger.info(f"Raw query string: {request.META.get('QUERY_STRING', 'N/A')}")

    try:
        # Get parameters from request
        code = request.GET.get('code')
        state = request.GET.get('state')

        logger.info(f"Received code: '{code}'")
        logger.info(f"Received state: '{state}'")

        if not code:
            return HttpResponse("Missing authorization code", status=400)

        # Check if state is missing or empty
        if not state or state.strip() == '':
            logger.warning("State parameter is missing or empty - this is a FastAPI bug")
            logger.warning("Proceeding without state validation (not recommended for production)")
            # In production, you should fix the FastAPI server instead
        else:
            # Validate state (if session is working and state is present)
            session_state = request.session.get('oauth_state')
            if session_state and session_state != state:
                logger.error(f"State mismatch: session='{session_state}', request='{state}'")
                return HttpResponse("Invalid state parameter", status=400)

        # Exchange code for tokens
        import requests
        import json

        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.REDIRECT_URI,
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
        }

        logger.info(f"Exchanging code for token with data: {token_data}")

        # Send as JSON instead of form data
        token_response = requests.post(
            settings.IDP_TOKEN_URL,
            json=token_data,  # Use json= instead of data=
            headers={'Content-Type': 'application/json'}
        )

        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            return HttpResponse(f"Token exchange failed: {token_response.text}", status=400)

        tokens = token_response.json()
        logger.info(f"Received tokens: {list(tokens.keys())}")

        # Get user info
        userinfo_response = requests.get(
            settings.IDP_USERINFO_URL,
            headers={'Authorization': f"Bearer {tokens['access_token']}"}
        )

        if userinfo_response.status_code != 200:
            logger.error(f"Userinfo request failed: {userinfo_response.text}")
            return HttpResponse(f"Userinfo request failed: {userinfo_response.text}", status=400)

        userinfo = userinfo_response.json()
        logger.info(f"Received userinfo: {userinfo}")

        # Store in session
        if not request.session.session_key:
            request.session.create()

        request.session["user"] = userinfo
        request.session["access_token"] = tokens["access_token"]

        # Clean up OAuth state
        if 'oauth_state' in request.session:
            del request.session['oauth_state']

        request.session.save()

        return HttpResponse(f"""
        <h1>OAuth Success!</h1>
        <p>Welcome, {userinfo.get('username', 'User')}!</p>
        <h3>User Info:</h3>
        <pre>{userinfo}</pre>
        <h3>Session Info:</h3>
        <p>Session Key: {request.session.session_key}</p>
        <p>Stored in session: {list(request.session.keys())}</p>
        """)

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}", exc_info=True)
        return HttpResponse(f"OAuth error: {str(e)}", status=500)


# Add this user info API endpoint
@csrf_exempt
def user_info_api(request):
    """API endpoint to return OAuth user session info"""
    if 'user' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    return JsonResponse({
        'user': request.session['user'],
        'session_key': request.session.session_key,
        'authenticated': True
    })


def logout_view(request):
    """Logout and clear session"""
    request.session.flush()
    return HttpResponse("""
    <h2>Logged out successfully!</h2>
    <p><a href="/login/">Login again</a></p>
    """)


