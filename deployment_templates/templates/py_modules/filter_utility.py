import base64
import json

def to_base64(s):
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")

def to_base64url(s):
    return base64.urlsafe_b64encode(s.encode("utf-8")).decode("utf-8")

def b64decode(s):
    return base64.b64decode(s.encode("utf-8")).decode("utf-8")

def loads(s):
    return json.loads(s)
