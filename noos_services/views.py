import logging

from django.contrib.auth.models import User, Group
from django.http import HttpResponse

from noos_services.models import Forcing, ForcingCouple, LoggingMessage, Node, NoosModel, SimulationCloud, \
    SimulationElement, SimulationDemand, SimulationMetadata, UploadedFile
from noos_services.serializers import ForcingCoupleSerializer, ForcingSerializer, GroupSerializer, \
    LoggingMessageSerializer, NodeSerializer, NoosModelSerializer, SimulationCloudSerializer, \
    SimulationDemandSerializer, SimulationElementSerializer, SimulationMetadataSerializer, UploadedFileSerializer, \
    UserSerializer

from rest_framework import viewsets, permissions
# Create your views here.

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
    schema = None
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
    schema = None
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
    schema = None
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
    Receives a POST request with one data fields ( 'json_txt' the related simulation's json ).

    read:
    API endpoint that allows simulationdemands to be viewed.
    Receives a GET request with an ID number.
    Returns one simulationdemands object.
    """
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = SimulationDemand.objects.filter(archived=False)
    serializer_class = SimulationDemandSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SimulationElementViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows simulationelements to be viewed or edited.

    list:
    API endpoint that allows simulationelements to be viewed.
    Receives a GET request.
    Returns the complete simulationelements list.

    create:
    API endpoint that allows simulationelements to be added.
    Receives a POST request with one data fields ( 'json_txt' the related simulation's json ).

    read:
    API endpoint that allows simulationelements to be viewed.
    Receives a GET request with an ID number.
    Returns one simulationelement object.
    """
    schema = None
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = SimulationElement.objects.all()
    serializer_class = SimulationElementSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SimulationCloudViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows simulationcloud to be viewed or edited.

    list:
    API endpoint that allows simulationcloud to be viewed.
    Receives a GET request.
    Returns the complete simulationcloud list.

    create:
    API endpoint that allows simulationcloud to be added.

    read:
    API endpoint that allows simulationcloud to be viewed.
    Receives a GET request with an ID number.
    Returns one simulationcloud object.
    """
    schema = None
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = SimulationCloud.objects.all()
    serializer_class = SimulationCloudSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SimulationMetadataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows simulationmetadata to be viewed or edited.

    list:
    API endpoint that allows simulationmetadata to be viewed.
    Receives a GET request.
    Returns the complete simulationmetadata list.

    create:
    API endpoint that allows simulationmetadata to be added.

    read:
    API endpoint that allows simulationmetadata to be viewed.
    Receives a GET request with an ID number.
    Returns one simulationmetadata object.
    """
    schema = None
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = SimulationMetadata.objects.all()
    serializer_class = SimulationMetadataSerializer

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
    Receives a POST request with six data fields ( 'status', 'message', 'node' the node 's ID, 'forcing_couple' the
    forcings's ID used, 'noos_model' the models's ID used, 'simulation_demand' the related simulation's ID ).

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
    schema = None
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Forcing.objects.all()
    serializer_class = ForcingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ForcingCoupleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ForcingCouples to be viewed or edited.
    """
    schema = None
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
    schema = None
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
    Receives a POST request with six data fields ( 'filename' name of uploaded file, 'json_txt' the related
    simulation's json, 'simulation' the related simulation's ID, 'node' the node's ID that upload the file,
    'noos_model' the model's ID used, 'forcing_couple' the forcings couple ID used ).

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
