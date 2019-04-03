from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .config import load_config
from .json_utils import dump_and_load_object
from .openid import Config, OpenID


def create_config():
    settings = load_config()
    return Config(settings['contact.email'], settings['redirect.url'],
                  settings['provider.url'], settings['client.secret'],
                  settings['client.id'])


async def home(request: Request):
    openid = OpenID(create_config())
    session = request.session
    session['state'], session['nonce'] = OpenID.create_nonce_and_state()
    session['login_url'] = openid.do_authorisation_request(
        session['nonce'],
        session['state']
    )

    return JSONResponse({'login_url': session['login_url']})


async def login(request: Request):
    if not request.session.get('login_url'):
        return JSONResponse({'error': 'no login url in session',
                             'error_code': 1})
    return Response(status_code=302,
                    headers={'location': request.session['login_url']})


async def user_area(request: Request):
    openid = OpenID(create_config())
    session = request.session

    if request.query_params.get('state') and request.query_params.get('code'):
        try:
            code = openid.check_state(
                dict(request.query_params),
                session.get('state')
            )
        except AssertionError:
            return JSONResponse({'error': 'state mismatch', 'error_code': 2})
        user_info = openid.get_user_info(code, session.get('state'))
        return JSONResponse({'GET': dict(request.query_params),
                             'user_info': dump_and_load_object(user_info)})

    return JSONResponse({'error': 'missing query string parameters',
                         'error_code': 3})
