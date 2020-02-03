"use strict";

$(function ($, L, window) {
  let drifter_type = $('#id_drifter_type');
  let drifter_name = $('#id_drifter_name');

  let twoDthreeD = $('#id_twoDthreeD');
  let buoyancy = $('#id_buoyancy');
  let beaching = $('#id_beaching');
  let natural_vertical_dispersion = $('#id_natural_vertical_dispersion');
  let dissolution = $('#id_dissolution');
  let evaporation = $('#id_evaporation');
  let horizontal_spreading = $('#id_horizontal_spreading');
  let sedimentation = $('#id_sedimentation');

  let title = $('#id_title');
  let simulation_type = $('#id_simulation_type');
  let simulation_start_time = $('#id_simulation_start_time');
  let simulation_end_time = $('#id_simulation_end_time');
  let release_times = $('#id_release_times');

  let geometry = $('#id_geometry');
  let latitudes = $('#id_lat');
  let longitudes = $('#id_lon');

  let nbr_particles = $('#id_number');
  let radius = $('#id_radius');
  let total_mass = $('#id_total_mass');

  let the_submit = $('#id_submit');
  let the_form = $('#id_demandform');

  let future = moment.utc();
  future.add(4,'days');
  let past = moment.utc();
  past.subtract(4,'days');
  let releaseTimeErrorMsg = "";
  let dynamicReleaseTimeErrorMsg = function () { return releaseTimeErrorMsg; };
  let timeLimitErrorMsg = "";
  let dynamicTimeLimitErrorMsg = function () { return timeLimitErrorMsg; };

  let goBack = function() {
      window.history.back();
  };

  const FORWARD = "forward";
  const BACKWARD = "backward";
  const POINT = "point";
  const POLYLINE = "polyline";
  const OBJECT = "object";
  const OIL = "oil";
  const TWOD = "2D";
  const THREED = "3D";
  const TIMEFORMAT01 = 'YYYY-MM-DDTHH:mm:ssZ';
  const TIMEFORMAT02 = 'YYYY-MM-DDTHH:mm:ssz';

  function NoTimeFoundException(message) {
      this.message = message;
      this.name = "NoTimeFoundException";
  }

  function OutOfTimeLimitException(message) {
      this.message = message;
      this.name = "OutOfTimeLimitException";
  }

  function TimesDoNotMatchTypeException(message) {
     this.message = message;
     this.name = "TimesDoNotMatchType";
  }

  /**
   * Format text geometrical float values properly
   * Basically make sure it ends at least with ".0" to make it clear that this is a float
   * @param geom_floats (a list of float objects)
   * @returns {string} (a string containg a list of floats separated by ",")
   */
  let geom_floats_as_str = function(geom_floats) {
      let txt_float_list = [];
      geom_floats.forEach(function(item, index, array) {
          let txtitem = ""+item;
          if (!txtitem.includes(".")) {
              txtitem = txtitem+".0";
          }
          txt_float_list.push(txtitem);
      });
      return txt_float_list.join(",");
  };

  /**
   * Extract float values from strings
   * @param txt_to_extract_from
   * @returns {[]}, a list of floats as float Objects
   */
  let extract_float_values = function(txt_to_extract_from) {
      let model_regex = /(-?\d*\.?\d*)/g;
      let all_vals = [...txt_to_extract_from.matchAll(model_regex)];
      let all_floats = [];
      all_vals.forEach(function(item, index, array) {
          let testval = parseFloat(item[1]);
          if (!isNaN(testval)) {
              all_floats.push(testval);
          }
      });
      return all_floats;
  };

  /**
   * Can be used for both lon and lat fields
   * This method is used by jquery.validator, see validator.addMethod and parameters for field validation.
   * @param str_for_floats (a list of float numbers represented as strings)
   * @param element (the element concerned)
   * @param param (the maximum value used, either 90 or 180
   * @returns {boolean}
   */
  let check_coord_vals = function(str_for_floats, element, param) {
      let the_floats = extract_float_values(str_for_floats);
      if (the_floats.length === 0) {
          return false;
      }
      let the_length = the_floats.length;
      let the_item = null;
      for(let idx=0;idx<the_length;idx++) {
          the_item = the_floats[idx];
          if (the_item < (-1.0*param) || the_item > param) {
             return false;
          }
      }
      let new_str_for_floats = geom_floats_as_str(the_floats);
      $(element.id).val(new_str_for_floats);
      return true;
  };

  /**
   * Extract_times form a text. Produces UTC moments
   * @param str_of_times (datetimes as text separated by ",")
   * @return {*} a list of timezone aware moment objects
   */
  let extract_times_from_txt = function(str_of_times) {
      let model_regex = /(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ)/g;
      let all_dates = [...str_of_times.matchAll(model_regex)];
      let list_moments = [];
      all_dates.forEach(function(item, index, array) {
          let iso_ok = item[1].replace(/Z$/,'+00:00');
          list_moments.push(moment.utc(iso_ok));
      });
      if (list_moments.length === 0) {
          throw new NoTimeFoundException(
              "Text cannot be converted in Time element, please use the default Template");
      }
      return list_moments;
  };

  /**
   * Rounds a moment to the nearest hour
   * @param mmt (a moment object)
   * @returns {*}
   */
  let round_to_hour_mmt = function(mmt){
    let txt_mmt = mmt.format(TIMEFORMAT01);
    let ceil_m = moment.utc(txt_mmt);
    ceil_m = ceil_m.minute() || ceil_m.second() || ceil_m.millisecond() ? ceil_m.add(1,
                                                 'hour').startOf('hour') : ceil_m.startOf('hour');
    // let txt_ceil = ceil_m.format('YYYY-MM-DDTHH:mm:ssZ');
    let floor_m = moment.utc(txt_mmt).startOf('hour');
    // let floor_m = moment(txt_mmt).startOf('hour');
    let txt_floor = floor_m.format(TIMEFORMAT01);
    txt_mmt = mmt.format(TIMEFORMAT01);
    let rounded_m = mmt;

    let unix_m = mmt.unix();
    let unix_ceil_m = ceil_m.unix();
    let unix_floor_m = floor_m.unix();
    let diff_m_ceil = unix_ceil_m - unix_m;
    let diff_m_floor = unix_m - unix_floor_m;
    if (diff_m_ceil > diff_m_floor) {
        rounded_m = floor_m;
    } else {
        rounded_m = ceil_m;
    }
    // let rounded_txt = rounded_m.format('YYYY-MM-DDTHH:mm:ssZ');
    return rounded_m;
  };

    /**
     * A method specific to round values of release_times field.
     * Datetime values passed as a text will be analysed, converted to moment object and then reformatted
     * @param param_release_times a text containing datetime values separated by ","
     * @returns {[]} a list of text values representing datetimes
     */
  let round_release_times = function (param_release_times) {
      let list_moments = extract_times_from_txt(param_release_times);
      let rounded_first = round_to_hour_mmt(list_moments[0]);
      list_moments[0] = rounded_first;
      let txt_list_moments = [];
      let tmp_time_txt = "";
      let res_replace = "";
      list_moments.forEach(function(item, index, array) {
          tmp_time_txt = item.format(TIMEFORMAT02);
          res_replace = tmp_time_txt.replace(/UTC$/,'Z');
          txt_list_moments.push(res_replace);
      });
      return txt_list_moments;
  };

    /**
     * This method is used by jquery.validator
     * The method checks if the text present in release_times can be converted into a list of strings representing
     * datetimes.
     * The first element the resulting list is rounded and assigned to start_time.
     * All elements are checked to stay within a -4days, + 4days frame relative to current datetime
     * @param str_release_times
     * @param element
     * @param param
     * @returns {boolean}
     */
  let check_release_times = function(str_release_times, element, param){
      let new_vals = [];
      try {
          let list_moments = extract_times_from_txt(str_release_times);
          let rounded_first = round_to_hour_mmt(list_moments[0]);
          let tmp_time_txt = "";
          let res_replace = "";
          list_moments[0]=rounded_first;
          list_moments.forEach(function(item, index, array) {
              check_time_limit_value(item, past, future);
              tmp_time_txt = item.format(TIMEFORMAT02);
              res_replace = tmp_time_txt.replace(/UTC$/,'Z');
              new_vals.push(res_replace);
          });
      } catch (e) {
          if (e instanceof NoTimeFoundException) {
             releaseTimeErrorMsg = e.message;
             return false;
          }
          if (e instanceof OutOfTimeLimitException) {
              releaseTimeErrorMsg = e.message;
              return false;
          }
      }

      $('#'+element.id).val(new_vals.join(","));
      simulation_start_time.val(new_vals[0]);
      return true;
  };

    /**
     * This function is used by the submitHandler().
     * This function checks that there are the same number of elements (float numbers separated by ",")
     * in fields "lat" and "lon"
     * @returns {boolean}
     */
  let check_lat_lon = function() {
      let lats_list = extract_float_values(latitudes.val());
      let longs_list = extract_float_values(longitudes.val());
      return lats_list.length === longs_list.length;
  };

    /**
     * This function is used by the submitHandler().
     * This function checks that the number of coordinates (lat, long), is consistent with the type of geometry
     * (POINT, POLYLINE)
     * A POINT geometry only needs one set of coordinates (lat, long)
     * A POLYLINE geometry requires exactly two set of coordinates (lat, long), (lat, long) to determin a line
     * @returns {boolean}
     */
  let check_lat_lon_geom = function() {
      let lats_list = extract_float_values(latitudes.val());
      let longs_list = extract_float_values(longitudes.val());
      let loc_geometry = geometry.val();
      if (loc_geometry === POINT) {
          if (lats_list.length!==1 || longs_list.length!==1) {
             return false
          }
      } else {
          if (loc_geometry === POLYLINE) {
              if (lats_list.length!==2 || longs_list.length!==2) {
                 return false
              }
          }
      }
      return true
  };

    /**
     * This function is used by the submitHandler().
     * This functions performs different checks
     * It checks that the start_time and end_time are in an order consistant with the type of demand ( FORWARD or BACKWARD )
     * A FORWARD search has a start_time BEFORE the end_time
     * A BACKWARD search has an end_time BEFORE the start_time
     * @returns {boolean}
     */
  let check_release_times_coherence = function() {
      let list_release_times = "";
      let list_start_time = "";
      let list_end_time = "";

      list_release_times = extract_times_from_txt(release_times.val());
      list_start_time = extract_times_from_txt(simulation_start_time.val());
      list_end_time = extract_times_from_txt(simulation_end_time.val());

      let list_past = [];
      let list_future = [];

      if (simulation_type.val() === BACKWARD ) {
          list_past = list_end_time;
          list_future = list_start_time;
      } else {
          if (simulation_type.val() === FORWARD) {
              list_past = list_start_time;
              list_future = list_end_time;
          }
      }
      if (list_past.length>0 && list_future.length>0) {
          let lpast = list_past[0];
          let lfuture = list_future[0];
          if (lpast > lfuture) {
              throw new TimesDoNotMatchTypeException(
                  "Time fields values are not in right order for this type of simulation");
          }
          let llength = list_release_times.length;
          let an_element = null;
          for (let idx = 0; idx<llength; idx++) {
              an_element = list_release_times[idx];
              if (an_element < lpast || an_element > lfuture) {
                  throw new OutOfTimeLimitException("Release times out of [start_time, end_time] limits");
              }
          }
      }
      return true;
  };

    /**
     * This function is used jquery.validator
     * It checks that a text can be transformed into a datetime object and rounds the datetime object
     * The rounded datetime is formatted back as text with a "Z" ending for utc time.
     * Function returns true if no errors have been found
     * @param str_time_field ( a text value from start_time or end_time)
     * @param element (the DOM element)
     * @param param (a bogus parameter)
     * @returns {boolean}
     */
  let check_time_fields = function(str_time_field, element, param){
      // extract_times_from_txt returns an array of strings
      let time_vals = extract_times_from_txt(str_time_field);
      if (time_vals.length === 0) {
          return false;
      }
      let new_vals = round_to_hour_mmt(time_vals[0]);
      let tmp_time_txt = new_vals.format(TIMEFORMAT01);
      let rounded_txt = tmp_time_txt.replace(/\+00:00$/,'Z');
      $(element.id).val(rounded_txt);
      return true;
  };


  /**
   * This function checks if a timevalue stays within the global simulation window [-4days, +4days]
   * @param moment_value (a moment object)
   * @param ppast
   * @param pfuture
   * @returns {boolean}
   */
  let check_time_limit_value = function(moment_value, ppast, pfuture){
      if (moment_value < ppast || moment_value > pfuture ) {
         let tmp_time_txt = moment_value.format(TIMEFORMAT01);
         let z_tmp_time_txt = tmp_time_txt.replace(/\+\d\d:\d\d$/,'Z');
         let err_mesg = "Time : "+z_tmp_time_txt+", out of [-4days, +4days] limit";
         throw new OutOfTimeLimitException(err_mesg);
      }
      return true;
  };

    /**
     * This function is used jquery.validator
     * This function checks if a timevalue stays within the global simulation window [-4days, +4days]
     * @param str_time_field
     * @param element
     * @param param
     * @returns {boolean}
     */
  let check_time_limit = function(str_time_field, element, param){
      let time_vals = extract_times_from_txt(str_time_field);
      if (time_vals.length === 0) {
          return false;
      }

      try {
          time_vals.forEach(function(item, index, array) {
              check_time_limit_value(item, past, future)
          });
      } catch (e) {
          if (e instanceof OutOfTimeLimitException) {
              timeLimitErrorMsg=e.message;
              return false;
          }
      }
      return true;
  };

  $.validator.addMethod("check_coord_vals",    check_coord_vals,    "Bogus message");
  $.validator.addMethod("check_release_times", check_release_times, dynamicReleaseTimeErrorMsg);
  $.validator.addMethod("check_time_fields",   check_time_fields,   "Bogus message");
  $.validator.addMethod("check_time_limit",    check_time_limit,    dynamicTimeLimitErrorMsg);

  let validator = the_form.validate({
    rules : {
       lon:{
          required:true,
          "check_coord_vals":180.0
       },
       lat: {
          required: true,
          "check_coord_vals": 90.0
       },
       simulation_end_time:{
          required:true,
          "check_time_fields":true,
          "check_time_limit":true
       },
       simulation_start_time:{
          required:true,
          "check_time_fields":true,
          "check_time_limit":true
       },
       release_times:{
          required:true,
          "check_release_times":true,
       }
    }, submitHandler: function(form) {
          try {
              check_release_times_coherence();
          } catch (e) {
              // Name undefined, not one of my Exceptions
              if (typeof e.name === 'undefined') {
                  validator.showErrors({"release_times": "Strange error"});
                  return false;
              }
              // Check for any exception for which Name would be defined but which are not mine
              let excnames = ['OutOfTimeLimitException','TimesDoNotMatchTypeException','NoTimeFoundException'];
              if ($.inArray(e.name,excnames) < 0) {
                  validator.showErrors({"release_times": "Strange error : "+e.name});
                  return false;
              }
              // My exceptions for which the message is in the exception
              let twoexcnames = ['OutOfTimeLimitException','TimesDoNotMatchTypeException'];
              if ($.inArray(e.name,twoexcnames) > -1) {
                  validator.showErrors({"release_times": e.message});
                  return false;
              }
              // At this point, it must be a NoTimeFoundException
              // Here, I set the message
              validator.showErrors({"release_times": "No valid time found in some field ???"});
              return false;
          }
          if (!check_lat_lon()) {
              validator.showErrors({
              "lat": "Number of lats and longs are different."
              });
              return false;
          }

          if (!check_lat_lon_geom()) {
              let err_msg = "";
              if (geometry.val() === POINT ) {
                 err_msg = "Point => 2 coordinates lat,lon";
              } else {
                  if (geometry.val() === POLYLINE ) {
                     err_msg = "Polyline => 4 coordinates lat,lat , lon,lon";
                  }
              }
              validator.showErrors({
              "lat": err_msg
              });
              return false;
          }

          form.submit();
    }, messages: {
          lon:{
              required : "This field is required",
              "check_coord_vals" : "valid values in [-{0}, {0}]"
          },
          lat:{
              required : "This field is required",
              "check_coord_vals" : "valid values in [-{0}, {0}]"
          },
          simulation_end_time:{
              required:"This field is required",
              "check_time_fields":"Text cannot be converted in Time element, please use the default Template",
              "check_time_limit": "Maximum simulation window is [-4days, +4days]"
          },
          simulation_start_time:{
              required:"This field is required",
              "check_time_fields":"Text cannot be converted in Time element, please use the default Template",
              "check_time_limit": "Maximum simulation window is [-4days, +4days]"
          },
          release_times:{
              required:"This field is required",
          },
    }
  });

  let Oil_options = {
     "": "",
     "gasoline": "gasoline",
     "kerosene": "kerosene",
     "light crude oil": "light crude oil",
     "diesel oil": "diesel oil",
     "heavy crude oil": "heavy crude oil",
     "fuel oil no. 6": "fuel oil no. 6",
     "heavy fuel oil": "heavy fuel oil"
  };

  let Object_options = {
     "": "",
     "Person-in-water (PIW), unknown state (mean values)": "PIW-1",
     "PIW,vertical PFD type III conscious": "PIW-2",
     "PIW, sitting, PFD type I or II": "PIW-3",
     "PIW, survival suit (face up)": "PIW-4",
     "PIW, scuba suit (face up)": "PIW-5",
     "PIW, deceased (face down)": "PIW-6",
     "Life-raft, no ballast (NB) system, general (mean values)": "LIFE-RAFT-NB-1",
     "Life-raft, no ballast system, no canopy, no drogue": "LIFE-RAFT-NB-2",
     "Life-raft, no ballast system, no canopy, with drogue": "LIFE-RAFT-NB-3",
     "Life-raft, no ballast system, with canopy, no drogue": "LIFE-RAFT-NB-4",
     "Life-raft, no ballast system, with canopy, with drogue": "LIFE-RAFT-NB-5",
     "Life-raft, shallow ballast (SB) system AND canopy, general (mean values)": "LIFE-RAFT-SB-6",
     "Life-raft, shallow ballast system, canopy, no drogue": "LIFE-RAFT-SB-7",
     "Life-raft, shallow ballast system AND canopy, with drogue": "LIFE-RAFT-SB-8",
     "Life-raft, shallow ballast system AND canopy, capsized": "LIFE-RAFT-SB-9",
     "Life Raft - Shallow ballast, canopy, Navy Sub Escape (SEIE) 1-man raft, NO drogue": "LIFE-RAFT-SB-10",
     "Life Raft - Shallow ballast, canopy, Navy Sub Escape (SEIE) 1-man raft, with drogue": "LIFE-RAFT-SB-11",
     "Life raft, deep ballast (DB) system, general, unknown capacity and loading (mean values)": "LIFE-RAFT-DB-10",
     "4-14 person capacity, deep ballast system, canopy (average)": "LIFE-RAFT-DB-11",
     "4-14 person capacity, deep ballast system, no drogue": "LIFE-RAFT-DB-12",
     "4-14 person capacity, deep ballast system, canopy, no drogue, light loading": "LIFE-RAFT-DB-13",
     "4-14 person capacity, deep ballast system, no drogue, heavy loading": "LIFE-RAFT-DB-14",
     "4-14 person capacity, deep ballast system, canopy, with drogue (average)": "LIFE-RAFT-DB-15",
     "4-14 person capacity, deep ballast system, canopy, with drogue, light loading": "LIFE-RAFT-DB-16",
     "4-14 person capacity, deep ballast system, canopy, with drogue, heavy loading": "LIFE-RAFT-DB-17",
     "15-50 person capacity, deep ballast system, canopy, general (mean values)": "LIFE-RAFT-DB-18",
     "15-50 person capacity, deep ballast system, canopy, no drogue, light loading": "LIFE-RAFT-DB-19",
     "15-50 person capacity, deep ballast system, canopy, with drogue, heavy loading": "LIFE-RAFT-DB-20",
     "Deep ballast system, general (mean values), capsized": "LIFE-RAFT-DB-21",
     "Deep ballast system, general (mean values), swamped": "LIFE-RAFT-DB-22",
     "Survival Craft - USCG Sea Rescue Kit - 3 ballasted life rafts and 300 meter of line": "USCG-RESCUE",
     "Survival Craft - SOLAS Hard Shell Life Capsule, 22 man": "LIFE-CAPSULE",
     "Life-raft, 4-6 person capacity, no ballast, with canopy, no drogue": "AVIATION-1",
     "Evacuation slide with life-raft, 46 person capacity": "AVIATION-2",
     "Survival Craft - Ovatek Hard Shell Life Raft, 4 and 7-man, lightly loaded, no drogue (average)": "OVATEK-CRAFT-1",
     "Survival Craft - Ovatek Hard Shell Life Raft, 4 man, lightly loaded, no drogue": "OVATEK-CRAFT-2",
     "Survival Craft - Ovatek Hard Shell Life Raft, 7 man, lightly loaded, no drogue": "OVATEK-CRAFT-3",
     "Survival Craft - Ovatek Hard Shell Life Raft, 4 and 7-man, fully loaded, drogued (average)": "OVATEK-CRAFT-4",
     "Survival Craft - Ovatek Hard Shell Life Raft, 4 man, fully loaded, drogued": "OVATEK-CRAFT-5",
     "Survival Craft - Ovatek Hard Shell Life Raft, 7 man, fully loaded, drogued": "OVATEK-CRAFT-6",
     "Kayak with person on aft deck": "PERSON-POWERED-VESSEL-1",
     "Surf board with person": "PERSON-POWERED-VESSEL-2",
     "Windsurfer with mast and sail in water": "PERSON-POWERED-VESSEL-3",
     "Outrigger canoe (*9)": "PERSON-POWERED-VESSEL-4",
     "Skiff, modified-v, cathedral-hull, runabout outboard powerboat": "SKIFF-1",
     "Skiff, V-hull": "SKIFF-2",
     "Skiff, swamped and capsized": "SKIFF-3",
     "Skiff, v-hull bow to stern (aluminium, Norway)": "SKIFF-4",
     "19 foot (5.8 m) fibreglass skiff (*9)": "SKIFF-6",
     "Rigid-hulled inflatable boat": "SKIFF-7",
     "Sport boat, no canvas (*1), modified V-hull": "SPORT-BOAT",
     "Sport fisher, center console (*2), open cockpit": "SPORT-FISHER",
     "Standup Paddle": "BEACHCRAFT-1",
     "Personal Water Craft (jetski) (*9)": "BEACHCRAFT-2",
     "Fishing vessel, general (mean values)": "FISHING-VESSEL-1",
     "Fishing vessel, Hawaiian Sampan (*3)": "FISHING-VESSEL-2",
     "Fishing vessel, Japanese side-stern trawler": "FISHING-VESSEL-3",
     "Fishing vessel, Japanese Longliner (*3)": "FISHING-VESSEL-4",
     "Fishing vessel, Korean fishing vessel (*4)": "FISHING-VESSEL-5",
     "Fishing vessel, Gill-netter with rear reel (*3)": "FISHING-VESSEL-6",
     "Poti Marara": "FISHING-VESSEL-7",
     "fishing skiff with sail": "FISHING-VESSEL-8",
     "Fishing vessel debris": "FV-DEBRIS",
     "Large vessel (250 m) in loaded condition. (*8)": "LARGE-VESSEL-1",
     "Large vessel (250 m) in ballast condition. (*8)": "LARGE-VESSEL-2",
     "50 degree listing ro-ro ship": "LARGE-VESSEL-3",
     "Coastal freighter. (*5)": "COASTAL-FREIGHTER",
     "Sailboat Mono-hull (Average)": "SAILBOAT-1",
     "Sailboat Mono-hull (Dismasted, Average)": "SAILBOAT-2",
     "Sailboat Mono-hull (Dismasted - rudder amidships)": "SAILBOAT-3",
     "Sailboat Mono-hull (Dismasted - rudder missing)": "SAILBOAT-4",
     "Sailboat Mono-hull (Bare-masted,  Average)": "SAILBOAT-5",
     "Sailboat Mono-hull (Bare-masted, rudder amidships)": "SAILBOAT-6",
     "Sailboat Mono-hull (Bare-masted, rudder hove-to)": "SAILBOAT-6b",
     "Sailboat Mono-hull, fin keel, shallow draft (was SAILBOAT-2)": "SAILBOAT-7",
     "Sunfish sailing dingy  -  Bare-masted, rudder missing": "SAILBOAT-8",
     "Sunfish sailboat no sail (*10)": "SAILBOAT-9",
     "cruising catamaran no sail": "SAILBOAT-10",
     "10 m sloop with lowered sails": "SAILBOAT-11",
     "80 foot trimaran upside down without rigging nor sail in water": "SAILBOAT-12",
     "Self-locating datum marker buoy - no windage": "SLDMB",
     "Navy Submarine EPIRB (SEPIRB)": "SEPIRB",
     "Bait/wharf box, holds a cubic metre of ice, mean values (*6)": "BAIT-BOX-1",
     "Bait/wharf box, holds a cubic metre of ice, lightly loaded": "BAIT-BOX-2",
     "Bait/wharf box, holds a cubic metre of ice, full loaded": "BAIT-BOX-3",
     "Immigration vessel, Cuban refugee-raft, no sail (*7)": "REFUGEE-RAFT-1",
     "Immigration vessel, Cuban refugee-raft, with sail (*7)": "REFUGEE-RAFT-2",
     "Sewage floatables, tampon applicator": "SEWAGE",
     "Medical waste (mean values)": "MED-WASTE-1",
     "Medical waste, vials": "MED-WASTE-2",
     "Medical waste, vials, large": "MED-WASTE-3",
     "Medical waste, vials, small": "MED-WASTE-4",
     "Medical waste, syringes": "MED-WASTE-5",
     "Medical waste, syringes, large": "MED-WASTE-6",
     "Medical waste, syringes, small": "MED-WASTE-7",
     "220 l (55-gallon) oil drum (*10)": "OIL-DRUM",
     "WWII L-MK2 mine (*10)": "MINE",
     "Dolphin carcass (*11)": "MARINE-MAMMALS-1",
     "Scaled down (1:3) 40-ft Container (70% submerged)": "CONTAINER-1",
     "20-ft Container (80% submerged)": "CONTAINER-2",
     "Container immersed at 10%": "CONTAINER-IMMERSED-10pc",
     "Container immersed at 20%": "CONTAINER-IMMERSED-20pc",
     "Container immersed at 30%": "CONTAINER-IMMERSED-30pc",
     "Container immersed at 40%": "CONTAINER-IMMERSED-40pc",
     "Container immersed at 50%": "CONTAINER-IMMERSED-50pc",
     "Container immersed at 60%": "CONTAINER-IMMERSED-60pc",
     "Container immersed at 70%": "CONTAINER-IMMERSED-70pc",
     "Container immersed at 80%": "CONTAINER-IMMERSED-80pc",
     "Container immersed at 90%": "CONTAINER-IMMERSED-90pc",
     "Container immersed at 100%": "CONTAINER-IMMERSED-100pc"
   };
  let Object_options_short = {
     "Person-in-water (PIW), unknown state (mean values)": "PIW-1",
     "PIW,vertical PFD type III conscious": "PIW-2",
     "PIW, sitting, PFD type I or II": "PIW-3",
     "PIW, survival suit (face up)": "PIW-4",
     "PIW, scuba suit (face up)": "PIW-5",
     "PIW, deceased (face down)": "PIW-6",
     "Life-raft, no ballast (NB) system, general (mean values)": "LIFE-RAFT-NB-1",
     "Life-raft, no ballast system, no canopy, no drogue": "LIFE-RAFT-NB-2",
     "Life-raft, no ballast system, no canopy, with drogue": "LIFE-RAFT-NB-3",
     "Life-raft, no ballast system, with canopy, no drogue": "LIFE-RAFT-NB-4",
     "Life-raft, no ballast system, with canopy, with drogue": "LIFE-RAFT-NB-5",
     "Life-raft, shallow ballast (SB) system AND canopy, general (mean values)": "LIFE-RAFT-SB-6",
     "Life-raft, shallow ballast system, canopy, no drogue": "LIFE-RAFT-SB-7",
     "Life-raft, shallow ballast system AND canopy, with drogue": "LIFE-RAFT-SB-8",
     "Life-raft, shallow ballast system AND canopy, capsized": "LIFE-RAFT-SB-9",
     "Life Raft - Shallow ballast, canopy, Navy Sub Escape (SEIE) 1-man raft, NO drogue": "LIFE-RAFT-SB-10",
     "Life Raft - Shallow ballast, canopy, Navy Sub Escape (SEIE) 1-man raft, with drogue": "LIFE-RAFT-SB-11",
     "Life raft, deep ballast (DB) system, general, unknown capacity and loading (mean values)": "LIFE-RAFT-DB-10",
     "4-14 person capacity, deep ballast system, canopy (average)": "LIFE-RAFT-DB-11",
     "4-14 person capacity, deep ballast system, no drogue": "LIFE-RAFT-DB-12",
     "4-14 person capacity, deep ballast system, canopy, no drogue, light loading": "LIFE-RAFT-DB-13",
     "4-14 person capacity, deep ballast system, no drogue, heavy loading": "LIFE-RAFT-DB-14",
     "4-14 person capacity, deep ballast system, canopy, with drogue (average)": "LIFE-RAFT-DB-15",
     "4-14 person capacity, deep ballast system, canopy, with drogue, light loading": "LIFE-RAFT-DB-16",
     "4-14 person capacity, deep ballast system, canopy, with drogue, heavy loading": "LIFE-RAFT-DB-17",
     "15-50 person capacity, deep ballast system, canopy, general (mean values)": "LIFE-RAFT-DB-18",
     "15-50 person capacity, deep ballast system, canopy, no drogue, light loading": "LIFE-RAFT-DB-19",
     "15-50 person capacity, deep ballast system, canopy, with drogue, heavy loading": "LIFE-RAFT-DB-20",
     "Deep ballast system, general (mean values), capsized": "LIFE-RAFT-DB-21",
     "Deep ballast system, general (mean values), swamped": "LIFE-RAFT-DB-22",
     "Survival Craft - USCG Sea Rescue Kit - 3 ballasted life rafts and 300 meter of line": "USCG-RESCUE",
     "Survival Craft - SOLAS Hard Shell Life Capsule, 22 man": "LIFE-CAPSULE",
     "Life-raft, 4-6 person capacity, no ballast, with canopy, no drogue": "AVIATION-1",
     "Evacuation slide with life-raft, 46 person capacity": "AVIATION-2",
     "Survival Craft - Ovatek Hard Shell Life Raft, 4 and 7-man, lightly loaded, no drogue (average)": "OVATEK-CRAFT-1",
     "Survival Craft - Ovatek Hard Shell Life Raft, 4 man, lightly loaded, no drogue": "OVATEK-CRAFT-2",
     "Survival Craft - Ovatek Hard Shell Life Raft, 7 man, lightly loaded, no drogue": "OVATEK-CRAFT-3",
     "Survival Craft - Ovatek Hard Shell Life Raft, 4 and 7-man, fully loaded, drogued (average)": "OVATEK-CRAFT-4",
     "Survival Craft - Ovatek Hard Shell Life Raft, 4 man, fully loaded, drogued": "OVATEK-CRAFT-5",
     "Survival Craft - Ovatek Hard Shell Life Raft, 7 man, fully loaded, drogued": "OVATEK-CRAFT-6",
     "Kayak with person on aft deck": "PERSON-POWERED-VESSEL-1",
     "Surf board with person": "PERSON-POWERED-VESSEL-2",
     "Windsurfer with mast and sail in water": "PERSON-POWERED-VESSEL-3",
     "Outrigger canoe (*9)": "PERSON-POWERED-VESSEL-4",
     "Skiff, modified-v, cathedral-hull, runabout outboard powerboat": "SKIFF-1",
     "Skiff, V-hull": "SKIFF-2",
     "Skiff, swamped and capsized": "SKIFF-3",
     "Skiff, v-hull bow to stern (aluminium, Norway)": "SKIFF-4",
     "19 foot (5.8 m) fibreglass skiff (*9)": "SKIFF-6",
     "Rigid-hulled inflatable boat": "SKIFF-7",
     "Sport boat, no canvas (*1), modified V-hull": "SPORT-BOAT",
     "Sport fisher, center console (*2), open cockpit": "SPORT-FISHER",
     "Standup Paddle": "BEACHCRAFT-1",
     "Personal Water Craft (jetski) (*9)": "BEACHCRAFT-2",
     "Fishing vessel, general (mean values)": "FISHING-VESSEL-1",
     "Fishing vessel, Hawaiian Sampan (*3)": "FISHING-VESSEL-2",
     "Fishing vessel, Japanese side-stern trawler": "FISHING-VESSEL-3",
     "Fishing vessel, Japanese Longliner (*3)": "FISHING-VESSEL-4",
     "Fishing vessel, Korean fishing vessel (*4)": "FISHING-VESSEL-5",
     "Fishing vessel, Gill-netter with rear reel (*3)": "FISHING-VESSEL-6",
     "Poti Marara": "FISHING-VESSEL-7",
     "fishing skiff with sail": "FISHING-VESSEL-8",
     "Fishing vessel debris": "FV-DEBRIS",
     "Large vessel (250 m) in loaded condition. (*8)": "LARGE-VESSEL-1",
     "Large vessel (250 m) in ballast condition. (*8)": "LARGE-VESSEL-2",
     "50 degree listing ro-ro ship": "LARGE-VESSEL-3",
     "Coastal freighter. (*5)": "COASTAL-FREIGHTER",
     "Sailboat Mono-hull (Average)": "SAILBOAT-1",
     "Sailboat Mono-hull (Dismasted, Average)": "SAILBOAT-2",
     "Sailboat Mono-hull (Dismasted - rudder amidships)": "SAILBOAT-3",
     "Sailboat Mono-hull (Dismasted - rudder missing)": "SAILBOAT-4",
     "Sailboat Mono-hull (Bare-masted,  Average)": "SAILBOAT-5",
     "Sailboat Mono-hull (Bare-masted, rudder amidships)": "SAILBOAT-6",
     "Sailboat Mono-hull (Bare-masted, rudder hove-to)": "SAILBOAT-6b",
     "Sailboat Mono-hull, fin keel, shallow draft (was SAILBOAT-2)": "SAILBOAT-7",
     "Sunfish sailing dingy  -  Bare-masted, rudder missing": "SAILBOAT-8",
     "Sunfish sailboat no sail (*10)": "SAILBOAT-9",
     "cruising catamaran no sail": "SAILBOAT-10",
     "10 m sloop with lowered sails": "SAILBOAT-11",
     "80 foot trimaran upside down without rigging nor sail in water": "SAILBOAT-12",
     "Self-locating datum marker buoy - no windage": "SLDMB",
     "Navy Submarine EPIRB (SEPIRB)": "SEPIRB",
     "Bait/wharf box, holds a cubic metre of ice, mean values (*6)": "BAIT-BOX-1",
     "Bait/wharf box, holds a cubic metre of ice, lightly loaded": "BAIT-BOX-2",
     "Bait/wharf box, holds a cubic metre of ice, full loaded": "BAIT-BOX-3",
     "Immigration vessel, Cuban refugee-raft, no sail (*7)": "REFUGEE-RAFT-1",
     "Immigration vessel, Cuban refugee-raft, with sail (*7)": "REFUGEE-RAFT-2",
     "Sewage floatables, tampon applicator": "SEWAGE",
     "Medical waste (mean values)": "MED-WASTE-1",
     "Medical waste, vials": "MED-WASTE-2",
     "Medical waste, vials, large": "MED-WASTE-3",
     "Medical waste, vials, small": "MED-WASTE-4",
     "Medical waste, syringes": "MED-WASTE-5",
     "Medical waste, syringes, large": "MED-WASTE-6",
     "Medical waste, syringes, small": "MED-WASTE-7",
     "220 l (55-gallon) oil drum (*10)": "OIL-DRUM",
     "WWII L-MK2 mine (*10)": "MINE",
     "Dolphin carcass (*11)": "MARINE-MAMMALS-1",
     "Scaled down (1:3) 40-ft Container (70% submerged)": "CONTAINER-1",
     "20-ft Container (80% submerged)": "CONTAINER-2",
     "Container immersed at 10%": "CONTAINER-IMMERSED-10pc",
     "Container immersed at 20%": "CONTAINER-IMMERSED-20pc",
     "Container immersed at 30%": "CONTAINER-IMMERSED-30pc",
     "Container immersed at 40%": "CONTAINER-IMMERSED-40pc",
     "Container immersed at 50%": "CONTAINER-IMMERSED-50pc",
     "Container immersed at 60%": "CONTAINER-IMMERSED-60pc",
     "Container immersed at 70%": "CONTAINER-IMMERSED-70pc",
     "Container immersed at 80%": "CONTAINER-IMMERSED-80pc",
     "Container immersed at 90%": "CONTAINER-IMMERSED-90pc",
     "Container immersed at 100%": "CONTAINER-IMMERSED-100pc"
   };

  let str = window.location.href;
  let n = str.search("simulationdemand/edit/");

  if (n === -1) {
     if (twoDthreeD.val() === THREED) {
        buoyancy.removeAttr("disabled");
        natural_vertical_dispersion.removeAttr("disabled");
     }

     if (twoDthreeD.val() === TWOD) {
        buoyancy.prop("checked", false);
        buoyancy.prop("disabled", "true");
        natural_vertical_dispersion.prop("checked", false);
        natural_vertical_dispersion.prop("disabled", "true");
     }

     if (drifter_type.val() === OIL) {
        dissolution.removeAttr("disabled");
        evaporation.removeAttr("disabled");
        horizontal_spreading.removeAttr("disabled");
        sedimentation.removeAttr("disabled");

        drifter_name.empty();
        $.each(Oil_options, function (key, value) {
            drifter_name.append($("<option></option>")
            .attr("value", value).text(key));
        });
     } else if (drifter_type.val() === OBJECT) {
        dissolution.prop("checked", false);
        dissolution.prop("disabled", "true");
        evaporation.prop("checked", false);
        evaporation.prop("disabled", "true");
        horizontal_spreading.prop("checked", false);
        horizontal_spreading.prop("disabled", "true");
        sedimentation.prop("checked", false);
        sedimentation.prop("disabled", "true");

        drifter_name.empty();
        $.each(Object_options, function (key, value) {
            drifter_name.append($("<option></option>")
            .attr("value", value).text(key));
        });
     } else {
        dissolution.removeAttr("disabled");
        evaporation.removeAttr("disabled");
        horizontal_spreading.removeAttr("disabled");
        sedimentation.removeAttr("disabled");

        drifter_name.empty();
        $.each(Oil_options, function (key, value) {
            drifter_name.append($("<option></option>")
            .attr("value", value).text(key));
        });
        $.each(Object_options_short, function (key, value) {
            drifter_name.append($("<option></option>")
            .attr("value", value).text(key));
        });
     }
  }

  twoDthreeD.on('change', function () {
      if ($(this).val() === THREED) {
         buoyancy.removeAttr("disabled");
         natural_vertical_dispersion.removeAttr("disabled");
      }
      if ($(this).val() === TWOD) {
         buoyancy.prop("checked", false);
         buoyancy.prop("disabled", "true");
         natural_vertical_dispersion.prop("checked", false);
         natural_vertical_dispersion.prop("disabled", "true");
      }
  });

    /**
     * Enable properties linked to OIL drifter
     * @param an_oil_property
     * @param poperty_value
     */
  let enable_oil_property = function(an_oil_property, poperty_value) {
      an_oil_property.removeAttr("readonly");
      an_oil_property.val(poperty_value);
  };

    /**
     * Disable properties linked to OIL drifter
     * @param an_oil_property
     * @param poperty_value
     */
  let disable_oil_property = function(an_oil_property, poperty_value) {
      an_oil_property.val(poperty_value);
      an_oil_property.prop("readonly","readonly");
  };

  drifter_type.on('change', function () {
      if ($(this).val() === OIL) {
         dissolution.removeAttr("disabled");
         evaporation.removeAttr("disabled");
         horizontal_spreading.removeAttr("disabled");
         sedimentation.removeAttr("disabled");

         drifter_name.empty();
         $.each(Oil_options, function (key, value) {
              drifter_name.append($("<option></option>")
              .attr("value", value).text(key));
         });

         enable_oil_property(total_mass, 5000);
         enable_oil_property(twoDthreeD, THREED);

      } else {
         dissolution.prop("checked", false);
         dissolution.prop("disabled", "true");
         evaporation.prop("checked", false);
         evaporation.prop("disabled", "true");
         horizontal_spreading.prop("checked", false);
         horizontal_spreading.prop("disabled", "true");
         sedimentation.prop("checked", false);
         sedimentation.prop("disabled", "true");

         drifter_name.empty();
         $.each(Object_options, function (key, value) {
             drifter_name.append($("<option></option>")
             .attr("value", value).text(key));
         });

         disable_oil_property(total_mass, 5000);
         disable_oil_property(twoDthreeD,TWOD);
      }
  });

  let the_button = $('#error_button');
  if ( typeof the_button !== "undefined" && the_button !== null  ) {
      the_button.click();
  }

  //Default, set all of these to checked
  beaching.prop("checked", true);
  buoyancy.prop("checked", true);
  dissolution.prop("checked", true);
  evaporation.prop("checked", true);
  horizontal_spreading.prop("checked", true);
  natural_vertical_dispersion.prop("checked", true);
  sedimentation.prop("checked", true);
  total_mass.val(5000);
  radius.val(1000);

}(window.jQuery, window.L, window, document));
