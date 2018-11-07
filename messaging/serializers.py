from rest_framework import serializers

from messaging.models import User, DirectMessage, Group, Message


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
        fields = ('id', 'content', 'created_at', 'sender', 'direct_message', 'group')
