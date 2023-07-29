from django.db import models
from django.contrib.auth.models import User, AnonymousUser

class Message(models.Model):
    sender_user = models.ForeignKey(User, related_name='sender', on_delete=models.SET(AnonymousUser))
    receiver_user = models.ForeignKey(User, related_name='receiver', on_delete=models.SET(AnonymousUser))
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Room(models.Model):
    sender_user = models.ForeignKey(User, related_name='room_sender', on_delete=models.SET(AnonymousUser))
    receiver_user = models.ForeignKey(User, related_name='room_receiver', on_delete=models.SET(AnonymousUser))
    room_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"{self.room_name}"

    def get_other_user(self, user_id):
        """
        Returns the other user in the room based on the given user_id.
        """
        if self.sender_user.id == user_id:
            return self.receiver_user
        elif self.receiver_user.id == user_id:
            return self.sender_user
        else:
            return None
