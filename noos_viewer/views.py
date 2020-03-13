import csv
import datetime as dt
import logging
import os

from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail, BadHeaderError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from noosDrift.settings import APPUSERS_GROUP, BASE_URL, MAIL_ADMIN_NOOSDRIFT, MEDIA_DIR, MEDIA_URL, \
    ODIN_MAILANSWERACCOUNT

from noos_services.archivehelper import ArchiveHelper
from noos_services.helper import Helper as ServiceSimulationDemandHelper
from noos_services.models import LoggingMessage, SimulationDemand
from noos_services.ns_const import MemorySimulationDemand, OtherConst, StatusConst
from noos_viewer.forms import ContactForm, SignUpForm, SimulationDemandForm, SimulationDemandEditedForm
from noos_viewer.helper import SimulationDemandHelper
from noos_viewer.models import UserProfile
from noos_viewer.tokens import account_activation_token

from requests.compat import urljoin

logger = logging.getLogger(__name__)


def simulation_demands(request):
    """
    A method to list all simulation demands
    :param request:
    :return:
    """
    name_and_method = "views.simulation_demands"
    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    logger.info("{}, start".format(name_and_method))
    simulations_list = ServiceSimulationDemandHelper.simulations_list()
    template_name = 'noos_viewer/simulationdemands.html'
    logger.info("{}, end".format(name_and_method))
    return render(request, template_name, {'simulations': simulations_list, 'num_rec': len(simulations_list)})


def update_simulation_demand(request):
    """
    A method to allow a simulation demand to be updated
    (What about the api in noos_services?
    The api in noos_services expects a JSON object that matches the model.
    Here we are working with a Form which does not match the model and that we have to transform first into a model
    object)
    :param request:
    :param simulationid:
    :return:
    """
    name_and_object = "views.update_simulation_demand"
    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    logger.info("{}, start".format(name_and_object))
    context = {}
    template_name = "noos_viewer/errpage.html"
    if request.method == 'POST':
        # logger.debug("signup, method POST")
        # logger.debug("{}, post {}".format(name_and_object, request.POST))
        form = SimulationDemandEditedForm(request.POST)
        demand_helper = SimulationDemandHelper()
        the_form = None
        try:
            simulationid = -999
            if form.is_valid():
                # logger.debug("{}, form is valid".format(name_and_object))
                simulation_demand_dict = demand_helper.extract_from_form_for_edit(form)
                # logger.debug("{}, demand id is : {}".format(name_and_object, simulation_demand_dict))
                simulationid = simulation_demand_dict[SimulationDemandHelper.ID]
                simulation_demand = SimulationDemand.active_objects.get(pk=simulationid)
                simulation_demand.protected = simulation_demand_dict[SimulationDemandHelper.PROTECTED]
                json_dict = simulation_demand.json_txt
                json_dict[SimulationDemandHelper.SIMULATION_DESCRIPTION][SimulationDemandHelper.TITLE] = \
                    simulation_demand_dict[SimulationDemandHelper.SIMULATION_DESCRIPTION][SimulationDemandHelper.TITLE]
                json_dict[SimulationDemandHelper.SIMULATION_DESCRIPTION][SimulationDemandHelper.SUMMARY] = \
                    simulation_demand_dict[SimulationDemandHelper.SIMULATION_DESCRIPTION][
                        SimulationDemandHelper.SUMMARY]
                json_dict[SimulationDemandHelper.SIMULATION_DESCRIPTION][SimulationDemandHelper.TAGS] = \
                    simulation_demand_dict[SimulationDemandHelper.SIMULATION_DESCRIPTION][SimulationDemandHelper.TAGS]
                simulation_demand.save()
                return redirect('noos_viewer:view_simulationdemand', simulationid=simulationid)
            else:
                logger.error("{}, form is not valid ????".format(name_and_object))
                for afield in form.fields:
                    logger.error("{}, afield : {}".format(name_and_object, afield))

                template_name = 'noos_viewer/edit_simulationdemand.html'
                logger.error("{}, errors : {}".format(name_and_object, form.errors))
                context = {'form': form}
        except ObjectDoesNotExist:
            context = {'err_mesg': "The form object doesn't exist."}
            logger.error("The form object doesn't exist.")
        except ValidationError as verr:
            mess_part1 = "{}, {} ".format(name_and_object, verr.message)
            context = {'err_mesg': mess_part1}
            logger.error(mess_part1)

    logger.info("{}, end".format(name_and_object))
    return render(request, template_name, context=context)


