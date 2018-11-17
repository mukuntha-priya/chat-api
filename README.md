Steps to run app:
1. pip install -r requirements.txt
2. python manage.py runserver

Steps to add users:
1. python manage.py shell
2. 
>>> from messaging.models import User
>>> u1 = User(name='apple')
>>> u1.save()

Sample flow:
1. Add users in the db
2. In the app, choose a user
3. Create a new group and start a conversation
4. Start a direct message from a group chat by clicking on another user's name 
5. Reply to a message to start a thread or view an existing thread