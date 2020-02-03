"use strict";

class NoosDriftData {
    constructor(simulationData) {
        let map_div = $('#mapid');
        this._map = new L.Map('mapid', { zoomControl: false, doubleClickZoom: false });
        this._demandId = simulationData[ "metadata" ][ "simulation_id" ];
        this._baseMap = L.tileLayer(
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            {
                'attribution': 'Base Map &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                'subdomains': [ 'a', 'b', 'c' ]
            });
        this._openSeaMapLayer = L.tileLayer(
            'https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
            {
                'attribution': '<a href="https://www.openseamap.org/index.php?id=imprint&L=1">OpenSeaMap</a>',
                'maxZoom': 17,
                'minZoom': 9,
                'maxNativeZoom': 17,
                'minNativeZoom': 9,
                pane: 'seamarks'
            });
        this._SuperEllipseMultiplyFactor = 4;
        this._ClusterMultiplyFactor = 3;
        this._EllipseMultiplyFactor = 3;
        this._MetOceanList = [ ["nws_sea_surface_height_above_geoid_", "Sea surface height"],
                               ["nws_sea_surface_salinity_", "Sea surface salinity"],
                               ["nws_sea_surface_temperature_", "Sea surface temperature"],
                               ["nws_surface_sea_water_velocity_", "Sea water velocity"],
                               ["nws_sea_surface_wave_significant_height_", "Sea surface wave significant height"],
                               ["nws_wind_speed_", "Wind speed"] ];
        this._ellipsesLayerGroup = L.layerGroup();
        this._trajectoriesLayerGroup = L.layerGroup();
        this._cloudsLayerGroup = L.layerGroup();
        this._MetOceanLayerGroup = L.layerGroup();
        this._dateTime = moment(simulationData[ "ellipses_and_clusters" ]["timestamp"]).utc();
        this._currentStep = 0;
        this._totalSteps = simulationData[ "metadata" ][ "tot_steps" ] - 1;
        this._MetOcean_bounds = L.latLngBounds(L.latLng(46, 13), L.latLng(62.74324, -16));

        // Time indicator
        $('#stepindic').html(this._dateTime.format("D MMMM YYYY HH:mm Z z"));

        // map buttons
        map_div.append("<div id='map_buttons' class='map-buttons-bottom text-center map_overlay_nav'>" +
            "<button type='button' class='btn btn-danger btn-circle btn-lg' id='firstEl' disabled>" +
            "<i class='material-icons'>first_page</i>" +
            "</button>" +
            "<button type='button' class='btn btn-danger btn-circle btn-lg' id='previousEl' disabled>" +
            "<i class='material-icons'>chevron_left</i>" +
            "</button>" +
            "<button type='button' class='btn btn-danger btn-circle btn-lg' id='nextEl'>" +
            "<i class='material-icons'>chevron_right</i>" +
            "</button>" +
            "<button type='button' class='btn btn-danger btn-circle btn-lg' id='lastEl'>" +
            "<i class='material-icons'>last_page</i>" +
            "</button>" +
            "</div>");

        // Sort and extract ellipses
        let sorted_ellipses = {};
        Object.keys(simulationData["ellipses_and_clusters"][ "ellipses" ]).sort().forEach(function(key) {
            sorted_ellipses[key] = simulationData["ellipses_and_clusters"][ "ellipses" ][key];
        });

        // Sort and extract trajectories
        let sorted_trajectories = {};
        Object.keys(simulationData["metadata"][ "trajectories" ]).sort().forEach(function(key) {
            sorted_trajectories[key] = simulationData["metadata"][ "trajectories" ][key];
        });



        // Find MME key
        //let mmeKey = undefined;
        let lineStyles = [ '', '8,8', '16,8', '16,8,4,8', '16,16', '1,4,1,4,1,16' ];
        //let lineColors = [ '#000', '#f0f', '#f80', '#f00' ];
        //let mme_i = 0;
        let mothy_i = 0;
        let oserit_i = 0;
        let opendrift_i = 0;
        let model_regex = new RegExp("^(.*)_(.*_.*)$");


        // Set colors
        $.each(sorted_ellipses, function (key, value) {
            let model_key = model_regex.exec(key)[1].toLowerCase();
            /*if (value[ "model_code" ] === "MME") {
                mmeKey = key;
                simulationData[ "ellipses_and_trajectories" ][ key ][ "option" ] = {
                    color: '#000',
                    dashArray: lineStyles[ mme_i ],
                    lineJoin: 'round',
                    patterns: [
                        {
                            offset: 25,
                            repeat: 50,
                            symbol: L.Symbol.arrowHead({
                                pixelSize: 15,
                                pathOptions: { fillOpacity: 1, weight: 0, color: '#000' }
                            })
                        }
                    ]
                };
                simulationData[ "ellipses_and_trajectories" ][ key ][ "ellipse" ][ "option" ] = {
                    color: '#000',
                    dashArray: lineStyles[ mme_i ],
                    fillOpacity: .3,
                    lineJoin: 'round'
                };
                mme_i = mme_i + 1;

            }*/
            if (model_key === "oserit") {
                sorted_trajectories[ key ][ "option" ] = {
                    color: '#f0f',
                    dashArray: lineStyles[ oserit_i ],
                    lineJoin: 'round',
                    patterns: [
                        {
                            offset: 25,
                            repeat: 50,
                            symbol: L.Symbol.arrowHead({
                                pixelSize: 15,
                                pathOptions: { fillOpacity: 1, weight: 0, color: '#f0f' }
                            })
                        }
                    ]
                };
                sorted_ellipses[ key ][ "option" ] = {
                    color: '#f0f',
                    dashArray: lineStyles[ oserit_i ],
                    fillOpacity: .3,
                    lineJoin: 'round'
                };
                oserit_i = oserit_i + 1;
            }
            if (model_key === "opendrift") {
                sorted_trajectories[ key ][ "option" ] = {
                    color: '#f80',
                    dashArray: lineStyles[ opendrift_i ],
                    lineJoin: 'round',
                    patterns: [
                        {
                            offset: 25,
                            repeat: 50,
                            symbol: L.Symbol.arrowHead({
                                pixelSize: 15,
                                pathOptions: { fillOpacity: 1, weight: 0, color: '#f80' }
                            })
                        }
                    ]
                };
                sorted_ellipses[ key ][ "option" ] = {
                    color: '#f80',
                    dashArray: lineStyles[ opendrift_i ],
                    fillOpacity: .3,
                    lineJoin: 'round'
                };
                opendrift_i = opendrift_i + 1;
            }
            if (model_key === "mothy") {
                sorted_trajectories[ key ][ "option" ] = {
                    color: '#f00',
                    dashArray: lineStyles[ mothy_i ],
                    lineJoin: 'round',
                    patterns: [
                        {
                            offset: 25,
                            repeat: 50,
                            symbol: L.Symbol.arrowHead({
                                pixelSize: 15,
                                pathOptions: { fillOpacity: 1, weight: 0, color: '#f00' }
                            })
                        }
                    ]
                };
                sorted_ellipses[ key ][ "option" ] = {
                    color: '#f00',
                    dashArray: lineStyles[ mothy_i ],
                    fillOpacity: .3,
                    lineJoin: 'round'
                };
                mothy_i = mothy_i + 1;
            }
        });

        // Create layers for MetOcean maps
        let that = this;
        $.each(this._MetOceanList, function (key, value){
            let MetOcean = L.imageOverlay("/noosdrift/api/media/maps/" + that._demandId + "/" + value[0] + that._dateTime.format("YYYYMMDDHHmm") + ".png", that._MetOcean_bounds);
            MetOcean.id = key.toString();
            that._MetOceanLayerGroup.addLayer(MetOcean);

            // Control for MetOcean maps
            $("#MetOceanSelect").append('<option value="' + key + '">' + value[1] + '</option>')
        });

        // Action for MetOcean maps
        $("#MetOceanSelect").on('change', function (event) {
            $.each(that._MetOceanLayerGroup.getLayers(), function (MetOceanKey, MetOceanValue) {
                if (MetOceanValue.id === event.target.value) {

                    MetOceanValue.addTo(that._map);
                } else {
                    if (that._map.hasLayer(MetOceanValue)) {
                        that._map.removeLayer(MetOceanValue);
                    }
                }
            });
        });

        // Create layers for MME "clusters"
        $.each(simulationData["ellipses_and_clusters"][ "clusters" ], function (key, value) {
            let multiply_factor = that._ClusterMultiplyFactor;
            let sorted_members = {};
            Object.keys(value["member_ellipses"]).sort().forEach(function(key) {
                sorted_members[key] = value["member_ellipses"][key];
            });

            let members_html = "";
            $.each(sorted_members, function (key, value) {
                if(sorted_members[key]["distance_from_cluster_centre"] !== null) {
                    let model_key = model_regex.exec(key)[ 1 ].toUpperCase();
                    let forcings_key = model_regex.exec(key)[ 2 ].toLowerCase();
                    members_html = members_html + model_key + ' (' + forcings_key + ') at ' + sorted_members[ key ][ "distance_from_cluster_centre" ].toFixed(2) + 'm<br>';
                }
            });

            let cluster = L.circle(L.latLng(value["lat"], value["lng"]), value["radius"] * multiply_factor, {
                color: '#000',
                dashArray: '',
                fillOpacity: .3,
                lineJoin: 'round'
            }).bindPopup('MME Cluster<br><br><span style="font-size: 0.8rem;">Members:<br>'+ members_html);
            cluster.id = "mme_Ellipse";
            that._ellipsesLayerGroup.addLayer(cluster);
        });

        // Create layers for MME "super-ellipse"
        if (typeof simulationData["ellipses_and_clusters"][ "super-ellipse" ] !== 'undefined') {
            let multiply_factor = that._SuperEllipseMultiplyFactor;
            let angle = simulationData["ellipses_and_clusters"][ "super-ellipse" ][ "ellipsis_major_axis_azimuth_angle" ] - 90.0;
            let surface_txt;
            let major_axis = simulationData["ellipses_and_clusters"][ "super-ellipse" ][ "ellipsis_major_axis" ] * multiply_factor;
            let minor_axis = simulationData["ellipses_and_clusters"][ "super-ellipse" ][ "ellipsis_minor_axis" ] * multiply_factor;
            let surface = Math.round(100 * Math.PI * major_axis * minor_axis ) / 100;

            if (surface <= 100) {
                surface_txt = surface + " m&sup2;"
            }
            else if (surface > 100 && surface <= 10000) {
                surface_txt =   Math.round(surface) / 100 + " dam&sup2;"
            }
            else if (surface > 10000 && surface <= 1000000) {
                surface_txt = Math.round( surface / 100) / 100 + " hm&sup2;"
            }
            else {
                surface_txt = Math.round( surface / 10000) / 100 + " km&sup2;"
            }

            if (angle < 0){
                angle = angle + 360.0;
            }
            else if (angle > 360.0) {
                angle = angle - 360.0;
            }

            let cluster = L.ellipse(L.latLng(simulationData["ellipses_and_clusters"][ "super-ellipse" ][ "centerlat" ], simulationData["ellipses_and_clusters"][ "super-ellipse" ][ "centerlon" ]),
                [ major_axis, minor_axis ],
                angle,
                {
                color: '#7FFF00',
                dashArray: '',
                fillOpacity: .3,
                lineJoin: 'round'
            }).bindPopup('Global<br>Surface : '+ surface_txt);
            cluster.id = "mme_Ellipse";
            that._ellipsesLayerGroup.addLayer(cluster);
        }

        // Control for MME
        $('#layercontroltable tbody tr:first').after('<tr class="table-dark table-row-mme"><td><input title="mme_Ellipse" type="checkbox" class="leaflet-control-layers-selector" id="mme_Ellipse"></td><td></td><td></td><td>MME</td></tr>');

        // Actions for MME
        $('#mme_Ellipse').on('change', function (event) {
            let isChecked = $(this).is(":checked");
            let all = $('#all_Ellipses');
            let allEllipsesUnchecked = $("input[id$='_Ellipse']:checkbox:not(:checked)");
            $.each(that._ellipsesLayerGroup.getLayers(), function (ellipKey, ellipValue) {
                if (ellipValue.id === event.target.id) {
                    if (that._map.hasLayer(ellipValue)) {
                        if (isChecked === false) {
                            all.prop('checked', false);
                            that._map.removeLayer(ellipValue);
                        }
                    } else {
                        if (isChecked === true) {
                            if (allEllipsesUnchecked.length === 0) {
                                all.prop('checked', true);
                            }
                            ellipValue.addTo(that._map);
                        }
                    }
                }
            });
        });

        // Create layers for init data
        $.each(sorted_trajectories, function (key, value) {
            let name_regex = model_regex.exec(key);
            let model_key = name_regex[1].toLowerCase();
            let forcings_key = name_regex[2].toLowerCase();

            // for Trajectories
            let trajectory = L.polyline(value[ "coordinates" ], value[ "option" ]).bindPopup(model_key.toUpperCase() + '<br><span style="font-size: 0.8rem;">(' + forcings_key.toLowerCase() + ')');
            let arrows = L.polylineDecorator(value[ "coordinates" ], value[ "option" ]).bindPopup(model_key.toUpperCase() + '<br><span style="font-size: 0.8rem;">(' + forcings_key.toLowerCase() + ')');
            trajectory.id = key.replace('.', '') + '_Trajectory';
            arrows.id = key.replace('.', '') + '_Trajectory';
            that._trajectoriesLayerGroup.addLayer(trajectory);
            that._trajectoriesLayerGroup.addLayer(arrows);

            //for ellipses
            if (sorted_ellipses[ key ][ "lat" ] !== null){

                let multiply_factor = that._EllipseMultiplyFactor;
                let angle = sorted_ellipses[ key ][ "angle" ] - 90.0;
                let surface_txt;
                let major_axis = sorted_ellipses[ key ][ "radiiSemiMajorAxis" ] * multiply_factor;
                let minor_axis = sorted_ellipses[ key ][ "radiiSemiMinorAxis" ] * multiply_factor;
                let surface = Math.round(100 * Math.PI * major_axis * minor_axis ) / 100;

                if (surface <= 100) {
                    surface_txt = surface + " m&sup2;"
                }
                else if (surface > 100 && surface <= 10000) {
                    surface_txt =   Math.round(surface) / 100 + " dam&sup2;"
                }
                else if (surface > 10000 && surface <= 1000000) {
                    surface_txt = Math.round( surface / 100) / 100 + " hm&sup2;"
                }
                else {
                    surface_txt = Math.round( surface / 10000) / 100 + " km&sup2;"
                }

                if (angle < 0){
                    angle = angle + 360.0;
                }
                else if (angle > 360.0) {
                    angle = angle - 360.0;
                }

                let ellipse = L.ellipse(L.latLng(sorted_ellipses[ key ][ "lat" ], sorted_ellipses[ key ][ "lng" ]), [ major_axis, minor_axis ], angle, sorted_ellipses[ key ][ "option" ]).bindPopup(model_key.toUpperCase() + '<br><span style="font-size: 0.8rem;">(' + forcings_key.toLowerCase() + ')<br>Surface : '+ surface_txt);
                ellipse.id = key.replace('.', '') + '_Ellipse';
                that._ellipsesLayerGroup.addLayer(ellipse);
            }


            //for Control
            $('#layercontroltable tbody tr:last').after('<tr><td><input title="' + key.replace('.', '') + '_Ellipse" type="checkbox" class="leaflet-control-layers-selector" id="' + key.replace('.', '') + '_Ellipse"></td><td><input title="' + key.replace('.', '') + '_Trajectory" type="checkbox" class="leaflet-control-layers-selector" id="' + key.replace('.', '') + '_Trajectory"></td><td><input title="' + key + '_Cloud" class="leaflet-control-layers-selector" type="radio" name="CloudRadios" id="' + key + '_Cloud" value="' + key + '"></td><td>' + model_key.toUpperCase() + '<br><span style="font-size: 0.8rem;">(' + forcings_key.toLowerCase() + ')</span></td></tr>');

            $('#' + key.replace('.', '') + '_Trajectory').on('change', function (event) {
                let isChecked = $(this).is(":checked");
                let all = $('#all_Trajectories');
                let allTrajectoriesUnchecked = $("input[id$='_Trajectory']:checkbox:not(:checked)");
                $.each(that._trajectoriesLayerGroup.getLayers(), function (trajKey, trajValue) {
                    if (trajValue.id === event.target.id) {
                        if (that._map.hasLayer(trajValue)) {
                            if (isChecked === false) {
                                all.prop('checked', false);
                                that._map.removeLayer(trajValue);
                            }
                        } else {
                            if (isChecked === true) {
                                if (allTrajectoriesUnchecked.length === 0) {
                                    all.prop('checked', true);
                                }
                                trajValue.addTo(that._map);
                            }
                        }
                    }
                });
            });

            $('#' + key.replace('.', '') + '_Ellipse').on('change', function (event) {
                let isChecked = $(this).is(":checked");
                let all = $('#all_Ellipses');
                let allEllipsesUnchecked = $("input[id$='_Ellipse']:checkbox:not(:checked)");
                $.each(that._ellipsesLayerGroup.getLayers(), function (ellipKey, ellipValue) {
                    if (ellipValue.id === event.target.id) {
                        if (that._map.hasLayer(ellipValue)) {
                            if (isChecked === false) {
                                all.prop('checked', false);
                                that._map.removeLayer(ellipValue);
                            }
                        } else {
                            if (isChecked === true) {
                                if (allEllipsesUnchecked.length === 0) {
                                    all.prop('checked', true);
                                }
                                ellipValue.addTo(that._map);
                            }
                        }
                    }
                });
            });
        });

        //Set bounding box
        this._map.fitBounds(simulationData["metadata"]["bbox_coords"]);


        // all trajectories action
        $('#all_Trajectories').on('change', function () {
            let allTrajectoriesUnchecked = $("input[id$='_Trajectory']:checkbox:not(:checked)");
            let allTrajectoriesChecked = $("input[id$='_Trajectory']:checkbox:checked");
            if ($(this).is(":checked")) {
                allTrajectoriesUnchecked.trigger('click');
            }
            if ($(this).is(":not(:checked)")) {
                allTrajectoriesChecked.trigger('click');
            }
        });

        $('#all_Ellipses').on('change', function () {
            let allEllipsesUnchecked = $("input[id$='_Ellipse']:checkbox:not(:checked)");
            let allEllipsesChecked = $("input[id$='_Ellipse']:checkbox:checked");
            if ($(this).is(":checked")) {
                allEllipsesUnchecked.trigger('click');
            }
            if ($(this).is(":not(:checked)")) {
                allEllipsesChecked.trigger('click');
            }
        });

        // Actions to get clouds
        $("input[id$='_Cloud']").on('change', function () {
            let radioValue = $(this).val();
            // Remove previous cloud
            that._cloudsLayerGroup.eachLayer(function (layer) {
                if (that._map.hasLayer(layer)) {
                    that._map.removeLayer(layer);
                }
            });
            that._cloudsLayerGroup.clearLayers();

            if ($(this).is(":checked")) {
                $.getJSON("/noosdrift/api/noos_viewer/simulationdemand/cloudofpoints/" + that._demandId + "/" + radioValue + "/" + that._currentStep + "/")
                    .done(function (simulationData) {
                        let theData = {
                            "type": "FeatureCollection",
                            "features": [ {
                                "type": "Feature",
                                "geometry": {
                                    "type": "MultiPoint",
                                    "coordinates": simulationData[ "coordinates" ]
                                }
                            } ]
                        };
                        let name_regex = model_regex.exec(simulationData["simulation_name"]);
                        let model_key = name_regex[1].toLowerCase();
                        let forcings_key = name_regex[2].toLowerCase();

                        let cloudMarkerOptions = {};
                        if (model_key === "oserit") {
                            cloudMarkerOptions = {
                                radius: 3,
                                fillColor: "#f0f",
                                color: "#000",
                                weight: 0.5,
                                opacity: 1,
                                fillOpacity: 1
                            };
                        }
                        if (model_key === "opendrift") {
                            cloudMarkerOptions = {
                                radius: 3,
                                fillColor: "#f80",
                                color: "#000",
                                weight: 0.5,
                                opacity: 1,
                                fillOpacity: 1
                            };
                        }
                        if (model_key === "mothy") {
                            cloudMarkerOptions = {
                                radius: 3,
                                fillColor: "#f00",
                                color: "#000",
                                weight: 0.5,
                                opacity: 1,
                                fillOpacity: 1
                            };
                        }

                        let cloudGeoJSONLayer = L.geoJSON(theData, {
                            pointToLayer: function (feature, latlng) {
                                return L.circleMarker(latlng, cloudMarkerOptions)
                            }
                        });
                        that._cloudsLayerGroup.addLayer(cloudGeoJSONLayer.bindPopup(model_key.toUpperCase() + '<br><span style="font-size: 0.8rem;">(' + forcings_key.toLowerCase() + ')'));
                        that._cloudsLayerGroup.addTo(that._map);
                    })
            }
        });


        // time navigation
        let firstButton = $("#firstEl");
        let previousButton = $("#previousEl");
        let nextButton = $("#nextEl");
        let lastButton = $("#lastEl");
        let timeProgressBar = $("#timeProgress");

        firstButton.on('click', function () {
            that._currentStep = 0;
            timeProgressBar.css("width", '0%');
            that.stepForward();
            firstButton.prop("disabled", true);
            previousButton.prop("disabled", true);
            if (that._totalSteps !== 1) {
                nextButton.prop("disabled", false);
                lastButton.prop("disabled", false);
            }

        });
        previousButton.on('click', function () {
            if (that._currentStep > 0) {
                that._currentStep = that._currentStep - 1;
                timeProgressBar.css("width", (that._currentStep / that._totalSteps) * 100 + '%');
                that.stepForward();
                if (that._currentStep === 0) {
                    firstButton.prop("disabled", true);
                    previousButton.prop("disabled", true);
                }
                if (that._currentStep < that._totalSteps) {
                    nextButton.prop("disabled", false);
                    lastButton.prop("disabled", false);
                }
            }
        });
        nextButton.on('click', function () {
            if (that._currentStep < that._totalSteps) {
                that._currentStep = that._currentStep + 1;
                timeProgressBar.css("width", (that._currentStep / that._totalSteps) * 100 + '%');
                that.stepForward();
                if (that._currentStep === that._totalSteps) {
                    nextButton.prop("disabled", true);
                    lastButton.prop("disabled", true);
                }
                if (that._currentStep > 0) {
                    firstButton.prop("disabled", false);
                    previousButton.prop("disabled", false);
                }
            }
        });
        lastButton.on('click', function () {
            that._currentStep = that._totalSteps;
            timeProgressBar.css("width", '100%');
            that.stepForward();
            nextButton.prop("disabled", true);
            lastButton.prop("disabled", true);
            if (that._totalSteps !== 1) {
                firstButton.prop("disabled", false);
                previousButton.prop("disabled", false);
            }
        });

        // clear clouds button
        $('#clear_Clouds').on('click', function () {
            $("input[id$='_Cloud']:radio:checked").prop("checked", false);
            that._cloudsLayerGroup.eachLayer(function (layer) {
                if (that._map.hasLayer(layer)) {
                    that._map.removeLayer(layer);
                }
            });
        });


        //Add base map
        this._map.addLayer(this._baseMap);

        //Add coordinates
        this._coordinatesControl = new L.control.coordinates({
            position: "topleft",
            decimals: 6, //optional default 4
            labelTemplateLat: "{y}", //optional default "Lat: {y}"
            labelTemplateLng: " <span style=\"color: #999;\">/</span> {x}", //optional default "Lng: {x}"
            enableUserInput: false, //optional default true
            useLatLngOrder: true //ordering of labels, default false-> lng-lat
        });
        this._coordinatesControl.addTo(this._map);

        //Add measurement tool
        this._measureControl = new L.Control.Measure({
            position: 'topleft',
            units: {
                sqKmeters: {
                    factor: 0.000001, // Required. Factor to apply when converting to this unit. Length in meters or area in sq meters will be multiplied by this factor.
                    display: 'Km²', // Required. How to display in results, like.. "300 Meters (0.3 My New Unit)".
                    decimals: 3 // Number of decimals to round results when using this unit. `0` is the default value if not specified.
                },
                Kmeters: {
                    factor: 0.001, // Required. Factor to apply when converting to this unit. Length in meters or area in sq meters will be multiplied by this factor.
                    display: 'Km', // Required. How to display in results, like.. "300 Meters (0.3 My New Unit)".
                    decimals: 3 // Number of decimals to round results when using this unit. `0` is the default value if not specified.
                }
            },
            localization: 'en',
            primaryLengthUnit: 'Kmeters',
            secondaryLengthUnit: 'undefined',
            primaryAreaUnit: 'sqKmeters',
            captureZIndex: 10000
        });
        this._measureControl.addTo(this._map);

        //Open sea map pane
        this._map.createPane('seamarks');
        this._map.getPane('seamarks').style.zIndex = '450';

        //MME ellipse pane
        this._map.createPane('mmeEllipse');
        this._map.getPane('mmeEllipse').style.zIndex = '460';

        this._map.on('zoomend', function() {
            if ($('#SeaMarks').prop('checked')) {
                if (this.getZoom() < 9 || this.getZoom() > 17) {
                    if (that.mapHasSeaMarks()) {
                        that.toggleSeaMarks();
                    }
                }
                else if (!that.mapHasSeaMarks()){
                    that.toggleSeaMarks();
                }
            }
        });
    }

