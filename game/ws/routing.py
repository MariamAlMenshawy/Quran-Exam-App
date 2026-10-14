from .consumers import LeaderboardConsumer
from django.urls import path

ws_urls = [
    path('ws/leaderboard/',LeaderboardConsumer.as_asgi()),
]