import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status

from auth.services import create_access_token


class TestAuthRoutes:
    """Test authentication routes."""

    @pytest.mark.asyncio
    async def test_signup_success(
        self, client, sample_user_data, mock_redis, mock_celery
    ):
        """Test successful user signup."""
        response = client.post("/api/v1/auth/signup", json=sample_user_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "User created"
        assert data["payload"]["username"] == sample_user_data["username"]
        assert data["payload"]["email"] == sample_user_data["email"]
        assert "password" not in data["payload"]

    @pytest.mark.asyncio
    async def test_signup_duplicate_username(
        self, client, sample_user_data, create_test_user, mock_redis, mock_celery
    ):
        """Test signup with duplicate username."""
        create_test_user(username=sample_user_data["username"])

        response = client.post("/api/v1/auth/signup", json=sample_user_data)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "Username already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(
        self, client, sample_user_data, create_test_user, mock_redis, mock_celery
    ):
        """Test signup with duplicate email."""
        create_test_user(email=sample_user_data["email"])

        response = client.post("/api/v1/auth/signup", json=sample_user_data)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "Email already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_success(self, client, create_test_user, mock_redis):
        """Test successful login."""
        _ = create_test_user(username="testuser", password="testpass", is_verified=True)

        with patch("db.redis.cache_user_data", new_callable=AsyncMock), patch(
            "db.redis.cache_user_notes", new_callable=AsyncMock
        ), patch("db.redis.cache_user_labels", new_callable=AsyncMock):
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "testuser", "password": "testpass"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_username(self, client, mock_redis):
        """Test login with invalid username."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "testpass"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid username" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client, create_test_user, mock_redis):
        """Test login with invalid password."""
        create_test_user(username="testuser", password="testpass", is_verified=True)

        response = client.post(
            "/api/v1/auth/login", json={"username": "testuser", "password": "wrongpass"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid Password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_unverified_user(self, client, create_test_user, mock_redis):
        """Test login with unverified user."""
        create_test_user(username="testuser", password="testpass", is_verified=False)

        response = client.post(
            "/api/v1/auth/login", json={"username": "testuser", "password": "testpass"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "User Not Verified" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_refresh_token_with_access_token(
        self, client, auth_headers, mock_redis
    ):
        """Test refresh token endpoint with access token (should fail)."""
        headers, _ = auth_headers()

        response = client.get("/api/v1/auth/refresh_token", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token" in response.json()["detail"]


def test_print_token(auth_headers):
    headers, _ = auth_headers()
    print("🔐", headers)
