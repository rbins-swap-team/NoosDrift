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

    list:
    API endpoint that allows users to be viewed.
    Receives a GET request.
    Returns the complete users list.

    read:
    API endpoint that allows users to be viewed.
    Receives a GET request with an ID number.
    Returns one users object.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.

    list:
    API endpoint that allows groups to be viewed.
    Receives a GET request.
    Returns the complete groups list.

    read:
    API endpoint that allows groups to be viewed.
    Receives a GET request with an ID number.
    Returns one group object.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class NodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows nodes to be viewed or edited.

    list:
    API endpoint that allows nodes to be viewed.
    Receives a GET request.
    Returns the complete nodes list.

    read:
    API endpoint that allows nodes to be viewed.
    Receives a GET request with an ID number.
    Returns one nodes object.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Node.objects.all()
    serializer_class = NodeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SimulationDemandViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows simulationdemands to be viewed or edited.

    list:
    API endpoint that allows simulationdemands to be viewed.
    Receives a GET request.
    Returns the complete simulationdemands list.

    create:
    API endpoint that allows simulationdemands to be added.
    Receives a POST request with one data fields ( 'json_txt' the related simulation's escaped json ).

    read:
    API endpoint that allows simulationdemands to be viewed.
    Receives a GET request with an ID number.
    Returns one simulationdemands object.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = SimulationDemand.objects.all()
    serializer_class = SimulationDemandSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LoggingMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows loggingmessages to be viewed or edited.

    list:
    API endpoint that allows loggingmessages to be viewed.
    Receives a GET request.
    Returns the complete loggingmessages list.

    create:
    API endpoint that allows loggingmessages to be added.
    Receives a POST request with six data fields ( 'status', 'message', 'node' the node 's ID, 'forcing_couple' the forcings's ID used, 'noos_model' the models's ID used, 'simulation_demand' the related simulation's ID ).

    read:
    API endpoint that allows loggingmessages to be viewed.
    Receives a GET request with an ID number.
    Returns one loggingmessages object.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = LoggingMessage.objects.all()
    serializer_class = LoggingMessageSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ForcingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows forcings to be viewed or edited.

    list:
    API endpoint that allows forcings to be viewed.
    Receives a GET request.
    Returns the complete forcings list.

    read:
    API endpoint that allows forcings to be viewed.
    Receives a GET request with an ID number.
    Returns one forcing object.
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
    API endpoint that allows noosmodels to be viewed or edited.

    list:
    API endpoint that allows noosmodels to be viewed.
    Receives a GET request.
    Returns the complete noosmodels list.

    read:
    API endpoint that allows noosmodels to be viewed.
    Receives a GET request with an ID number.
    Returns one noosmodels object.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = NoosModel.objects.all()
    serializer_class = NoosModelSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UploadedFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows uploadedfiles to be viewed or edited.

    list:
    API endpoint that allows uploadedfiles to be viewed.
    Receives a GET request.
    Returns the complete uploadedfiles list.

    create:
    API endpoint that allows uploadedfiles to be added.
    Receives a POST request with six data fields ( 'filename' name of uploaded file, 'json_txt' the related simulation's escaped json, 'simulation' the related simulation's ID, 'node' the node's ID that upload the file, 'noos_model' the model's ID used, 'forcing_couple' the forcings couple ID used ).

    read:
    API endpoint that allows uploadedfiles to be viewed.
    Receives a GET request with an ID number.
    Returns one uploadedfiles object.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
