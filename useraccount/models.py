from django.core import validators
from django.db import models
from django.db.models import CASCADE
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# Create your models here
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    mobile_number = models.CharField(_('mobile number'), null=True, blank=True, max_length=11)
    description = models.CharField(_("description"), max_length=255, blank=True)
    location = models.CharField(_("location"), max_length=255, blank=True)
    last_seen = models.DateTimeField(_("last seen"), default=timezone.now)
    is_banned = models.BooleanField(_("banned"), default=False)

    is_register_auth_completed = models.BooleanField(_("Register Authenticated is complete "), default=False)
    is_register_data_completed = models.BooleanField(_("Register Data is complete "), default=False)

    is_vip = models.BooleanField(_("vip"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _("profiles")

    def __str__(self):
        return f" name: {self.user.first_name} , family: {self.user.last_name} , mail : {self.user.email}, joined : {self.date_joined} "

    def __unicode__(self):
        return self.user.username
