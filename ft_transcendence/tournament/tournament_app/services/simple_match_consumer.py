from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.dateparse import parse_datetime
import json
import aiohttp

players = []
selfPlayers = []
matchs = []

class SimpleConsumer(AsyncWebsocketConsumer):

	id = 0

	def safe_int(self, value, default=0):

		try:
			return int(value)
		except (TypeError, ValueError) as e:
			print(e)
			return default

	async def connect(self):
		
		await self.accept() 
		self.id = self.scope["url_route"]["kwargs"]["user_id"]
		self.name = self.scope["url_route"]["kwargs"]["user_name"]
		players[:] = [p for p in players if p.get('playerId') != self.id]
		busy =  await self.is_in_match()
		players.append(
			{'playerId': self.id, 'playerName': self.name, 'busy': busy})
		selfPlayers.append({'playerId': self.id, 'socket': self})
		await SimpleConsumer.send_list('player', players)
		await SimpleConsumer.send_list('match', matchs)

	async def disconnect(self, close_code):

		global selfPlayers
		global players
		player = next(
			(p for p in players if p.get('playerId') == self.id), None)
		if player:
			busy = next(
				(p for p in players if p.get('playerId') == player.get('busy')),
			None)
			if busy:
				busy['busy'] = None			
		selfPlayers[:] = [p for p in selfPlayers if p['socket'] != self]
		players[:] = [p for p in players if p['playerId'] != self.id]
		await SimpleConsumer.send_list('player', players)

	async def is_in_match(self):

		async with aiohttp.ClientSession() as session:
			async with session.get(				
					f"http://match:8002/match/is_in_match/?playerId={self.id}"
				) as response:
				if response.status == 200:
					data = await response.json()
					p1 = self.safe_int(data.get('p1', None))
					p2 = self.safe_int(data.get('p2', None))
					return p1 if self.id != p1 else p2
				return None

	@staticmethod
	async def send_list(message_type, source):	

		for selfplay in selfPlayers:
			await selfplay['socket'].send(text_data=json.dumps({
				"type": message_type + "List",			
				message_type + "s": source
			}))

	async def receive(self, text_data):	

		data = json.loads(text_data)
		match data:			
			case {
				"type": "playerClick",
		 		"selectedId": selectedId,
				"selectedName": selectedName
			}:
				await self.invitation(selectedId, selectedName)				
			case {
				"type": "confirmation",
				"response": response,
				"applicantId": applicantId
			}:
				await self.confirmation(response, applicantId)		
			case _:
				pass

	async def invitation(self, selectedId, selectedName):
	
		selectedPlayer = next(
			(p for p in players if p['playerId'] == selectedId), None)
		selfSelectedPlayer = next(
			(p for p in selfPlayers if p['playerId'] == selectedId), None)	
		applicantPlayer = next(
			(p for p in players if p['playerId'] == self.id), None)
		applicantPlayer = next(
			(p for p in players if p['playerId'] == self.id), None)
		if (await self.self_invitation(
			selectedId, selectedPlayer, selectedName)):
			return
		if await self.cancel_invitation(
			applicantPlayer, selectedPlayer, selfSelectedPlayer, selectedId):
			return
		if applicantPlayer and applicantPlayer.get('busy'):
			await self.send_back("selfBusy")
			return
		if selectedPlayer and selectedPlayer.get('busy'):
			await self.send_back("selectedBusy")
			return	
		await self.send_demand(
			selfSelectedPlayer, selectedPlayer,	applicantPlayer)

	async def self_invitation(self, selectedId, selectedPlayer, selectedName):

		if selectedId == self.id and not selectedPlayer.get('busy'):
			selectedPlayer['busy'] = -selectedId
			match_id = await self.start_match(
				self.id, self.name, -selectedId, selectedName)
			await self.send_confirmation_back(
				self, True, selectedId, selectedName,
				selectedId, selectedName, match_id
			)
			await SimpleConsumer.match_update()
			return True
		return False

	async def send_back(self, response):	

		await self.send(text_data=json.dumps({
			"type": "invitation",
			"subtype": "back",
			"applicantId": self.id,
			"applicantName": self.name,
			"response": response
		}))
		
	async def cancel_invitation(self,
		applicantPlayer, selectedPlayer, selfSelectedPlayer, selectedId):
	
		if self.is_busy_with(applicantPlayer, selectedId):
			await self.send_cancel(
				self, selectedId, selectedPlayer.get('playerName'))		
			await self.send_cancel(
				selfSelectedPlayer['socket'], self.id, self.name)	
			selectedPlayer['busy'], applicantPlayer['busy'] = None, None					
			match = next(
				(m for m in matchs 
	 				if self.id in (m.get('playerId'), m.get('otherId'))),
				None)
			if match:
				await self.stop_match(self.id, match.get('matchId'))						
			return True
		return False

	def is_busy_with(self, player1, player2_id):

		if player1 and player1.get('busy') \
			and player1.get('busy') == player2_id:
			return True
		return False

	async def send_cancel(self, socket, target_id, target_name):

		await socket.send(text_data=json.dumps({
			"type": "invitation",
			"subtype": "cancel",
			"targetId": target_id,
			"targetName": target_name			
		}))
		
	async def send_demand(self, 
		selfSelectedPlayer, selectedPlayer, applicantPlayer):

		await selfSelectedPlayer['socket'].send(text_data=json.dumps({
			"type": "invitation",
			"subtype": "demand",
			"applicantId": self.id,
			"applicantName": self.name
		}))		
		selectedPlayer['busy'] = applicantPlayer.get('playerId')
		applicantPlayer['busy'] = selectedPlayer.get('playerId')
			
	async def confirmation(self, response, applicantId):

		match_id = None
		selfApplicantPlayer = next(
			(p for p in selfPlayers if p['playerId'] == applicantId), None)
		selected_player = next(
			(p for p in players if p['playerId'] == self.id), None)
		applicant_player = next(
			(p for p in players if p['playerId'] == applicantId), None)
		app_name = applicant_player.get('playerName')
		if response:
			if self.is_busy_with(applicant_player, self.id):			
				match_id = await self.start_match(applicantId,
					applicant_player.get('playerName'), self.id, self.name)
			else:		
				return
		elif self.is_busy_with(applicant_player, self.id):
			applicant_player['busy'], selected_player['busy'] = None, None			
		else:			
			return	
		await self.send_confirmation_back(
			selfApplicantPlayer['socket'],
			response, applicantId, app_name, self.id, self.name, match_id)
		await self.send_confirmation_back(
			self, response, applicantId, app_name,
			applicantId, app_name, match_id)
		await SimpleConsumer.match_update()

	async def send_confirmation_back(self,
		socket, response, applicant_id, applicant_name,
		target_id, target_name, match_id):

		await socket.send(text_data=json.dumps({
			"type": "invitation",
			"subtype": "confirmation",
			"response": response,
			"applicantId": applicant_id,
			"applicantName": applicant_name,
			"targetId": target_id,
			"targetName": target_name,		
			"matchId": match_id	
		}))

	async def start_match(self,
		applicantId, applicantName, other_id, other_name):

		multy = True if applicantId == -other_id else False
		async with aiohttp.ClientSession() as session:
			async with session.get(				
    				f"http://match:8002/match/new-match/?multy={multy}&m=s"
    				f"&p1Id={applicantId}&p1Name={applicantName}"
    				f"&p2Id={other_id}&p2Name={other_name}"
				) as response:
				if response.status == 201:
					data = await response.json()
					match_id = data.get('matchId', None)
					matchs.append({
						"matchId": match_id,
						"playerId": applicantId,
						"playerName": applicantName, 
						"otherId": other_id,
						"otherName": other_name,
						"multy": multy		
					})
					return match_id
				return None

	async def stop_match(self, applicant_id, match_id):

		url = f"http://match:8002/match/stop-match/{applicant_id}/{match_id}/"

		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				status = response.status
				data = await response.json()		
		if response.status == 200:			
			matchs[:] = [m for m in matchs
				if m.get("matchId") != match_id]
			await SimpleConsumer.match_update()

	@staticmethod
	def watch_dog(request):
	
		match_id = int(request.GET.get('matchId'))
		match = next(
			(m for m in matchs if m.get("matchId") == match_id), None)
		if match:
			p1_id = int(request.GET.get('p1Id'))
			p2_id = int(request.GET.get('p2Id'))
			if p2_id < 0:
				p2_id = p1_id 
			return {
				"p1": any(p.get('playerId') == p1_id for p in players),
				"p2": any(p.get('playerId') == p2_id for p in players)
			}
		else:
			return None
		
	@staticmethod
	async def match_update():
		await SimpleConsumer.send_list('match', matchs)

	@staticmethod
	async def match_players_update(data):

		match_id = data.get("matchId", None)
		players = data.get("players", [])
		match = next(
			(m for m in matchs if m.get("matchId") == match_id), None)
		if match:
			match["players"] = players	
			await SimpleConsumer.send_list('match', matchs)
	
	@staticmethod
	async def match_result(data):

		p1_id = data.get('p1Id')
		p2_id = data.get('p2Id')
		match_id = data.get('matchId')
		p1 = next((p for p in players if p.get("playerId") == p1_id), None)
		p2 = next((p for p in players if p.get("playerId") == p2_id), None)
		if p1:
			p1["busy"] = None
		if p2:
			p2["busy"] = None 
		match = next(
			(m for m in matchs if m.get("matchId") == match_id), None)
		if match: 
			matchs[:] = [m for m in matchs if m.get("matchId") != match_id]
			await SimpleConsumer.send_list('match', matchs)
			await SimpleConsumer.send_db(data)

	@staticmethod
	async def send_db(match_results):

		from tournament_app.views import send_db as sdb
		p1 = max(1, match_results["p1Id"] or 0)
		p2 = max(1, match_results["p2Id"] or 0)
		win = max(1, match_results["winnerId"] or 0)
		score_p1 = match_results["score"][0]
		score_p2 = match_results["score"][1]
		if match_results["startTime"]:
			start_time = parse_datetime(match_results["startTime"])
		else:
			start_time = None
		if match_results["endTime"]:
			end_time = parse_datetime(match_results["endTime"])
		else:
			end_time = None
		data = {
			"player1": p1,
			"player2": p2,
			"winner": win,
			"score_p1": score_p1,
			"score_p2": score_p2,
			"start_time": start_time.isoformat() if start_time else None,
			"end_time": end_time.isoformat() if end_time else None,
		}
		await sdb("api/match/", data)
		await SimpleConsumer.send_db_stats(sdb, p1, p2, win, score_p1, score_p2)

	@staticmethod
	async def send_db_stats(sdb, p1, p2, win, score_p1, score_p2):

		data_p1 = {
			"is_won": 1 if win == p1 else 0,
			"is_lost": 1 if win != p1 else 0,
			"points_scored": score_p1,
			"points_conceded": score_p2,
		}
		data_p2 = {
			"is_won": 1 if win == p2 else 0,
			"is_lost": 1 if win != p2 else 0,
			"points_scored": score_p2,
			"points_conceded": score_p1,
		}
		path_p1 = f"api/player/{p1}/stats/update-stats/"
		await sdb(path_p1, data_p1)
		path_p2 = f"api/player/{p2}/stats/update-stats/"
		await sdb(path_p2, data_p2)
