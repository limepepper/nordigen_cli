import json
from pathlib import Path

from api.models.tokens import JWTConfig
from limepepper_utils.jwt.utils import random_hex_string
from limepepper_utils.xdg import XDGBasedir

from nordigen_cli import __app_name__


class Config:
    DEBUG = False
    TESTING = False

    @staticmethod
    def get_handler():
        return JWTConfig(**Config._load_mock_config())

    default_config = {
        "SECRET_KEY": random_hex_string(length=32),
        "ISSUER": "nordigen-mock-api",
        "AUDIENCE": "nordigen-clients",
    }

    @staticmethod
    def _load_mock_config():
        mock_config = Path(XDGBasedir.get_app_dir(__app_name__)) / "mock.json"
        if not mock_config.parent.exists():
            mock_config.parent.mkdir(exist_ok=True, parents=True)
        if not mock_config.exists():
            with open(mock_config, "w") as f:
                json.dump(Config.default_config, f, indent=4)
        with open(mock_config) as f:
            return json.load(f)
