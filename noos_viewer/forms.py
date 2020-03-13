from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError as CValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm, password_validation
from django.contrib.auth.models import User
import logging
from noos_services.ns_const import DRIFTER_NAME_ALL_CHOICES, MemorySimulationDemand, OtherConst
from noos_services.validationhelper import ValidationHelper as VHelper

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    name = forms.CharField(required=True,
                           label='Name',
                           max_length=100,
                           widget=forms.TextInput(attrs={'placeholder': 'Please type your name here',
                                                         'autocorrect': 'off',
                                                         'spellcheck': 'false',
                                                         'class': 'form-control'}))
    from_email = forms.EmailField(required=True,
                                  label='E-mail',
                                  max_length=100,
                                  widget=forms.TextInput(attrs={'placeholder': 'Please provide a valid email address',
                                                                'autocorrect': 'off',
                                                                'spellcheck': 'false',
                                                                'class': 'form-control'}))
    subject = forms.CharField(required=True,
                              label='Subject',
                              max_length=100,
                              widget=forms.TextInput(attrs={'placeholder': 'Please provide a subject',
                                                            'autocorrect': 'off',
                                                            'spellcheck': 'false',
                                                            'class': 'form-control'}))
    message = forms.CharField(required=True,
                              label='Message',
                              widget=forms.Textarea(attrs={"rows": 3,
                                                           'class': 'form-control',
                                                           'autocorrect': 'off',
                                                           'spellcheck': 'true',
                                                           'placeholder': 'Please type your message here'}))
    captcha = CaptchaField()


class SignUpForm(UserCreationForm):
    username_constraints = 'No spaces.<br>150 characters or fewer.<br>Letters, digits and @/./+/-/_ only.'
    username = forms.CharField(label='Username',
                               max_length=150,
                               help_text=username_constraints,
                               widget=forms.TextInput(attrs={'placeholder': 'Please provide a username',
                                                             'autocorrect': 'off',
                                                             'spellcheck': 'false',
                                                             'class': 'form-control'}))
    email = forms.EmailField(label='E-mail',
                             max_length=100,
                             widget=forms.TextInput(attrs={'placeholder': 'Please provide a valid email address',
                                                           'autocorrect': 'off',
                                                           'spellcheck': 'false',
                                                           'class': 'form-control'}))
    first_name = forms.CharField(label='First name',
                                 max_length=100,
                                 widget=forms.TextInput(attrs={'placeholder': 'Please provide your first name',
                                                               'autocorrect': 'off',
                                                               'spellcheck': 'false',
                                                               'class': 'form-control'}))
    last_name = forms.CharField(label='Last name',
                                max_length=100,
                                widget=forms.TextInput(attrs={'placeholder': 'Please provide your last name',
                                                              'autocorrect': 'off',
                                                              'spellcheck': 'false',
                                                              'class': 'form-control'}))
    organization = forms.CharField(label='Organization',
                                   max_length=100,
                                   widget=forms.TextInput(attrs={
                                       'placeholder': 'Please provide the organization name you belongs to',
                                       'autocorrect': 'off',
                                       'spellcheck': 'false',
                                       'class': 'form-control'}))
    motivation = forms.CharField(label='Motivation',
                                 widget=forms.Textarea(attrs={"rows": 3,
                                                              'placeholder': 'Why do you need an account?',
                                                              'autocorrect': 'off',
                                                              'spellcheck': 'true',
                                                              'class': 'form-control'}))
    password1 = forms.CharField(label='Password',
                                strip=False,
                                widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
                                help_text=password_validation.password_validators_help_text_html())
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'organization', 'motivation', 'password1',
                  'password2',)


