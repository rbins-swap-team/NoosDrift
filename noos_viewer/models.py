from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    """
    UserProfile is a little more information to classic auth.User data.
    So there is a OneToOne link between a UserProfile and auth.User.

    This model is meant for app users.
    The link is
    UserProfile 1 -> 1 auth.User
    but there can be auth.User instances without UserProfile
    auth.User 1 -> 0..1 UserProfile
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    motivation = models.TextField(default='')
    organisation = models.TextField(default='')
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return '{}: {} {} {} {}'.format(self.pk, self.user.username, self.user.email, self.organisation,
                                        self.motivation)

    @receiver(post_save, sender=User)
    def update_user_profile(sender, instance, created, **kwargs):
        # logger.debug("update_user_profile, start")
        # logger.debug("update_user_profile, type of 'instance': {}".format(type(instance)))
        # How come, instance here is USER ????
        if created:
            # logger.debug("update_user_profile, creating UserProfile")
            theprofile = UserProfile.objects.create(user=instance)
            theprofile.save()
            # logger.debug("update_user_profile, UserProfile, created")
