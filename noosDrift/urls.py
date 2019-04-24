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
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from noos_services import views
from django.conf import settings
from django.conf.urls.static import static
from noosDrift.settings import SCHEMA_URL
from django.views.generic.base import RedirectView
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import CoreJSONRenderer, JSONOpenAPIRenderer, OpenAPIRenderer
from noos_services.permissions import IsReadOnly

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

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'^noos_services/', include('noos_services.urls')),
                  url(r'^', include(router.urls)),
                  url(r'^favicon.ico$',
                      RedirectView.as_view(url="/noosdrift/api/static/favicon.ico", permanent=False), name="favicon"),
                  # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                  url(r'^api-token-auth/', obtain_jwt_token),
                  url(r'^api-token-verify/', verify_jwt_token),
                  url(r'^api-token-refresh/', refresh_jwt_token),
                  url(r'^schema/core.json$', schema_core_json_view),
                  url(r'^schema/openapi.json$', schema_open_json_view),
                  url(r'^schema/openapi.yaml$', schema_open_yaml_view),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
