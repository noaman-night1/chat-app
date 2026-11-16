import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message

ONLINE_USERS = {}

def safe_group_name(name):
    return re.sub(r'[^a-zA-Z0-9\-\.]', '_', name)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        await self.accept()
        
        if self.user.is_authenticated:
            self.group_name = safe_group_name(f"user_{self.user.username}")
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.channel_layer.group_add("online_users", self.channel_name)
            ONLINE_USERS[self.user.username] = ONLINE_USERS.get(self.user.username, 0) + 1
            await self.broadcast_online_users()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            self.group_name = safe_group_name(f"user_{self.user.username}")
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await self.channel_layer.group_discard("online_users", self.channel_name)
            if self.user.username in ONLINE_USERS:
                ONLINE_USERS[self.user.username] -= 1
                if ONLINE_USERS[self.user.username] <= 0:
                    del ONLINE_USERS[self.user.username]
            await self.broadcast_online_users()

    async def broadcast_online_users(self):
        await self.channel_layer.group_send(
            "online_users",
            {"type": "user_status", "online_users": list(ONLINE_USERS.keys())}
        )

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'online_users': event['online_users']
        }))

    async def notify(self, event):
        await self.send(text_data=json.dumps(event['data']))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = safe_group_name(f'chat_{self.room_name}')
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.get_or_create_room(self.room_name)
        past_messages = await self.get_past_messages(self.room_name)
        await self.send(text_data=json.dumps({
            'type': 'history',
            'messages': past_messages
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')
        username = data.get('username') or (self.user.username if self.user.is_authenticated else None)

        # JDID: Typing Indicator
        if msg_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'username': username,
                    'is_typing': data.get('is_typing')
                }
            )
            return

        # Message normal
        message = data.get('message')
        receiver = data.get('receiver')
        
        if not message or not username:
            return

        saved = await self.save_message(self.room_name, username, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': saved['timestamp'],
            }
        )

        if receiver:
            receiver_group = safe_group_name(f"user_{receiver}")
            await self.channel_layer.group_send(
                receiver_group,
                {
                    "type": "notify",
                    "data": {"type": "new_message", "sender": username, "message": message}
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    # JDID: Sift l'typing l React
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username'],
            'is_typing': event['is_typing']
        }))

    @database_sync_to_async
    def get_or_create_room(self, room_name):
        Room.objects.get_or_create(name=room_name)

    @database_sync_to_async
    def save_message(self, room_name, username, content):
        room = Room.objects.get(name=room_name)
        msg = Message.objects.create(room=room, username=username, content=content)
        return {'timestamp': msg.created_at.strftime('%H:%M')}

    @database_sync_to_async
    def get_past_messages(self, room_name):
        room = Room.objects.get(name=room_name)
        messages = Message.objects.filter(room=room).order_by('created_at')
        return [
            {'username': msg.username, 'message': msg.content, 'timestamp': msg.created_at.strftime('%H:%M')} 
            for msg in messages
        ]