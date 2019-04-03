from logging import warning
from uuid import uuid1

from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware

from archesky_authentication_server.config import load_config
from .views import home, login, user_area

debug = load_config()['debug']
if debug:
    warning('Running in debug mode.')

app = Starlette(debug)
app.add_route('/', home, ['GET'])
app.add_route('/login', login, ['GET'])
app.add_route('/user_area', user_area, ['GET'])
app.add_middleware(SessionMiddleware, secret_key=str(uuid1()))
