from django.contrib.auth.models import User, Group
from noos_services.models import Node, SimulationDemand, LoggingMessage, Forcing, NoosModel, ForcingCouple, UploadedFile
from rest_framework import viewsets, permissions
from noos_services.serializers import UserSerializer, GroupSerializer, NodeSerializer, SimulationDemandSerializer, \
                                      LoggingMessageSerializer, ForcingSerializer, NoosModelSerializer, \
                                      ForcingCoupleSerializer, UploadedFileSerializer
import logging

# Create your views here.
from django.http import HttpResponse

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse("Hello, world. You're at the noos drift  index.")


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class NodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows nodes to be viewed or edited.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Node.objects.all()
    serializer_class = NodeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SimulationDemandViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SimulationDemands to be viewed or edited.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = SimulationDemand.objects.all()
    serializer_class = SimulationDemandSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LoggingMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows LoggingMessages to be viewed or edited.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = LoggingMessage.objects.all()
    serializer_class = LoggingMessageSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ForcingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Forcings to be viewed or edited.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Forcing.objects.all()
    serializer_class = ForcingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ForcingCoupleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ForcingCouples to be viewed or edited.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = ForcingCouple.objects.all()
    serializer_class = ForcingCoupleSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NoosModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows NoosModel objects to be viewed or edited.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = NoosModel.objects.all()
    serializer_class = NoosModelSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UploadedFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows UploadedFile objects to be viewed or edited.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
