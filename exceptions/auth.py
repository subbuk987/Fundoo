class AuthError(Exception):
    """Custom exception for auth errors"""

    def __init__(self, message):
        self.message = message


class InvalidToken(AuthError):
    """Custom exception for Invalid Token Errors"""

class AccessTokenRequired(AuthError):
    """Custom exception for access token required"""

class RefreshTokenRequired(AuthError):
    """Custom exception for refresh token required"""