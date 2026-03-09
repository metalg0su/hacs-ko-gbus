class GBusApiClientError(Exception):
    """API 에러 기본 클래스."""


class GBusApiClientCommunicationError(GBusApiClientError):
    """API 통신 에러."""


class GBusApiClientAuthenticationError(GBusApiClientError):
    """API 인증 에러."""
