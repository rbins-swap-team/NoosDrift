"use strict";

$(function ($, L, window, document) {
    $('.btn').mouseup(function () {
        this.blur()
    });

    let SimulationId = undefined;
    var regex = new RegExp("^.*\\/\\/.*\\/noos_viewer\\/simulationdemand\\/viewresults\\/(\\d+)\\/.*?$");
    var results = regex.exec(window.location.href);
    if (results !== null) {
        SimulationId = results[ 1 ];
    }

    let map = $('#mapid');

    //map to bottom of page
    map.css('height', '100vh');
    map.height(map.height() - map.offset().top);
    $(window).resize(function () {
        map.css('height', '100vh');
        map.height(map.height() - map.offset().top);
    });

    $.getJSON("/noosdrift/api/noos_viewer/simulationdemand/viewresultsstart/" + SimulationId + "/")
        .done(function (simulationData) {
            $("#simulationtitle").html(simulationData[ "title" ]);
            const noosDriftData = new NoosDriftData(simulationData, $, window, L);

            //CONTROL LAYERS
            //Reset checkboxes on page reload
            $('input[type="checkbox"]').each(function () {
                $(this).prop('checked', false);
            });
            $('input[id="mme_Ellipse"]').trigger('click');
            $('input[id="all_Trajectories"]').trigger('click');
            //Show panel
            $('#tune_map_button').trigger('click');

            //Open Sea Map
            $('#SeaMarks').on('change', function () {
                if ($(this).is(":checked")) {
                    if (noosDriftData.mapGetZoom() < 9) {
                        noosDriftData.mapSetZoom(9);
                    } else if (noosDriftData.mapGetZoom() > 17) {
                        noosDriftData.mapSetZoom(17);
                    }
                    if (!noosDriftData.mapHasSeaMarks()) {
                        noosDriftData.toggleSeaMarks();
                    }
                } else {
                    if (noosDriftData.mapHasSeaMarks()) {
                        noosDriftData.toggleSeaMarks();
                    }
                }
            });
        })
        .fail(function () {
            console.log("No Data for simulation #" + SimulationId);
        })
        .always(function () {
        });
}(window.jQuery, window.L, window, document));
