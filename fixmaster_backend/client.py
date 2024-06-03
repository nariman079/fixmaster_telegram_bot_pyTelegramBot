from requests import get, post, delete, Response, put, patch


class FixMasterClient:
    BASE_URL = ['https://booking.fix-mst.ru/bot-api', 'http://localhost:8000/bot-api'][0]
    CREATE_ORGANIZATION_URL = BASE_URL + '/organization/create/'
    ORGANIZATION_TYPES_URL = 'https://booking.fix-mst.ru/api/organizations-types/'
    VERIFY_ORGANIZATION_URL = BASE_URL + '/organization/verify/'
    DELETE_MASTER_URL = BASE_URL + '/masters/'
    CREATE_MASTER_URL = BASE_URL + '/masters/'
    EDIT_MASTER_URL = BASE_URL + '/masters/'
    MASTER_SERVICES_URL = BASE_URL + '/masters/{}/services/'
    SERVICE_DETAIL_URL = BASE_URL + '/service/{}'
    GET_ORGANIZATION_BY_TELEGRAM_ID_URL = BASE_URL + '/organization/get-by-telegram_id/'
    GET_ORGANIZATION_DATA_BY_TELEGRAM_ID_URL = BASE_URL + '/organization-data/get-by-telegram_id/'
    GET_ACCOUNT_URL = BASE_URL + '/get-my-profile/'
    GET_MODERATOR_URL = BASE_URL + '/moderator/'

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

    def verify_organization(self, organization_id: int, verify: bool):
        response = post(
            self.VERIFY_ORGANIZATION_URL + f'{organization_id}/',
            headers=self.headers,
            json={
                'is_verify': verify
            },
        )
        return response

    def get_organization_by_telegram_id(self, telegram_id: str):
        response = get(
            self.GET_ORGANIZATION_BY_TELEGRAM_ID_URL + f'{telegram_id}',
            headers=self.headers,
        )
        return response

    def get_organization_data_by_telegram_id(self, telegram_id: str) -> Response:
        response = get(
            self.GET_ORGANIZATION_DATA_BY_TELEGRAM_ID_URL + f'{telegram_id}',
            headers=self.headers,
        )
        return response

    def get_moderator(self, moderator_data: dict) -> Response:
        response = post(
            self.GET_MODERATOR_URL,
            headers=self.headers,
            json=moderator_data,
        )
        return response

    def delete_master(self, master_id: int) -> int:
        response = delete(
            self.DELETE_MASTER_URL + f"{master_id}",
            headers=self.headers
        )
        return response.status_code

    def create_master(self, master_data: dict) -> Response:
        response = post(
            self.CREATE_MASTER_URL,
            headers=self.headers,
            json=master_data
        )
        print(response.json())
        return response

    def edit_master(self, master_data: dict, master_id: int) -> Response:
        response = patch(
            self.EDIT_MASTER_URL + f"{master_id}",
            headers=self.headers,
            json=master_data
        )
        return response

    def get_master_services(self, master_id: int) -> Response:
        response = get(
            self.MASTER_SERVICES_URL.format(master_id),
            headers=self.headers
        )
        return response

    def get_service_detail(self, service_id: int) -> Response:
        response = get(
            self.SERVICE_DETAIL_URL.format(service_id),
            headers=self.headers
        )
        return response

    def create_service(self, service_data: dict, master_id: int) -> Response:
        response = post(
            self.MASTER_SERVICES_URL.format(master_id),
            headers=self.headers,
            json=service_data,
        )
        print(response.json())
        return response
