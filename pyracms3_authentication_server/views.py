from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.view import view_config

from .openid import Config, OpenID


# noinspection PyUnresolvedReferences
def create_config(request: Request):
    settings = request.registry.settings
    return Config(settings['contact.email'], settings['redirect.url'],
                  settings['provider.url'], settings['client.secret'],
                  settings['client.id'])


@view_config(route_name='home', renderer='json')
def home(request: Request):
    openid = OpenID(create_config(request))
    session = request.session
    session['state'], session['nonce'] = OpenID.create_nonce_and_state()
    session['login_url'] = openid.do_authorisation_request(
        session['nonce'],
        session['state']
    )

    return {'login_url': session['login_url']}


@view_config(route_name='login')
def login_view(request: Request):
    raise HTTPFound(request.session['login_url'])


@view_config(route_name='user_area', renderer='json')
def user_area_view(request: Request):
    openid = OpenID(create_config(request))
    session = request.session

    if request.GET.get('state') and request.GET.get('code'):
        try:
            code = openid.check_state(dict(request.GET), session.get('state'))
        except AssertionError:
            return {'error': 'state mismatch'}
        user_info = openid.get_user_info(code, session.get('state'))
        return {'GET': dict(request.GET), 'user_info': user_info}

    return {'error': 'missing query string parameters'}
