from channels.generic.websocket import AsyncWebsocketConsumer
import json
import urllib
from match_app.views import pongs
import aiohttp
import asyncio

players = []

class MatchConsumer(AsyncWebsocketConsumer):

	async def connect(self):

		print(f"CONNECT MATCH CONSUMER: {players}", flush=True)

		query_string = self.scope["query_string"].decode() 	
		params = urllib.parse.parse_qs(query_string)
		self.player_id = int(params.get("playerId", [None])[0])
		self.match_id = self.scope["url_route"]["kwargs"]["matchId"]    
		print(f"CMC p:{self.player_id} m:{self.match_id}", flush=True)	
		await self.accept()
		if await self.filter_player(self.match_id, self.player_id):
			await self.close(code=3000)
			return		
		players.append({
			'playerId': self.player_id,
			'matchId': self.match_id,
			'socket': self,
			'dir': None
		})		
		await self.send_players_update()	

	async def disconnect(self, close_code):

		print(f"DISCONNECT MATCH CONSUMER p:{self.player_id} m:{self.match_id}", flush=True)
			
		players[:] = [p for p in players if p['playerId'] != self.player_id]		
		await self.send_players_update()

	async def filter_player(self, match_id, player_id):

		pong = next((p for p in pongs if p.id == match_id), None)
		if not pong:
			print(f"MATCH DON'T EXIST p:{player_id} m:{match_id}", flush=True)			
			return True
		if pong and \
			player_id < 0 and \
			player_id not in pong.plyIds:
			print(f"2ND PLAYER FILTERED p:{player_id} m:{match_id}", flush=True)			
			return True
		player = next(
			(p for p in players if p.get('playerId') == player_id), None)
		if player:
			print(f"PLAYER YET EXIST p:{player_id} m:{match_id}", flush=True)			
			return True
		return False

	async def receive(self, text_data):

		data = json.loads(text_data)	
		for p in players: 
			if p['socket'] == self:
				p['dir'] = data.get('dir')

	async def send_players_update(self):
	
		print(f"MATCH CONSUMER SEND PLAYERS UPDATE p:{self.player_id} m:{self.match_id}", flush=True)

		await asyncio.sleep(1)
		async with aiohttp.ClientSession() as session:
			async with session.post(
				"http://tournament:8001/tournament/match-players-update/",
				json={
				"matchId": self.match_id,
				"players": [{
					key : value for key, value in p.items() if key == 'playerId'
					} for p in players if p.get('matchId') == self.match_id				
				]}) as resp:
					if resp.status != 200 and resp.status != 201:
						err = await resp.text()
						print(f"Error HTTP {resp.status}: {err}", flush=True)
