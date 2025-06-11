from fastapi import status


class UserNotFound(Exception):
    """Custom Exception for User not found"""

    def __init__(self, detail: str,
                 status_code: int = status.HTTP_404_NOT_FOUND):
        self.detail = detail
        self.status_code = status_code


class UserAlreadyExist(Exception):
    """Custom Exception for User already exists"""

    def __init__(self, detail: str,
                 status_code: int = status.HTTP_409_CONFLICT):
        self.detail = detail
        self.status_code = status_code
