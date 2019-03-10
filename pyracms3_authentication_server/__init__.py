from pyramid.config import Configurator
from pyramid.renderers import JSON
from pyramid_beaker import session_factory_from_settings


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
    config.include('pyramid_beaker')
    config.include('.routes')
    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)
    config.scan()
    return config.make_wsgi_app()