def cloud_of_points_for_demand(request, simulationid, modelcouple, stepidx):
    """
    Returns a cloud of points such as calculated for a specific demand by a specific model for a specific moment
    :param request:
    :param simulationid:
    :param modelcouple:
    :param stepidx:
    :return:
    """
    the_cloud = {}
    try:
        the_cloud = SimulationDemandHelper.cloud_of_points_for_demand(simulationid, modelcouple, stepidx)
    except ObjectDoesNotExist:
        logger.error("cloud_of_points_for_demand, demand : {} does not exist or is archived".format(simulationid))

    return JsonResponse(the_cloud)


def report_row(simulation_demand):
    """
    One row from the report generated by make_report_file
    :param simulation_demand:
    :return:
    """
    name_and_method = "views.report_row"
    logger.info("{}, start".format(name_and_method))
    creation_time = simulation_demand.created_time
    stcreation_time = dt.datetime.strftime(creation_time, MemorySimulationDemand.TIMESTAMPFORMAT)
    json_data = simulation_demand.json_txt
    initial_conditions = json_data[MemorySimulationDemand.INITIAL_CONDITION]
    geom = initial_conditions[MemorySimulationDemand.GEOMETRY]
    lat = None
    lon = None
    logger.debug("{}, geom : {}".format(name_and_method, geom))
    if geom == OtherConst.POINT:
        logger.debug("{}, it's a point".format(name_and_method))
        lat = "{}".format(initial_conditions[MemorySimulationDemand.LAT])
        logger.debug("{}, lat : {}".format(name_and_method, initial_conditions[MemorySimulationDemand.LAT]))
        lon = "{}".format(initial_conditions[MemorySimulationDemand.LON])
    else:
        lat = "{}".format(initial_conditions[MemorySimulationDemand.LAT][0])
        lon = "{}".format(initial_conditions[MemorySimulationDemand.LON][0])

    drifter_type = json_data[MemorySimulationDemand.DRIFTER][MemorySimulationDemand.DRIFTER_TYPE]

    logger.debug("{}, retrieving INIT_SIMULATIONS for demand : {}".format(name_and_method, simulation_demand.pk))
    start_messages = LoggingMessage.objects.filter(simulation_demand=simulation_demand,
                                                   status=StatusConst.INIT_SIMULATION).all().order_by('created')
    logger.debug("{}, number INIT_SIMULATION messages : {}".format(name_and_method, len(start_messages)))
    if len(start_messages) < 1:
        return None

    first_message = start_messages[0]
    start_time = ""
    if first_message:
        start_time = dt.datetime.strftime(first_message.created, MemorySimulationDemand.TIMESTAMPFORMAT)

    end_messages = LoggingMessage.objects.filter(simulation_demand=simulation_demand,
                                                 status=StatusConst.ANALYSIS_OK).all().order_by('created')
    end_time = ""
    if len(end_messages) > 0:
        first_message = end_messages[0]
        end_time = dt.datetime.strftime(first_message.created, MemorySimulationDemand.TIMESTAMPFORMAT)

    a_row = {'id': simulation_demand.pk,
             'title': json_data[MemorySimulationDemand.SIMULATION_DESCRIPTION][MemorySimulationDemand.TITLE],
             'user': simulation_demand.user.email,
             'drifter_type': drifter_type,
             'lat': lat,
             'long': lon,
             'creation_date': stcreation_time,
             'start_time': start_time,
             'end_time': end_time,
             'status': simulation_demand.status
             }

    logger.info("{}, end".format(name_and_method))
    return a_row


