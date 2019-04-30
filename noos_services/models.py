from django.db import models
import coreapi
import glob
import json
import jsonfield
import logging
from noosDrift.settings import ACTIVE_NODES

logger = logging.getLogger(__name__)


class NodeConnection:
    """
    A class used to store the parameters of a connection
     * client object
     * schema object
     * token object
     * user object

     NodeConnections are stored in a list object created in the settings.
     NodeConnections are not stored in the database
    """

    def __init__(self, user=None, client=None, schema=None, token=None):
        self.user = user
        self.client = client
        self.schema = schema
        self.token = token

    def set_user(self, user):
        self.user = user

    def get_user(self):
        return self.user

    def set_client(self, client):
        self.client = client

    def get_client(self):
        return self.client

    def set_token(self, token):
        self.token = token

    def get_token(self):
        return self.token

    def get_schema(self):
        return self.schema

    def set_schema(self, schema):
        self.schema = schema

    def ready_for_verify(self):
        assert self.user is not None, "NodeConnection.ready_for_verify, user is None"
        assert self.client is not None, "NodeConnection.ready_for_verify, client is None"
        assert self.schema is not None, "NodeConnection.ready_for_verify, schema is None"
        assert self.token is not None, "NodeConnection.ready_for_verify, token is None"
        return True

    def ready_for_connect(self):
        assert self.user is not None, "NodeConnection.ready_for_verify, user is None"
        return True


