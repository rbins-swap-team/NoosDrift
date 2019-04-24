"""
WSGI config for noosDrift project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.path.isfile('/etc/apache2/Django_env_vars/noosdrift.py'):
    exec(open('/etc/apache2/Django_env_vars/noosdrift.py').read())
elif os.path.isfile('/opt/noosdrift/Django_env_vars/noosdrift.py'):
    exec(open('/opt/noosdrift/Django_env_vars/noosdrift.py').read())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'noosDrift.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root=os.path.join(BASE_DIR, 'static'), prefix='/noosdrift/api/static/')
