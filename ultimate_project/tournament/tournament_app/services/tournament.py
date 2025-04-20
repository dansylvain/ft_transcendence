import json
import requests
import asyncio
import aiohttp
from django.utils.dateparse import parse_datetime

class Tournament():
	
	id = 0
	def __init__(self, applicantId):
		
		Tournament.id += 1
		self.id = Tournament.id
		self.launch = False
		self.players = []
		self.matchs = []
		self.n_match = 0
		self.r_match = 0

	async def append_player(self, player):

		self.players.append(player)
		if len(self.players) >= 4 and not self.launch:	
			await self.launchTournament()	
				
	async def remove_player(self, player):

		print(f"REMOVE PLAYER {player.id}", flush=True)
		self.players[:] = [p for p in self.players if p != player]
		if not self.players:	
			await self.del_tournament()

	async def del_tournament(self):

		print(f"DEL TOURNAMENT {self.id}", flush=True)
		from tournament_app.services.tournament_consumer \
			import tournaments, TournamentConsumer
		tournaments[:] = [t for t in tournaments if t.id != self.id]
		await TournamentConsumer.send_tournaments()

	async def launchTournament(self):

		self.launch = True
		p1 = (self.players[0].id, self.players[0].name)
		p2 = (self.players[1].id, self.players[1].name)
		p3 = (self.players[2].id, self.players[2].name)
		p4 = (self.players[3].id, self.players[3].name)
		await self.start_match(p1, p2, "m2")
		await self.start_match(p3, p4, "m3")

	async def start_match(self, p1, p2, local_match_id):

		print(f"START MATCH p1:{p1[0]} {p1[1]} p2:{p2[0]} {p2[1]} lmt:{local_match_id}", flush=True)
		
		multy = self.is_multyplayers(p1, p2)
		async with aiohttp.ClientSession() as session:
			async with session.get(				
    				f"http://match:8002/match/new-match/?multy={multy}"
					f"&p1Id={p1[0]}&p1Name={p1[1]}&p2Id={p2[0]}&p2Name={p2[1]}"
				) as response:
				if response.status == 201:
					data = await response.json()
					match_id = data.get('matchId', None)					
					link_match = self.create_link_match(
						p1, p2, match_id, local_match_id
					)
					match = {
						"matchId": match_id,						
						"linkMatch": link_match
					}
					self.matchs.append(match)
					print(f"FIN STARTMATCH {link_match}", flush=True)
					return link_match
				else:  
					err = await response.text()
					print(f"Error HTTP {response.status}: {err}", flush=True)
	
	def is_multyplayers(self, p1, p2):
		
		p1_creator_id = next(
			(p.creator_id for p in self.players if p.id == p1[0]), None)
		p2_creator_id = next(
			(p.creator_id for p in self.players if p.id == p2[0]), None)
		return p1_creator_id == p2_creator_id

	def create_link_match(self, p1, p2, match_id, local_match_id):

		self.n_match += 1
		return {
			"type": "linkMatch",
			"tournamentId": self.id,
			"localMatchId": local_match_id,			
			"matchId": match_id,
			"p1Id": p1[0],
			"p2Id": p2[0],
			"p1Name": p1[1],
			"p2Name": p2[1],
			"nMatch": self.n_match
		} 

	async def match_result(self, data):

		self.r_match += 1
		match_id = data.get('matchId')		
		match = next(
			(m for m in self.matchs if m.get('matchId') == match_id), None)
		if match:
			match_result = {				
				"type": "matchResult",
				"tournamentId": self.id,
				"localMatchId": match.get('linkMatch', {}).get('localMatchId'),
				"nMatch": match.get('linkMatch', {}).get('nMatch'),			
				**data			
			}
			match['matchResult'] = match_result
			match['matchPlayersUpdate'] = None
		await self.workflow(match_result)

	async def workflow(self, match_result):

		if self.r_match == 1:
			await self.send_all_players(match_result)
			link_match = self.create_inter_link(match_result, "m1")
			await self.send_all_players(link_match)
		elif self.r_match == 2:		
			await self.send_all_players(match_result)
			nxt_plys = self.get_next_players()
			if not None in (nxt_plys[0][0], nxt_plys[1][0]):
				link_match = await self.start_match(
					nxt_plys[0], nxt_plys[1], "m1")							
				await self.send_all_players(link_match)
			else:
				link_match = self.create_fake_link(match_result, "m1", nxt_plys)
				await self.send_all_players(link_match)
				await self.create_fake_match(link_match, nxt_plys)
		elif self.r_match == 3:
			await self.send_all_players(match_result)
			tournament_result = self.get_tournament_result(match_result)
			await self.send_all_players(tournament_result)
			await self.send_db(tournament_result)
			asyncio.create_task(self.end_remove())
			self.launch = False

	def create_inter_link(self, match_result, local_match_id):
				
		winner_id = match_result.get('winnerId')
		winner_name = match_result.get('winnerName')	
		n_match = match_result.get('nMatch')
		print(f"n_match ******************************************************************* {n_match}", flush=True)
		if n_match == 1:
			p1_id = winner_id
			p1_name = winner_name
			p2_id = 0
			p2_name = " - "
		elif n_match == 2:
			p1_id = 0
			p1_name = " - "
			p2_id = winner_id
			p2_name = winner_name
		return {
			"type": "linkMatch",
			"tournamentId": self.id,
			"localMatchId": local_match_id,			
			"matchId": 0,
			"p1Id": p1_id,
			"p2Id": p2_id,
			"p1Name": p1_name,
			"p2Name": p2_name
		}

	def create_fake_link(self, match_result, local_match_id, nxt_plys):
		
		self.n_match += 1
		match_id = -match_result.get('matchId')
		link_match = {
			"type": "linkMatch",
			"tournamentId": self.id,
			"localMatchId": local_match_id,			
			"matchId": match_id,
			"p1Id": nxt_plys[0][0],
			"p2Id": nxt_plys[1][0],
			"p1Name": nxt_plys[0][1],
			"p2Name": nxt_plys[1][1],
			"nMatch": self.n_match
		}
		match = {
			"matchId": match_id,						
			"linkMatch": link_match
		}
		self.matchs.append(match)
		return link_match
	
	async def create_fake_match(self, link_match, nxt_plys):
		
		if nxt_plys[0][0]:
			winner = nxt_plys[0]
			looser =  nxt_plys[1]
		elif nxt_plys[1][0]:
			winner = nxt_plys[1]
			looser = nxt_plys[0]
		else:
			winner = (None, "nobody")
			looser = (None, "nobody")
		data = {
			"matchId": link_match.get('matchId'),
			"winnerId": winner[0],
			"looserId": looser[0],
			"winnerName": winner[1],
			"looserName": looser[1],
			"p1Id": link_match.get('p1Id'),
			"p2Id": link_match.get('p2Id'),
			"score": [0, 0],
			"nMatch": link_match.get('nMatch')
		}
		await self.match_result(data)

	async def end_remove(self):

		print(f"END REMOVE", flush=True)
		# await asyncio.sleep(30)
		# await self.del_tournament()

	def get_next_players(self):

		return (
			(
				self.matchs[0].get('matchResult', {}).get('winnerId'),
				self.matchs[0].get('matchResult', {}).get('winnerName')
			),	
			(
				self.matchs[1].get('matchResult', {}).get('winnerId'),
				self.matchs[1].get('matchResult', {}).get('winnerName')
			)
		)
		
	def get_tournament_result(self, match_result):

		return {
			"type": "tournamentResult",
			"tournamentId": self.id,
			"winnerId": match_result.get('winnerId'),
			"winnerName": match_result.get('winnerName'),
			"looserId": match_result.get('looserId'),
			"looserName": match_result.get('looserName'),
			"matchs": self.matchs
		}

	async def send_all_players(self, packet):

		from tournament_app.services.tournament_consumer \
			import TournamentConsumer
		await TournamentConsumer.send_all_players(packet)

	async def save_tournament_matches(self, matches, tournament_id):
		
		from tournament_app.views import send_db as sdb

		
        # Loops 3 times because there is 3 matches within a tournament
		for i in range(3):
			# `or 0` Handles `None` users
			p1 = max(1, matches[i]["matchResult"]["p1Id"] or 0)
			p2 = max(1, matches[i]["matchResult"]["p2Id"] or 0)
			win = max(1, matches[i]["matchResult"]["winnerId"] or 0)
			score_p1 = matches[i]["matchResult"]["score"][0]
			score_p2 = matches[i]["matchResult"]["score"][1]
			tournament = tournament_id
			# Compile each key in a JSON body
			# HERE FOR MY DATA
			start_time = parse_datetime(matches[i]["matchResult"]["startTime"])
			end_time = parse_datetime(matches[i]["matchResult"]["endTime"])
			
			data = {
				"player1": p1,
				"player2": p2,
				"winner": win,
				"score_p1": score_p1,
				"score_p2": score_p2,
				"start_time": start_time.isoformat() if start_time else None,
    			"end_time": end_time.isoformat() if end_time else None,
				"tournament": tournament,
			}
			path = "api/match/"
			await sdb(path, data)
			# Update Players stats
			data_p1 = {
				"is_won": 1 if win == p1 else 0,
				"is_lost": 1 if win != p1 else 0,
				"points_scored": score_p1,
				"points_conceded": score_p2,
				"nb_tournaments_played": 1 if i == 0 else 0,
				"nb_tournaments_won": 1 if win == p1 and i == 2 else 0,
			}
			data_p2 = {
				"is_won": 1 if win == p2 else 0,
				"is_lost": 1 if win != p2 else 0,
				"points_scored": score_p2,
				"points_conceded": score_p1,
				"nb_tournaments_played": 1 if i == 0 else 0,
				"nb_tournaments_won": 1 if win == p2 and i == 2 else 0,
			}
			# Send updates to player statistics
			path_p1 = f"api/player/{p1}/stats/update-stats/"
			await sdb(path_p1, data_p1)
			path_p2 = f"api/player/{p2}/stats/update-stats/"
			await sdb(path_p2, data_p2)

   

	async def extract_last_tournament_id(self):
		async with aiohttp.ClientSession() as session:
			async with session.get(
				f"http://databaseapi:8007/api/tournament/") as response:				
				if response.status in (200, 201):
					full_response = await response.json()
                    # [-1] access the last json block
					return full_response[-1]["id"]

	async def send_db(self, tournament_result):
		
		from tournament_app.views import send_db as sdb
		path = "api/tournament/"
		winner = max(1, tournament_result["winnerId"] or 0)
		
        # Update the tournament table first...
		data_tournament = {
			"winner_tournament" : winner,
		}
		await sdb(path, data_tournament)
		
        # ... and retrieve it's databaseID afterwards to pass it as argument
		id_tournament = await self.extract_last_tournament_id()
		all_matches = tournament_result["matchs"]
		
		await self.save_tournament_matches(all_matches, id_tournament)
		
	async def match_players_update(self, match_update):

		print(f"MATCH PLAYERS UPDATE {match_update}", flush=True)
		match = next(
			(m for m in self.matchs
			if m.get('matchId') == match_update.get('matchId'))
		, None)
		if match:
			match_update['type'] = 'matchPlayersUpdate'
			match_update['tournamentId'] = self.id
			match_update['localMatchId'] = match.get('linkMatch', {}).get(
				'localMatchId')
			match_update['p1Id'] = match.get('linkMatch', {}).get('p1Id')
			match_update['p2Id'] = match.get('linkMatch', {}).get('p2Id')
			match['matchPlayersUpdate'] = match_update
			await self.send_match_players_update()

	async def send_match_players_update(self):	

		from tournament_app.services.tournament_consumer \
			import TournamentConsumer
		await TournamentConsumer.send_matchs_players_update()
					