from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from game.views import Leaderboard
import json


class LeaderboardConsumer(WebsocketConsumer):

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            "leaderboard",
            self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({
            "type": "leaderboard_update",
            "users": Leaderboard.get_top_users()
        }))

    def disconnect(self, close_code):
        print(f"Leaderboard WebSocket disconnected: {close_code}")
        async_to_sync(self.channel_layer.group_discard)(
            "leaderboard",
            self.channel_name
        )

    def leaderboard_update(self, event):
        self.send(text_data=json.dumps(event["data"]))
