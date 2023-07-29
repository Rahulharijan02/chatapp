


import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

from .models import Room
from chat.models import Message

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def save_message(self, message, sender_id, receiver_id):
        try:
            sender_user = User.objects.get(id=sender_id)
            receiver_user = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            # Handle the case when the sender or receiver user does not exist
            self.send(text_data=json.dumps({
                'message': 'Invalid sender or receiver',
                'sender_name': 'Server',
            }))
            return

        new_message = Message.objects.create(
            message=message, sender_user=sender_user, receiver_user=receiver_user
        )
        new_message.save()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']
        sender_name = text_data_json['sender_name']
        room_name = self.room_name  # Get the room_name from URL parameters

        # Retrieve the room based on the room_name
        try:
            room = Room.objects.get(room_name=room_name)
        except Room.DoesNotExist:
            # Handle the case when the room does not exist
            self.send(text_data=json.dumps({
                'message': 'Room does not exist',
                'sender_name': 'Server',
            }))
            return

        # Determine the receiver's ID based on the sender's ID and room
        if room.sender_user.id == sender_id:
            receiver_id = room.receiver_user.id
        else:
            receiver_id = room.sender_user.id

        # Save the message in the database
        self.save_message(message, sender_id, receiver_id)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'sender_name': sender_name
            }
        )

    def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']  # Update this line to use 'sender_id' instead of 'sender'
        receiver_id = event['receiver_id']
        sender_name = event['sender_name']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,  # Update this line to use 'sender_id' instead of 'sender'
            'receiver_id': receiver_id,
            'sender_name': sender_name,
        }))
