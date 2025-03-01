from channels.generic.websocket import AsyncWebsocketConsumer
import json

players = []


class MyConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.matchId = self.scope["url_route"]["kwargs"]["match_id"]
        print(f"new user connection for match: {self.matchId}", flush=True)
        await self.accept()
        id = len(players) + 1
        players.append(
            {"playerId": id, "matchId": self.matchId
             , "socket": self, "dir": None}
        )

    async def disconnect(self, close_code):
        global players
        print("disconnected", flush=True)
        for p in players:
            if p["socket"] == self:
                print(p["id"], flush=True)
        players = [p for p in players if p["socket"] != self]

    async def receive(self, text_data):

        data = json.loads(text_data)
        # print(
        # 	f"ici houston, voila l'action {data.get('action')}, \
        # 		et puis voila la direction {data.get('direction')}\n"
        # )
        for p in players:
            if p["socket"] == self:
                p["dir"] = data.get("dir")
                # print('is talking', p['id'], flush=True)

        # await self.send(
        # 	text_data=json.dumps(
        # 		f"from server ici houston, \
        # 							on a recu ça {text_data}"
        # 	)

    # )  # Envoie une réponse