def make_report_file(request):
    """
    Make a report file and send a mail to tell the admin
    :param request:
    :return:
    """
    name_and_method = "views.make_report_file"
    logger.info("{}, start".format(name_and_method))

    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    os.chdir(MEDIA_DIR)
    strtime = dt.datetime.now().strftime("%Y%m%d-%H%M%s")
    file_name = "report-{}.csv".format(strtime)
    archive_file_path = os.path.join(MEDIA_DIR, file_name)
    url_archive_file_path = urljoin(base=MEDIA_URL, url=file_name)
    # logger.info("{}, report url : {}".format(name_and_method, archive_file_path))
    logger.info("{}, report url : {}".format(name_and_method, url_archive_file_path))

    with open(archive_file_path, 'w', newline='') as csv_file:
        fieldnames = ["id", "title", "user", "drifter_type", "lat", "long", "creation_date", "start_time", "end_time",
                      "status"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=';', quotechar='"',
                                quoting=csv.QUOTE_NONE)
        writer.writeheader()
        all_demands = SimulationDemand.objects.all().order_by('created_time')
        for a_demand in all_demands:
            a_row = report_row(a_demand)
            if a_row:
                writer.writerow(a_row)

    template_name = "noos_viewer/report_available.html"
    context = {"domain": "odnature.naturalsciences.be",
               "urlpath": url_archive_file_path}

    msg_template = "noos_viewer/report_available_msg.html"
    message = render_to_string(msg_template, context=context)
    send_mail("NOOS-Drift Report File", message, ODIN_MAILANSWERACCOUNT, [MAIL_ADMIN_NOOSDRIFT])

    logger.info("{}, end".format(name_and_method))
    return render(request, template_name, context=context)


def archive_simulations(request):
    """
    Executed on the Central. Calls a helper to archive simulation demands
    :param request:
    :return:
    """

    name_and_method = "views.archive_simulations"
    logger.info("{}, start".format(name_and_method))

    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    ArchiveHelper.archive_simulations()

    template_name = "noos_viewer/simulations_archived.html"
    logger.info("{}, end".format(name_and_method))
    return render(request, template_name)


def simulation_init(request, simulationid):
    """
    Called from user interface. The starting point to work with a demand (or simulation).
    This sends back basic demand information.
    :param request:
    :param simulationid:
    :return:
    """
    name_and_method = "views.simulation_init"
    logger.info("{}, start".format(name_and_method))

    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    try:
        init_dict = SimulationDemandHelper.simulation_init(simulationid)
    except ObjectDoesNotExist:
        logger.error("{}, No object with id : {}".format(name_and_method, simulationid))
        init_dict = {}

    logger.info("{}, end".format(name_and_method))

    return JsonResponse(init_dict)


def simulations_for_demand(request, simulationid, stepidx):
    """
    A method to send back the list of SimulationElements (Ellipses, Clusters) for a demand for a particular step.
    :param request:
    :param simulationid:
    :param stepidx:
    :return:
    """
    name_and_method = "views.simulations_for_demand"
    logger.info("{}, start".format(name_and_method))

    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    try:
        step_data = SimulationDemandHelper.simulations_for_demand(simulationid, stepidx)
    except ObjectDoesNotExist:
        logger.error("{}, No object with id : {}".format(name_and_method, simulationid))
        step_data = {}

    logger.info("{}, end".format(name_and_method))

    return JsonResponse(step_data)


def view_results_simulation_demand_start(request, simulationid):
    """
    A method to view the analysis results for this simulation. This method is special because it initialises some
    page elements so it aggregates things that will be called upon later.
    :param request:
    :param simulationid: the simulation
    :return:
    """
    name_and_method = "views.view_results_simulation_demand_start"
    if request.user is None or not request.user.is_authenticated:
        return redirect('home')
    logger.info("{}, start".format(name_and_method))
    context = {}
    try:
        simulation_demand = SimulationDemand.active_objects.get(pk=simulationid)
        template_name = 'noos_viewer/analysisresults.html'
        logger.info("{}, end".format(name_and_method))
        context = {"startData": {"demandid": simulationid}}
        return render(request, template_name, context=context)
    except ObjectDoesNotExist:
        the_message = "{}, no object with id : {}".format(name_and_method, simulationid)
        logger.error(the_message)
        template_name = "noos_viewer/errpage.html"
        context = {'err_mesg': the_message}
    return render(request, template_name, context=context)


