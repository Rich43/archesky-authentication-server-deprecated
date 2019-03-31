from json import JSONEncoder, dumps

from starlette.responses import JSONResponse


class ObjectJSONEncoder(JSONEncoder):
    def default(self, obj):
        types = [str, int, bool, list, dict, type(None)]
        if hasattr(obj, "__dict__"):
            filtered = {k: v for k, v in obj.__dict__.items()
                        if any([isinstance(v, x) for x in types])}
        else:
            filtered = {}
        return filtered


def dump_object(obj):
    return dumps(obj, cls=ObjectJSONEncoder)


def json_response_object(obj):
    return JSONResponse(dump_object(obj))
