from oic import rndstr
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import MyModel

from oic.oic import Client, RegistrationResponse, AuthorizationResponse, ProviderConfigurationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from json import dumps, load


@view_config(route_name='home', renderer='json')
def my_view(request: Request):
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

    try:
        query = request.dbsession.query(MyModel)
        one = query.filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'one': one, 'project': 'pyracms3_auth_server', 'provider_info': provider_info,
            'client_reg': client_reg, 'auth_req': auth_req, 'login_url': login_url,
            'token_endpoint': client.token_endpoint}


def create_client(request):
    config_file = load(open(request.registry.settings['config.file']))
    client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
    client.client_id = config_file['web']['client_id']
    client.provider_config("https://accounts.google.com")

    info = {"client_id": client.client_id,
            "client_secret": config_file['web']['client_secret'],
            "redirect_uris": config_file['web']['redirect_uris'],
            "contacts": ["RichieS@GMail.com"]}
    client_reg = RegistrationResponse(**info)
    client.store_registration_info(client_reg)
    return client, client_reg, client.provider_info


@view_config(route_name='login')
def login_view(request: Request):
    raise HTTPFound(request.session['login_url'])


@view_config(route_name='user_area', renderer='json')
def user_area_view(request: Request):
    client, client_reg, provider_info = create_client(request)

    if request.GET.get('state') and request.GET.get('code'):
        response = dumps(dict(request.GET))

        a_resp = client.parse_response(AuthorizationResponse, info=response)

        try:
            assert a_resp.get("state") == request.session.get("state")
        except AssertionError:
            return {"error": "state mismatch", "a_resp": a_resp, "session": request.session}

        args = {
            "code": a_resp["code"],
            "redirect_uri": client.registration_response["redirect_uris"][0],
            "token_endpoint": client.token_endpoint,
            "response_type": "code",
            "scope": "openid email",
            "client_id": client.client_id
        }

        resp = client.do_access_token_request(state=a_resp["state"],
                                              request_args=args,
                                              scope="openid email",
                                              authn_method="client_secret_post")

        if resp.get("error"):
            user_info = None
        else:
            user_info = client.do_user_info_request(state=a_resp["state"])

        return {'GET': response, 'a_resp': a_resp, 'resp': resp, 'user_info': user_info}

    return {}


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
