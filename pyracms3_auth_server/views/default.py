from json import dumps

from oic import rndstr
from oic.oic import Client, RegistrationResponse, AuthorizationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='home', renderer='json')
def home(request: Request):
    client, client_reg, provider_info = create_client(request)
    request.session["state"] = rndstr()
    request.session["nonce"] = rndstr()
    args = {
        "client_id": client.client_id,
        "response_type": "code",
        "scope": ["openid email"],
        "nonce": request.session["nonce"],
        "redirect_uri": client.registration_response["redirect_uris"][0],
        "state": request.session["state"],
    }

    auth_req = client.construct_AuthorizationRequest(request_args=args)
    login_url = auth_req.request(client.authorization_endpoint)
    request.session['login_url'] = login_url

    return {'login_url': login_url}


@view_config(route_name='login')
def login_view(request: Request):
    raise HTTPFound(request.session['login_url'])


@view_config(route_name='user_area', renderer='json')
def user_area_view(request: Request):
    client, client_reg, provider_info = create_client(request)

    if request.GET.get('state') and request.GET.get('code'):
        query_string_json = dumps(dict(request.GET))

        parsed_response = client.parse_response(AuthorizationResponse,
                                                info=query_string_json)

        try:
            assert parsed_response.get("state") == request.session.get("state")
        except AssertionError:
            return {"error": "state mismatch"}

        args = {
            "code": parsed_response["code"],
            "redirect_uri": client.registration_response["redirect_uris"][0],
            "token_endpoint": client.token_endpoint,
            "response_type": "code",
            "scope": "openid email",
            "client_id": client.client_id
        }

        access_token_response = client.do_access_token_request(
            state=parsed_response["state"],
            request_args=args,
            scope="openid email",
            authn_method="client_secret_post"
        )

        if access_token_response.get("error"):
            user_info = None
        else:
            user_info = client.do_user_info_request(
                state=parsed_response["state"]
            )

        return {'GET': dict(request.GET), 'user_info': user_info}

    return {"error": "missing query string parameters"}


def create_client(request):
    settings = request.registry.settings
    client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
    client.client_id = settings['client.id']
    client.provider_config(settings['provider.url'])

    info = {"client_id": settings['client.id'],
            "client_secret": settings['client.secret'],
            "redirect_uris": [settings['redirect.url']],
            "contacts": [settings['contact.email']]}
    client_reg = RegistrationResponse(**info)
    client.store_registration_info(client_reg)
    return client, client_reg, client.provider_info


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_pyracms3_auth_server_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development_example.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
