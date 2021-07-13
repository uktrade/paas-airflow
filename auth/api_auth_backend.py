"""Default authentication backend - everything is allowed"""
from functools import wraps

from flask import request, make_response, Response
from mohawk import Receiver
from mohawk.exc import MissingAuthorization, CredentialsLookupError, MacMismatch

from auth import config

CLIENT_AUTH = None


def init_app(_):
    """Initializes authentication backend"""


def _unauthorized():
    """
    Indicate that authorization is required
    :return:
    """
    return Response("Unauthorized", 401)


def lookup_credentials(sender_id):
    """
    Look up hawk credentials from auth config
    """
    if sender_id in config.AIRFLOW_API_HAWK_CREDENTIALS:
        return {
            'id': sender_id,
            'key': config.AIRFLOW_API_HAWK_CREDENTIALS[sender_id],
            'algorithm': 'sha256',
        }

    raise LookupError('unknown sender')


def requires_authentication(function):
    """Decorator for functions that require hawk authentication"""

    @wraps(function)
    def decorated(*args, **kwargs):
        try:
            receiver = Receiver(
                lookup_credentials,
                request.headers.get('Authorization'),
                request.url,
                request.method,
                content=request.data,
                content_type=request.headers.get('Content-Type'),
            )
        except (MissingAuthorization, CredentialsLookupError, MacMismatch):
            return _unauthorized()

        response = make_response(function(*args, **kwargs))
        receiver.respond(content=response.data, content_type=response.content_type)
        response.headers['Server-Authorization'] = receiver.response_header
        return response

    return decorated
