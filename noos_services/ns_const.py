class MemorySimulationDemand:
    JSON_TXT = 'json_txt'
    SIMULATION_DESCRIPTION = 'simulation_description'
    DRIFTER = 'drifter'
    INITIAL_CONDITION = 'initial_condition'
    MODEL_SETUP = 'model_set_up'

    CREATED_TIME = "created_time"
    ID = "id"
    PROTECTED = "protected"
    REQUEST_ID = "request_id"
    STATUS = "status"

    SIMULATION_TYPE = "simulation_type"
    SIMULATION_END_TIME = "simulation_end_time"
    SIMULATION_START_TIME = "simulation_start_time"
    SUMMARY = "summary"
    TAGS = "tags"
    TITLE = "title"

    DRIFTER_NAME = "drifter_name"
    DRIFTER_TYPE = "drifter_type"
    TOTAL_MASS = "total_mass"

    CONE = "cone"
    GEOMETRY = "geometry"
    LAT = "lat"
    LON = "lon"
    NUMBER = "number"
    RADIUS = "radius"
    TIME = "time"
    RELEASE_TIMES = "release_times"

    MODEL = "model"
    TWODTHREED = "2D/3D"
    FORM_TWODTHREED = "twoDthreeD"
    BEACHING = "beaching"
    BUOYANCY = "buoyancy"
    CURRENT = "current"
    DISSOLUTION = "dissolution"
    EVAPORATION = "evaporation"
    HORIZONTAL_SPREADING = "horizontal_spreading"
    NATURAL_VERTICAL_DISPERTION = "natural_vertical_dispersion"
    SEDIMENTATION = "sedimentation"
    WAVES = "waves"
    WIND = "wind"
    OCEAN_FORCING = "ocean_forcing"
    WIND_FORCING = "wind_forcing"

    TIMESTAMPFORMAT = "%Y-%m-%dT%H:%M:%SZ"

    USERNAME = "username"

    ERROR_MESSAGES = "counterrormessages"
    UPLOAD_MESSAGES = "countuploadmessages"
    END_PROCESS = "countendprocessmessages"

    CBVALS = [BEACHING, BUOYANCY, DISSOLUTION, EVAPORATION, HORIZONTAL_SPREADING, NATURAL_VERTICAL_DISPERTION,
              SEDIMENTATION]

    ZIP_URL = "zipurl"


class SignalsConst:
    CENTRAL_MESSAGE = "central_message"
    COUPLE_CODE = "couple_code"
    FILENAME = "filename"
    FORCING_COUPLE = "forcing_couple"
    FORCING_COUPLE_ID = "forcing_couple_id"
    IMMUTABLE = "immutable"
    JSON_FILE = "json_file"
    JSON_TXT = "json_txt"
    LAST_COUPLE = "last_couple"
    LOG_MESSAGE = "log_message"
    LOG_STATUS = "log_status"
    MESSAGE = "message"
    NODE = "node"
    NODE_ID = "node_id"
    NOOS_MODEL = "noos_model"
    NOOS_MODEL_CODE = "noos_model_code"
    NOOS_MODEL_ID = "noos_model_id"
    SIMULATION = "simulation"
    SIMULATION_DEMAND = "simulation_demand"
    SIMULATION_DEMAND_ID = "simulation_demand_id"
    STATUS = "status"
    THEJSONTXT = "thejsontxt"


class StatusConst:
    ANALYSIS_ERROR = "ANALYSIS_ERROR"
    ANALYSIS_OK = "ANALYSIS_OK"
    FORCING_ERROR = "FORCING-ERROR"
    FORCING_FILE_UPLOADED = "FORCING-FILE-UPLOADED"
    FORCING_PROCESSING = "FORCING-PROCESSING"
    INIT_SIMULATION = "INIT-SIMULATION"
    MODEL_FAILED = "MODEL-FAILED"
    MODEL_REVOKED = "MODEL-REVOKED"
    NETCDF_PROCESSING = "NETCDF-PROCESSING"
    NODE_ERROR = "NODE-ERROR"
    NODE_END_PROCESSING = "NODE-END-PROCESSING"
    OK = "OK"
    POSTPROCESSING_FAILED = "POSTPROCESSING-FAILED"
    PREPROCESSING_FAILED = "PREPROCESSING-FAILED"
    RESULT_FILE_ERROR = "RESULT-FILE-ERROR"
    SEND_FAILED = "SEND-FAILED"
    START_ANALYSIS = "START-ANALYSIS"
    SUBMITTED = "SUBMITTED"
    UPLOAD_FAILED = "UPLOAD-FAILED"
    UNKNOWN_FAILED = "UNKNOWN-FAILED"