def view_results_simulation_demand(request, simulationid):
    """
    A method to view the analysis results for this simulation
    :param request:
    :param simulationid: the simulation
    :return:
    """
    name_and_method = "views.view_results_simulation_demand"
    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    logger.info("{}, start".format(name_and_method))

    try:
        zip_url = ServiceSimulationDemandHelper.get_zip_url(simulationid)
        template_name = 'noos_viewer/analysisresults.html'
        context = {"startData": {"demandid": simulationid}}
        if zip_url:
            context['zipurl'] = zip_url

        logger.info("{}, end".format(name_and_method))
    except ObjectDoesNotExist:
        the_message = "{}, no object with id : {}".format(name_and_method, simulationid)
        logger.error(the_message)
        template_name = "noos_viewer/errpage.html"
        context = {'err_mesg': the_message}

    logger.info("{}, end".format(name_and_method))
    return render(request, template_name, context)


def create_simulation_demand(request):
    """
    A method to create a new simulation demand
    (What about the api in services? The api in service expects a JSON object that matches the model.
    Here we are working with a Form which does not match the model and that we have to transform first into a model
    object)
    :param request:
    :return:
    """
    name_and_method = "views.create_simulation_demand"
    logger.info("{}, start".format(name_and_method))
    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    context = {}
    template_name = ""
    if request.method == 'POST':
        # logger.debug("signup, method POST")
        # logger.debug("{}, post {}".format(name_and_method, request.POST))
        form = SimulationDemandForm(request.POST)
        template_name = 'noos_viewer/edit_simulationdemand.html'
        demand_helper = SimulationDemandHelper()
        try:
            if form.is_valid():
                # logger.debug("{}, form is valid".format(name_and_method))
                simulation_demand_dict = demand_helper.extract_from_form_for_new(form)
                new_demand = SimulationDemand()
                new_demand.user = request.user
                new_demand.status = StatusConst.SUBMITTED
                new_demand.protected = simulation_demand_dict[SimulationDemandHelper.PROTECTED]
                new_demand.json_txt = simulation_demand_dict[SimulationDemandHelper.JSON_TXT]
                new_demand.full_clean()
                # logger.debug("{}, Saving new demand".format(name_and_method))
                new_demand.save()
                # logger.debug("{}, Extracting demand data".format(name_and_method))
                new_demand_dict = demand_helper.extract_simulation_dict(new_demand)
                del new_demand_dict[MemorySimulationDemand.WAVES]
                del new_demand_dict[MemorySimulationDemand.WIND]
                del new_demand_dict[MemorySimulationDemand.CURRENT]
                the_form = SimulationDemandForm(initial=new_demand_dict)
                template_name = 'noos_viewer/simulationdemand.html'
                context = {'form': the_form, 'theid': new_demand.pk,
                           'sim_status': new_demand_dict[MemorySimulationDemand.STATUS],
                           'user_msg': 'Demand Created'}
                # logger.debug("{}, New demand data for form".format(name_and_method))
            else:
                logger.error("{}, form is not valid ????".format(name_and_method))
                for afield in form.fields:
                    logger.error("{}, afield : {}".format(name_and_method, afield))

                template_name = 'noos_viewer/edit_simulationdemand.html'
                logger.error("{}, errors : {}".format(name_and_method, form.errors))
                context = {'form': form}
        except ValidationError as verr:
            logger.error(name_and_method, verr.message)

    # logger.debug("{}, {}".format(name_and_method, template_name))
    logger.info("{}, end".format(name_and_method))
    return render(request, template_name, context=context)


