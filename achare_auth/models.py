from django.db import models
from django.utils import timezone
import string
import random


class FlowToken(models.Model):
    code = models.CharField(max_length=10, unique=True, editable=False)
    mobile_number = models.CharField(max_length=11)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.code} - {self.mobile_number} {self.timestamp} "

    def save(self, *args, **kwargs):
        if not self.pk:
            # Generate a unique code for new instances
            self.code = self._generate_code()
        super().save(*args, **kwargs)

    def _generate_code(self):
        # Generate a random code consisting of uppercase letters and digits
        code_length = 6
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(chars) for _ in range(code_length))
        return code
