from channels.generic.websocket import AsyncWebsocketConsumer
from typing import List
import json
import html

from tournament_app.services.tournament import Tournament

players : List["TournamentConsumer"] = []
tournaments : List["Tournament"] = []

class TournamentConsumer(AsyncWebsocketConsumer):

	id = 0

	async def connect(self):

		await self.accept()
		self.id = int(self.scope["url_route"]["kwargs"]["user_id"])
		self.name = self.scope["url_route"]["kwargs"]["user_name"]
		self.creator_id = int(self.scope["url_route"]["kwargs"]["creator_id"])
		players.append(self)
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

	@staticmethod
	async def match_result(data):

		tournament = TournamentConsumer.find_tournament(data.get('matchId'))
		if tournament:
			await tournament.match_result(data)

	@staticmethod
	async def match_players_update(data):

		tournament = TournamentConsumer.find_tournament(data.get('matchId'))
		if tournament:
			await tournament.match_players_update(data)

	@staticmethod
	def watch_dog(request):

		match_id = int(request.GET.get('matchId'))
		tournament = TournamentConsumer.find_tournament(match_id)
		if tournament: 
			p1_id = int(request.GET.get('p1Id'))
			p2_id = int(request.GET.get('p2Id'))
			return {
				"p1": any(p.id == p1_id for p in players),
				"p2": any(p.id == p2_id for p in players)
			}
		else:
			return None

	@staticmethod
	def find_tournament(match_id):
		
		return next((
			t for t in tournaments
			if any(match_id == m.get("matchId") for m in t.matchs)
		), None)
	
	async def receive(self, text_data):

		data = json.loads(text_data)

		match data:
			case {"type": "newPlayer", "playerName": player_name}:
				await self.new_player(player_name)
			case {"type": "newTournament"}:
				await self.new_tournament()
			case {"type": "enterTournament", "tournamentId": tournament_id}:		
				await self.enter_tournament(tournament_id)
			case {"type": "quitTournament"}:		
				await self.quit_tournament()
			case _:
				pass
	
	async def new_player(self, player_name):

		player_name = html.escape(player_name)
		twin_player = next((p for p in players if p.name == player_name), None)
		if twin_player:			
			id = 0
		else:
			TournamentConsumer.id -= 1
			id = TournamentConsumer.id			
		await self.send(text_data=json.dumps({
			"type": "newPlayerId",			
			"playerId": id,
			"playerName": player_name
		}))
		
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
		for player in players:
			await player.send(text_data=json.dumps(pack))

	@staticmethod
	async def send_all_players(packet):
	
		for player in players:				
			await player.send(text_data=json.dumps(packet))
			