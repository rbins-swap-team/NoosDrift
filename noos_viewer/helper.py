import logging

from noos_services.ns_const import MemorySimulationDemand, OtherConst
from noos_services.models import Forcing, ForcingCouple, NoosModel, SimulationCloud, SimulationDemand, \
    SimulationElement, SimulationMetadata
logger = logging.getLogger(__name__)


class SimulationDemandHelper(MemorySimulationDemand):

    @staticmethod
    def simulation_init(simulationid):
        """
        All basic elements of a demand.
        This method is called by the Web-Interface to start working on demand results and get the basic info.
        :param simulationid:
        :return:
        """
        object_and_method = "Helper.simulation_init"
        logger.info("{}, start".format(object_and_method))
        the_simulation = SimulationDemand.active_objects.get(pk=simulationid)
        simulation_title = the_simulation.json_txt[MemorySimulationDemand.SIMULATION_DESCRIPTION][
            MemorySimulationDemand.TITLE]
        simulation_summary = the_simulation.json_txt[MemorySimulationDemand.SIMULATION_DESCRIPTION][
            MemorySimulationDemand.SUMMARY]
        metadata = SimulationMetadata.objects.get(simulation=the_simulation)
        simulation_doc = SimulationElement.objects.get(simulation=the_simulation, idx=0)

        init_dict = {"ellipses_and_clusters": simulation_doc.json_data, "metadata": metadata.metadata,
                     "title": simulation_title, "summary": simulation_summary}
        logger.info("{}, simulation title : {}".format(object_and_method, simulation_title))
        logger.info("{}, end".format(object_and_method))
        return init_dict

    @staticmethod
    def simulations_for_demand(simulationid, stepidx):
        """
        Returns a particular step of a specific simulation
        :param simulationid:
        :param stepidx:
        :return:
        """
        object_and_method = "Helper.simulations_for_demand"
        logger.info("{}, start".format(object_and_method))
        the_simulation = SimulationDemand.active_objects.get(pk=simulationid)
        simulation_element = SimulationElement.objects.get(simulation=the_simulation, idx=stepidx)
        logger.info("{}, end".format(object_and_method))

        return {"ellipses_and_clusters": simulation_element.json_data}

    def extract_simulation_dict(self, simulation_demand):
        """
        This method receives a SimulatonDemand object and transforms it into a dictionary with keys or different
        elements of the object.json_txt field.
        This is very useful to feed the dictionary to a SimulationDemandForm
        :param simulation_demand: A SimulationDemand object
        :return: A dictionary with object values.
        """
        name_and_method = "Helper.extract_simulation_dict"
        logger.info("{}, start".format(name_and_method))
        json_dict = simulation_demand.json_txt

        simulation_demand_dict = {self.ID: simulation_demand.id,
                                  self.CREATED_TIME: simulation_demand.created_time.strftime("%Y-%m-%dT%H:%M")}

        if simulation_demand.status is not None and simulation_demand.status not in [""]:
            simulation_demand_dict[self.STATUS] = simulation_demand.status
        else:
            # logger.debug("{}, status is None or empty ??".format(name_and_method))
            simulation_demand_dict[self.STATUS] = 'OK?'

        simulation_demand_dict[self.PROTECTED] = simulation_demand.protected
        simulation_demand_dict[self.TITLE] = json_dict[self.SIMULATION_DESCRIPTION][self.TITLE]
        simulation_demand_dict[self.SUMMARY] = json_dict[self.SIMULATION_DESCRIPTION][self.SUMMARY]
        if self.TAGS in json_dict[self.SIMULATION_DESCRIPTION]:
            simulation_demand_dict[self.TAGS] = ",".join(json_dict[self.SIMULATION_DESCRIPTION][self.TAGS])
        else:
            simulation_demand_dict[self.TAGS] = None

        simulation_demand_dict[self.SIMULATION_TYPE] = json_dict[self.SIMULATION_DESCRIPTION][self.SIMULATION_TYPE]
        simulation_demand_dict[self.SIMULATION_START_TIME] = json_dict[self.SIMULATION_DESCRIPTION][
            self.SIMULATION_START_TIME]
        simulation_demand_dict[self.SIMULATION_END_TIME] = json_dict[self.SIMULATION_DESCRIPTION][
            self.SIMULATION_END_TIME]

        simulation_demand_dict[self.DRIFTER_TYPE] = json_dict[self.DRIFTER][self.DRIFTER_TYPE]
        simulation_demand_dict[self.DRIFTER_NAME] = json_dict[self.DRIFTER][self.DRIFTER_NAME]
        if simulation_demand_dict[self.DRIFTER_TYPE] == OtherConst.OBJECT:
            simulation_demand_dict[self.TOTAL_MASS] = 5000
        else:
            simulation_demand_dict[self.TOTAL_MASS] = json_dict[self.DRIFTER][self.TOTAL_MASS]

        simulation_demand_dict[self.GEOMETRY] = json_dict[self.INITIAL_CONDITION][self.GEOMETRY]

        if self.LON in json_dict[self.INITIAL_CONDITION]:
            if isinstance(json_dict[self.INITIAL_CONDITION][self.LON], list):
                strlist = []
                for el in json_dict[self.INITIAL_CONDITION][self.LON]:
                    strlist.append("{}".format(el))
                simulation_demand_dict[self.LON] = ",".join(strlist)
            if isinstance(json_dict[self.INITIAL_CONDITION][self.LON], float):
                simulation_demand_dict[self.LON] = "{}".format(json_dict[self.INITIAL_CONDITION][self.LON])
        else:
            simulation_demand_dict[self.LON] = None

        if self.LAT in json_dict[self.INITIAL_CONDITION]:
            if isinstance(json_dict[self.INITIAL_CONDITION][self.LAT], list):
                strlist = []
                for el in json_dict[self.INITIAL_CONDITION][self.LAT]:
                    strlist.append("{}".format(el))
                simulation_demand_dict[self.LAT] = ",".join(strlist)
            if isinstance(json_dict[self.INITIAL_CONDITION][self.LAT], float):
                simulation_demand_dict[self.LAT] = "{}".format(json_dict[self.INITIAL_CONDITION][self.LAT])
        else:
            simulation_demand_dict[self.LAT] = None

        simulation_demand_dict[self.RADIUS] = json_dict[self.INITIAL_CONDITION][self.RADIUS]
        if self.RADIUS in json_dict[self.INITIAL_CONDITION]:
            if isinstance(json_dict[self.INITIAL_CONDITION][self.RADIUS], list):
                strlist = []
                for el in json_dict[self.INITIAL_CONDITION][self.RADIUS]:
                    strlist.append("{}".format(el))
                simulation_demand_dict[self.RADIUS] = ",".join(strlist)
            if isinstance(json_dict[self.INITIAL_CONDITION][self.RADIUS], float):
                simulation_demand_dict[self.RADIUS] = "{}".format(json_dict[self.INITIAL_CONDITION][self.RADIUS])
        else:
            simulation_demand_dict[self.RADIUS] = None

        simulation_demand_dict[self.NUMBER] = json_dict[self.INITIAL_CONDITION][self.NUMBER]

        release_times = json_dict[self.INITIAL_CONDITION][self.TIME]
        if isinstance(release_times, str):
            simulation_demand_dict[self.RELEASE_TIMES] = release_times
        elif isinstance(release_times, list):
            simulation_demand_dict[self.RELEASE_TIMES] = ",".join(release_times)

        simulation_demand_dict[self.CONE] = "true"
        if json_dict[self.INITIAL_CONDITION].get(self.CONE, False) is False:
            simulation_demand_dict[self.CONE] = "false"

        simulation_demand_dict[self.FORM_TWODTHREED] = json_dict[self.MODEL_SETUP].get(self.TWODTHREED, OtherConst.TWOD)
        simulation_demand_dict[self.BEACHING] = json_dict[self.MODEL_SETUP].get(self.BEACHING, False)
        simulation_demand_dict[self.BUOYANCY] = json_dict[self.MODEL_SETUP].get(self.BUOYANCY, False)
        simulation_demand_dict[self.CURRENT] = json_dict[self.MODEL_SETUP].get(self.CURRENT, False)

        simulation_demand_dict[self.DISSOLUTION] = json_dict[self.MODEL_SETUP].get(self.DISSOLUTION, False)
        simulation_demand_dict[self.EVAPORATION] = json_dict[self.MODEL_SETUP].get(self.EVAPORATION, False)
        simulation_demand_dict[self.HORIZONTAL_SPREADING] = json_dict[self.MODEL_SETUP].get(self.HORIZONTAL_SPREADING,
                                                                                            False)
        simulation_demand_dict[self.NATURAL_VERTICAL_DISPERTION] = json_dict[self.MODEL_SETUP].get(
            self.NATURAL_VERTICAL_DISPERTION, False)
        simulation_demand_dict[self.SEDIMENTATION] = json_dict[self.MODEL_SETUP].get(self.SEDIMENTATION, False)
        simulation_demand_dict[self.WAVES] = json_dict[self.MODEL_SETUP].get(self.WAVES, False)
        simulation_demand_dict[self.WIND] = json_dict[self.MODEL_SETUP].get(self.WIND, False)

        logger.info("{}, end".format(name_and_method))
        return simulation_demand_dict

    @staticmethod
    def str_to_float_list(str_floats):
        """
        Convert a string containing a list of floats as text into a list of float objects.
        The floats elements in the text are separated by ","
        :param str_floats:
        :return:
        """
        strels = str_floats.split(",")
        list_fvals = []
        for anel in strels:
            try:
                fval = float(anel)
                list_fvals.append(fval)
            except ValueError:
                pass

        return list_fvals

    def extract_from_form_for_new(self, simulation_demand_form):
        """
        Extract a Dictionary from a SimulationDemandForm
        This method is called by the view. The result will be used to create the SimulationDemand object
        :param simulation_demand_form:
        :return:
        """
        name_and_method = "extract_from_form_for_new"
        logger.info("{}, start".format(name_and_method))
        form_dict = {self.PROTECTED: False}
        if self.PROTECTED in simulation_demand_form.cleaned_data:
            form_dict[self.PROTECTED] = simulation_demand_form.cleaned_data[self.PROTECTED]

        alltags_str = simulation_demand_form.cleaned_data[self.TAGS]
        alltags_list = []
        for tag_el in alltags_str.split(","):
            alltags_list.append(tag_el)

        simulation_description_dict = {self.TITLE: simulation_demand_form.cleaned_data[self.TITLE],
                                       self.SUMMARY: simulation_demand_form.cleaned_data[self.SUMMARY],
                                       self.TAGS: alltags_list,
                                       self.SIMULATION_TYPE: simulation_demand_form.cleaned_data[
                                           self.SIMULATION_TYPE],
                                       self.SIMULATION_START_TIME: simulation_demand_form.cleaned_data[
                                           self.SIMULATION_START_TIME],
                                       self.SIMULATION_END_TIME: simulation_demand_form.cleaned_data[
                                           self.SIMULATION_END_TIME]}

        drifter_dict = {self.DRIFTER_TYPE: simulation_demand_form.cleaned_data[self.DRIFTER_TYPE],
                        self.DRIFTER_NAME: simulation_demand_form.cleaned_data[self.DRIFTER_NAME],
                        self.TOTAL_MASS: simulation_demand_form.cleaned_data[self.TOTAL_MASS]}

        form_value_list = simulation_demand_form.cleaned_data[self.RELEASE_TIMES]
        timelist = []
        for listel in form_value_list:
            if isinstance(listel, str):
                timelist.append(listel)

        initial_condition_dict = {self.GEOMETRY: simulation_demand_form.cleaned_data[self.GEOMETRY],
                                  self.LON: simulation_demand_form.cleaned_data[self.LON],
                                  self.LAT: simulation_demand_form.cleaned_data[self.LAT],
                                  self.RADIUS: simulation_demand_form.cleaned_data[self.RADIUS],
                                  self.NUMBER: simulation_demand_form.cleaned_data[self.NUMBER],
                                  self.TIME: timelist,
                                  self.CONE: False}

        if self.CONE in simulation_demand_form.cleaned_data:
            initial_condition_dict[self.CONE] = True

        model_set_up_dict = {self.TWODTHREED: simulation_demand_form.cleaned_data[self.FORM_TWODTHREED]}

        # logger.debug("extract_from_form_for_new, cleaned_date, beaching : {} ".format(
        #     simulation_demand_form.cleaned_data[self.BEACHING]))
        # logger.debug("extract_from_form_for_new, cleaned_date, buoyancy : {} ".format(
        #    simulation_demand_form.cleaned_data[self.BUOYANCY]))

        for aval in self.CBVALS:
            assign = False
            if aval in simulation_demand_form.cleaned_data:
                assign = simulation_demand_form.cleaned_data[aval]
            model_set_up_dict[aval] = assign

        model_set_up_dict[self.CURRENT] = True
        model_set_up_dict[self.WAVES] = True
        model_set_up_dict[self.WIND] = True

        # logger.debug("extract_from_form_for_new, beaching : {} ".format(model_set_up_dict[self.BEACHING]))
        # logger.debug("extract_from_form_for_new, buoyancy : {} ".format(model_set_up_dict[self.BUOYANCY]))
        # logger.debug("extract_from_form_for_new, current : {} ".format(model_set_up_dict[self.CURRENT]))

        json_dict = {self.SIMULATION_DESCRIPTION: simulation_description_dict,
                     self.DRIFTER: drifter_dict,
                     self.INITIAL_CONDITION: initial_condition_dict,
                     self.MODEL_SETUP: model_set_up_dict}

        form_dict[self.JSON_TXT] = json_dict
        logger.info("{}, end".format(name_and_method))
        return form_dict

    def extract_from_form_for_edit(self, simulation_demand_form):
        """
        Called for Web-Interface.
        Extracts minimum values to update SimulationDemand
        :param simulation_demand_form:
        :return:
        """
        object_and_name = "Helper.extract_from_form_for_edit"
        logger.info("{}, start".format(object_and_name))
        form_dict = {self.ID: simulation_demand_form.cleaned_data[self.ID]}
        simulation_description_dict = {self.TITLE: simulation_demand_form.cleaned_data[self.TITLE]}
        simulation_description_dict.update({self.SUMMARY: simulation_demand_form.cleaned_data[self.SUMMARY]})
        strtagslist = simulation_demand_form.cleaned_data[self.TAGS]
        taglist = []
        for atag in strtagslist.split(','):
            taglist.append(atag)
        simulation_description_dict.update({self.TAGS: taglist})

        form_dict[self.PROTECTED] = False
        if self.PROTECTED in simulation_demand_form.cleaned_data:
            form_dict[self.PROTECTED] = simulation_demand_form.cleaned_data[self.PROTECTED]

        form_dict[self.SIMULATION_DESCRIPTION] = simulation_description_dict
        # logger.info("{}, {}".format(object_and_name, form_dict))
        logger.info("{}, end".format(object_and_name))
        return form_dict

    @staticmethod
    def cloud_of_points_for_demand(demand_id, name_triplet, step_idx):
        """
        Called by cloud_of_points_for_demand. This is the method which really performs the extraction
        :param demand_id:
        :param name_triplet:
        :param step_idx:
        :return:
        """
        object_and_name = "Helper.cloud_of_points_for_demand"
        SimulationDemand.active_objects.get(pk=demand_id)
        logger.info("{}, start".format(object_and_name))
        # logger.debug("{}, parameters : {}, {}, {}".format(object_and_name, demand_id, name_triplet, step_idx))

        a_list = name_triplet.split("_")
        if len(a_list) != 3:
            raise ValueError("parameter : {}, cannot be parsed into a model_current-model_wind-model".format(
                name_triplet))
            
        model_name = a_list[0]
        current_name = a_list[1]
        wind_name = a_list[2]

        # logger.debug("{}, model : {}, current : {}, wind : {}".format(object_and_name, model_name, current_name,
        #                                                              wind_name))

        the_model = NoosModel.objects.get(code=model_name)
        current_forcing = Forcing.objects.get(code=current_name)
        wind_forcing = Forcing.objects.get(code=wind_name)

        forcing_couple = ForcingCouple.objects.get(noos_model=the_model, oceanical=current_forcing,
                                                   meteorological=wind_forcing)
        the_cloud = SimulationCloud.objects.get(simulation=demand_id, idx=step_idx, noos_model=the_model,
                                                forcing_couple=forcing_couple)
        model_couple_code = "{}_{}".format(the_model.code, forcing_couple.couple_code())
        noos_model_couple = "{}_{}".format(the_model.id, forcing_couple.id)
        the_cloud = {"coordinates": the_cloud.cloud_data["coordinates"], "model_couple_id": noos_model_couple,
                     "simulation_name": model_couple_code}
        logger.info("{}, end".format(object_and_name))
        return the_cloud