class SimulationDemandForm(forms.Form, MemorySimulationDemand):
    # Simulation description
    id = forms.IntegerField(label='Id',
                            required=False,
                            widget=forms.NumberInput(attrs={'disabled': 'true',
                                                            'class': 'form-control'}))
    created_time = forms.CharField(label='Created Time',
                                   required=False,
                                   widget=forms.TextInput(attrs={'disabled': 'true',
                                                                 'placeholder': 'YYYY-MM-DDTHH:MM:SSZ',
                                                                 'class': 'form-control'}))
    title = forms.CharField(label='Title',
                            max_length=100,
                            widget=forms.TextInput(attrs={
                                'placeholder': 'Please provide a title to identify your simulation',
                                'class': 'form-control'}))

    SIMULATION_TYPE_CHOICES = (('', ''), (OtherConst.FORWARD, "Forward"), (OtherConst.BACKWARD, "Backward"),)

    simulation_type = forms.ChoiceField(label="Type",
                                        choices=SIMULATION_TYPE_CHOICES,
                                        initial="",
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    summary = forms.CharField(label='Summary',
                              widget=forms.Textarea(attrs={
                                  'placeholder': 'Please provide a summary to identify your simulation',
                                  "rows": 3,
                                  'class': 'form-control'}))
    status = forms.CharField(label='Status',
                             max_length=15,
                             required=False,
                             widget=forms.TextInput(attrs={'disabled': 'true',
                                                           'class': 'form-control'}))
    tags = forms.CharField(label="Tags",
                           max_length=200,
                           widget=forms.TextInput(attrs={'data-role': 'tagsinput',
                                                         'class': 'form-control'}))
    simulation_start_time = forms.CharField(label='Start Time',
                                            widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DDTHH:MM:SSZ',
                                                                          'class': 'form-control'}))
    simulation_end_time = forms.CharField(label='End Time',
                                          widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DDTHH:MM:SSZ',
                                                                        'class': 'form-control'}))
    protected = forms.BooleanField(label='Protected',
                                   initial=False,
                                   required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                                     'style': 'margin: 0;'
                                                                              'margin-top: 0px;'
                                                                              'margin-top: 0.75rem;'}))

    # Drifter part
    DRIFTER_TYPE_CHOICES = (('', ''), ("oil", "Oil"), ("object", "Object"),)
    drifter_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}),
                                     choices=DRIFTER_TYPE_CHOICES,
                                     label="Drifter Type", initial="")

    drifter_name = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}),
                                     choices=DRIFTER_NAME_ALL_CHOICES,
                                     label="Drifter Name", initial="")

    total_mass = forms.IntegerField(label='Total Mass (kg)', required=False, min_value=0, max_value=100000000,
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))

    # Initial Condition part
    GEOMETRY_CHOICES = (('', ''), (OtherConst.POINT, OtherConst.POINT), (OtherConst.POLYLINE, OtherConst.POLYLINE),)
    geometry = forms.ChoiceField(label="Geometry",
                                 choices=GEOMETRY_CHOICES,
                                 initial="",
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    lat = forms.CharField(label='Latitude (Dec Deg)',
                          max_length=100,
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    lon = forms.CharField(label='Longitude (Dec Deg)',
                          max_length=100,
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    radius = forms.IntegerField(label='Radius (m)',
                                max_value=20000,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
    number = forms.IntegerField(label='Number of particles',
                                initial=1000,
                                max_value=5000,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
    release_times = forms.CharField(label='Release Times',
                                    max_length=100,
                                    widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DDTHH:MM:SSZ',
                                                                  'class': 'form-control'}))
    cone = forms.BooleanField(label='Cone',
                              initial=False,
                              required=False)

    # Model set up
    TWODTHREED_CHOICES = (
        (OtherConst.TWOD, OtherConst.TWOD),
        (OtherConst.THREED, OtherConst.THREED),
    )
    twoDthreeD = forms.ChoiceField(label="2D/3D",
                                   choices=TWODTHREED_CHOICES,
                                   initial=OtherConst.THREED,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    beaching = forms.BooleanField(label='Beaching',
                                  required=False,
                                  initial=False,
                                  widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                                    'style': 'margin: 0;'
                                                                             'margin-top: 0px;'
                                                                             'margin-top: 0.75rem;'}))
    buoyancy = forms.BooleanField(label='Buoyancy',
                                  required=False,
                                  initial=False,
                                  widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                                    'style': 'margin: 0; '
                                                                             'margin-top: 0px;'
                                                                             'margin-top: 0.75rem;'}))

    dissolution = forms.BooleanField(label='Dissolution',
                                     required=False,
                                     initial=False,
                                     widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                                       'style': 'margin: 0;'
                                                                                'margin-top: 0px;'
                                                                                'margin-top: 0.75rem;'}))
    evaporation = forms.BooleanField(label='Evaporation',
                                     required=False,
                                     initial=False,
                                     widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                                       'style': 'margin: 0;'
                                                                                'margin-top: 0px;'
                                                                                'margin-top: 0.75rem;'}))
    horizontal_spreading = forms.BooleanField(label='Horizontal spreading',
                                              required=False,
                                              initial=False,
                                              widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                                                'style': 'margin: 0;'
                                                                                         'margin-top: 0px;'
                                                                                         'margin-top: 0.75rem;'}))
    natural_vertical_dispersion = forms.BooleanField(label='Natural vertical dispersion',
                                                     required=False,
                                                     initial=False,
                                                     widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                                                       'style': 'margin: 0;'
                                                                                                'margin-top: 0px;'
                                                                                                'margin-top: 1.5rem;'}))
    sedimentation = forms.BooleanField(label='Sedimentation',
                                       required=False,
                                       initial=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                                         'style': 'margin: 0;'
                                                                                  'margin-top: 0px;'
                                                                                  'margin-top: 0.75rem;'}))

    def clean_simulation_start_time(self):
        name_and_method = "SimulationDemandForm.clean_simulation_start_time"
        logger.info("{}, start".format(name_and_method))
        data = self.cleaned_data[self.SIMULATION_START_TIME]
        try:
            VHelper.validating_simulation_start_time(data)
        except CValidationError as cv_err:
            logger.error("{}, {}".format(name_and_method, cv_err.message))
            raise forms.ValidationError(cv_err.message)
        except ValueError as err:
            raise err

        logger.info("{}, end".format(name_and_method))
        return data

    def clean_twoDthreeD(self):
        name_and_method = "SimulationDemandForm.clean_twoDthreeD"
        logger.info("{}, start".format(name_and_method))
        data = self.cleaned_data[self.FORM_TWODTHREED]

        if self.cleaned_data[self.DRIFTER_TYPE] == OtherConst.OBJECT:
            logger.info("{}, end".format(name_and_method))
            return OtherConst.TWOD

        logger.info("{}, end".format(name_and_method))
        return data

    def clean_simulation_end_time(self):
        name_and_method = "SimulationDemandForm.clean_simulation_end_time"
        logger.info("{}, start".format(name_and_method))
        data = self.cleaned_data[self.SIMULATION_END_TIME]
        try:
            VHelper.validating_simulation_end_time(data)
        except CValidationError as cv_err:
            logger.error("{}, {}".format(name_and_method, cv_err.message))
            raise forms.ValidationError(cv_err.message)
        except ValueError as err:
            raise err

        logger.info("{}, end".format(name_and_method))
        return data

    def clean_lat(self):
        name_and_method = "SimulationDemandForm.clean_lat"
        logger.info("{}, start".format(name_and_method))
        data = self.cleaned_data[self.LAT]
        # logger.info("{}, clean_data : {}".format(name_and_method, data))
        data_els = data.split(",")
        float_list = []
        for a_str_float in data_els:
            try:
                a_float = float(a_str_float.strip())
                float_list.append(a_float)
            except ValueError:
                logger.error("{}, Error in lat : {} is not a float".format(name_and_method, a_str_float))

        try:
            logger.info("{}, call_validator_helper".format(name_and_method))
            VHelper.validating_float_coord(lat_or_lon=self.LAT, coordinate_values=float_list)
        except CValidationError as cv_err:
            raise forms.ValidationError(cv_err.message)

        logger.info("{}, end".format(name_and_method))
        return float_list

    def clean_lon(self):
        name_and_method = "SimulationDemandForm.clean_lon"
        data = self.cleaned_data[self.LON]
        logger.info("{}, start".format(name_and_method))
        data_els = data.split(",")
        float_list = []
        for a_str_float in data_els:
            try:
                a_float = float(a_str_float.strip())
                float_list.append(a_float)
            except ValueError:
                logger.error("{}, Error in lat : {} is not a float".format(name_and_method, a_str_float))

        try:
            logger.info("{}, call_validator_helper".format(name_and_method))
            VHelper.validating_float_coord(lat_or_lon=self.LON, coordinate_values=float_list)
        except CValidationError as cv_err:
            raise forms.ValidationError(cv_err.message)
        logger.info("{}, end".format(name_and_method))
        return float_list

    def clean_total_mass(self):
        name_and_method = "SimulationDemandForm.clean_total_mass"
        logger.info("{}, start".format(name_and_method))
        data = self.cleaned_data[self.TOTAL_MASS]
        drifter_type = self.cleaned_data[self.DRIFTER_TYPE]

        new_data = None
        try:
            logger.info("{}, call_validator_helper".format(name_and_method))
            new_data = VHelper.validating_total_mass(drifter_type=drifter_type, data=data)
        except CValidationError as cv_err:
            raise forms.ValidationError(cv_err.message)
        logger.info("{}, end".format(name_and_method))
        return new_data

    def clean_evaporation(self):
        name_and_method = "SimulationDemandForm.clean_evaporation"
        logger.info("{}, start".format(name_and_method))
        data = self.cleaned_data[self.EVAPORATION]

        if self.cleaned_data[self.DRIFTER_TYPE] == OtherConst.OBJECT:
            return False
        logger.info("{}, end".format(name_and_method))
        return data

    def clean_horizontal_spreading(self):
        name_and_method = "SimulationDemandForm.clean_horizontal_spreading"
        logger.info("{}, start".format(name_and_method))
        data = self.cleaned_data[self.HORIZONTAL_SPREADING]

        if self.cleaned_data[self.DRIFTER_TYPE] == OtherConst.OBJECT:
            return False
        logger.info("{}, end".format(name_and_method))
        return data

    def clean_sedimentation(self):
        data = self.cleaned_data[self.SEDIMENTATION]
        name_and_method = "SimulationDemandForm.clean_sedimentation"
        logger.info("{}, start".format(name_and_method))
        if self.cleaned_data[self.DRIFTER_TYPE] == OtherConst.OBJECT:
            return False
        logger.info("{}, end".format(name_and_method))
        return data

    def clean_dissolution(self):
        data = self.cleaned_data[self.DISSOLUTION]
        name_and_method = "SimulationDemandForm.clean_dissolution"
        logger.info("{}, start".format(name_and_method))
        if self.cleaned_data[self.DRIFTER_TYPE] == OtherConst.OBJECT:
            return False
        logger.info("{}, end".format(name_and_method))
        return data

    def clean_number(self):
        data = self.cleaned_data[self.NUMBER]
        name_and_method = "SimulationDemandForm.clean_number"
        logger.info("{}, start".format(name_and_method))
        drifter_type = self.cleaned_data[self.DRIFTER_TYPE]

        try:
            VHelper.validating_number(drifter_type=drifter_type, data=data)
        except CValidationError as cv_err:
            raise forms.ValidationError(cv_err.message)
        logger.info("{}, end".format(name_and_method))
        return data

    def clean_radius(self):
        data = self.cleaned_data[self.RADIUS]
        name_and_method = "SimulationDemandForm.clean_radius"
        logger.info("{}, start".format(name_and_method))
        try:
            VHelper.validating_radius(data=data)
        except CValidationError as cv_err:
            raise forms.ValidationError(cv_err.message)
        logger.info("{}, end".format(name_and_method))
        return data

    def clean_release_times(self):
        name_and_method = "SimulationDemandForm.clean_release_times"
        logger.info("{}, start".format(name_and_method))
        data = self.cleaned_data[self.RELEASE_TIMES]
        clean_release_times = ""
        if data:
            try:
                clean_release_times = VHelper.validating_release_times(data)
            except CValidationError as cv_err:
                raise forms.ValidationError(cv_err.message)

        logger.info("{}, end".format(name_and_method))
        return clean_release_times

    def clean(self):
        cleaned_data = super().clean()
        name_and_method = "SimulationDemandForm.clean"
        logger.info("{}, start".format(name_and_method))
        logger.info("{}, validating times".format(name_and_method))

        time_fields_list = [self.RELEASE_TIMES, self.SIMULATION_START_TIME,
                            self.SIMULATION_END_TIME, self.SIMULATION_TYPE]

        error_in_time_fields = False
        for a_time_field in time_fields_list:
            if a_time_field in self.errors.keys():
                error_in_time_fields = True

        if error_in_time_fields is False:
            txt_release_times = cleaned_data[self.RELEASE_TIMES]

            txt_start_time = cleaned_data[self.SIMULATION_START_TIME]

            txt_end_time = cleaned_data[self.SIMULATION_END_TIME]

            simulation_type = cleaned_data[self.SIMULATION_TYPE]
            release_times = None
            start_time = None
            end_time = None
            try:
                release_times = VHelper.validating_release_times_datetime(txt_release_times)
            except CValidationError as cv_err:
                self.add_error("release_times", forms.ValidationError(message=cv_err.message))

            try:
                start_time = VHelper.validating_simulation_time_data_time(txt_start_time)
            except CValidationError as cv_err:
                self.add_error("start_time", forms.ValidationError(message=cv_err.message))

            try:
                end_time = VHelper.validating_simulation_time_data_time(txt_end_time)
            except CValidationError as cv_err:
                self.add_error("end_time", forms.ValidationError(message=cv_err.message))

            try:
                VHelper.validating_release_times_coherence(release_times=release_times, start_time=start_time,
                                                           end_time=end_time, simulation_type=simulation_type)
            except CValidationError as cv_err:
                self.add_error("release_times", forms.ValidationError(message=cv_err.message))

        else:
            logger.error("{}, There was an error in time related fields".format(name_and_method))

        geom_fields_list = [self.LAT, self.LON, self.GEOMETRY]

        error_in_geom_fields = False
        for a_geom_field in geom_fields_list:
            if a_geom_field in self.errors.keys():
                error_in_geom_fields = True

        if error_in_geom_fields is False:
            # logger.info("{}, validating lat/lon".format(name_and_method))
            lats = cleaned_data[self.LAT]
            lons = cleaned_data[self.LON]
            try:
                VHelper.validating_coordinates_consistency(cleaned_data[self.GEOMETRY], lats, lons)
            except CValidationError as cv_err:
                self.add_error(self.LAT, forms.ValidationError(message=cv_err.message))
        else:
            logger.error("{}, There was an error in the geom fields".format(name_and_method))

        logger.info("{}, validating drifter_type".format(name_and_method))

        drifter_fields_list = [self.DRIFTER_TYPE, self.DRIFTER_NAME]
        error_in_drifter_fields = False
        for a_drifter_field in drifter_fields_list:
            if a_drifter_field in self.errors.keys():
                logger.error("{}, Error for field {}".format(name_and_method, self.errors[self.DRIFTER_NAME]))
                error_in_drifter_fields = True

        if error_in_drifter_fields is False:

            drifter_type = cleaned_data[self.DRIFTER_TYPE]
            drifter_name = cleaned_data[self.DRIFTER_NAME]
            try:
                VHelper.validating_drifter_name(drifter_type, drifter_name)
            except CValidationError as cv_err:
                self.add_error(self.DRIFTER_TYPE, forms.ValidationError(message=cv_err.message))
        else:
            logger.error("{}, There was an error in the drifter fields".format(name_and_method))

        logger.info("{}, end".format(name_and_method))

        return cleaned_data


