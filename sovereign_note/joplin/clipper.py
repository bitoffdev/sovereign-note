class JoplinWebClipperClient:
    def __init__(self, base_url: str, auth_token: str):
        self._base_url = base_url
        self._auth_token = auth_token
        self.check_config()

    @classmethod
    def create_local(cls, auth_token: str):
        return cls("http://localhost:41184", auth_token)

    def check_config(self):
        response = requests.get(f"{self._base_url}/ping")
        assert response.content == b"JoplinClipperServer"

    def list_notes(self):
        response = requests.get(
            f"{self._base_url}/notes", params={"token": self._auth_token}
        )
        return response.json()
