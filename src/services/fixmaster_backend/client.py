from requests import get, post


class FixMasterClient:
    BASE_URL = 'http://localhost:8000/bot-api'
    GET_ACCOUNT_URL = BASE_URL + '/get-my-profile/'

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _post(self,request_url: str, body: dict):
        """
        Custom POST method
        """
        self.headers = {
            'Content-Type':'application_json',
            'Api-Key': self.api_key
        }
        return post(
            request_url,
            headers=self.headers,
            data=body
        )

    def _get(self, request_url: str, *args, **kwargs):
        """
                Custom POST method
                """
        self.headers = {
            'Content-Type': 'application_json',
            'Api-Key': self.api_key,
        }
        return get(
            request_url,
            headers=self.headers,
            params=kwargs
        )

    def get_profile(self, **kwargs) -> dict:
        response = self._get(
            request_url=self.GET_ACCOUNT_URL,
            **kwargs
        )
        print(response.status_code)
        return response.json()