class SimulationDemandEditedForm(forms.Form, MemorySimulationDemand):
    id = forms.IntegerField(label='Id',
                            required=False,
                            widget=forms.NumberInput(attrs={'disabled': 'true',
                                                            'class': 'form-control'}))
    # Simulation description
    title = forms.CharField(label='Title',
                            max_length=100,
                            widget=forms.TextInput(attrs={
                                'placeholder': 'Please provide a title to identify your simulation',
                                'class': 'form-control'}))

    summary = forms.CharField(label='Summary',
                              widget=forms.Textarea(attrs={
                                  'placeholder': 'Please provide a summary to identify your simulation',
                                  "rows": 3,
                                  'class': 'form-control'}))

    tags = forms.CharField(label="Tags",
                           max_length=200,
                           widget=forms.TextInput(attrs={'data-role': 'tagsinput',
                                                         'class': 'form-control'}))

    protected = forms.BooleanField(label='Protected',
                                   initial=False,
                                   required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                                                     'style': 'margin: 0;'
                                                                              'margin-top: 0px;'
                                                                              'margin-top: 0.75rem;'}))

    def clean(self):
        cleaned_data = super().clean()
        name_and_method = "SimulationDemandEditedForm.clean"
        logger.info("{}, start".format(name_and_method))
        logger.info("{}, end".format(name_and_method))
        return cleaned_data
