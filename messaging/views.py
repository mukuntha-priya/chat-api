import os

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json

from messaging.serializers import UserSerializer, GroupSerializer, DirectMessageSerializer, MessageSerializer, \
    DirectMessageHistorySerializer, GroupHistorySerializer
from .models import User, Message, Group, DirectMessage, DirectMessageHistory, GroupHistory


# Create your views here.
def index(request):
    return HttpResponse("Hello World")


# http://localhost:8000/slack/all-users
def all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/users?pattern=x
def get_users(request):
    users = User.objects.filter(name__contains=request.GET["pattern"])
    serializer = UserSerializer(users, many=True)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/groups/{group_id}
def group(request, group_id):
    group = Group.objects.get(pk=group_id)
    serializer = GroupSerializer(group)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/groups ( POST: {"name": "xyz", "users": [1, 2]} )
@csrf_exempt
def create_group(request):
    data = json.loads(request.body.decode("utf-8"))
    group_name = data['name']
    user_ids = data['users']
    group = Group.objects.create(name=group_name)
    add_users_to_group(group, user_ids)
    serializer = GroupSerializer(group)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/groups/3/users ( POST: {"users": [1, 2]} )
@csrf_exempt
def add_users(request, group_id):
    data = json.loads(request.body.decode("utf-8"))
    user_ids = data['users']
    group = Group.objects.get(id=group_id)
    add_users_to_group(group, user_ids)
    serializer = GroupSerializer(group)
    return JsonResponse(serializer.data, safe=False)


def add_users_to_group(group, user_ids):
    users = User.objects.filter(id__in=user_ids)
    for user in users:
        group.users.add(user)


# http://localhost:8000/slack/messages/dm/user/3
def get_direct_message_list(request, user_id):
    direct_messages = DirectMessage.objects.filter(Q(user1__id=user_id) | Q(user2__id=user_id))
    direct_messages_history = []
    for dm in direct_messages:
            history = DirectMessageHistory.objects.filter(direct_message=dm, user__id=user_id)
            if len(history) > 0:
                direct_messages_history.append(history[0])
            else:
                user = User.objects.get(id=user_id)
                direct_messages_history.append(DirectMessageHistory(direct_message=dm, user=user, last_seen_message=None))
    serializer = DirectMessageHistorySerializer(direct_messages_history, many=True)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/messages/groups/user/3
def get_group_list(request, user_id):
    groups = Group.objects.filter(users__id=user_id)
    group_history = []
    for group in groups:
        history = GroupHistory.objects.filter(group=group, user__id=user_id)
        if len(history) > 0:
            group_history.append(history[0])
        else:
            user = User.objects.get(id=user_id)
            group_history.append(GroupHistory(group=group, user=user, last_seen_message=None))
    serializer = GroupHistorySerializer(group_history, many=True)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/messages/dm/3?user=x
def get_direct_messages(request, dm_id):
    last_seen_message = None
    messages = Message.objects.filter(direct_message__id=dm_id).order_by('-created_at')
    if len(messages) > 0:
        last_seen_message = messages[0]
    history = DirectMessageHistory.objects.filter(direct_message__id=dm_id, user__id=request.GET['user'])
    if len(history) > 0:
        history.update(last_seen_message=last_seen_message)
    else:
        user = User.objects.get(id=request.GET['user'])
        direct_message = DirectMessage.objects.get(id=dm_id)
        history = DirectMessageHistory(user=user, direct_message=direct_message, last_seen_message=last_seen_message)
        history.save()

    messages = Message.objects.filter(direct_message__id=dm_id).order_by('created_at')
    serializer = MessageSerializer(messages, many=True)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/messages/groups/3?user=x
def get_group_messages(request, group_id):
    last_seen_message = None
    messages = Message.objects.filter(group__id=group_id).order_by('-created_at')
    if len(messages) > 0:
        last_seen_message = messages[0]
    history = GroupHistory.objects.filter(group__id=group_id, user__id=request.GET['user'])
    if len(history) > 0:
        history.update(last_seen_message=last_seen_message)
    else:
        user = User.objects.get(id=request.GET['user'])
        group = Group.objects.get(id=group_id)
        history = GroupHistory(user=user, group=group, last_seen_message=last_seen_message)
        history.save()

    messages = Message.objects.filter(group__id=group_id).order_by('created_at')
    serializer = MessageSerializer(messages, many=True)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/messages/dm?user1=x&user2=y
def get_direct_message(request):
    user_id1 = request.GET['user1']
    user_id2 = request.GET['user2']
    direct_message = DirectMessage.objects.filter((Q(user1__id=user_id1) & Q(user2__id=user_id2)) |
                                                  (Q(user2__id=user_id1) & Q(user1__id=user_id2)))
    if len(direct_message) > 0:
        serializer = DirectMessageSerializer(direct_message[0])
        return JsonResponse(serializer.data, safe=False)
    dm = DirectMessage.objects.create(user1=User.objects.get(id=user_id1),
                                      user2=User.objects.get(id=user_id2))
    serializer = DirectMessageSerializer(dm)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/messages/add
# (POST: { "userId": 1, "content": "Another one", "groupId": null, "directMessageId": 1 })
@csrf_exempt
def add_message(request):
    data = json.loads(request.body.decode("utf-8"))
    message = create_message(data, None)
    serializer = MessageSerializer(message)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/messages/thread
# (POST: { "userId": 1, "content": "Another one", "groupId": null, "directMessageId": 1, "originalMessageId": 1 })
@csrf_exempt
def create_thread(request):
    data = json.loads(request.body.decode("utf-8"))
    thread_id = get_new_thread_id()
    message = create_message(data, thread_id)
    original_message_id = data['originalMessageId']
    Message.objects.filter(id=original_message_id).update(thread_id=thread_id)
    serializer = MessageSerializer(message)
    return JsonResponse(serializer.data, safe=False)


# http://localhost:8000/slack/messages/thread/add
# (POST: { "userId": 1, "content": "Another one", "groupId": null, "directMessageId": 1, "threadId": 1 })
@csrf_exempt
def add_to_thread(request):
    data = json.loads(request.body.decode("utf-8"))
    message = create_message(data, data['threadId'])
    serializer = MessageSerializer(message)
    return JsonResponse(serializer.data, safe=False)


def create_message(data, thread_id):
    user_id = data['userId']
    sender = User.objects.get(id=user_id)
    content = data['content']
    if data['directMessageId'] is not None:
        dm = DirectMessage.objects.get(id=data['directMessageId'])
        message = Message(sender=sender, content=content, direct_message=dm, thread_id=thread_id)
        message.save()
        DirectMessageHistory.objects.filter(direct_message=dm, user__id=user_id).update(last_seen_message=message)
    else:
        group = Group.objects.get(id=data['groupId'])
        message = Message(sender=sender, content=content, group=group, thread_id=thread_id)
        message.save()
        GroupHistory.objects.filter(group=group, user__id=user_id).update(last_seen_message=message)
    return message


def get_new_thread_id():
    message = Message.objects.latest('thread_id')
    if message is not None:
        if message.thread_id is not None:
            return message.thread_id + 1
    return 1


def get_image(request):
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'anonymous.jpg')
    image_data = open(file_path, "rb").read()
    return HttpResponse(image_data, content_type="image/jpeg")
