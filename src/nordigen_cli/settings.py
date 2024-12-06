from pathlib import Path

from fast_api.config import FormatChoices
from pydantic_settings import BaseSettings


class SettingsRuntime(BaseSettings):
    api: str
    secret_id: str
    secret_key: str
    access_token_file: Path
    refresh_token_file: Path
    verbose: int = 1
    output_format: FormatChoices

    def is_valid(self):
        return all(
            [
                self.api,
                self.secret_id,
                self.secret_key,
                self.access_token_file,
                self.refresh_token_file,
            ]
        )