class JsonMmeElementsConst:
    ANGLE = "ellipsis_major_axis_azimuth_angle"
    AZIMUTH_DIRECTION_FROM_START = "azimuth_direction_of_center_from_start"
    COVERAGE = "coverage"
    DISTANCE_FROM_CLUSTER_CENTRE = "distance_from_cluster_centre"
    DISTANCE_FROM_START = "distance_of_center_from_start"
    DISTANCE_STD = "distance_std"
    ELLIPSES = "ellipses"
    CLUSTERS = "clusters"
    CENTERLON = "centerlon"
    CENTERLAT = "centerlat"
    FEATURES = "features"
    LAT = "latitude_of_center"
    LATMAX = "latmax"
    LATMIN = "latmin"
    LNG = "longitude_of_center"
    LONGEST_ELLIPSIS_AXIS = "longest_ellipsis_axis"
    LONMAX = "lonmax"
    LONMIN = "lonmin"
    MEMBERS = "members"
    MODEL = "model"
    MODELNAME = "model_name"
    OCEAN_FORCING = "ocean_forcing"
    ORIGINAL_DEMAND = "original_demand"
    PROPERTIES = "properties"
    SEMMAJAXIS = "ellipsis_major_axis"
    SEMMINAXIS = "ellipsis_minor_axis"
    SIMULATIONS = "simulations"
    SUPER_ELLIPSE = "super-ellipse"
    TIME = "time"
    WIND_FORCING = "wind_forcing"


class JsonSimulationElementsConst:
    ANGLE = "angle"
    AZIMUTH_DIRECTION_FROM_START = "azimuth_direction_of_center_from_start"
    CLUSTERS = "clusters"
    COORDINATES = "coordinates"
    COUPLE_CODE = "couple_code"
    DISTANCE_STD = "distance_std"
    DISTANCE_FROM_CLUSTER_CENTER = "distance_from_cluster_centre"
    DISTANCE_FROM_START = "distance_of_center_from_start"
    ELLIPSES = "ellipses"
    GEOMETRY = "geometry"
    MEMBER_ELLIPSES = "member_ellipses"
    LAT = "lat"
    LNG = "lng"
    RADIUS = "radius"
    SEMMAJAXIS = "radiiSemiMajorAxis"
    SEMMINAXIS = "radiiSemiMinorAxis"
    SIMULATION_NAME = "simulation_name"
    STEP = "step"
    SUPER_ELLIPSE = "super-ellipse"
    TIMESTAMP = "timestamp"


class OtherConst:
    BACKWARD = "backward"
    BBOX_COORDS = "bbox_coords"
    BBOX_CENTER = "bbox_center"
    CENTRAL_NODE_ID = 1
    CLOUD = "CLOUD"
    CLOUD_AND_ELLIPSES = "C"
    CLUSTERS = "CLUSTERS"
    COORDINATES = "coordinates"
    DOCUMENT = "DOCUMENT"
    ELLIPSE = "ELLIPSE"
    END_TIME = "end_time"
    FORWARD = "forward"
    INIT_PARAMETERS = "init_parameters"
    METADATA = "METADATA"
    MME_CODE = "mme"
    MME_FORCING_COUPLE_ID = 10
    MME_MODEL_ID = 4
    MME_OUTPUT = "mme_output"
    OBJECT = "object"
    OIL = "oil"
    PARAMETERS_DIR_NAME = "parameters"
    POINT = "point"
    POLYLINE = "polyline"
    START_TIME = "start_time"
    STEP = "step"
    TOT_STEPS = "tot_steps"
    THREED = "3D"
    TRAJECTORIES = "trajectories"
    TRAJECTORY = "trajectory"
    TWOD = "2D"
    SIMULATION_ID = "simulation_id"
    SIMULATION_NAME = "simulation_name"
    SIMULATION_NAMES = "simulation_names"


