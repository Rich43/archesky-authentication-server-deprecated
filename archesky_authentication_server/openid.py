from dataclasses import dataclass
from json import dumps

from oic import rndstr
from oic.oic import RegistrationResponse, Client, AuthorizationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD


@dataclass
class Config:
    contact_email: str
    redirect_url: str
    provider_url: str
    client_secret: str
    client_id: str


class OpenID(Config):
    def __init__(self, config: Config):
        self.config = config
        self.client: Client = None
        self.create_client()
        self.register_client()

    @staticmethod
    def create_nonce_and_state():
        return rndstr(), rndstr()

    def create_client(self):
        client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
        client.client_id = self.config.client_id
        client.provider_config(self.config.provider_url)
        self.client = client

    def register_client(self):
        info = {"client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "redirect_uris": [self.config.redirect_url],
                "contacts": [self.config.contact_email]}
        client_reg = RegistrationResponse(**info)
        self.client.store_registration_info(client_reg)

    def do_authorisation_request(self, nonce: str, state: str):
        args = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "scope": ["openid email"],
            "nonce": nonce,
            "redirect_uri": self.config.redirect_url,
            "state": state,
        }

        auth_req = self.client.construct_AuthorizationRequest(request_args=args)
        return auth_req.request(self.client.authorization_endpoint)

    def check_state(self, get_parameters: dict, state: str):
        parsed_response = self.client.parse_response(
            AuthorizationResponse,
            info=dumps(get_parameters)
        )
        assert parsed_response.get("state") == state
        return parsed_response['code']

    def get_user_info(self, code: str, state: str):
        args = {
            'code': code,
            'redirect_uri': self.config.redirect_url,
            'token_endpoint': self.client.token_endpoint,
            'response_type': 'code',
            'scope': 'openid email',
            'client_id': self.client.client_id
        }

        access_token_response = self.client.do_access_token_request(
            state=state,
            request_args=args,
            scope='openid email',
            authn_method='client_secret_post'
        )

        if access_token_response.get('error'):
            user_info = None
        else:
            user_info = self.client.do_user_info_request(
                state=state
            )
        return user_info
