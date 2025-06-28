from auth.authentication import Auth


class TestAuthentication:
    """Test authentication utilities."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword"
        hashed = Auth.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert Auth.check_password(password, hashed)

    def test_check_password_correct(self):
        """Test correct password verification."""
        password = "testpassword"
        hashed = Auth.hash_password(password)

        assert Auth.check_password(password, hashed) is True

    def test_check_password_incorrect(self):
        """Test incorrect password verification."""
        password = "testpassword"
        wrong_password = "wrongpassword"
        hashed = Auth.hash_password(password)

        assert Auth.check_password(wrong_password, hashed) is False

    def test_different_hashes_same_password(self):
        """Test that same password produces different hashes."""
        password = "testpassword"
        hash1 = Auth.hash_password(password)
        hash2 = Auth.hash_password(password)

        assert hash1 != hash2
        assert Auth.check_password(password, hash1)
        assert Auth.check_password(password, hash2)