    stepForward() {
        let that = this;
        let allEllipsesChecked = $("input[id$='_Ellipse']:checkbox:checked");
        let allCloudsChecked = $("input[id$='_Cloud']:radio:checked");
        let MetOceanChecked = $("#MetOceanSelect").val();

        $.getJSON("/noosdrift/api/noos_viewer/simulationdemand/elements/" + this._demandId + "/" + this._currentStep + "/")
            .done(function (simulationData) {
                // Remove previous ellipses
                that._ellipsesLayerGroup.eachLayer(function (layer) {
                    if (that._map.hasLayer(layer)) {
                        that._map.removeLayer(layer);
                    }
                });
                that._ellipsesLayerGroup.clearLayers();
                // Remove previous cloud
                that._cloudsLayerGroup.eachLayer(function (layer) {
                    if (that._map.hasLayer(layer)) {
                        that._map.removeLayer(layer);
                    }
                });
                that._cloudsLayerGroup.clearLayers();
                // Remove previous MetOcean
                that._MetOceanLayerGroup.eachLayer(function (layer) {
                    if (that._map.hasLayer(layer)) {
                        that._map.removeLayer(layer);
                    }
                });
                that._MetOceanLayerGroup.clearLayers();

                // Update date
                this._dateTime = moment(simulationData[ "ellipses_and_clusters" ]["timestamp"]).utc();
                $('#stepindic').html(this._dateTime.format("D MMMM YYYY HH:mm Z z"));

                // Sort and extract ellipses
                let sorted_ellipses = {};
                Object.keys(simulationData["ellipses_and_clusters"][ "ellipses" ]).sort().forEach(function(key) {
                    sorted_ellipses[key] = simulationData["ellipses_and_clusters"][ "ellipses" ][key];
                });

                let model_regex = new RegExp("^(.*)_(.*_.*)$");

                let lineStyles = [ '', '8,8', '16,8', '16,8,4,8', '16,16', '1,4,1,4,1,16' ];
                //let lineColors = [ '#000', '#f0f', '#f80', '#f00' ];
                //let mme_i = 0;
                let mothy_i = 0;
                let oserit_i = 0;
                let opendrift_i = 0;
                $.each(sorted_ellipses, function (key, value) {
                    let model_key = model_regex.exec(key)[1].toLowerCase();
                    /*if (value[ "model_code" ] === "MME") {
                        simulationData[ "ellipses_and_trajectories" ][ key ][ "ellipse" ][ "option" ] = {
                            color: '#000',
                            dashArray: lineStyles[ mme_i ],
                            fillOpacity: .3,
                            lineJoin: 'round'
                        };
                        mme_i = mme_i + 1;

                    }*/
                    if (model_key === "oserit") {
                        sorted_ellipses[ key ][ "option" ] = {
                            color: '#f0f',
                            dashArray: lineStyles[ oserit_i ],
                            fillOpacity: .3,
                            lineJoin: 'round'
                        };
                        oserit_i = oserit_i + 1;
                    }
                    if (model_key === "opendrift") {
                        sorted_ellipses[ key ][ "option" ] = {
                            color: '#f80',
                            dashArray: lineStyles[ opendrift_i ],
                            fillOpacity: .3,
                            lineJoin: 'round'
                        };
                        opendrift_i = opendrift_i + 1;
                    }
                    if (model_key === "mothy") {
                        sorted_ellipses[ key ][ "option" ] = {
                            color: '#f00',
                            dashArray: lineStyles[ mothy_i ],
                            fillOpacity: .3,
                            lineJoin: 'round'
                        };
                        mothy_i = mothy_i + 1;
                    }
                });

                // Create layers for MME "clusters"
                $.each(simulationData["ellipses_and_clusters"][ "clusters" ], function (key, value) {
                    let multiply_factor = that._ClusterMultiplyFactor;
                    let sorted_members = {};
                    Object.keys(value["member_ellipses"]).sort().forEach(function(key) {
                        sorted_members[key] = value["member_ellipses"][key];
                    });

                    let members_html = "";
                    $.each(sorted_members, function (key, value) {
                        if(sorted_members[key]["distance_from_cluster_centre"] !== null){
                            let model_key = model_regex.exec(key)[1].toUpperCase();
                            let forcings_key = model_regex.exec(key)[2].toLowerCase();
                            members_html = members_html + model_key +' (' + forcings_key +  ') at '+ sorted_members[key]["distance_from_cluster_centre"].toFixed(2) +'m<br>';
                        }
                    });

                    let cluster = L.circle(L.latLng(value["lat"], value["lng"]), value["radius"] * multiply_factor, {
                        color: '#000',
                        dashArray: '',
                        fillOpacity: .3,
                        lineJoin: 'round'
                    }).bindPopup('MME Cluster<br><br><span style="font-size: 0.8rem;">Members:<br>'+ members_html);
                    cluster.id = "mme_Ellipse";
                    that._ellipsesLayerGroup.addLayer(cluster);
                });

                // Create layers for MME "super-ellipse"
                if (typeof simulationData["ellipses_and_clusters"][ "super-ellipse" ] !== 'undefined') {
                    let multiply_factor = that._SuperEllipseMultiplyFactor;
                    let angle = simulationData["ellipses_and_clusters"][ "super-ellipse" ][ "ellipsis_major_axis_azimuth_angle" ] - 90.0;
                    let surface_txt;
                    let major_axis = simulationData["ellipses_and_clusters"][ "super-ellipse" ][ "ellipsis_major_axis" ] * multiply_factor;
                    let minor_axis = simulationData["ellipses_and_clusters"][ "super-ellipse" ][ "ellipsis_minor_axis" ] * multiply_factor;
                    let surface = Math.round(100 * Math.PI * major_axis * minor_axis ) / 100;

                    if (surface <= 100) {
                        surface_txt = surface + " m&sup2;"
                    }
                    else if (surface > 100 && surface <= 10000) {
                        surface_txt =   Math.round(surface) / 100 + " dam&sup2;"
                    }
                    else if (surface > 10000 && surface <= 1000000) {
                        surface_txt = Math.round( surface / 100) / 100 + " hm&sup2;"
                    }
                    else {
                        surface_txt = Math.round( surface / 10000) / 100 + " km&sup2;"
                    }

                    if (angle < 0){
                        angle = angle + 360.0;
                    }
                    else if (angle > 360.0) {
                        angle = angle - 360.0;
                    }

                    let cluster = L.ellipse(L.latLng(simulationData["ellipses_and_clusters"][ "super-ellipse" ][ "centerlat" ], simulationData["ellipses_and_clusters"][ "super-ellipse" ][ "centerlon" ]),
                        [ major_axis, minor_axis ], angle,
                        {
                        color: '#7FFF00',
                        dashArray: '',
                        fillOpacity: .3,
                        lineJoin: 'round'
                    }).bindPopup('Global<br>Surface : '+ surface_txt);
                    cluster.id = "mme_Ellipse";
                    that._ellipsesLayerGroup.addLayer(cluster);
                }

                // Updating ellipses
                $.each(sorted_ellipses, function (key) {

                    if (sorted_ellipses[ key ][ "lat" ] !== null) {

                        let multiply_factor = that._EllipseMultiplyFactor;
                        let angle = sorted_ellipses[ key ][ "angle" ] - 90.0;
                        let surface_txt;
                        let major_axis = sorted_ellipses[ key ][ "radiiSemiMajorAxis" ] * multiply_factor;
                        let minor_axis = sorted_ellipses[ key ][ "radiiSemiMinorAxis" ] * multiply_factor;
                        let surface = Math.round(100 * Math.PI * major_axis * minor_axis ) / 100;

                        if (surface <= 100) {
                            surface_txt = surface + " m&sup2;"
                        }
                        else if (surface > 100 && surface <= 10000) {
                            surface_txt =   Math.round(surface) / 100 + " dam&sup2;"
                        }
                        else if (surface > 10000 && surface <= 1000000) {
                            surface_txt = Math.round( surface / 100) / 100 + " hm&sup2;"
                        }
                        else {
                            surface_txt = Math.round( surface / 10000) / 100 + " km&sup2;"
                        }

                        if (angle < 0){
                            angle = angle + 360.0;
                        }
                        else if (angle > 360.0) {
                            angle = angle - 360.0;
                        }

                        let model_key = model_regex.exec(key)[1].toLowerCase();
                        let forcings_key = model_regex.exec(key)[2].toLowerCase();
                        let ellipse = L.ellipse(L.latLng(sorted_ellipses[ key ][ "lat" ], sorted_ellipses[ key ][ "lng" ]), [ major_axis, minor_axis ], angle, sorted_ellipses[ key ][ "option" ]).bindPopup(model_key.toUpperCase() + '<br><span style="font-size: 0.8rem;">(' + forcings_key.toLowerCase() + ')<br>Surface : '+ surface_txt);
                        ellipse.id = key.replace('.', '') + '_Ellipse';
                        that._ellipsesLayerGroup.addLayer(ellipse);
                    }


                });

                allEllipsesChecked.each(function (key, value) {
                    $.each(that._ellipsesLayerGroup.getLayers(), function (ellipKey, ellipValue) {
                        if (ellipValue.id === value.id) {
                            ellipValue.addTo(that._map);
                        }
                    });
                });

                // Updating MetOcean
                $.each(that._MetOceanList, function (key, value){
                    let MetOcean = L.imageOverlay("/noosdrift/api/media/maps/" + that._demandId + "/" + value[0] + moment(simulationData[ "ellipses_and_clusters" ]["timestamp"]).utc().format("YYYYMMDDHHmm") + ".png", that._MetOcean_bounds);
                    MetOcean.id = key.toString();
                    that._MetOceanLayerGroup.addLayer(MetOcean);
                });

                if (MetOceanChecked !== "") {
                    $.each(that._MetOceanLayerGroup.getLayers(), function (MetOceanKey, MetOceanValue) {
                        if (MetOceanValue.id === MetOceanChecked) {
                            MetOceanValue.addTo(that._map);
                        } else {
                            if (that._map.hasLayer(MetOceanValue)) {
                                that._map.removeLayer(MetOceanValue);
                            }
                        }
                    });
                }

                // Updating Clouds
                allCloudsChecked.each(function (key, value) {
                    $.getJSON("/noosdrift/api/noos_viewer/simulationdemand/cloudofpoints/" + that._demandId + "/" + value.value + "/" + that._currentStep + "/")
                        .done(function (simulationData) {
                            let theData = {
                                "type": "FeatureCollection",
                                "features": [ {
                                    "type": "Feature",
                                    "geometry": {
                                        "type": "MultiPoint",
                                        "coordinates": simulationData[ "coordinates" ]
                                    }
                                } ]
                            };
                            let name_regex = model_regex.exec(simulationData[ "simulation_name" ]);
                            let model_key = name_regex[1].toLowerCase();
                            let forcings_key = name_regex[2].toLowerCase();
                            let cloudMarkerOptions = {};
                            if (model_key === "oserit") {
                                cloudMarkerOptions = {
                                    radius: 3,
                                    fillColor: "#f0f",
                                    color: "#000",
                                    weight: 0.5,
                                    opacity: 1,
                                    fillOpacity: 1
                                };
                            }
                            if (model_key === "opendrift") {
                                cloudMarkerOptions = {
                                    radius: 3,
                                    fillColor: "#f80",
                                    color: "#000",
                                    weight: 0.5,
                                    opacity: 1,
                                    fillOpacity: 1
                                };
                            }
                            if (model_key === "mothy") {
                                cloudMarkerOptions = {
                                    radius: 3,
                                    fillColor: "#f00",
                                    color: "#000",
                                    weight: 0.5,
                                    opacity: 1,
                                    fillOpacity: 1
                                };
                            }

                            let cloudGeoJSONLayer = L.geoJSON(theData, {
                                pointToLayer: function (feature, latlng) {
                                    return L.circleMarker(latlng, cloudMarkerOptions)
                                }
                            });
                            that._cloudsLayerGroup.addLayer(cloudGeoJSONLayer.bindPopup(model_key.toUpperCase() + '<br><span style="font-size: 0.8rem;">(' + forcings_key.toLowerCase() + ')'));
                            that._cloudsLayerGroup.addTo(that._map);
                        })
                });
            })
            .fail(function () {
                console.log("Failed step");
            })
            .always(function () {
            });
    }

    toggleSeaMarks() {
        if (this._map.hasLayer(this._openSeaMapLayer)) {
            this._map.removeLayer(this._openSeaMapLayer);
        } else {
            this._openSeaMapLayer.addTo(this._map);
        }
    }

    mapHasSeaMarks() {
        return this._map.hasLayer(this._openSeaMapLayer);
    }

    mapGetZoom() {
        return this._map.getZoom();
    }

    mapSetZoom(zoomLevel){
        this._map.setZoom(zoomLevel);
    }
}