def new_from_model_simulation_demand(request, simulationid):
    """
    A method to get back a Form object that contains some data copied from an existing simulation demand.
    :param request:
    :param simulationid: The simulation demand which will be used to set some data values
    :return:
    """
    name_and_method = "new_from_model_simulation_demand"
    logger.info("{}, start".format(name_and_method))
    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    demand_helper = SimulationDemandHelper()
    template_name = 'noos_viewer/edit_simulationdemand.html'
    context = {}

    try:
        simulation_demand = SimulationDemand.active_objects.get(pk=simulationid)
        simulation_demand_dict = demand_helper.extract_simulation_dict(simulation_demand)
        del simulation_demand_dict[SimulationDemandHelper.ID]
        del simulation_demand_dict[SimulationDemandHelper.STATUS]
        del simulation_demand_dict[SimulationDemandHelper.CREATED_TIME]
        del simulation_demand_dict[MemorySimulationDemand.WAVES]
        del simulation_demand_dict[MemorySimulationDemand.WIND]
        del simulation_demand_dict[MemorySimulationDemand.CURRENT]
        # logger.debug("newfrommodel_simulationdemand, start_time : {}".format(
        #    simulation_demand_dict[SimulationDemandHelper.SIMULATION_START_TIME]))
        # logger.debug("newfrommodel_simulationdemand, end_time : {}".format(
        #    simulation_demand_dict[SimulationDemandHelper.SIMULATION_END_TIME]))
        simulation_demand_form = SimulationDemandForm(initial=simulation_demand_dict)

        template_name = 'noos_viewer/edit_simulationdemand.html'
        otherhtml = urljoin(BASE_URL, 'noos_viewer/simulationdemand/create/')
        context = {'form': simulation_demand_form,
                   'plaintext_class': 'form-control',
                   'nexthtml': otherhtml}
    except ObjectDoesNotExist:
        template_name = 'noos_viewer/errpage.html'
        themessage = "{}, no object with id : {}".format(name_and_method, simulationid)
        logger.error(themessage)
        context = {'err_mesg': themessage}

    logger.info("{}, end".format(name_and_method))
    return render(request, template_name, context)


def new_simulationdemand(request):
    """
    A method to get back a blank From object, create an empty Form page and receive information for a brand new
    simulation demand
    :param request:
    :return:
    """

    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    simulation_demand_form = SimulationDemandForm()
    template_name = 'noos_viewer/edit_simulationdemand.html'
    other_html = urljoin(BASE_URL, 'noos_viewer/simulationdemand/create/')
    return render(request, template_name, {
        'form': simulation_demand_form,
        'plaintext_class': 'form-control',
        'nexthtml': other_html})


def toggle_protection(request, simulationid):
    """
    A method to toggle the value the protection field of a demand
    :param request:
    :param simulationid: The simulation demand for which has to be changed
    :return
    """
    name_and_method = "toggle_protection"
    logger.info("{}, start".format(name_and_method))

    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    # logger.debug("{}, looking for object with id : {}".format(name_and_method, simulationid))
    try:
        simulation_demand = SimulationDemand.active_objects.get(pk=simulationid)
        # logger.debug("{}, Found_simulationdemand, with id : {}".format(name_and_method, simulation_demand.id))
        simulation_demand.protected = not simulation_demand.protected
        simulation_demand.save()
        simulations_list = ServiceSimulationDemandHelper.simulations_list()
        template_name = 'noos_viewer/simulationdemands.html'
        context = {'simulations': simulations_list, 'num_rec': len(simulations_list)}
    except ObjectDoesNotExist:
        themessage = "{}, no object with id : {}".format(name_and_method, simulationid)
        logger.error(themessage)
        template_name = "noos_viewer/errpage.html"
        context = {'err_mesg': themessage}

    logger.info("{}, end".format(name_and_method))
    return render(request, template_name, context)


def edit_simulationdemand(request, simulationid):
    """
    A method to get a form for editing part of a simulation demand's data
    :param request:
    :param simulationid: The simulation demand which the user wants to edit
    :return:
    """
    name_and_method = "views.edit_simulationdemand"
    logger.info("{}, start".format(name_and_method))
    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    template_name = ""
    context = {}
    if request.method == 'GET':
        try:
            simulation_demand = SimulationDemand.active_objects.get(pk=simulationid)
            demand_helper = SimulationDemandHelper()
            simulation_demand_dict = demand_helper.extract_simulation_dict(simulation_demand)
            zipurl = ServiceSimulationDemandHelper.get_zip_url(simulationid)
            del simulation_demand_dict[MemorySimulationDemand.WAVES]
            del simulation_demand_dict[MemorySimulationDemand.WIND]
            del simulation_demand_dict[MemorySimulationDemand.CURRENT]
            simulation_demand_form = SimulationDemandForm(initial=simulation_demand_dict)

            template_name = 'noos_viewer/edit_simulationdemand.html'
            next_html = urljoin(BASE_URL, 'noos_viewer/simulationdemand/update/')

            context = {'form': simulation_demand_form,
                       'plaintext_class': 'form-control-plaintext',
                       'nexthtml': next_html,
                       'theid': simulationid}
            if zipurl:
                context['zipurl'] = zipurl

        except ObjectDoesNotExist:
            template_name = 'noos_viewer/errpage.html'
            themessage = "{}, no object with id : {}".format(name_and_method, simulationid)
            logger.error(themessage)
            context = {'err_mesg': themessage}

    elif request.method == 'POST':
        pass
    else:
        pass

    logger.info("{}, end".format(name_and_method))
    return render(request, template_name, context)


