import bcrypt
from loguru import logger

from api.models.user import UnknownUserError, UserInDB

#


class BadSaltError(Exception):
    pass


class UserDb:
    fake_users_db = {
        "johndoe": {
            "id": "johndoe",
            "hashed_password": (
                "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
            ),
            "disabled": False,
        },
        "alice": {
            "id": "alice",
            "full_name": "Alice Wonderson",
            "hashed_password": "fakehashedsecret2",
            "disabled": True,
        },
        "716642b2-977f-4ca9-a723-f36b84676c89": {
            "id": "716642b2-977f-4ca9-a723-f36b84676c89",
            "full_name": "Alice Wonderson",
            "hashed_password": "fakehashedsecret2",
            "disabled": True,
        },
        "fcc71b93-ac1c-4dda-81ac-4402ca9a455e": {
            "id": "fcc71b93-ac1c-4dda-81ac-4402ca9a455e",
            "full_name": "This user is disabled",
            "hashed_password": (
                "$2y$10$plIE5GI1l6GYy.o.L1Mhb.TQdVp.IfRd4kyLLq4dVutS058zUCL2y"
            ),
            "disabled": True,
        },
        "6cbb24a6-28b9-441e-9184-3e93d6497594": {
            "id": "6cbb24a6-28b9-441e-9184-3e93d6497594",
            "full_name": "This user is good",
            "hashed_password": (
                "$2y$10$uiy/tSwUATKi1Qay4ZdMoe73ycdH83dp5WRv873ya7rXTqkVe4vO2"
            ),
            "disabled": False,
        },
        "7946d2f5-f7d2-4f25-8d01-f1a9434e0b6f": {
            "id": "7946d2f5-f7d2-4f25-8d01-f1a9434e0b6f",
            "full_name": "This user is good to go",
            "hashed_password": (
                "$2y$10$j4VGKJCkCTjSYmhA5ot9m.deZ5Sc29lJA4eJPwnbobRCT6qicyNye"
            ),
            "disabled": False,
        },
    }

    @classmethod
    def get_user(cls, id: str) -> UserInDB:
        if id in cls.fake_users_db:
            user_dict = cls.fake_users_db[id]
            return UserInDB(**user_dict)
        raise UnknownUserError(id)

    # @classmethod
    # def get_password_hash(cls, password):
    #     return cls.pwd_context.hash(password)

    @classmethod
    def get_password_hash(cls, password):
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        string_password = hashed_password
        return string_password

    # @classmethod
    # def verify_password(cls, plain_password, hashed_password):
    #     return bcrypt.checkpw(
    #         plain_password.encode("utf-8"), hashed_password.encode("utf8")
    #     )

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        password_byte_enc = plain_password.encode("utf-8")
        hashed_password = hashed_password.encode("utf-8")
        try:
            return bcrypt.checkpw(password_byte_enc, hashed_password)
        except ValueError as exc:
            logger.debug(f"Error verifying password: {exc}")
            raise BadSaltError(exc) from exc
