"""noosDrift URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic.base import RedirectView, TemplateView
from noos_services import views
from noos_services.permissions import IsReadOnly
from noos_viewer import views as noos_viewer_views
from noosDrift.settings import SCHEMA_URL, BASE_URL
from requests.compat import urljoin
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token
from rest_framework.renderers import CoreJSONRenderer, JSONOpenAPIRenderer, OpenAPIRenderer
from rest_framework.schemas import get_schema_view

schema_core_json_view = get_schema_view(title='NOOS-Drift - CoreJSON - API',
                                        renderer_classes=[CoreJSONRenderer],
                                        permission_classes=[IsReadOnly],
                                        url=SCHEMA_URL,
                                        description='NOOS-Drift API for inter-node communication, CoreJSON format. '
                                                    'Production version.')
schema_open_json_view = get_schema_view(title='NOOS-Drift - OpenAPI-JSON - API',
                                        renderer_classes=[JSONOpenAPIRenderer],
                                        permission_classes=[IsReadOnly],
                                        url=SCHEMA_URL,
                                        description='NOOS-Drift API for inter-node communication. OpenAPI JSON format. '
                                                    'Next version, to take advantage of the full set of OpenAPI '
                                                    'functionality in a near future.')
schema_open_yaml_view = get_schema_view(title='NOOS-Drift - OpenAPI-YAML - API',
                                        renderer_classes=[OpenAPIRenderer],
                                        permission_classes=[IsReadOnly],
                                        url=SCHEMA_URL,
                                        description='NOOS-Drift API for inter-node communication. OpenAPI YAML format. '
                                                    'Next version, to take advantage of the full set of OpenAPI '
                                                    'functionality in a near future.')

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'nodes', views.NodeViewSet)
router.register(r'simulationdemands', views.SimulationDemandViewSet)
router.register(r'loggingmessages', views.LoggingMessageViewSet)
router.register(r'forcings', views.ForcingViewSet)
router.register(r'noosmodels', views.NoosModelViewSet)
router.register(r'uploadedfiles', views.UploadedFileViewSet)
router.register(r'simulationelements', views.SimulationElementViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

icon_url = urljoin(urljoin(BASE_URL, "static/"), "favicon.ico")

urlpatterns = [
                  path('signup/', noos_viewer_views.signup, name='signup'),
                  path('accounts/', include('django.contrib.auth.urls')),
                  path('noos_services/', include('noos_services.urls')),
                  re_path(r'^favicon.ico$', RedirectView.as_view(url=icon_url, permanent=False), name="favicon"),
                  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                  path('noos_viewer/', include('noos_viewer.urls')),
                  path('admin/', admin.site.urls),
                  path('captcha/', include('captcha.urls')),
                  path('api-token-auth', obtain_jwt_token),
                  path('api-token-verify', verify_jwt_token),
                  path('api-token-refresh', refresh_jwt_token),
                  path('schema/core.json', schema_core_json_view),
                  path('schema/openapi.json', schema_open_json_view),
                  path('schema/openapi.yaml', schema_open_yaml_view),
                  path('home/', TemplateView.as_view(template_name='noos_viewer/home.html'), name='home'),
                  re_path(r'^', include(router.urls)),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
