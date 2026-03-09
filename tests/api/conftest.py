"""API 테스트 공통 fixtures."""

import os

import pytest
from pytest_socket import _remove_restrictions


@pytest.fixture(autouse=True)
def allow_real_socket():
    """API 테스트에서 외부 소켓 허용."""
    _remove_restrictions()
    yield


@pytest.fixture
def api_key() -> str:
    """API 서비스 키."""
    key = os.environ.get("GBUS_API_KEY")
    if not key:
        pytest.skip("GBUS_API_KEY 환경변수가 설정되지 않음")
    return key
