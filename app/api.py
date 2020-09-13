import json
from bottle import HTTPResponse

def ping_response(api_version, author, color, head, tail):
    return HTTPResponse(
        status=200,
        headers={
            "Content-Type": "application/json"
        },
        body=json.dumps({
            "apiversion": api_version,
            "author": author,
            "color": color,
            "head": head,
            "tail": tail
        })
    )

def start_response():
    return HTTPResponse(
        status=200,
    )

def move_response(move):
    assert move in ['up', 'down', 'left', 'right'], \
        "Move must be one of [up, down, left, right]"

    return HTTPResponse(
        status=200,
        headers={
            "Content-Type": "application/json"
        },
        body=json.dumps({
            "move": move
        })
    )

def end_response():
    return HTTPResponse(
        status=200
    )
