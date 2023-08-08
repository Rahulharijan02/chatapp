



from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.views import View
from chat.models import Room, Message
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('rooms')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'chat/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken')
            return redirect('register')

  
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('login')  

    return render(request, 'chat/register.html')


def logout_view(request):
    logout(request)
    return redirect('login') 




class GetAllUsers(LoginRequiredMixin, View): 
    def get(self, request):
        users = User.objects.all()
        return render(request, 'chat/all_users.html', {"users": users})

    def post(self, request):
        sender = request.user.id
        receiver = request.POST['users']
        sender_user = User.objects.get(id=sender)
        receiver_user = User.objects.get(id=receiver)
        request.session['receiver_user'] = receiver
        get_room = Room.objects.filter(
            Q(sender_user=sender_user, receiver_user=receiver_user) | Q(sender_user=receiver_user, receiver_user=sender_user))
        if get_room:
            room_name = get_room[0].room_name
        else:
            new_room = get_random_string(10)
            while True:
                room_exists = Room.objects.filter(room_name=new_room).exists()
                if room_exists:
                    new_room = get_random_string(10)
                else:
                    break
            create_room = Room.objects.create(sender_user=sender_user, receiver_user=receiver_user, room_name=new_room)
            create_room.save()
            room_name = create_room.room_name
        return redirect('room', room_name=room_name)

    
class ChatRoom(LoginRequiredMixin, View):
    def get(self, request, room_name, *args, **kwargs):
        
        room = get_object_or_404(Room, room_name=room_name)
        sender_id = request.user.id
        sender_name = request.user.username
        receiver = room.receiver_user if room.sender_user.id == sender_id else room.sender_user 

        if receiver is None:
            return redirect('rooms')  

       
        messages = Message.objects.filter(Q(sender_user=sender_id, receiver_user=receiver.id) |
                                          Q(sender_user=receiver.id, receiver_user=sender_id)).order_by('timestamp')
        user = User.objects.get(pk=receiver.id)

        return render(request, 'chat/room.html', {  
            'room_name': room_name,
            'sender_id': sender_id,
            'receiver_id': receiver.id,
            'messages': messages,
            'sender_name': sender_name,
            'users' : user,
        })
    
   