from channels.generic.websocket import AsyncWebsocketConsumer
import json
from tournament_app.services.tournament import Tournament
from typing import List
import aiohttp

players : List["TournamentConsumer"] = []
tournaments : List["Tournament"] = []

class TournamentConsumer(AsyncWebsocketConsumer):

	async def connect(self):

		await self.accept()
		self.id = self.scope["url_route"]["kwargs"]["user_id"]
		self.name = self.scope["url_route"]["kwargs"]["user_name"]
		players.append(self)
		# await self.send(text_data=json.dumps({
		# 	"type": "selfAssign", "selfId": self.id})) 
		await self.send_list("player", players)
		await TournamentConsumer.send_tournaments()

	async def disconnect(self, close_code):

		await self.remove_player_in_tournaments()
		players[:] = [p for p  in players if p.id != self.id]
		await self.send_list("player", players)

	async def send_list(self, message_type, source):	

		for player in players:
			await player.send(text_data=json.dumps({
				"type": message_type + "List",			
				message_type + "s": [
					{message_type + "Id": s.id, message_type + "Name": s.name}
						for s in source
				]
			}))
			
	@staticmethod
	async def send_tournaments():	

		print(f"SEND TOURNAMENT", flush=True)	
		for player in players:
			await player.send(text_data=json.dumps({
				"type": "tournamentList",			
				"tournaments": [
					{
						"tournamentId": t.id,
						"players": [{"playerId": p.id} for p in t.players],
						"matchs": t.matchs  
					} for t in tournaments
				]
			}))

	async def receive(self, text_data):

		print(f"RECEIVE", flush=True)
		data = json.loads(text_data)
		match data:
			case {"type": "newTournament"}:
				await self.new_tournament()
			case {"type": "enterTournament", "tournamentId": tournament_id}:		
				await self.enter_tournament(tournament_id)
			case {"type": "quitTournament"}:		
				await self.quit_tournament()
			case _:
				pass

	async def new_tournament(self):	

		tournament = Tournament(self.id)
		tournaments.append(tournament)
		await self.enter_tournament(tournament.id)

	async def enter_tournament(self, tournament_id):

		tournament = next(
			(t for t in tournaments if t.id == tournament_id), None)		
		if tournament and self not in tournament.players:
			await self.remove_player_in_tournaments()
			await tournament.append_player(self)
		await TournamentConsumer.send_tournaments()	

	async def remove_player_in_tournaments(self):

		for tournament in tournaments:
			if self in tournament.players:
				await tournament.remove_player(self)

	async def quit_tournament(self):

		await self.remove_player_in_tournaments()			
		await TournamentConsumer.send_tournaments()

	@staticmethod
	async def send_matchs_players_update():

		matchs_players_up = [
			m.get('matchPlayersUpdate') for t in tournaments for m in t.matchs
			if m.get('matchPlayersUpdate')
		]
		pack = {
			"type": "matchsPlayersUpdate",
			"pack": matchs_players_up
		}
		print(f"PACK: {pack}", flush=True)
		for player in players:
			await player.send(text_data=json.dumps(pack))
	