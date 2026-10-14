from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from quran_app.asgi import application
from globals.test_objects import create_user
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

class TestLeaderboardWebSocket(TransactionTestCase):
    def endpoint(self):
        return "/ws/leaderboard/"

    async def test_client_connect(self):
        communicator = WebsocketCommunicator(application,self.endpoint())
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_client_receives_first_leaderboard(self):
        await database_sync_to_async(create_user)()
        communicator = WebsocketCommunicator(application,self.endpoint())
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        res = await communicator.receive_json_from()
        self.assertEqual(res["type"], "leaderboard_update")
        self.assertIn("users", res)
        self.assertLessEqual(len(res["users"]), 10)
        await communicator.disconnect()

    async def test_clients_receive_leaderboard_update(self):
        await database_sync_to_async(create_user)()
        communicator1 = WebsocketCommunicator(application, self.endpoint())
        communicator2 = WebsocketCommunicator(application, self.endpoint())
        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()
        self.assertTrue(connected1)
        self.assertTrue(connected2)
        await communicator1.receive_json_from()
        await communicator2.receive_json_from()
        channel_layer = get_channel_layer()
        updated_data = {
            "type": "leaderboard_update",
            "users": [
                {
                    "id": 1,
                    "full_name": "Test User",
                    "total_points": 15,
                }
            ],
        }
        await channel_layer.group_send(
            "leaderboard",
            {
                "type": "leaderboard_update","data": updated_data,
            },
        )
        res1 = await communicator1.receive_json_from()
        res2 = await communicator2.receive_json_from()
        self.assertEqual(res1, updated_data)
        self.assertEqual(res2, updated_data)
        await communicator1.disconnect()
        await communicator2.disconnect()