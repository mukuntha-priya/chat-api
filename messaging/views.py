from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.db.models import Q
import json
from .models import User, Message, Group, DirectMessage


# Create your views here.
def index(request):
    return HttpResponse("Hello World")


# http://localhost:8000/slack/all-users
def all_users(request):
    return HttpResponse(User.objects.all().values())


# http://localhost:8000/slack/users?pattern=x
def get_users(request):
    return HttpResponse(User.objects.filter(name__contains=request.GET["pattern"]).values())


# http://localhost:8000/slack/groups/{group_id}
def group(request, group_id):
    group = Group.objects.get(pk=group_id)
    return HttpResponse(group)


# http://localhost:8000/slack/groups ( POST: {"name": "xyz", "users": [1, 2]} )
@csrf_exempt
def create_group(request):
    data = json.loads(request.body.decode("utf-8"))
    group_name = data['name']
    user_ids = data['users']
    group = Group.objects.create(name=group_name)
    add_users_to_group(group, user_ids)
    return HttpResponse(group.values())


# http://localhost:8000/slack/groups/3/users ( POST: {"users": [1, 2]} )
@csrf_exempt
def add_users(request, group_id):
    data = json.loads(request.body.decode("utf-8"))
    user_ids = data['users']
    group = Group.objects.get(id=group_id)
    add_users_to_group(group, user_ids)
    return HttpResponse(group)


def add_users_to_group(group, user_ids):
    users = User.objects.filter(id__in=user_ids)
    for user in users:
        group.users.add(user)


# http://localhost:8000/slack/messages/dm?userId=3
def get_direct_message_list(request):
    user_id = request.GET["userId"]
    direct_messages = DirectMessage.objects.filter(Q(user1__id=user_id) | Q(user2__id=user_id))
    return HttpResponse(to_json(direct_messages))


# http://localhost:8000/slack/messages/groups?userId=3
def get_group_list(request):
    user_id = request.GET["userId"]
    groups = Group.objects.filter(users__id=user_id)
    return HttpResponse(to_json(groups))


# http://localhost:8000/slack/messages/dm/3
def get_direct_messages(request, dm_id):
    messages = Message.objects.filter(direct_message__id=dm_id)
    return HttpResponse(to_json(messages))


# http://localhost:8000/slack/messages/group/3
def get_group_messages(request, group_id):
    messages = Message.objects.filter(group__id=group_id)
    return HttpResponse(to_json(messages))


# http://localhost:8000/slack/messages/add
# (POST: { "userId": 1, "content": "Another one", "group_id": null, "direct_message_id": 1 })
@csrf_exempt
def add_message(request):
    data = json.loads(request.body.decode("utf-8"))
    sender = User.objects.get(id=data['userId'])
    content = data['content']
    if data['direct_message_id'] is not None:
        dm = DirectMessage.objects.get(id=data['direct_message_id'])
        message = Message(sender=sender, content=content, direct_message=dm)
    else:
        group = Group.objects.get(id=data['group_id'])
        message = Message(sender=sender, content=content, group=group)
    message.save()
    return HttpResponse(message)


def to_json(data):
    return serializers.serialize("json", data)
