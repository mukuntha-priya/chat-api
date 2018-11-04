from django.db import models
import datetime


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class DirectMessage(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_2')

    def __str__(self):
        return self.user1.name + self.user2.name


class Group(models.Model):
    name = models.CharField(max_length=20)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class Message(models.Model):
    content = models.CharField(max_length=250)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    direct_message = models.ForeignKey(DirectMessage, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
