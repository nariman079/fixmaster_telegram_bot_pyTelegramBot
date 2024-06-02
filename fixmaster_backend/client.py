from requests import get, post


class FixMasterClient:
    BASE_URL = 'https://booking.fix-mst.ru/bot-api'
    GET_ACCOUNT_URL = BASE_URL + '/get-my-profile/'
    GET_MODERATOR_URL = BASE_URL + '/moderator/'
    CREATE_ORGANIZATION_URL = BASE_URL + '/organization/create/'
    ORGANIZATION_TYPES_URL = 'https://booking.fix-mst.ru/api/organizations-types/'
    VERIFY_ORGANIZATION_URL = BASE_URL + '/organization/verify/'
    GET_ORGANIZATION_BY_TELEGRAM_ID_URL = BASE_URL + '/organization/get-by-telegram_id/'

    def __init__(self, api_key: str):
        self.api_key = api_key
        print(api_key)
        self.headers = {
            'Content-Type': 'application/json',
            'Api-Key': api_key
        }

    def _post(self, request_url: str, body: dict):
        """
        Custom POST method
        """
        return post(
            request_url,
            headers=self.headers,
            data=body,
        )

    def _get(self, request_url: str, *args, **kwargs):
        """
        Custom POST method
        """

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
        return response.json()

    def get_organization_types(self):
        response = self._get(
            self.ORGANIZATION_TYPES_URL
        )
        return response.json()

    def create_organization(self, organization_data: dict):
        response = post(
            self.CREATE_ORGANIZATION_URL,
            headers=self.headers,
            json=organization_data,
        )
        return response.json()

    def get_moderator(self, moderator_data: dict):
        response = post(
            self.GET_MODERATOR_URL,
            headers=self.headers,
            json=moderator_data,
        )
        return response

    def verify_organization(self, organization_id: int, verify: bool):
        response = post(
            self.VERIFY_ORGANIZATION_URL+f'{organization_id}/',
             headers=self.headers,
            json={
                'is_verify': verify
            },
        )
        print(response.status_code)
        return response

    def get_organization_by_telegram_id(self, telegram_id: int):
        response = get(
            self.GET_ORGANIZATION_BY_TELEGRAM_ID_URL + f'{telegram_id}',
            headers=self.headers,
        )
        return response

    def get_organization_data(self, telegram_id):
