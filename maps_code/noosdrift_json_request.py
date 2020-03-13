#!/usr/bin/env python

import os
import json


class Noosdrift_JSON_request:
    filename = ""

    def __init__(self, myfilename):
        """
        Noosdrift_JSON_request builder
        :param myfilename:
        """

        if os.path.isfile(myfilename):
            fin = open(myfilename)
            self.__dict__ = json.load(fin)
        else:
            print('filename does not exist - create an empty structure')
            self.set_default_values()

        self.filename = myfilename
        return

    def set_default_values(self):
        """
        Initialize a Noosdrift_JSON_request object from scratch
        :return:
        """

        self.__dict__ = {}
        self.__dict__["simulation_description"] = {}
        self.__dict__["simulation_description"]["request_id"] = None
        self.__dict__["simulation_description"]["owner_id"] = None
        self.__dict__["simulation_description"]["title"] = None
        self.__dict__["simulation_description"]["tags"] = None
        self.__dict__["simulation_description"]["simulation_type"] = None
        self.__dict__["simulation_description"]["simulation_start_time"] = None
        self.__dict__["simulation_description"]["simulation_end_time"] = None

        self.__dict__["drifter"] = {}
        self.__dict__["drifter"]["drifter_type"] = None
        self.__dict__["drifter"]["drifter_name"] = None
        self.__dict__["drifter"]["total_mass"] = None

        self.__dict__["initial_condition"] = {}
        self.__dict__["initial_condition"]["geometry"] = None
        self.__dict__["initial_condition"]["lon"] = None
        self.__dict__["initial_condition"]["lat"] = None
        self.__dict__["initial_condition"]["radius"] = None
        self.__dict__["initial_condition"]["number"] = None
        self.__dict__["initial_condition"]["time"] = None
        self.__dict__["initial_condition"]["z"] = None
        self.__dict__["initial_condition"]["cone"] = None

        self.__dict__["model_set_up"] = {}
        self.__dict__["model_set_up"]["model"] = None
        self.__dict__["model_set_up"]["ocean_forcing"] = None
        self.__dict__["model_set_up"]["wind_forcing"] = None
        self.__dict__["model_set_up"]["2D/3D"] = None
        self.__dict__["model_set_up"]["current"] = None
        self.__dict__["model_set_up"]["waves"] = None
        self.__dict__["model_set_up"]["wind"] = None
        self.__dict__["model_set_up"]["beaching"] = None
        self.__dict__["model_set_up"]["horizontal spreading"] = None
        self.__dict__["model_set_up"]["natural_vertical_dispersion"] = None
        self.__dict__["model_set_up"]["buoyancy"] = None
        self.__dict__["model_set_up"]["evaporation"] = None
        self.__dict__["model_set_up"]["dissolution"] = None
        self.__dict__["model_set_up"]["sedimentation"] = None

        self.__dict__["simulation_result"] = {}
        self.__dict__["simulation_result"]["status_code"] = None
        self.__dict__["simulation_result"]["result_filename"] = None
        return

    def check_validity(self):
        """
        This function actually aims at checking if the __dict__ object contains all the entry
        :return: True if the dictionary contains the expected mandatary keys
        """

        is_valid = True

        # check simulation description
        if "simulation_description" in self.__dict__:
            mandatory_elements = ("request_id", "owner_id", "title", "tags", "simulation_type", "simulation_start_time",
                                  "simulation_end_time")
            for element in mandatory_elements:
                if element not in self.__dict__["simulation_description"]:
                    is_valid = False
        else:
            is_valid = False

            # check drifter
        if "drifter" in self.__dict__:
            mandatory_elements = ("drifter_type", "drifter_name")
            for element in mandatory_elements:
                if element not in self.__dict__["drifter"]:
                    is_valid = False
        else:
            is_valid = False

            # check "initial_condition"
        if "initial_condition" in self.__dict__:
            mandatory_elements = ("lon", "lat", "radius", "number", "time", "z")
            for element in mandatory_elements:
                if element not in self.__dict__["initial_condition"]:
                    is_valid = False
        else:
            is_valid = False

            # check "model_set_up"
        if "model_set_up" in self.__dict__:
            mandatory_elements = (
                "model", "ocean_forcing", "wind_forcing", "2D/3D", "current", "waves", "wind", "beaching",
                "horizontal spreading", "natural_vertical_dispersion", "buoyancy", "evaporation",
                "dissolution", "sedimentation")
            for element in mandatory_elements:
                if element not in self.__dict__["model_set_up"]:
                    is_valid = False
        else:
            is_valid = False
        return is_valid

    def set_value(self, name, value):
        ''' generic set value function'''
        found = False

        for primary_object in self.__dict__:
            for key in self.__dict__[primary_object]:
                if key == name:
                    found = True
                    self.__dict__[primary_object][name] = value

        if found == False:
            print(f"Unable to assign value {value} to param {name} (param {name} not found)")

        return

    def get_value(self, name):
        ''' generic get_value() function'''
        found = False

        for primary_object in self.__dict__:
            for key in self.__dict__[primary_object]:
                if key == name:
                    found = True
                    return self.__dict__[primary_object][name]

        if found == False:
            print(f"get_value ---- param {name} not found")

        return -1

    def get_simulation_description(self):
        ''' get_simulation_description(self) returns the json object simulation_description'''
        return self.__dict__["simulation_description"]

    def get_drifter(self):
        ''' get_drifter(self) returns the json object drifter'''
        return self.__dict__["drifter"]

    def get_initial_condition(self):
        ''' get_initial_condition(self) returns the json object initial_condition'''
        return self.__dict__["initial_condition"]

    def get_model_set_up(self):
        ''' get_model_set_up(self) returns the json object model_set_up'''
        return self.__dict__["model_set_up"]

    def get_simulation_result(self):
        ''' get_simulation_result(self) returns the json object simulation_result'''
        try:
            simulation_result = self.__dict__["simulation_result"]
        except:
            self.__dict__["simulation_result"] = None
        return self.__dict__["simulation_result"]

    def set_filename(self, filename):
        ''' set_filename()'''
        self.filename = filename

    def set_status_code(self, status_code):
        '''
        set_status_code() set the status_code value


        0 : Model simulation successfully completed (no error)
        1 : ERROR: initial position out of model domain
        2 : ERROR: initial position on land
        3 : ERROR: Simulation start and/or end time are not in the forcing availability period [today – 4 days, today + 4 days]
        4 : ERROR : Release time of Lagrangian particle out of the simulation start time and end time windows
        5 : ERROR : Drifter type unknown or not available in the model
        6 : ERROR: Model cannot handle the requested set-up -> set-up has been adapted
        7 : ERROR: any other error in the model pre-processing
        8 : ERROR: any error in the model processing
        9 : ERROR: any error in the model post-processing : preparation of the model output
        '''
        try:
            simulation_result = self.__dict__["simulation_result"]
        except:
            self.__dict__["simulation_result"] = {}
        self.__dict__["simulation_result"]["status_code"] = status_code

    def get_status_code(self):
        '''
           get_status_code() returns the status_code value
        '''

        try:
            status_code = self.__dict__["simulation_result"]
        except:
            self.__dict__["simulation_result"] = {}

        try:
            status_code = self.__dict__["simulation_result"]["status_code"]
        except:
            self.__dict__["simulation_result"]["status_code"] = None

        return self.__dict__["simulation_result"]["status_code"]

    def set_result_filename(self, value):
        try:
            self.__dict__["simulation_result"]
        except:
            self.__dict__["simulation_result"] = {}
        self.__dict__["simulation_result"]["result_filename"] = value
        return

    def export(self):
        '''
            the function export() updates the noosdrift request file.
            useful for keeping up to date at the metadata contained in the file between the different stages of the noosdrift request
        '''
        print(self.filename)
        try:
            fout = open(self.filename, 'w')
            json.dump(self.__dict__, fout)
            fout.close()
        except:
            print(f'Unable to export json request file data in {self.filename}')
        return
