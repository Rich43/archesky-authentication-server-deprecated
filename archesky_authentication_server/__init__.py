from logging import warning
from os.path import exists
from uuid import uuid1

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware

from .views import home, login, user_area


def main(debug: bool):
    error = 'Missing config.ini, try renaming config_example.ini?'
    assert exists('config.ini'), error
    if debug:
        warning('Running in debug mode.')
    app = Starlette(debug)
    app.add_route('/', home, ['GET'])
    app.add_route('/login', login, ['GET'])
    app.add_route('/user_area', user_area, ['GET'])
    app.add_middleware(SessionMiddleware, secret_key=str(uuid1()))
    uvicorn.run(app, host='0.0.0.0', port=8000)


def run_debug():
    main(True)


def run_production():
    main(False)
