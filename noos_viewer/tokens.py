from noos_viewer.models import UserProfile
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    # def _make_hash_value(self, profile, timestamp):
    def _make_hash_value(self, user, timestamp):
        profiles = UserProfile.objects.filter(user__pk=user.pk)
        return (
                # six.text_type(profile.user.pk) + six.text_type(timestamp) +
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(profiles[0].email_confirmed)
                # six.text_type(profile.email_confirmed)
        )
    # def _make_hash_value(self, user, timestamp):
    #     # Ensure results are consistent across DB backends
    #     login_timestamp = ''
    #     if user.last_login is None:
    #     else:
    #         user.last_login.replace(microsecond=0, tzinfo=None)
    #
    #     return (
    #         six.text_type(user.pk) + user.password +
    #         six.text_type(login_timestamp) + six.text_type(timestamp)
    #     )


account_activation_token = AccountActivationTokenGenerator()
