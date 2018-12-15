import os

try:
    import ptvsd
    ptvsd.enable_attach(address=('0.0.0.0', 3000))
except:
    print('ptvsd disabled')

framework = os.environ.get('FRAMEWORK', 'falcon')
print('Running {} app'.format(framework))

application = None # required by gunicorn

if framework == 'falcon':
    from infrastructure.framework.falcon.app import app as application
elif framework == 'flask':
    from infrastructure.framework.flask.app import app as application
