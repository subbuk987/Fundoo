class AuthError(Exception):
    """Custom exception for auth errors"""

    def __init__(self, message):
        self.message = message