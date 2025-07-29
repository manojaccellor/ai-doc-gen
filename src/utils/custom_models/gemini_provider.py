from pydantic_ai.providers.google_gla import GoogleGLAProvider


class CustomGeminiGLA(GoogleGLAProvider):
    def __init__(self, api_key: str, base_url: str, *args, **kwargs) -> None:
        # Ensure the base URL ends with /v1beta for Gemini API
        if not base_url.endswith('/v1beta'):
            if base_url.endswith('/'):
                base_url = base_url.rstrip('/') + '/v1beta'
            else:
                base_url = base_url + '/v1beta'
        
        self._x_base_url = base_url
        super().__init__(api_key, *args, **kwargs)

    @property
    def base_url(self) -> str:
        return self._x_base_url
