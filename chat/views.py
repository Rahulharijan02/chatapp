# from django.contrib.auth.mixins import LoginRequiredMixin 
# from django.contrib.auth.models import User
# from django.db.models import Q
# from django.shortcuts import render, redirect, get_object_or_404
# from django.utils.crypto import get_random_string 
# from django.views import View
# from chat.models import Room, Message
# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages




# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('rooms')  
            
#         else:
#             messages.error(request, 'Invalid credentials')
    
#     return render(request, 'chat/login.html')

# def register_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
        
#         # Check if the username is already taken
#         if User.objects.filter(username=username).exists():
#             messages.error(request, 'Username is already taken')
#             return redirect('register')
        
#         # Create the new user
#         user = User.objects.create_user(username=username, password=password)
#         login(request, user)
#         return redirect('login')  # Replace 'index' with your desired redirect URL

#     return render(request, 'chat/register.html')

# def logout_view(request):
#     logout(request)
#     return redirect('login') 


# class GetAllUsers(LoginRequiredMixin, View): 
#     def get( self, request):
# # to get the list of all users from the database
#         print(request.user)
#         users = User.objects.all()
#         return render(request, 'chat/all_users.html', {"users" : users})


#     def post(self, request):
#         sender = request.user.id
#         receiver = request.POST['users']
#         sender_user = User.objects.get(id=sender)
#         receiver_user = User.objects.get(id=receiver)
#         request.session['receiver_user'] = receiver
#         get_room = Room.objects.filter(Q(sender_user=sender_user,receiver_user=receiver_user)|Q(sender_user=receiver_user,receiver_user=sender_user))
#         if get_room:
#             room_name = get_room[0].room_name
#         else:
#             new_room = get_random_string(10)
#             while True:
#                 room_exits = Room.objects.filter(room_name=new_room)
#                 if room_exits:
#                     new_room = get_random_string(10)
#                 else:
#                     break
#             create_room = Room.objects.create(sender_user=sender_user,receiver_user=receiver_user,room_name=new_room)
#             create_room.save()
#             room_name = create_room.room_name
#         return redirect('room', room_name=room_name)

            

# class ChatRoom(LoginRequiredMixin, View):
#     queryset = Room.objects.all()

#     def get(self, request, room_name, *args, **kwargs):
#         room = get_object_or_404(Room, room_name=room_name)
#         sender = request.user.id
#         sender_name = request.user.username
#         if room.receiver_user.id == sender:
#             receiver = room.sender_user.id
#         else:
#             receiver = room.receiver_user.id

#         # get all the previous messages from the database
#         messages = Message.objects.filter(Q(sender_user=sender, receiver_user=receiver) |
#                                           Q(sender_user=receiver, receiver_user=sender)).order_by('timestamp')

#         return render(request, 'chat/room.html', {
#             'room_name': room_name,
#             'sender_id': sender,
#             'receiver_id': receiver,
#             'messages': messages,
#             'sender_name': sender_name
#         })



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

        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken')
            return redirect('register')

        # Create the new user
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('login')  # Replace 'index' with your desired redirect URL

    return render(request, 'chat/register.html')

def logout_view(request):
    logout(request)
    return redirect('login') 

class GetAllUsers(LoginRequiredMixin, View): 
    def get(self, request):
        # Get the list of all users from the database
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
        receiver = room.receiver_user if room.sender_user.id == sender_id else room.sender_user #C

        if receiver is None:
            # Handle the case when the user is not part of the room
            return redirect('rooms')  # Replace 'rooms' with the URL name for your list of chat users

        # get all the previous messages from the database
        messages = Message.objects.filter(Q(sender_user=sender_id, receiver_user=receiver.id) |
                                          Q(sender_user=receiver.id, receiver_user=sender_id)).order_by('timestamp')

        return render(request, 'chat/room.html', {  # Replace 'path/to/your/room.html' with the actual template path
            'room_name': room_name,
            'sender_id': sender_id,
            'receiver_id': receiver.id,
            'messages': messages,
            'sender_name': sender_name,
        })