# Create your models here.
class Node(models.Model):
    """
    A Node is a instance of a running Django noos-drift application
    Central is a special Node that recieves and propagates user simulation demands and recieves the results
    sent back by the Nodes
    """
    user = models.ForeignKey('auth.User', related_name='nodes', on_delete=models.CASCADE)
    description = models.TextField(default='')
    country = models.TextField(default='')
    hostname = models.TextField(default='')
    is_active = models.BooleanField(default=True)
    model = models.ForeignKey('NoosModel', related_name='nodes', on_delete=models.CASCADE, blank=True, null=True)
    node_connection = None

    def __str__(self):
        return u'%d: %s' % (self.pk, self.description)

    def add_local_simulation_demands(self, auser, filesfilter):
        """
        A function to insert a list of Simulation demands in the Node, when the simulation demands are files located
        on the computer.
        :param auser: The user who makes the demand
        :param filesfilter: a filter to use only json files
        :return:
        """
        # I would like a loop here that would process all requests files that are in a directory
        # requests files are json files with the request data
        # once a request has been sent it is renamed in order not to be processed again
        # here the parameters will already be tested as valid json before they are sent.
        # function .loads does the loading and the grammatical testing
        logger.info("Node.add_local_requests, start of")
        jsonlist = glob.glob(filesfilter)
        afile = ''
        arequest = ''
        # TODO: Change for better use of try except
        for fname in jsonlist:
            try:
                afile = open(fname, "r")
            except FileNotFoundError as fnferr:
                logger.error("Node.add_local_requests, could not find file : {}, {}".format(fname, fnferr))
                pass

            try:
                arequest = json.load(afile)
            except json.decoder.JSONDecodeError as decoderr:
                logger.error("Node.add_local_requests, {}".format(decoderr))
                afile.close()
                pass

            afile.close()
            atxtrequest = json.dumps(arequest, separators=(',', ':'))
            self.add_simulation_demand(atxtrequest, auser)

        logger.info("Node.add_local_requests, end of")
        return None

    def add_simulation_demand(self, a_txt_simulation_demand, node_user):
        """
        A method to send a simulation demand to a Node
        :param a_txt_simulation_demand: This is a JSON representation of a Simulation Demand.
        It must contain a json_txt field
        :param node_user:
        :return:
        """
        object_and_method_name = "Node.add_simulation_demand"
        logger.info("{}, start of".format(object_and_method_name))
        logger.info("{}, checking connection".format(object_and_method_name))
        if self.node_connection is None:
            if self.pk in ACTIVE_NODES.keys():
                self.node_connection = ACTIVE_NODES.get(self.pk)
                self.refresh_token()
            else:
                self.node_connection = NodeConnection(user=node_user)
                self.connect_client()
                ACTIVE_NODES[self.pk] = self.node_connection
        else:
            self.refresh_token()

        action = ['simulationdemands', 'create']
        try:
            logger.info("{}, json params : {}".format(object_and_method_name, a_txt_simulation_demand))
            message_parameters = json.loads(a_txt_simulation_demand)
            logger.info("{}, before action".format(object_and_method_name))
            the_client = self.node_connection.get_client()
            the_schema = self.node_connection.get_schema()
            result = the_client.action(the_schema, action, message_parameters)
            logger.info("{}, after action".format(object_and_method_name))
            logger.info("{}, result {}".format(object_and_method_name, result))
        except coreapi.exceptions.ErrorMessage as exc:
            logger.error("{}, {}".format(object_and_method_name, exc.error))
            raise exc
        except json.decoder.JSONDecodeError as decoderr:
            logger.error("{}, {}".format(object_and_method_name, decoderr))
            raise decoderr

        logger.info("{}, end of".format(object_and_method_name))
        return result

    def add_logging_message(self, message_parameters, the_user):
        """
        A method for sending logging messages to the node. The messages will be stored in the LogginMessage table
        :param message_parameters: A dictionary for a LoggingMessage object
        :param the_user: The user that posts the message
        :return:
        """
        if self.node_connection is None:
            if self.pk in ACTIVE_NODES.keys():
                self.node_connection = ACTIVE_NODES.get(self.pk)
                self.refresh_token()
            else:
                self.node_connection = NodeConnection(user=the_user)
                self.connect_client()
                ACTIVE_NODES[self.pk] = self.node_connection
        else:
            self.refresh_token()

        action = ['loggingmessages', 'create']
        try:
            logger.info("Node.add_logging_message, before action")
            the_client = self.node_connection.get_client()
            the_schema = self.node_connection.get_schema()
            logger.info(the_schema)
            result = the_client.action(the_schema, action, message_parameters)
            logger.info("Node.add_logging_message, after action")
            logger.info("Node.add_logging_message, result {}".format(result))
        except coreapi.exceptions.ErrorMessage as exc:
            logger.error("Node.add_logging_message, {}".format(exc.error))
            raise exc
        except json.decoder.JSONDecodeError as decoderr:
            logger.error("Node.add_logging_message, {}".format(decoderr))
            raise decoderr

        logger.info("Node.add_logging_message, end of")
        return result

    def add_uploadedfile(self, message_parameters, the_user):
        """
        A method to inform the Central Node that a new result file has been uploaded. This message is written on the
        Central in the uploadedfile table. When the Central writes in the uploaded file table, this triggers the
        unpacking of the file.
        :param message_parameters: A dictionary which describes the UploadedFile object
        :param the_user:
        :return:
        """
        if self.node_connection is None:
            if self.pk in ACTIVE_NODES.keys():
                self.node_connection = ACTIVE_NODES.get(self.pk)
                self.refresh_token()
            else:
                self.node_connection = NodeConnection(user=the_user)
                self.connect_client()
                ACTIVE_NODES[self.pk] = self.node_connection
        else:
            self.refresh_token()

        action = ['uploadedfiles', 'create']
        try:
            logger.info("Node.add_uploadedfile, before action")
            the_client = self.node_connection.get_client()
            the_schema = self.node_connection.get_schema()
            logger.info(the_schema)
            result = the_client.action(the_schema, action, message_parameters)
            logger.info("Node.add_uploadedfile, after action")
            logger.info("Node.add_uploadedfile, result {}".format(result))
        except coreapi.exceptions.ErrorMessage as exc:
            logger.error("Node.add_uploadedfile, {}".format(exc.error))
            raise exc
        except json.decoder.JSONDecodeError as decoderr:
            logger.error("Node.add_uploadedfile, {}".format(decoderr))
            raise decoderr

        logger.info("Node.add_uploadedfile, end of")
        return result

    def verify_token(self):
        """
        A method to verify the validity of a token this function supposes a connection is active
        :return:
        """
        # verify_token checks if a token is still valid
        logger.info("Node.verify_token, start of")
        assert self.node_connection is not None, "NodeConnection.verify_token, node_connection is None"

        self.node_connection.ready_for_verify()

        action = ['api-token-verify', 'create']
        try:
            logger.info("Node.verify_token, before action")
            aclient = self.node_connection.get_client()
            aschema = self.node_connection.get_schema()
            atoken = self.node_connection.get_token()
            auser = self.node_connection.get_user()
            params = {'token': atoken}
            result = aclient.action(aschema, action, params)
            logger.info("Node.verify_token, after action")
            logger.info("Node.verify_token, result {}".format(result))
            self.node_connection = NodeConnection(user=auser, client=aclient, schema=aschema, token=result['token'])
        except coreapi.exceptions.ErrorMessage as exc:
            # logger.error("Node.verify_token, {}".format(exc.error))
            # https://core-api.github.io/python-client/api-guide/document/#error
            logger.error("Node.verify_token, title {}".format(exc.error.title))
            raise exc

        logger.info("Node.verify_token, end of")
        return None

    def refresh_token(self):
        """
        A method to refresh a token. This function supposes that a connection is already active
        :return:
        """
        logger.info("Node.refresh_token, start of")
        assert self.node_connection is not None, "NodeConnection.refresh_token, node_connection is None"

        try:
            self.verify_token()
        except AssertionError as aerr:
            logger.error("Node.refresh_token, {}".format(aerr))
            raise aerr

        except coreapi.exceptions.ErrorMessage as exc:
            theerror = exc.error
            if theerror is None:
                logger.error("Node.refresh_token, error object is null")
                raise exc

            thedata = theerror.__dict__['_data']
            if thedata is None:
                logger.error("Node.refresh_token, data in error object is null")
                raise exc

            nfe = thedata['non_field_errors']
            if nfe is None:
                logger.error("Node.refresh_token, 'non_field_errors' in error object is null")
                raise exc

            if nfe[0] != 'Signature has expired.':
                logger.error("Node.refresh_token, error {} is unexpected".format(nfe[0]))
                raise exc

            logger.info("Node.refresh_token, attempting to create a new connection")
            self.connect_client()
            return None

        action = ['api-token-refresh', 'create']
        try:
            logger.info("Node.refresh_token, before action")
            aclient = self.node_connection.get_client()
            aschema = self.node_connection.get_schema()
            atoken = self.node_connection.get_token()
            auser = self.node_connection.get_user()
            params = {'token': atoken}
            result = aclient.action(aschema, action, params)
            logger.info("Node.refresh_token, after action")
            logger.info("Node.refresh_token, result {}".format(result))
            self.node_connection = NodeConnection(user=auser, client=aclient, schema=aschema, token=result['token'])
        except coreapi.exceptions.ErrorMessage as exc:
            logger.error("Node.refresh_token, {}".format(exc.error))
            raise exc

        logger.info("Node.refresh_token, end of")
        return None

    def set_user(self, auser):
        self.node_connection = NodeConnection(user=auser)

    def connect_client(self):
        logger.info("Node.connect_client, start of")
        assert self.node_connection is not None, "NodeConnection.connect_client, node_connection is None"

        try:
            self.node_connection.ready_for_connect()
        except AssertionError as aerr:
            logger.error("Node.connect_client, connection data not properly filled")
            logger.error("Node.connect_client, {}".format(aerr))
            raise aerr

        node_client = coreapi.Client()

        node_schema = node_client.get(self.hostname)
        logger.info("####Not Logged schema")
        logger.info(node_schema)
        action = ['api-token-auth', 'create']
        node_user = self.node_connection.get_user()
        params = {'username': node_user['username'], 'password': node_user['pwd']}
        try:
            logger.info("Node.connect_client, getting token")
            result = node_client.action(node_schema, action, params)
            logger.info("Node.connect_client, new token {}".format(result))
        except coreapi.exceptions.ErrorMessage as err:
            logger.error("Node.connect_client : {}".format(err.error))
            raise err

        auth = coreapi.auth.TokenAuthentication(
            scheme='JWT',
            token=result['token']
        )

        logger.info("Node.connect_client, creating authenticated client")
        node_client = coreapi.Client(auth=auth)
        node_schema = node_client.get(self.hostname)
        logger.info("####Logged in schema")
        logger.info(node_schema)
        logger.info("Node.connect_client, store user,client,schema and token in connection object")
        self.node_connection = NodeConnection(user=node_user, client=node_client, schema=node_schema,
                                              token=result['token'])
        logger.info("Node.connect_client, end of")
        return None


