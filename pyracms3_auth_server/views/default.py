from oic import rndstr
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import MyModel

from oic.oic import Client, RegistrationResponse, AuthorizationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from json import dumps


@view_config(route_name='home', renderer='json')
def my_view(request: Request):
    client, client_reg, provider_info = create_client(request)
    request.session["state"] = rndstr()
    request.session["nonce"] = rndstr()
    args = {
        "client_id": client.client_id,
        "response_type": "code",
        "scope": ["openid"],
        "nonce": request.session["nonce"],
        "redirect_uri": client.registration_response["redirect_uris"][0],
        "state": request.session["state"]
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
            'client_reg': client_reg, 'auth_req': auth_req, 'login_url': login_url}


def create_client(request):
    client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
    issuer = "https://login.microsoftonline.com/common/v2.0/"
    provider_info = client.provider_config(issuer)
    info = {"client_id": request.registry.settings['client.id'],
            "client_secret": request.registry.settings['client.secret'],
            "redirect_uris": ['http://localhost:6543/user_area'], "contacts": ["pynguins@outlook.com"]}
    client_reg = RegistrationResponse(**info)
    client.store_registration_info(client_reg)
    return client, client_reg, provider_info


@view_config(route_name='login')
def login_view(request: Request):
    raise HTTPFound(request.session['login_url'])


@view_config(route_name='user_area', renderer='json')
def user_area_view(request: Request):
    client, client_reg, provider_info = create_client(request)

    if request.GET.get('state') and request.GET.get('code'):
        response = dumps(dict(request.GET))

        a_resp = client.parse_response(AuthorizationResponse, info=response)

        assert a_resp["state"] == request.session["state"]
        args = {
            "code": a_resp["code"],
            "redirect_uri": client.registration_response["redirect_uris"][0]
        }

        resp = client.do_access_token_request(state=a_resp["state"],
                                              request_args=args,
                                              authn_method="client_secret_basic")

        return {'GET': response, 'a_resp': a_resp, 'resp': resp}

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