DRIFTER_NAME_OIL_CHOICES = (('', ''),
                            ('gasoline', 'gasoline'),
                            ('kerosene', 'kerosene'),
                            ('light crude oil', 'light crude oil'),
                            ('diesel oil', 'diesel oil'),
                            ('heavy crude oil', 'heavy crude oil'),
                            ('fuel oil no. 6', 'fuel oil no. 6'),
                            ('heavy fuel oil', 'heavy fuel oil'),)


DRIFTER_NAME_OBJECT_CHOICES = (("", ""),
                               ("PIW-1", "Person-in-water (PIW), unknown state (mean values)"),
                               ("PIW-2", "PIW,vertical PFD type III conscious"),
                               ("PIW-3", "PIW, sitting, PFD type I or II"),
                               ("PIW-4", "PIW, survival suit (face up)"),
                               ("PIW-5", "PIW, scuba suit (face up)"),
                               ("PIW-6", "PIW, deceased (face down)"),
                               ("LIFE-RAFT-NB-1", "Life-raft, no ballast (NB) system, general (mean values)"),
                               ("LIFE-RAFT-NB-2", "Life-raft, no ballast system, no canopy, no drogue"),
                               ("LIFE-RAFT-NB-3", "Life-raft, no ballast system, no canopy, with drogue"),
                               ("LIFE-RAFT-NB-4", "Life-raft, no ballast system, with canopy, no drogue"),
                               ("LIFE-RAFT-NB-5", "Life-raft, no ballast system, with canopy, with drogue"),
                               ("LIFE-RAFT-SB-6",
                                "Life-raft, shallow ballast (SB) system AND canopy, general (mean values)"),
                               ("LIFE-RAFT-SB-7", "Life-raft, shallow ballast system, canopy, no drogue"),
                               ("LIFE-RAFT-SB-8", "Life-raft, shallow ballast system AND canopy, with drogue"),
                               ("LIFE-RAFT-SB-9", "Life-raft, shallow ballast system AND canopy, capsized"),
                               ("LIFE-RAFT-SB-10",
                                "Life Raft - Shallow ballast, canopy, Navy Sub Escape (SEIE) 1-man raft, NO drogue"),
                               ("LIFE-RAFT-SB-11",
                                "Life Raft - Shallow ballast, canopy, Navy Sub Escape (SEIE) 1-man raft, with drogue"),
                               ("LIFE-RAFT-DB-10",
                                "Life raft, deep ballast (DB) system, general, unknown capacity and loading (mean values)"),
                               ("LIFE-RAFT-DB-11", "4-14 person capacity, deep ballast system, canopy (average)"),
                               ("LIFE-RAFT-DB-12", "4-14 person capacity, deep ballast system, no drogue"),
                               ("LIFE-RAFT-DB-13",
                                "4-14 person capacity, deep ballast system, canopy, no drogue, light loading"),
                               ("LIFE-RAFT-DB-14",
                                "4-14 person capacity, deep ballast system, no drogue, heavy loading"),
                               ("LIFE-RAFT-DB-15",
                                "4-14 person capacity, deep ballast system, canopy, with drogue (average)"),
                               ("LIFE-RAFT-DB-16",
                                "4-14 person capacity, deep ballast system, canopy, with drogue, light loading"),
                               ("LIFE-RAFT-DB-17",
                                "4-14 person capacity, deep ballast system, canopy, with drogue, heavy loading"),
                               ("LIFE-RAFT-DB-18",
                                "15-50 person capacity, deep ballast system, canopy, general (mean values)"),
                               ("LIFE-RAFT-DB-19",
                                "15-50 person capacity, deep ballast system, canopy, no drogue, light loading"),
                               ("LIFE-RAFT-DB-20",
                                "15-50 person capacity, deep ballast system, canopy, with drogue, heavy loading"),
                               ("LIFE-RAFT-DB-21", "Deep ballast system, general (mean values), capsized"),
                               ("LIFE-RAFT-DB-22", "Deep ballast system, general (mean values), swamped"),
                               ("USCG-RESCUE", "Survival Craft - USCG Sea Rescue Kit - 3 ballasted life rafts and 300 meter of line"),
                               ("LIFE-CAPSULE", "Survival Craft - SOLAS Hard Shell Life Capsule, 22 man"),
                               ("AVIATION-1", "Life-raft, 4-6 person capacity, no ballast, with canopy, no drogue"),
                               ("AVIATION-2", "Evacuation slide with life-raft, 46 person capacity"),
                               ("OVATEK-CRAFT-1",
                                "Survival Craft - Ovatek Hard Shell Life Raft, 4 and 7-man, lightly loaded, no drogue (average)"),
                               ("OVATEK-CRAFT-2",
                                "Survival Craft - Ovatek Hard Shell Life Raft, 4 man, lightly loaded, no drogue"),
                               ("OVATEK-CRAFT-3",
                                "Survival Craft - Ovatek Hard Shell Life Raft, 7 man, lightly loaded, no drogue"),
                               ("OVATEK-CRAFT-4",
                                "Survival Craft - Ovatek Hard Shell Life Raft, 4 and 7-man, fully loaded, drogued (average)"),
                               ("OVATEK-CRAFT-5",
                                "Survival Craft - Ovatek Hard Shell Life Raft, 4 man, fully loaded, drogued"),
                               ("OVATEK-CRAFT-6",
                                "Survival Craft - Ovatek Hard Shell Life Raft, 7 man, fully loaded, drogued"),
                               ("PERSON-POWERED-VESSEL-1", "Kayak with person on aft deck"),
                               ("PERSON-POWERED-VESSEL-2", "Surf board with person"),
                               ("PERSON-POWERED-VESSEL-3", "Windsurfer with mast and sail in water"),
                               ("PERSON-POWERED-VESSEL-4", "Outrigger canoe (*9)"),
                               ("SKIFF-1", "Skiff, modified-v, cathedral-hull, runabout outboard powerboat"),
                               ("SKIFF-2", "Skiff, V-hull"),
                               ("SKIFF-3", "Skiff, swamped and capsized"),
                               ("SKIFF-4", "Skiff, v-hull bow to stern (aluminium, Norway)"),
                               ("SKIFF-6", "19 foot (5.8 m) fibreglass skiff (*9)"),
                               ("SKIFF-7", "Rigid-hulled inflatable boat"),
                               ("SPORT-BOAT", "Sport boat, no canvas (*1), modified V-hull"),
                               ("SPORT-FISHER", "Sport fisher, center console (*2), open cockpit"),
                               ("BEACHCRAFT-1", "Standup Paddle"),
                               ("BEACHCRAFT-2", "Personal Water Craft (jetski) (*9)"),
                               ("FISHING-VESSEL-1", "Fishing vessel, general (mean values)"),
                               ("FISHING-VESSEL-2", "Fishing vessel, Hawaiian Sampan (*3)"),
                               ("FISHING-VESSEL-3", "Fishing vessel, Japanese side-stern trawler"),
                               ("FISHING-VESSEL-4", "Fishing vessel, Japanese Longliner (*3)"),
                               ("FISHING-VESSEL-5", "Fishing vessel, Korean fishing vessel (*4)"),
                               ("FISHING-VESSEL-6", "Fishing vessel, Gill-netter with rear reel (*3)"),
                               ("FISHING-VESSEL-7", "Poti Marara"),
                               ("FISHING-VESSEL-8", "fishing skiff with sail"),
                               ("FV-DEBRIS", "Fishing vessel debris"),
                               ("LARGE-VESSEL-1", "Large vessel (250 m) in loaded condition. (*8)"),
                               ("LARGE-VESSEL-2", "Large vessel (250 m) in ballast condition. (*8)"),
                               ("LARGE-VESSEL-3", "50 degree listing ro-ro ship"),
                               ("COASTAL-FREIGHTER", "Coastal freighter. (*5)"),
                               ("SAILBOAT-1", "Sailboat Mono-hull (Average)"),
                               ("SAILBOAT-2", "Sailboat Mono-hull (Dismasted, Average)"),
                               ("SAILBOAT-3", "Sailboat Mono-hull (Dismasted - rudder amidships)"),
                               ("SAILBOAT-4", "Sailboat Mono-hull (Dismasted - rudder missing)"),
                               ("SAILBOAT-5", "Sailboat Mono-hull (Bare-masted,  Average)"),
                               ("SAILBOAT-6", "Sailboat Mono-hull (Bare-masted, rudder amidships)"),
                               ("SAILBOAT-6b", "Sailboat Mono-hull (Bare-masted, rudder hove-to)"),
                               ("SAILBOAT-7", "Sailboat Mono-hull, fin keel, shallow draft (was SAILBOAT-2)"),
                               ("SAILBOAT-8", "Sunfish sailing dingy  -  Bare-masted, rudder missing"),
                               ("SAILBOAT-9", "Sunfish sailboat no sail (*10)"),
                               ("SAILBOAT-10", "cruising catamaran no sail"),
                               ("SAILBOAT-11", "10 m sloop with lowered sails"),
                               ("SAILBOAT-12", "80 foot trimaran upside down without rigging nor sail in water"),
                               ("SLDMB", "Self-locating datum marker buoy - no windage"),
                               ("SEPIRB", "Navy Submarine EPIRB (SEPIRB)"),
                               ("BAIT-BOX-1", "Bait/wharf box, holds a cubic metre of ice, mean values (*6)"),
                               ("BAIT-BOX-2", "Bait/wharf box, holds a cubic metre of ice, lightly loaded"),
                               ("BAIT-BOX-3", "Bait/wharf box, holds a cubic metre of ice, full loaded"),
                               ("REFUGEE-RAFT-1", "Immigration vessel, Cuban refugee-raft, no sail (*7)"),
                               ("REFUGEE-RAFT-2", "Immigration vessel, Cuban refugee-raft, with sail (*7)"),
                               ("SEWAGE", "Sewage floatables, tampon applicator"),
                               ("MED-WASTE-1", "Medical waste (mean values)"),
                               ("MED-WASTE-2", "Medical waste, vials"),
                               ("MED-WASTE-3", "Medical waste, vials, large"),
                               ("MED-WASTE-4", "Medical waste, vials, small"),
                               ("MED-WASTE-5", "Medical waste, syringes"),
                               ("MED-WASTE-6", "Medical waste, syringes, large"),
                               ("MED-WASTE-7", "Medical waste, syringes, small"),
                               ("OIL-DRUM", "220 l (55-gallon) oil drum (*10)"),
                               ("MINE", "WWII L-MK2 mine (*10)"),
                               ("MARINE-MAMMALS-1", "Dolphin carcass (*11)"),
                               ("CONTAINER-1", "Scaled down (1:3) 40-ft Container (70% submerged)"),
                               ("CONTAINER-2", "20-ft Container (80% submerged)"),
                               ("CONTAINER-IMMERSED-10pc", "Container immersed at 10%"),
                               ("CONTAINER-IMMERSED-20pc", "Container immersed at 20%"),
                               ("CONTAINER-IMMERSED-30pc", "Container immersed at 30%"),
                               ("CONTAINER-IMMERSED-40pc", "Container immersed at 40%"),
                               ("CONTAINER-IMMERSED-50pc", "Container immersed at 50%"),
                               ("CONTAINER-IMMERSED-60pc", "Container immersed at 60%"),
                               ("CONTAINER-IMMERSED-70pc", "Container immersed at 70%"),
                               ("CONTAINER-IMMERSED-80pc", "Container immersed at 80%"),
                               ("CONTAINER-IMMERSED-90pc", "Container immersed at 90%"),
                               ("CONTAINER-IMMERSED-100pc", "Container immersed at 100%"),
                               )

