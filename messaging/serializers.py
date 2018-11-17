from rest_framework import serializers

from messaging.models import User, DirectMessage, Group, Message, DirectMessageHistory, GroupHistory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name')


class DirectMessageSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)

    class Meta:
        model = DirectMessage
        fields = ('id', 'user1', 'user2')


class GroupSerializer(serializers.ModelSerializer):
    users = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'users')


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    direct_message = DirectMessageSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'content', 'created_at', 'sender', 'direct_message', 'group', 'thread_id')


class DirectMessageHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    direct_message = DirectMessageSerializer(read_only=True)
    unreadCount = serializers.SerializerMethodField()

    def get_unreadCount(self, obj):
        dm_id = obj.direct_message.id
        messages = Message.objects.filter(direct_message__id=dm_id)
        if len(messages) > 0:
            if obj.last_seen_message is not None:
                return len(Message.objects.filter(direct_message__id=dm_id, created_at__gt=obj.last_seen_message.created_at))
            else:
                return len(messages)
        else:
            return 0

    class Meta:
        model = DirectMessageHistory
        fields = ('user', 'direct_message', 'unreadCount')


class GroupHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    unreadCount = serializers.SerializerMethodField()

    def get_unreadCount(self, obj):
        group_id = obj.group.id
        messages = Message.objects.filter(group__id=group_id)
        if len(messages) > 0:
            if obj.last_seen_message is not None:
                return len(Message.objects.filter(group__id=group_id, created_at__gt=obj.last_seen_message.created_at))
            else:
                return len(messages)
        else:
            return 0

    class Meta:
        model = GroupHistory
        fields = ('user', 'group', 'unreadCount')