class SimulationDemand(models.Model):
    """
    A Simulation demand is created by a user and propagated to all Nodes
    Is linked to signals
       * simulation_demand_is_recieved
       * simulation_demand_is_created
    """
    user = models.ForeignKey('auth.User', related_name='simulations', on_delete=models.SET_NULL, blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    # json_txt = models.TextField(default='{}')
    json_txt = jsonfield.JSONField()

    def __str__(self):
        return u'%d: %s, %s' % (self.pk, self.created_time, self.json_txt)


class Forcing(models.Model):
    """
    Forcings are names associated with a set of parameters and calculation procedure that will be run on each Node
    Each Node will run a set of forcings for on simulation demand.
    The Forcings used by each Node are the ones active on the Node.
    Forcings have a use_type "O" or "M" for Oceanic or Meteorological
    """

    code = models.TextField(default='', null=False)
    display_name = models.TextField(default='', null=False)
    description = models.TextField(default='', null=False)
    use_type = models.TextField(default="O")

    # TODO : check if need parameter name for json and slugname to build the archive file
    #  example mws1.5 (wished parameter name in json file) <=> mws1dot5 (slugname now present in field code)

    def __str__(self):
        return u'%d: %s, %s, %s, %s' % (self.pk, self.code, self.display_name, self.description, self.use_type)


class NoosModel(models.Model):
    """
    The Models used
    Each Node should run one Model, a Model can Only be used on one Node
    """
    code = models.TextField(default='', null=False)
    display_name = models.TextField(default='', null=False)
    description = models.TextField(default='', null=False)


class LoggingMessage(models.Model):
    """
    Track Messages on Central and Nodes
    Is linked to signal
       * logging_message_is_created
    """
    node = models.ForeignKey('Node', related_name='loggingmessages', on_delete=models.CASCADE)
    forcing_couple = models.ForeignKey('ForcingCouple', related_name='loggingmessages', on_delete=models.CASCADE,
                                       blank=True, null=True)
    simulation_demand = models.ForeignKey('SimulationDemand', related_name='loggingmessages', on_delete=models.CASCADE)
    noos_model = models.ForeignKey('NoosModel', related_name='loggingmessages', on_delete=models.CASCADE,
                                   blank=True, null=True)

    status = models.TextField(default='')
    message = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u'%d: %s, %s, %s, %s, %s, %s' % (
            self.pk, self.status, self.created, self.message, self.node, self.simulation_demand, self.forcing_couple)


class ForcingCouple(models.Model):
    """
     A couple of forcings that should be used together when the model is called.
     A model will always be called with such a couple as parameters
     A list of such couples will be used for each model
    """

    noos_model = models.ForeignKey('NoosModel', related_name='forcing_couples', on_delete=models.CASCADE, blank=True,
                                   null=True)
    oceanical = models.ForeignKey('Forcing', related_name='couple_a', on_delete=models.CASCADE, blank=True,
                                  null=True)
    meteorological = models.ForeignKey('Forcing', related_name='couple_b', on_delete=models.CASCADE, blank=True,
                                       null=True)
    is_active = models.BooleanField(default=False, null=False)

    def couple_code(self):
        concat_code = self.oceanical.code + '_' + self.meteorological.code
        return concat_code

    def __str__(self):
        return u'%d: %s, %s, %s' % (self.pk, self.noos_model, self.oceanical, self.meteorological)


class UploadedFile(models.Model):
    """
    Track result files uploaded to Central
    """
    node = models.ForeignKey('Node', related_name='uploadedfiles', on_delete=models.CASCADE)
    simulation = models.ForeignKey('SimulationDemand', related_name='uploadedfiles', on_delete=models.CASCADE)
    noos_model = models.ForeignKey('NoosModel', related_name='uploadedfiles', on_delete=models.CASCADE,
                                   blank=True, null=True)
    forcing_couple = models.ForeignKey('ForcingCouple', related_name='uploadedfiles', on_delete=models.CASCADE,
                                       blank=True, null=True)

    filename = models.TextField(default='')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    # json_txt = models.TextField(default='{}')
    json_txt = jsonfield.JSONField()

    def __str__(self):
        return u'%d: %s, %s, %s, %s, %s, %s, %s, %s' % (self.pk, self.node, self.simulation, self.noos_model,
                                                        self.forcing_couple, self.filename, self.json_txt,
                                                        self.created, self.modified)
