class TestAuthServices:
    """Test authentication services."""

    def test_create_access_token(self, create_test_user, db_session):
        """Test access token creation."""
        user = create_test_user()
        data = {"username": user.username, "user_id": str(user.id)}

        from auth.services import create_access_token

        token = create_access_token(data, user.secret_key)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, create_test_user, db_session):
        """Test refresh token creation."""
        user = create_test_user()
        data = {"username": user.username, "user_id": str(user.id)}

        from auth.services import create_access_token

        token = create_access_token(data, user.secret_key, refresh=True)

        assert token is not None
        assert isinstance(token, str)
