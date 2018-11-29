import json
from datetime import datetime
import inspect

def is_public(v):
    return isinstance(v, property)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        try:
            return { k: v for k,v in obj.__class__.__dict__.items() if not k.startswith('_')}
        except:
            return super().default(obj)


def response(obj):
    return json.dumps(obj, cls=CustomJSONEncoder)
