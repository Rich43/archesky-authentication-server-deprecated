from uuid import uuid1

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware

from .views import home, login, user_area


def main(debug: bool):
    app = Starlette(debug)
    app.add_route('/', home, ['GET'])
    app.add_route('/login', login, ['GET'])
    app.add_route('/user_area', user_area, ['GET'])
    app.add_middleware(SessionMiddleware, secret_key=str(uuid1()))
    uvicorn.run(app, host='0.0.0.0', port=8000)
