from django.contrib.auth.models import User, Group
from noos_services.models import Forcing, ForcingCouple, LoggingMessage, Node, NoosModel, \
    SimulationCloud, SimulationDemand, SimulationElement, SimulationMetadata, UploadedFile
from noos_services.ns_const import MemorySimulationDemand, OtherConst, StatusConst
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)


class SimulationDemandSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    mandatory_json_fields = [MemorySimulationDemand.SIMULATION_DESCRIPTION, MemorySimulationDemand.DRIFTER,
                             MemorySimulationDemand.INITIAL_CONDITION, MemorySimulationDemand.MODEL_SETUP]

    class Meta:
        model = SimulationDemand
        fields = ('url', MemorySimulationDemand.ID, 'user', MemorySimulationDemand.CREATED_TIME,
                  MemorySimulationDemand.JSON_TXT)

    def create(self, validated_data):
        name_and_method = "SimulationDemandSerializer.create"
        logger.info("{}, start of".format(name_and_method))
        # logger.debug("{}, validated_data : {}".format(name_and_method, validated_data))

        validated_data[MemorySimulationDemand.STATUS] = StatusConst.SUBMITTED

        json_data = validated_data[MemorySimulationDemand.JSON_TXT]

        drifter_type = json_data[MemorySimulationDemand.DRIFTER][MemorySimulationDemand.DRIFTER_TYPE]
        if drifter_type == OtherConst.OBJECT:
            json_data[MemorySimulationDemand.DRIFTER][MemorySimulationDemand.TOTAL_MASS] = -1
            json_data[MemorySimulationDemand.MODEL_SETUP][MemorySimulationDemand.NUMBER] = 1000
            json_data[MemorySimulationDemand.MODEL_SETUP][MemorySimulationDemand.TWODTHREED] = OtherConst.TWOD
            json_data[MemorySimulationDemand.MODEL_SETUP][MemorySimulationDemand.DISSOLUTION] = False
            json_data[MemorySimulationDemand.MODEL_SETUP][MemorySimulationDemand.EVAPORATION] = False
            json_data[MemorySimulationDemand.MODEL_SETUP][MemorySimulationDemand.HORIZONTAL_SPREADING] = False
            json_data[MemorySimulationDemand.MODEL_SETUP][MemorySimulationDemand.NATURAL_VERTICAL_DISPERTION] = False
            json_data[MemorySimulationDemand.MODEL_SETUP][MemorySimulationDemand.SEDIMENTATION] = False

        init_cond = json_data[MemorySimulationDemand.INITIAL_CONDITION]
        geom_type = init_cond[MemorySimulationDemand.GEOMETRY]
        if geom_type == OtherConst.POINT:
            # logger.debug("{}, geometry is point".format(name_and_method))
            str_val = init_cond[MemorySimulationDemand.LAT]
            lst_float = []
            if isinstance(str_val, list):
                # logger.debug("{}, lat is list".format(name_and_method))
                if isinstance(str_val[0], str):
                    lst_float.append(float(str_val[0]))
                if isinstance(str_val[0], float):
                    lst_float.append(str_val[0])
            if isinstance(str_val, str):
                # logger.debug("{}, lat is string".format(name_and_method))
                lst_float.append(float(str_val))
            if isinstance(str_val, float):
                # logger.debug("{}, lat is float".format(name_and_method))
                lst_float.append(str_val)

            init_cond[MemorySimulationDemand.LAT] = lst_float

            # logger.debug("{}, lat = {}".format(name_and_method, init_cond[MemorySimulationDemand.LAT]))

            str_val = init_cond[MemorySimulationDemand.LON]
            lst_float = []
            if isinstance(str_val, list):
                # logger.debug("{}, lon is list".format(name_and_method))
                if isinstance(str_val[0], str):
                    lst_float.append(float(str_val[0]))
                if isinstance(str_val[0], float):
                    lst_float.append(str_val[0])
            if isinstance(str_val, str):
                lst_float.append(float(str_val))
            if isinstance(str_val, float):
                lst_float.append(str_val)

            init_cond[MemorySimulationDemand.LON] = lst_float

        elif geom_type == OtherConst.POLYLINE:
            str_val = init_cond[MemorySimulationDemand.LAT]
            list_vals = []
            if isinstance(str_val, str):
                list_vals = str_val.split(",")
            elif isinstance(str_val, list):
                list_vals.extend(str_val)

            if isinstance(list_vals[0], float):
                init_cond[MemorySimulationDemand.LAT] = list_vals
            elif isinstance(list_vals[0], str):
                init_cond[MemorySimulationDemand.LAT] = [float(list_vals[0]), float(list_vals[1])]

            str_val = init_cond[MemorySimulationDemand.LON]
            list_vals = []
            if isinstance(str_val, str):
                list_vals = str_val.split(",")
            elif isinstance(str_val, list):
                list_vals.extend(str_val)

            if isinstance(list_vals[0], float):
                init_cond[MemorySimulationDemand.LON] = list_vals
            elif isinstance(list_vals[0], str):
                init_cond[MemorySimulationDemand.LON] = [float(list_vals[0]), float(list_vals[1])]

        ori_release_times = init_cond[MemorySimulationDemand.TIME]
        release_times = []
        if isinstance(ori_release_times, list):
            # logger.debug("{}, release_times is list".format(name_and_method))
            release_times.extend(ori_release_times)
        elif isinstance(ori_release_times, str):
            # logger.debug("{}, release_times is string".format(name_and_method))
            txt_list = ori_release_times.split(",")
            for a_txt in txt_list:
                # logger.debug("{}, adding a string relesae_time element : {}".format(name_and_method, a_txt))
                release_times.append(a_txt.strip())

        init_cond[MemorySimulationDemand.TIME] = release_times
        # logger.debug("{}, final value of release_time : {}".format(name_and_method,
        #                                                           init_cond[MemorySimulationDemand.TIME]))

        simulation_demand = SimulationDemand.objects.create(**validated_data)
        logger.info("{}, end of".format(name_and_method))
        return simulation_demand


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Node
        fields = ('url', 'id', 'user', 'country', 'description', 'hostname', 'is_active')


class LoggingMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoggingMessage
        fields = ('url', 'id', 'status', 'message', 'node', 'forcing_couple', 'noos_model', 'simulation_demand',
                  'created')

    def create(self, validated_data):
        # logger.debug("LoggingMessageSerializer.create, start of")
        # logger.debug("LoggingMessageSerializer.create, {}".format(validated_data))
        del validated_data['user']
        logging_message = LoggingMessage.objects.create(**validated_data)
        # logger.debug("LoggingMessageSerializer.create, end of")
        return logging_message


class UserSerializer(serializers.ModelSerializer):
    nodes = NodeSerializer(many=True, read_only=True)
    requests = SimulationDemandSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'is_active', 'password', 'last_name', 'first_name', 'groups',
                  'nodes', 'requests')

    def create(self, validated_data):
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class NoosModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NoosModel
        fields = ('id', 'url', 'display_name', 'description', 'code')


class ForcingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Forcing
        fields = ('id', 'url', 'display_name', 'description', 'code', 'use_type')


class ForcingCoupleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ForcingCouple
        fields = ('id', 'url', 'node', 'oceanical', 'meteorological', 'is_active')


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ('url', 'id', 'filename', 'json_txt', 'simulation', 'node', 'noos_model', 'forcing_couple')

    def create(self, validated_data):
        # logger.debug("UploadedFileSerializer.create, start of")
        # logger.debug("UploadedFileSerializer.create, {}".format(validated_data))
        del validated_data['user']
        uploaded_file = UploadedFile.objects.create(**validated_data)
        # logger.debug("UploadedFileSerializer.create, end of")
        return uploaded_file


class SimulationElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationElement
        fields = ('id', 'url', 'simulation', 'idx', 'timestamp', 'json_data')

    def create(self, validated_data):
        # logger.debug("SimulationElementsSerializer.create, start of")
        # logger.debug("SimulationElementsSerializer.create, {}".format(validated_data))
        simulation_element = SimulationElementSerializer.objects.create(**validated_data)
        # logger.debug("SimulationElementsSerializer.create, end of")
        return simulation_element


class SimulationCloudSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationCloud
        fields = ('id', 'url', 'simulation', 'node', 'noos_model', 'forcing_couple', 'idx', 'timestamp', 'json_data')

    def create(self, validated_data):
        # logger.debug("SimulationCloudSerializer.create, start of")
        # logger.debug("SimulationCloudSerializer.create, {}".format(validated_data))
        simulation_cloud = SimulationCloudSerializer.objects.create(**validated_data)
        # logger.debug("SimulationCloudSerializer.create, end of")
        return simulation_cloud


class SimulationMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationMetadata
        fields = ('id', 'url', 'simulation', 'metadata')

    def create(self, validated_data):
        # logger.debug("SimulationMetadataSerializer.create, start of")
        # logger.debug("SimulationMetadataSerializer.create, {}".format(validated_data))
        metadata = SimulationMetadataSerializer.objects.create(**validated_data)
        # logger.debug("SimulationCloudSerializer.create, end of")
        return metadata
