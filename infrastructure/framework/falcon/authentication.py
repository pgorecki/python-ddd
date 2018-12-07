import falcon
import base64
from infrastructure.framework.falcon.base import RouteController

class UnauthenticatedException(Exception):
    """ Use this exception when authentication fails """
    pass

class ForbiddenException(Exception):
    """ Use this exception when permission check fails """
    pass

def authenticate(method):
    def wrapper(self, req, res):
        assert isinstance(self, RouteController), '@authenticate must be used with RouteController or derived classes'
        assert self._authentication_service is not None,\
            'You are using @authenticate for route {} but AuthenticationService not injected into {}'\
            .format(req.relative_uri, type(self).__name__)
        
        user = self._authentication_service.authenticate(req)       
        req.context['user_id'] = user.id
        return method(self, req, res)
    return wrapper


class BasicAuthenticationService:
    def __init__(self, users_repository):
        self._users_repository = users_repository
    
    def authenticate(self, req):
        if req.auth is None:
            raise falcon.HTTPError(
                status=falcon.HTTP_401,
                title='Authentication failed',
                description='Authorization header is missing'
                )

        auth_type, credentials = req.auth.split(' ')
              
        if auth_type.lower() != 'basic':
            raise falcon.HTTPError(
                status=falcon.HTTP_401,
                title='Authentication failed',
                description="Expected 'Authorization: Basic <credentials>' header"
                )

        try:
            decoded_credentials = base64.b64decode(credentials)
            login, password = decoded_credentials.decode().split(':')
        except Exception as e:
            raise falcon.HTTPError(
                status=falcon.HTTP_401,
                title='Authentication failed',
                description='Invalid credentials ({})'.format(e)
                )
        user = self._users_repository.get_user_by_login_and_password(login, password)

        if user is None:
            raise falcon.HTTPError(
                status=falcon.HTTP_401,
                title='Authentication failed',
                description='Invalid credentials'
                )
        return user