import os

framework = os.environ.get('FRAMEWORK', 'falcon')
print('Running {} app'.format(framework))

application = None # required by gunicorn

if framework == 'falcon':
    from infrastructure.framework.falcon.app import app as application
elif framework == 'flask':
    from infrastructure.framework.flask.app import app as application