DRIFTER_NAME_ALL_CHOICES = (('', ''),
                            ('gasoline', 'gasoline'),
                            ('kerosene', 'kerosene'),
                            ('light crude oil', 'light crude oil'),
                            ('diesel oil', 'diesel oil'),
                            ('heavy crude oil', 'heavy crude oil'),
                            ('fuel oil no. 6', 'fuel oil no. 6'),
                            ('heavy fuel oil', 'heavy fuel oil'),
                            ("PIW-1", "Person-in-water (PIW), unknown state (mean values)"),
                            ("PIW-2", "PIW,vertical PFD type III conscious"),
                            ("PIW-3", "PIW, sitting, PFD type I or II"),
                            ("PIW-4", "PIW, survival suit (face up)"),
                            ("PIW-5", "PIW, scuba suit (face up)"),
                            ("PIW-6", "PIW, deceased (face down)"),
                            ("LIFE-RAFT-NB-1", "Life-raft, no ballast (NB) system, general (mean values)"),
                            ("LIFE-RAFT-NB-2", "Life-raft, no ballast system, no canopy, no drogue"),
                            ("LIFE-RAFT-NB-3", "Life-raft, no ballast system, no canopy, with drogue"),
                            ("LIFE-RAFT-NB-4", "Life-raft, no ballast system, with canopy, no drogue"),
                            ("LIFE-RAFT-NB-5", "Life-raft, no ballast system, with canopy, with drogue"),
                            ("LIFE-RAFT-SB-6",
                             "Life-raft, shallow ballast (SB) system AND canopy, general (mean values)"),
                            ("LIFE-RAFT-SB-7", "Life-raft, shallow ballast system, canopy, no drogue"),
                            ("LIFE-RAFT-SB-8", "Life-raft, shallow ballast system AND canopy, with drogue"),
                            ("LIFE-RAFT-SB-9", "Life-raft, shallow ballast system AND canopy, capsized"),
                            ("LIFE-RAFT-SB-10",
                             "Life Raft - Shallow ballast, canopy, Navy Sub Escape (SEIE) 1-man raft, NO drogue"),
                            ("LIFE-RAFT-SB-11",
                             "Life Raft - Shallow ballast, canopy, Navy Sub Escape (SEIE) 1-man raft, with drogue"),
                            ("LIFE-RAFT-DB-10",
                             "Life raft, deep ballast (DB) system, general, unknown capacity and loading (mean values)"),
                            ("LIFE-RAFT-DB-11", "4-14 person capacity, deep ballast system, canopy (average)"),
                            ("LIFE-RAFT-DB-12", "4-14 person capacity, deep ballast system, no drogue"),
                            ("LIFE-RAFT-DB-13",
                             "4-14 person capacity, deep ballast system, canopy, no drogue, light loading"),
                            ("LIFE-RAFT-DB-14",
                             "4-14 person capacity, deep ballast system, no drogue, heavy loading"),
                            ("LIFE-RAFT-DB-15",
                             "4-14 person capacity, deep ballast system, canopy, with drogue (average)"),
                            ("LIFE-RAFT-DB-16",
                             "4-14 person capacity, deep ballast system, canopy, with drogue, light loading"),
                            ("LIFE-RAFT-DB-17",
                             "4-14 person capacity, deep ballast system, canopy, with drogue, heavy loading"),
                            ("LIFE-RAFT-DB-18",
                             "15-50 person capacity, deep ballast system, canopy, general (mean values)"),
                            ("LIFE-RAFT-DB-19",
                             "15-50 person capacity, deep ballast system, canopy, no drogue, light loading"),
                            ("LIFE-RAFT-DB-20",
                             "15-50 person capacity, deep ballast system, canopy, with drogue, heavy loading"),
                            ("LIFE-RAFT-DB-21", "Deep ballast system, general (mean values), capsized"),
                            ("LIFE-RAFT-DB-22", "Deep ballast system, general (mean values), swamped"),
                            ("USCG-RESCUE",
                             "Survival Craft - USCG Sea Rescue Kit - 3 ballasted life rafts and 300 meter of line"),
                            ("LIFE-CAPSULE", "Survival Craft - SOLAS Hard Shell Life Capsule, 22 man"),
                            ("AVIATION-1", "Life-raft, 4-6 person capacity, no ballast, with canopy, no drogue"),
                            ("AVIATION-2", "Evacuation slide with life-raft, 46 person capacity"),
                            ("OVATEK-CRAFT-1",
                             "Survival Craft - Ovatek Hard Shell Life Raft, 4 and 7-man, lightly loaded, no drogue (average)"),
                            ("OVATEK-CRAFT-2",
                             "Survival Craft - Ovatek Hard Shell Life Raft, 4 man, lightly loaded, no drogue"),
                            ("OVATEK-CRAFT-3",
                             "Survival Craft - Ovatek Hard Shell Life Raft, 7 man, lightly loaded, no drogue"),
                            ("OVATEK-CRAFT-4",
                             "Survival Craft - Ovatek Hard Shell Life Raft, 4 and 7-man, fully loaded, drogued (average)"),
                            ("OVATEK-CRAFT-5",
                             "Survival Craft - Ovatek Hard Shell Life Raft, 4 man, fully loaded, drogued"),
                            ("OVATEK-CRAFT-6",
                             "Survival Craft - Ovatek Hard Shell Life Raft, 7 man, fully loaded, drogued"),
                            ("PERSON-POWERED-VESSEL-1", "Kayak with person on aft deck"),
                            ("PERSON-POWERED-VESSEL-2", "Surf board with person"),
                            ("PERSON-POWERED-VESSEL-3", "Windsurfer with mast and sail in water"),
                            ("PERSON-POWERED-VESSEL-4", "Outrigger canoe (*9)"),
                            ("SKIFF-1", "Skiff, modified-v, cathedral-hull, runabout outboard powerboat"),
                            ("SKIFF-2", "Skiff, V-hull"),
                            ("SKIFF-3", "Skiff, swamped and capsized"),
                            ("SKIFF-4", "Skiff, v-hull bow to stern (aluminium, Norway)"),
                            ("SKIFF-6", "19 foot (5.8 m) fibreglass skiff (*9)"),
                            ("SKIFF-7", "Rigid-hulled inflatable boat"),
                            ("SPORT-BOAT", "Sport boat, no canvas (*1), modified V-hull"),
                            ("SPORT-FISHER", "Sport fisher, center console (*2), open cockpit"),
                            ("BEACHCRAFT-1", "Standup Paddle"),
                            ("BEACHCRAFT-2", "Personal Water Craft (jetski) (*9)"),
                            ("FISHING-VESSEL-1", "Fishing vessel, general (mean values)"),
                            ("FISHING-VESSEL-2", "Fishing vessel, Hawaiian Sampan (*3)"),
                            ("FISHING-VESSEL-3", "Fishing vessel, Japanese side-stern trawler"),
                            ("FISHING-VESSEL-4", "Fishing vessel, Japanese Longliner (*3)"),
                            ("FISHING-VESSEL-5", "Fishing vessel, Korean fishing vessel (*4)"),
                            ("FISHING-VESSEL-6", "Fishing vessel, Gill-netter with rear reel (*3)"),
                            ("FISHING-VESSEL-7", "Poti Marara"),
                            ("FISHING-VESSEL-8", "fishing skiff with sail"),
                            ("FV-DEBRIS", "Fishing vessel debris"),
                            ("LARGE-VESSEL-1", "Large vessel (250 m) in loaded condition. (*8)"),
                            ("LARGE-VESSEL-2", "Large vessel (250 m) in ballast condition. (*8)"),
                            ("LARGE-VESSEL-3", "50 degree listing ro-ro ship"),
                            ("COASTAL-FREIGHTER", "Coastal freighter. (*5)"),
                            ("SAILBOAT-1", "Sailboat Mono-hull (Average)"),
                            ("SAILBOAT-2", "Sailboat Mono-hull (Dismasted, Average)"),
                            ("SAILBOAT-3", "Sailboat Mono-hull (Dismasted - rudder amidships)"),
                            ("SAILBOAT-4", "Sailboat Mono-hull (Dismasted - rudder missing)"),
                            ("SAILBOAT-5", "Sailboat Mono-hull (Bare-masted,  Average)"),
                            ("SAILBOAT-6", "Sailboat Mono-hull (Bare-masted, rudder amidships)"),
                            ("SAILBOAT-6b", "Sailboat Mono-hull (Bare-masted, rudder hove-to)"),
                            ("SAILBOAT-7", "Sailboat Mono-hull, fin keel, shallow draft (was SAILBOAT-2)"),
                            ("SAILBOAT-8", "Sunfish sailing dingy  -  Bare-masted, rudder missing"),
                            ("SAILBOAT-9", "Sunfish sailboat no sail (*10)"),
                            ("SAILBOAT-10", "cruising catamaran no sail"),
                            ("SAILBOAT-11", "10 m sloop with lowered sails"),
                            ("SAILBOAT-12", "80 foot trimaran upside down without rigging nor sail in water"),
                            ("SLDMB", "Self-locating datum marker buoy - no windage"),
                            ("SEPIRB", "Navy Submarine EPIRB (SEPIRB)"),
                            ("BAIT-BOX-1", "Bait/wharf box, holds a cubic metre of ice, mean values (*6)"),
                            ("BAIT-BOX-2", "Bait/wharf box, holds a cubic metre of ice, lightly loaded"),
                            ("BAIT-BOX-3", "Bait/wharf box, holds a cubic metre of ice, full loaded"),
                            ("REFUGEE-RAFT-1", "Immigration vessel, Cuban refugee-raft, no sail (*7)"),
                            ("REFUGEE-RAFT-2", "Immigration vessel, Cuban refugee-raft, with sail (*7)"),
                            ("SEWAGE", "Sewage floatables, tampon applicator"),
                            ("MED-WASTE-1", "Medical waste (mean values)"),
                            ("MED-WASTE-2", "Medical waste, vials"),
                            ("MED-WASTE-3", "Medical waste, vials, large"),
                            ("MED-WASTE-4", "Medical waste, vials, small"),
                            ("MED-WASTE-5", "Medical waste, syringes"),
                            ("MED-WASTE-6", "Medical waste, syringes, large"),
                            ("MED-WASTE-7", "Medical waste, syringes, small"),
                            ("OIL-DRUM", "220 l (55-gallon) oil drum (*10)"),
                            ("MINE", "WWII L-MK2 mine (*10)"),
                            ("MARINE-MAMMALS-1", "Dolphin carcass (*11)"),
                            ("CONTAINER-1", "Scaled down (1:3) 40-ft Container (70% submerged)"),
                            ("CONTAINER-2", "20-ft Container (80% submerged)"),
                            ("CONTAINER-IMMERSED-10pc", "Container immersed at 10%"),
                            ("CONTAINER-IMMERSED-20pc", "Container immersed at 20%"),
                            ("CONTAINER-IMMERSED-30pc", "Container immersed at 30%"),
                            ("CONTAINER-IMMERSED-40pc", "Container immersed at 40%"),
                            ("CONTAINER-IMMERSED-50pc", "Container immersed at 50%"),
                            ("CONTAINER-IMMERSED-60pc", "Container immersed at 60%"),
                            ("CONTAINER-IMMERSED-70pc", "Container immersed at 70%"),
                            ("CONTAINER-IMMERSED-80pc", "Container immersed at 80%"),
                            ("CONTAINER-IMMERSED-90pc", "Container immersed at 90%"),
                            ("CONTAINER-IMMERSED-100pc", "Container immersed at 100%"),)
