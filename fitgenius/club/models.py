from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Club(models.Model):
    name = models.CharField(max_length=255)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clubs')

    def __str__(self):
        return self.name
