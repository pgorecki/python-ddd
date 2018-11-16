import os

# def create_app(config):
#     print('creating app, config:', config)
#     from infrastructure.framework.flask.app import app
#     return app

framework = os.environ['FRAMEWORK']
print('Running {} app'.format(framework))

application = None # required by gunicorn?

if framework == 'falcon':
    from infrastructure.framework.falcon.app import app as application
elif framework == 'flask':
    from infrastructure.framework.flask.app import app as application

