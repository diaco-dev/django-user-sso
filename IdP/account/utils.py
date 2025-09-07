def get_userinfo(user):
    """
    Return user information for OIDC UserInfo endpoint
    """
    return {
        'sub': str(user.id),
        'preferred_username': user.username,
        'email': user.email,
        'phone_number': user.phone_number,
    }