def view_simulationdemand(request, simulationid):
    """
    A method to view the data values of a simulation demand
    :param request:
    :param simulationid: The simulation demand which the user wants to view
    :return:
    """
    name_and_method = "view_simulationdemand"
    logger.info("{}, start".format(name_and_method))
    if request.user is None or not request.user.is_authenticated:
        return redirect('home')

    demand_helper = SimulationDemandHelper()
    # logger.debug("{}, looking for object with id : {}".format(name_and_method,simulationid))
    try:
        simulation_demand = SimulationDemand.active_objects.get(pk=simulationid)
        # logger.debug("{}, Found_simulationdemand, with id : {}".format(name_and_method,simulation_demand.id))
        # logger.debug("{}, Preparing the dictionary".format(name_and_method))
        simulation_demand_dict = demand_helper.extract_simulation_dict(simulation_demand)
        # logger.info("{}, simulation_demand : {}".format(name_and_method, simulation_demand_dict))
        the_form = SimulationDemandForm(simulation_demand_dict)
        zip_url = None
        if simulation_demand_dict[MemorySimulationDemand.STATUS] == StatusConst.OK:
            zip_url = ServiceSimulationDemandHelper.get_zip_url(simulation_demand_dict[MemorySimulationDemand.ID])

        # local_title = simulation_demand_dict[SimulationDemandHelper.TITLE]
        # logger.debug("{}, title is , {}".format(name_and_method, local_title))
        # logger.debug("{}, zip_url is , {}".format(name_and_method, zip_url))
        sim_status = simulation_demand_dict[MemorySimulationDemand.STATUS]
        # logger.debug("{}, sim_status is , {}".format(name_and_method, sim_status))
        template_name = 'noos_viewer/simulationdemand.html'
        response_context = {'form': the_form,
                            'theid': simulationid,
                            "sim_status": sim_status,
                            'user_msg': ''}
        if zip_url:
            response_context['zipurl'] = zip_url

    except ObjectDoesNotExist:
        themessage = "{}, no object with id : {}".format(name_and_method, simulationid)
        logger.error(themessage)
        template_name = "noos_viewer/errpage.html"
        response_context = {'err_mesg': themessage}

    logger.info("{}, end".format(name_and_method))
    return render(request, template_name, response_context)


