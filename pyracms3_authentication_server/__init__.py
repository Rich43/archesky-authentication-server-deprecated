import uuid

from pyramid.config import Configurator
from pyramid.renderers import JSON
from pyramid.session import SignedCookieSessionFactory


def custom_json_renderer():
    """
    Return a custom json renderer that can deal with some datetime objects.
    """
    def object_adapter(obj, request):
        types = [str, int, bool, list, dict, type(None)]
        if hasattr(obj, "__dict__"):
            filtered = {k: v for k, v in obj.__dict__.items()
                        if any([isinstance(v, x) for x in types])}
        else:
            filtered = {}
        return filtered

    json_renderer = JSON()
    json_renderer.add_adapter(object, object_adapter)
    return json_renderer


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_renderer('json', custom_json_renderer())
    config.set_session_factory(SignedCookieSessionFactory(str(uuid.uuid1())))
    config.include('.routes')
    config.scan()
    return config.make_wsgi_app()
