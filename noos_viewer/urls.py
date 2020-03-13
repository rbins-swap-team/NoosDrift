from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from noos_viewer import views as noos_viewer_views
from django.views.generic.base import TemplateView

app_name = 'noos_viewer'

urlpatterns = [
    path('contactform/', noos_viewer_views.contact_form, name='contactform'),
    path('message_sent/', noos_viewer_views.message_sent, name='message_sent'),

    path('signup/', noos_viewer_views.signup, name='signup'),
    # ask for empty form
    path('simulationdemands/archive/', noos_viewer_views.archive_simulations, name='archive_simulationdemands'),
    path('simulationdemands/makereportfile/', noos_viewer_views.make_report_file, name='makereportfile'),
    path('simulationdemands/', noos_viewer_views.simulation_demands, name='simulationdemands'),
    path('simulationdemand/new/', noos_viewer_views.new_simulationdemand, name='new_simulationdemand'),

    # update data for simulation using post data
    path('simulationdemand/update/', noos_viewer_views.update_simulation_demand, name='update_simulationdemand'),

    # prepare form with simulation data to be used as model
    path('simulationdemand/newfrommodel/<int:simulationid>/', noos_viewer_views.new_from_model_simulation_demand,
         name='newfrommodel_simulationdemand'),

    # create new simulation database object using post data
    path('simulationdemand/create/', noos_viewer_views.create_simulation_demand, name='create_simulationdemand'),

    # set protection
    path('simulationdemand/toggleprotection/<int:simulationid>/', noos_viewer_views.toggle_protection,
         name='protect_simulationdemand'),

    # prepare form to edit simulation database object
    path('simulationdemand/edit/<int:simulationid>/', noos_viewer_views.edit_simulationdemand,
         name='edit_simulationdemand'),

    # get back data of simulation object to be displayed
    # Just see the simulation
    path('simulationdemand/<int:simulationid>/', noos_viewer_views.view_simulationdemand, name='view_simulationdemand'),
    # get the analysis page
    path('simulationdemand/viewresults/<int:simulationid>/', noos_viewer_views.view_results_simulation_demand,
         name='viewresults_simulationdemand'),
    # Start viewing results with init (metadata)
    path('simulationdemand/viewresultsstart/<int:simulationid>/', noos_viewer_views.simulation_init,
         name='viewresults_start'),
    # Viewing a particular step in the results
    path('simulationdemand/elements/<int:simulationid>/<int:stepidx>/', noos_viewer_views.simulations_for_demand,
         name='view_simulationelements'),
    # Viewing a cloud of points
    path('simulationdemand/cloudofpoints/<int:simulationid>/<str:modelcouple>/<int:stepidx>/',
         noos_viewer_views.cloud_of_points_for_demand, name='view_simulation_cloudofpoints'),

    # accounts and passwords
    path('account_activation_sent/', noos_viewer_views.account_activation_sent, name='account_activation_sent'),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
            noos_viewer_views.activate, name='activate'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
