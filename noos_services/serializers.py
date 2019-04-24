from django.contrib.auth.models import User, Group
from noos_services.models import Node, SimulationDemand, LoggingMessage, NoosModel, UploadedFile, Forcing, ForcingCouple
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)


class SimulationDemandSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    mandatory_json_fields = ["simulation_description", "drifter", "initial_condition", "model_set_up"]

    class Meta:
        model = SimulationDemand
        fields = ('url', 'id', 'user', 'created_time', 'json_txt')

    #    def validate(self, data):
    #        logger.debug("SimulationDemandSerializer.create, start of")
    #        logger.debug("SimulationDemandSerializer.create, validated_data : {}".format(data))

    # def validate_json_txt(self, value):
    #    """
    #    Json part validation function. This is a function to validate the data in field "json_txt".
    #    The data in field "json_txt" is in TEXT from, that follows JSON rules.
    #    So it has to be transformed into Python objects first (that's the json.loads())
    #    Only then will it be examined for validation errors.
    #    """
    #    logger.info("SimulationDemandSerializer.validate_json_txt, start of")
    #    try:
    #        logger.info("SimulationDemandSerializer.validate_json_txt, extracting json")
    #        json_dict = json.loads(value)
    #        logger.info("SimulationDemandSerializer.validate_json_txt, json_txt : {}".format(json_dict))
    #        for afield in SimulationDemandSerializer.mandatory_json_fields:
    #            if afield not in json_dict:
    #                raise serializers.ValidationError("no '{}' field in data".format(afield))

    #        newvalue = json.dumps(json_dict, separators=(',', ':'))
    #        logger.info("SimulationDemandSerializer.validate_json_txt, json_txt: {}".format(newvalue))
    #    except (ValueError, KeyError, TypeError, serializers.ValidationError) as err:
    #        logger.error("JSON format error")
    #        raise err

    #    logger.info("SimulationDemandSerializer.validate_json_txt, end of")
    #    return newvalue

    def create(self, validated_data):
        logger.debug("SimulationDemandSerializer.create, start of")
        logger.debug("SimulationDemandSerializer.create, validated_data : {}".format(validated_data))
        simulation_demand = SimulationDemand.objects.create(**validated_data)
        logger.debug("SimulationDemandSerializer.create, end of")
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

    #    def validate(self, data):
    #        logger.debug("SimulationDemandSerializer.create, start of")
    #        logger.debug("SimulationDemandSerializer.create, validated_data : {}".format(data))

    def create(self, validated_data):
        logger.debug("LoggingMessageSerializer.create, start of")
        logger.debug("LoggingMessageSerializer.create, {}".format(validated_data))
        del validated_data['user']
        logging_message = LoggingMessage.objects.create(**validated_data)
        logger.debug("LoggingMessageSerializer.create, end of")
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
        logger.debug("UploadedFileSerializer.create, start of")
        logger.debug("UploadedFileSerializer.create, {}".format(validated_data))
        del validated_data['user']
        uploaded_file = UploadedFile.objects.create(**validated_data)
        logger.debug("UploadedFileSerializer.create, end of")
        return uploaded_file
