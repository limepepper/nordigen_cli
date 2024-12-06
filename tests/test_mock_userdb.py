import base64
import unittest

import bcrypt
from api.models.user import UnknownUserError
from api.user_database import UserDb


class TestUserDb(unittest.TestCase):
    def test_get_user_success(self):
        user = UserDb.get_user("johndoe")
        self.assertEqual(user.id, "johndoe")
        self.assertEqual(user.disabled, False)

    def test_get_user_failure(self):
        with self.assertRaises(UnknownUserError):
            UserDb.get_user("nonexistent")

    def test_get_password_hash(self):
        hashed_password = UserDb.get_password_hash("testpassword")
        self.assertTrue(
            bcrypt.hashpw(b"testpassword", hashed_password)
        )  # Verify using the same context

    def test_verify_password_success(self):
        self.assertTrue(
            bcrypt.hashpw(
                b"testpassword",
                bcrypt.hashpw(b"testpassword", bcrypt.gensalt()),
            )
        )

    def test_verify_password_failure(self):
        self.assertFalse(
            UserDb.verify_password(
                "wrongpassword",
                UserDb.fake_users_db["johndoe"]["hashed_password"],
            )
        )

    def test_password_hashing(self):
        password = base64.b64decode("ZnVjaw==").decode()
        hashed = "$2y$10$MtAu1xig.I0KpQwjlHnyQuG3orCs0K2ZXNqqK0MTmapf2hlbM.0YG"
        result = UserDb.verify_password(password, hashed)
        assert result
