from noos_services.ns_const import DRIFTER_NAME_OIL_CHOICES, DRIFTER_NAME_OBJECT_CHOICES, MemorySimulationDemand, \
    OtherConst

from django.core.exceptions import ValidationError
import datetime as dt
import logging
import pytz

logger = logging.getLogger(__name__)


class ValidationHelper:

    @staticmethod
    def clean_dissolution(drifter_type, data):
        if drifter_type == OtherConst.OBJECT:
            return False

        return data

    @staticmethod
    def validating_drifter_name(drifter_type, drifter_name):
        name_and_method = "ValidationHelper.validating_drifter_name"
        logger.info("{}, start".format(name_and_method))
        err_msg = "Invalid drifter type : {}, only object/oil".format(drifter_type)
        if drifter_type not in [OtherConst.OBJECT, OtherConst.OIL]:
            logger.error("{}, {}".format(name_and_method, err_msg))
            raise ValidationError(err_msg)
        ok_list = []
        if drifter_type == OtherConst.OIL:
            choices_list = DRIFTER_NAME_OIL_CHOICES
        else:
            choices_list = DRIFTER_NAME_OBJECT_CHOICES

        for a_tuple in choices_list:
            if a_tuple[1] != "":
                ok_list.append(a_tuple[0])
        # logger.debug("{}, Drifter_name list (valid choices) : {}".format(name_and_method, ok_list))
        # logger.debug("{}, Drifter_name to validate : {}".format(name_and_method, drifter_name))

        if drifter_name not in ok_list:
            err_msg = "Invalid drifter name : {}, not allowed for drifter_type {}".format(drifter_name, drifter_type)
            logger.error("{}, {}".format(name_and_method, err_msg))
            raise ValidationError(err_msg)

        return drifter_name

    @staticmethod
    def validating_geometry(data):
        err_msg = "Invalid geometry : {}, only point/polyline ".format(data)
        if data not in [OtherConst.POINT, OtherConst.POLYLINE]:
            raise ValidationError(err_msg)
        return data

    @staticmethod
    def clean_horizontal_spreading(drifter_type, data):
        if drifter_type == OtherConst.OBJECT:
            return False

        return data

    @staticmethod
    def validating_main_keys(json_data):
        name_and_method = "ValidationHelper.validating_main_keys"
        logger.info("{}, start".format(name_and_method))
        list_keys = json_data.keys()
        to_check = [MemorySimulationDemand.SIMULATION_DESCRIPTION, MemorySimulationDemand.DRIFTER,
                    MemorySimulationDemand.INITIAL_CONDITION, MemorySimulationDemand.MODEL_SETUP]
        for el_to_check in to_check:
            if el_to_check not in list_keys:
                errmsg = "No '{}' part".format(MemorySimulationDemand.SIMULATION_DESCRIPTION)
                logger.error("{}, {}".format(name_and_method, errmsg))
                raise ValidationError(errmsg)

        logger.info("{}, ok".format(name_and_method))

    @staticmethod
    def validating_float_coord(lat_or_lon, coordinate_values):
        """
        Validates checks if -90.0<lat<90.0 and -180.0< long<180.0
        :param lat_or_lon: the type of coordinate (lat or long)
        :param coordinate_values: a list of floats
        """
        name_and_method = "ValidationHelper.validating_float_coord"
        logger.info("{}, start".format(name_and_method))
        # logger.debug("{}, clean_data : {}".format(name_and_method, data))

        for a_value in coordinate_values:
            if not isinstance(a_value, float):
                err_msg = "Invalid value {} : {}".format(lat_or_lon, a_value)
                logger.error("{}, {}".format(name_and_method, err_msg))
                raise ValidationError(err_msg)
            if lat_or_lon == MemorySimulationDemand.LAT:
                if a_value < -90.0 or a_value > 90.0:
                    err_msg = "Invalid value {} : {}. Value must be between -90.0 and 90.0".format(lat_or_lon, a_value)
                    raise ValidationError(err_msg)
            elif lat_or_lon == MemorySimulationDemand.LON:
                if a_value < -180.0 or a_value > 180.0:
                    err_msg = "Invalid value {} : {}. Value must be between -180.0 and 180.0".format(lat_or_lon,
                                                                                                     a_value)
                    raise ValidationError(err_msg)

        logger.info("{}, end".format(name_and_method))
        return None

    @staticmethod
    def validating_number(drifter_type, data):

        if data is None:
            raise ValidationError("No number of particles??")

        try:
            data += 1
            data -= 1
        except TypeError:
            msgtmp = "Illegal value {} in '{}', only positive integers"
            raise ValidationError(msgtmp.format(data, MemorySimulationDemand.NUMBER))

        if data > 5000 or data < 0:
            tmp_msg = "Illegal value {} in '{}', maximum value is 5000"
            the_msg = tmp_msg.format(data, MemorySimulationDemand)
            raise ValidationError(the_msg)

        if drifter_type == OtherConst.OBJECT:
            return 1000
        return data

    @staticmethod
    def validating_radius(data):
        if data is None:
            return data

        try:
            data += 1
            data -= 1
        except TypeError:
            msgtmp = "Illegal value {} in '{}', only positive integers"
            raise ValidationError(msgtmp.format(data, MemorySimulationDemand.RADIUS))
        if data > 20000 or data < 0:
            tmp_msg = "Illegal value {} in '{}', maximum value is 20000"
            the_msg = tmp_msg.format(data, MemorySimulationDemand)
            raise ValidationError(the_msg)

        return data

    @staticmethod
    def txt_as_time(time_txt):
        name_and_method = "ValidationHelper.txt_as_time"
        logger.info("{}, start".format(name_and_method))
        # logger.debug("{}, time_txt : {}".format(name_and_method, time_txt))
        mesg_tmp = "Invalid value {} in '{}', value does not match format : YYYY-MM-DDTHH:mm:ssZ"
        err_msg = mesg_tmp.format(time_txt.strip(), MemorySimulationDemand.TIME, MemorySimulationDemand.TIMESTAMPFORMAT)
        try:
            # logger.debug("{}, Trying to format {}".format(name_and_method, time_txt))
            tm_strip = time_txt.strip()
            # logger.debug("{}, tm_strip : {}".format(name_and_method, tm_strip))
            the_time = dt.datetime.strptime(tm_strip, MemorySimulationDemand.TIMESTAMPFORMAT)
            utc_time_element = pytz.utc.localize(the_time)
            # logger.debug("{}, UTC formated time {}".format(name_and_method, utc_time_element))
        except (ValueError, ValidationError) as the_err:
            logger.error("{}, {}".format(name_and_method, the_err))
            raise ValidationError(err_msg)

        logger.info("{}, end".format(name_and_method))
        return utc_time_element

    @staticmethod
    def txt_list_to_time_list(timestamps_list):
        name_and_method = "ValidationHelper.txt_list_to_time_list"
        logger.info("{}, start".format(name_and_method))
        the_timestamp_list = []
        if isinstance(timestamps_list, list):
            # logger.debug("{}, receiving list, value : {}".format(name_and_method, timestamps_list))
            if isinstance(timestamps_list[0], str):
                for a_txt in timestamps_list:
                    # logger.debug("{}, list contains string".format(name_and_method))
                    the_timestamp_list.append(ValidationHelper.txt_as_time(a_txt.strip()))
            elif isinstance(timestamps_list[0], dt.datetime):
                # logger.debug("{}, list contains datetimes".format(name_and_method))
                the_timestamp_list.extend(timestamps_list)
        elif isinstance(timestamps_list, str):
            # logger.debug("{}, receiving string, value : {}".format(name_and_method, timestamps_list))
            other_list = timestamps_list.split(",")
            for a_txt in other_list:
                if isinstance(a_txt, dt.datetime):
                    # logger.debug("{}, string list contains datetime ???".format(name_and_method))
                    the_timestamp_list.append(a_txt)
                elif isinstance(a_txt, str):
                    # logger.debug("{}, string list contains string".format(name_and_method))
                    the_timestamp_list.append(ValidationHelper.txt_as_time(a_txt.strip()))
        logger.info("{}, end".format(name_and_method))
        return the_timestamp_list

    @staticmethod
    def validating_release_times_datetime(data):
        name_and_method = "ValidationHelper.validating_release_times_datetime"
        logger.info("{}, start".format(name_and_method))
        txt_timestmaps_list = []
        if isinstance(data, str):
            txt_timestmaps_list = data.split(",")
        else:
            txt_timestmaps_list.extend(data)
        release_times = []
        for a_txt_timestamp in txt_timestmaps_list:
            a_timestamp = ValidationHelper.txt_as_time(a_txt_timestamp)
            ValidationHelper.validating_in_time_limits(a_timestamp)
            release_times.append(a_timestamp)

        logger.info("{}, end".format(name_and_method))
        return release_times

    @staticmethod
    def validating_sedimentation(drifter_type, data):
        if drifter_type == OtherConst.OBJECT:
            return False

        return data

    @staticmethod
    def validating_simulation_time_data_time(data):
        name_and_method = "ValidationHelper.validating_simulation_time_data"
        logger.info("{}, start".format(name_and_method))
        time_element = ValidationHelper.txt_as_time(data)
        ValidationHelper.validating_in_time_limits(time_element)
        return time_element

    @staticmethod
    def validating_simulation_end_time(data):
        name_and_method = "ValidationHelper.validating_simulation_end_time"
        logger.info("{}, start".format(name_and_method))
        end_time = ValidationHelper.txt_as_time(data)
        ValidationHelper.validating_in_time_limits(end_time)
        clean_data = end_time.strftime(MemorySimulationDemand.TIMESTAMPFORMAT)
        logger.info("{}, end".format(name_and_method))
        return clean_data

    @staticmethod
    def validating_simulation_start_time(data):
        name_and_method = "ValidationHelper.validating_simulation_start_time"
        logger.info("{}, start".format(name_and_method))
        start_time = ValidationHelper.txt_as_time(data)
        ValidationHelper.validating_in_time_limits(start_time)
        clean_data = start_time.strftime(MemorySimulationDemand.TIMESTAMPFORMAT)
        logger.info("{}, end".format(name_and_method))
        return clean_data

    @staticmethod
    def validating_release_times(data):
        name_and_method = "ValidationHelper.validating_release_times"
        logger.info("{}, start".format(name_and_method))
        logger.info("{}, data : {}".format(name_and_method, data))
        clean_txt_timestamps = []
        release_times = ValidationHelper.txt_list_to_time_list(data)

        for a_timestamp in release_times:
            clean_data = a_timestamp.strftime(MemorySimulationDemand.TIMESTAMPFORMAT)
            clean_txt_timestamps.append(clean_data)

        logger.info("{}, end".format(name_and_method))
        # clean_string = ",".join(clean_txt_timestamps)
        return clean_txt_timestamps

    @staticmethod
    def validating_release_times_coherence(release_times, start_time, end_time, simulation_type):
        name_and_method = "ValidationHelper.validating_release_times_coherence"
        logger.info("{}, start".format(name_and_method))
        the_future = None
        the_past = None
        if simulation_type == OtherConst.FORWARD:
            the_past = start_time
            the_future = end_time
        elif simulation_type == OtherConst.BACKWARD:
            the_past = end_time
            the_future = start_time

        for a_release_time in release_times:
            # logger.debug("{}, type a_release_time {}".format(name_and_method, type(a_release_time)))
            # logger.debug("{}, type the_past {}".format(name_and_method, type(the_past)))
            # logger.debug("{}, type the_future {}".format(name_and_method, type(the_future)))
            if a_release_time < the_past or a_release_time > the_future:
                err_msg = "Release times out of [start_time, end_time] limits"
                logger.error("{}, {}".format(name_and_method, err_msg))
                raise ValidationError(err_msg)

        logger.info("{}, end".format(name_and_method))
        return None

    @staticmethod
    def validating_simulation_type(data):
        err_msg = "Invalid simulation type : {}, only {}/{}".format(data, OtherConst.FORWARD, OtherConst.BACKWARD)
        if data not in [OtherConst.FORWARD, OtherConst.BACKWARD]:
            raise ValidationError(err_msg)

        return data

    @staticmethod
    def validating_in_time_limits(a_datetime):
        four_days = dt.timedelta(days=4)
        when_am_i = dt.datetime.utcnow()
        four_days_ago = when_am_i - four_days
        four_days_from_now = when_am_i + four_days
        utc_four_days_from_now = pytz.utc.localize(four_days_from_now)
        utc_four_days_ago = pytz.utc.localize(four_days_ago)
        err_msg = "Time : {} out of [-4day, +4days] window".format(a_datetime)
        if a_datetime > utc_four_days_from_now or a_datetime < utc_four_days_ago:
            raise ValidationError(err_msg)
        return None

    @staticmethod
    def validating_total_mass(drifter_type, data):
        name_and_method = "ValidationHelper.validating_simulation_start_time"
        logger.info("{}, start".format(name_and_method))
        try:
            data += 1
            data -= 1
        except TypeError:
            tmp_msg = "Illegal value {} in '{}', only positive integers"
            the_msg = tmp_msg.format(data, MemorySimulationDemand.TOTAL_MASS)
            logger.error("{}, {}".format(name_and_method, the_msg))
            raise ValidationError(the_msg)

        if drifter_type == OtherConst.OIL:
            if data > 10000000 or data < 0:
                tmp_msg = "Illegal value {} in '{}', value must be > 0,  and < 10000000"
                the_msg = tmp_msg.format(data, MemorySimulationDemand.TOTAL_MASS)
                logger.error("{}, {}".format(name_and_method, the_msg))
                raise ValidationError(the_msg)
        else:
            if data != -1:
                return -1
        logger.info("{}, end".format(name_and_method))
        return data

    @staticmethod
    def validating_coordinates_consistency(geometry_type, lats_list, lons_list):
        name_and_method = "ValidationHelper.validating_coordinates_consistency"
        logger.info("{}, start".format(name_and_method))
        if len(lats_list) != len(lons_list):
            raise ValidationError("number of latitudes != number of longitudes")
        if geometry_type == OtherConst.POINT and len(lats_list) != 1:
            raise ValidationError("{} geometry, number of latitudes and number of longitudes must = 1".format(
                OtherConst.POINT))
        if geometry_type == OtherConst.POLYLINE and len(lats_list) != 2:
            raise ValidationError("{} geometry, number of latitudes and number of longitudes must = 2".format(
                OtherConst.POLYLINE))
        logger.info("{}, end".format(name_and_method))
        return None
