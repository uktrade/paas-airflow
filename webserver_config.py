from flask_appbuilder.security.manager import AUTH_OAUTH

from airflow.www.security import AirflowSecurityManager
from auth import config

WTF_CSRF_ENABLED = True

AUTH_TYPE = AUTH_OAUTH
AUTH_USER_REGISTRATION_ROLE = 'Admin'
AUTH_USER_REGISTRATION = True
AUTH_ROLES_SYNC_AT_LOGIN = True

OAUTH_PROVIDERS = [
    {
        'name': 'authbroker',
        'token_key': 'access_token',
        'icon': 'fa-lock',
        'remote_app': {
            'api_base_url': config.AUTHBROKER_URL + 'api/v1/user/',  # type: ignore
            'access_token_url': config.AUTHBROKER_URL + 'o/token/',  # type: ignore
            'authorize_url': config.AUTHBROKER_URL + 'o/authorize/',  # type: ignore
            'request_token_url': None,
            'client_id': config.AUTHBROKER_CLIENT_ID,
            'client_secret': config.AUTHBROKER_CLIENT_SECRET,
            'access_token_method': 'POST',
            'client_kwargs': {'scope': 'read write'},
        },
    }
]


class CustomSecurityManager(AirflowSecurityManager):
    def oauth_user_info(self, provider, response=None):  # pylint: disable=method-hidden
        user_json = self.appbuilder.sm.oauth_remotes[provider].get('me').json()
        return {
            'username': user_json['user_id'],
            'email': user_json['email'],
            'first_name': user_json['first_name'],
            'last_name': user_json['last_name'],
        }


SECURITY_MANAGER_CLASS = CustomSecurityManager