def signup(request):
    """
    A method to add another user to the known users
    :param request:
    :return:
    """
    name_and_method = "views.signup"
    logger.info("{}, start".format(name_and_method))
    # logger.debug("signup")
    if request.method == 'POST':
        # logger.debug("signup, method POST")
        form = SignUpForm(request.POST)
        if form.is_valid():
            # logger.debug("signup, method POST, form is valid")
            # logger.debug("signup, before form.save()")
            user = form.save()
            appusers = Group.objects.get(name=APPUSERS_GROUP)
            user.is_active = False
            user.groups.add(appusers)
            # logger.debug("signup, saving user")
            user.save(force_update=True)
            user.refresh_from_db()  # load the profile instance created by the signal
            theprofile = UserProfile.objects.get(user=user)

            motivationtxt = form.cleaned_data.get('motivation')
            # logger.debug("signup, setting motivation to {}".format(motivationtxt))
            theprofile.motivation = motivationtxt
            # logger.debug("signup, setting organization")
            organizationtxt = form.cleaned_data.get('organization')
            # logger.debug("signup, setting organization to {}".format(organizationtxt))
            theprofile.organization = organizationtxt
            # logger.debug("In signup, saving user with profile updated")
            # user.save()
            # logger.debug("signup, saving profile element in user ???")
            theprofile.save(force_update=True)

            the_user = User.objects.get(username=user.username)

            subject = '[NOOS-Drift]  New registration request'

            message = render_to_string('noos_viewer/account_activation_email.html', {
                'profile': theprofile,
                'user': the_user,
                # 'domain': 'localhost:8000',
                'domain': 'odnature.naturalsciences.be',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            message_user = render_to_string('noos_viewer/account_signup_accepted.html', {
                'user': the_user
            })

            send_mail(subject, message, ODIN_MAILANSWERACCOUNT, [MAIL_ADMIN_NOOSDRIFT])
            send_mail(subject, message_user, ODIN_MAILANSWERACCOUNT, [the_user.email])

            return redirect('noos_viewer:account_activation_sent')
        else:
            logger.error("{}, form is not valid ????".format(name_and_method))
            for afield in form.fields:
                logger.error("{}, afield : {}".format(name_and_method, afield))

            logger.error("{}, errors : {}".format(name_and_method, form.errors))
    else:
        form = SignUpForm()

    template_name = 'noos_viewer/signup.html'
    logger.info("{}, end".format(name_and_method))
    return render(request, template_name, {'form': form})


def contact_form(request):
    """
    Send a mail using form info
    :param request:
    :return:
    """
    name_and_method = "contact_form"
    logger.info("{}, start".format(name_and_method))
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            logger.info("{}, the message : {}".format(name_and_method, message))
            mail_message = render_to_string('noos_viewer/email.html', {
                'name': name,
                "subject": subject,
                'themessage': message
            })
            try:
                send_mail(subject, mail_message, from_email, [MAIL_ADMIN_NOOSDRIFT])
                logger.info("{}, (redirection) end".format(name_and_method))
                return redirect('noos_viewer:message_sent')

            except BadHeaderError:
                logger.error("{}, error end".format(name_and_method))
                return HttpResponse('Invalid header found.')

    template_name = 'noos_viewer/contact_form.html'
    logger.info("{}, to the form end".format(name_and_method))
    return render(request, template_name, {'form': form})


def account_activation_sent(request):
    """
    A method to confirm activation has been sent
    :param request:
    :return:
    """
    template_name = 'noos_viewer/account_activation_sent.html'
    return render(request, template_name)


def message_sent(request):
    """
    A method to confirm activation has been sent
    :param request:
    :return:
    """
    template_name = 'noos_viewer/message_sent.html'
    return render(request, template_name)


def activate(request, uidb64, token):
    """
    A method to activate a user profile
    :param request:
    :param uidb64:
    :param token:
    :return:
    """
    logger.info("activate, start")
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        # logger.debug("In activate, getting back user")
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # logger.debug("activate, we have a user and token is ok")
        user.is_active = True
        theprofile = UserProfile.objects.get(user=user)
        theprofile.email_confirmed = True
        # logger.debug("activate, saving user")
        user.save(force_update=True)
        # logger.debug("activate, user, saved")
        # logger.debug("activate, saving profile")
        theprofile.save(force_update=True)
        # logger.debug("activate, profile, saved")

        subject = '[NOOS-Drift] Your registration request'

        message = render_to_string('noos_viewer/account_activation_done.html', {
            'user': theprofile.user,
            'domain': 'odnature.naturalsciences.be',
        })

        message_admin = render_to_string('noos_viewer/account_activation_admin_done.html', {
            'user': theprofile.user
        })

        # send_mail(subject, message, user.email, [])
        send_mail(subject, message, ODIN_MAILANSWERACCOUNT, [theprofile.user.email])

        send_mail(subject, message_admin, ODIN_MAILANSWERACCOUNT, [MAIL_ADMIN_NOOSDRIFT])

        # login(request, user)
        # logger.debug("activate, user ok, we have logged-in, redirecting")
        return redirect('home')
    else:
        # logger.debug("activate, no user or problem with token ???")
        template_name = 'noos_viewer/account_activation_invalid.html'
        return render(request, template_name)
