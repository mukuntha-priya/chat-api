from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('all-users', views.all_users, name='all_users'),
    path('users', views.get_users, name='get_users'),
    path('groups/<int:group_id>', views.group, name='group'),
    path('groups', views.create_group, name='create_group'),
    path('groups/<int:group_id>/users', views.add_users, name='add_users'),
    path('messages/dm', views.get_direct_message_list, name='get_direct_message_list'),
    path('messages/groups', views.get_group_list, name='get_group_list'),
    path('messages/dm/<int:dm_id>', views.get_direct_messages, name='get_direct_messages'),
    path('messages/group/<int:group_id>', views.get_group_messages, name='get_group_messages'),
    path('messages/add', views.add_message, name='add_message'),
]

