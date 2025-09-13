from flask import Response
from collections import OrderedDict
import json

def success(data=None, message="Success", status_code=200):
    response = OrderedDict([
        ("status", True),
        ("message", message),
        ("data", data)
    ])
    return Response(
        json.dumps(response, ensure_ascii=False),
        status=status_code,
        mimetype='application/json'
    )

def error(message="Error", status_code=400, data=None):
    response = OrderedDict([
        ("status", False),
        ("message", message),
        ("data", data)
    ])
    return Response(
        json.dumps(response, ensure_ascii=False),
        status=status_code,
        mimetype='application/json'
    )
