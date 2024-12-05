import importlib
import json
import os
import socket
import threading
import time
import typing
from collections.abc import Generator
from contextlib import closing
from pathlib import Path

import pytest
import uvicorn
import yaml
from api.app import create_app
from api.auth import create_jwt_pair_for_uuid
from api.models.user import UserInDB
from loguru import logger
from starlette.responses import Response

logger.trace(f"in conftestenv var REQUESTS_DEBUGGER: {os.getenv('REQUESTS_DEBUGGER')}")

importlib.import_module("requests_debugger")


# def pytest_runtest_setup(item):
#     # called for running each test in 'a' directory
#     print("setting up", item)


def pytest_cmdline_main(config):
    # called for running each test in 'a' directory
    logger.trace("pytest_cmdline_main up", config)


class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")


@pytest.fixture(scope="module")
def test_app():
    return create_app()


@pytest.fixture(scope="module")
def free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        return port


@pytest.fixture(scope="module")
def test_server(test_app, free_port) -> Generator:
    def run_server():
        uvicorn.run(
            test_app,
            host="127.0.0.1",
            port=free_port,
            log_level="debug",
        )

    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()

    time.sleep(1)
    yield f"http://127.0.0.1:{free_port}"


@pytest.fixture
def config_file(tmp_path):
    return tmp_path / "config.json"


@pytest.fixture
def access_token_file(tmp_path):
    return tmp_path / "access.json"


@pytest.fixture
def refresh_token_file(tmp_path):
    return tmp_path / "refresh.json"


@pytest.fixture(scope="module")
def test_data():
    conf = yaml.safe_load(Path("tests/data/users.yml").read_text())
    return {item["name"]: UserInDB(**item) for item in conf["users"]}


@pytest.fixture(scope="module")
def good_user_and_tokens(test_data):
    user = test_data["good_user"]
    access_token, refresh_token = create_jwt_pair_for_uuid(
        uuid=user.id,
        expiry_delta_sec=3600,
    )
    return user, access_token, refresh_token
