import threading
import time
import match_app.services.match_consumer as match_consumer
import asyncio
import json
import aiohttp
from enum import Enum
import requests

import match_app.services.pong_physics as physics
import match_app.services.pong_scores as scores

class State(Enum):
	waiting = "waiting"
	running = "running"
	end = "end"

class Pong:

	id = 0

	def __init__(self, multy, p1, p2):

		self.init_vars(multy, p1, p2)
		threading.Thread(target=self.launchTask, daemon=True).start()

	def init_vars(self, multy, p1, p2):

		Pong.id += 1
		self.id = Pong.id
		self.multy = multy	
		self.plyIds = [p1[0], p2[0]]
		self.names = [p1[1], p2[1]]
		print(f"DANS LE MATCH LA PUTEEE {self.plyIds} {self.names}", flush=True)
		self.state = State.waiting
		self.start_flag = False
		self.pause = True
		self.score = [0, 0]
		self.max_score = 2
		self.point_delay = 1
		self.start_delay = 4
		self.max_wait_delay = 2000
		self.users = []
		self.players = None		
		self.winner = None
		self.myEventLoop = None
		self.tasks = None
		self.init_physics()

	def init_physics(self):

		self.has_wall = False
		# self.pad_height = 100	
		# self.pads_y = [self.pad_height / 2 + 50, self.pad_height / 2 + 50]		
		# self.pads_y = [50, 50]		
		self.ball_rst = [50, 50]
		self.ball = self.ball_rst.copy()
		self.ball_speed = 0.2
		self.vect = self.get_random_vector() 
		self.pad_speed = 2
		self.max_ball_speed = 100 # //! 10
		self.ball_acceleration = 1.3
		self.bounce_delay = 0.01
		self.send_delay = 0.01
		self.gear_delay = 0.01
		self.init_bounces_sides()

	def init_bounces_sides(self):
		
		self.pad_height = 20
		self.pads_y = [50, 50]	
		self.pads_offset = 5
		self.pads_width = 5
		self.ball_ray = 1
		self.x_left_pad = self.pads_offset + self.pads_width + self.ball_ray
		self.x_rght_pad = 100 - self.x_left_pad
		self.y_top = 0 + self.ball_ray
		# self.y_top = 30 + self.ball_ray
		self.y_bot = 100 - self.ball_ray
		# self.y_bot = 70 - self.ball_ray
	
	def launchTask(self):
		# self.myEventLoop.create_task(self.sendState()),

		self.myEventLoop = asyncio.new_event_loop()
		asyncio.set_event_loop(self.myEventLoop)
		self.tasks = [
			self.myEventLoop.create_task(self.launch_game()),
			self.myEventLoop.create_task(self.watch_dog())		
		]
		try:
			self.myEventLoop.run_until_complete(
				asyncio.gather(*self.tasks, return_exceptions=True))
		finally:
			self.myEventLoop.close()				
			from match_app.views import del_pong
			del_pong(self.id)
			print(f"Event loop fermé proprement pour match {self.id}", flush=True)

	async def launch_game(self):
			
		while self.state != State.end:		
			self.has_wall = False	
			self.get_users()		
			if None not in self.players:			
				await self.run_game()						
			else:
				self.set_waiting_state(self.players)	
			await self.sendState();						
			await asyncio.sleep(self.gear_delay)

		print(f"in match after WHILE id:{self.id}", flush=True)

	def get_users(self):

		self.users = [p for p in match_consumer.players
			if self.id == p["matchId"]]
		self.players = [next(
			(p for p in self.users if self.plyIds[0] == p["playerId"]),
			None), next(
			(p for p in self.users if self.plyIds[1] == p["playerId"]),
			None)
		]

	async def send_start(self, delay):

		for p in self.users:
			await p["socket"].send(text_data=json.dumps({
				"type": "timestamp",
				"timestamp": time.time(),
				"delay": delay
			}))

	async def run_game(self):
		
		if not self.start_flag:
			await self.send_start(3)
			self.tasks.append(
				self.myEventLoop.create_task(self.watch_cat(self.start_delay)))
		self.state = State.running
		self.winner = None
		self.start_flag = True
		self.wall_flag = True

		self.pad_commands(self.players)	
		if not self.pause:	
			await self.scores()
			await self.bounces()										
			self.move_ball()
						
	def set_waiting_state(self, players):

		if self.start_flag:
			if players[0]:
				self.winner = self.plyIds[0]
			elif players[1]:
				self.winner = self.plyIds[1]
			else:
				self.winner = None
		self.state = State.waiting

	async def watch_dog(self):
		
		delay = 0
		while self.state != State.end:			
			if self.state == State.running:
				delay = 0
			if delay > self.max_wait_delay:
				print(f"stopped by wathdog", flush=True)
				await self.stop(None)
				return
			if not self.start_flag:
				await self.are_alives_players()
			delay += 1
			await asyncio.sleep(1.00)

	async def are_alives_players(self):

		async with aiohttp.ClientSession() as session:
			async with session.get(
				f"http://tournament:8001/tournament/watch-dog/"
				f"?matchId={self.id}"
				f"&p1Id={self.plyIds[0]}&p2Id={self.plyIds[1]}"
			) as response:				
				if response.status not in (200, 201):
					err = await response.text()
					print(f"Error HTTP {response.status}: {err}", flush=True)
					return
				data = await response.json()
				print(f"PLAYERS CHECKING ALIVE: {data}", flush=True)
				await self.alives_players_strategy(data)

	async def alives_players_strategy(self, data):

		alives_players = (data.get("p1"), data.get("p2"))
		if all(alives_players):
			return
		if not any(alives_players):
			self.winner = None
		elif alives_players[0]:
			self.winner = self.plyIds[0]
		elif alives_players[1]:
			self.winner = self.plyIds[1]	
		await self.stop(None)

	async def watch_cat(self, pause_delay):

		self.pause = True
		delay = 0
		while self.state != State.end:
			if delay >= pause_delay:				
				self.pause = False
				break
			delay += 1
			await asyncio.sleep(1.00)

	async def stop(self, playerId):

		print(f"STOP playerId: {playerId}", flush=True)

		if not playerId or playerId in self.plyIds: 	
			if not any((self.winner, self.multy)) and \
				all((playerId, self.start_flag)):							
				self.winner = self.plyIds[0] \
					if playerId == self.plyIds[1] else self.plyIds[1]				
			await self.sendFinalState()
			return True
		return False

	async def sendState(self):		
		
		# while self.state != State.end:	
			# self.users = [p for p in match_consumer.players
			# 	if self.id == p["matchId"]]
			for p in self.users:
				# state = self.state
				if self.state != State.end:
					try:												
						await p["socket"].send(text_data=json.dumps({
							"state": self.state.name,
							"yp1": self.pads_y[0],
							"yp2": self.pads_y[1],
							"plyIds": self.plyIds,
							"names": self.names,
							"ball": self.ball,
							"score": self.score,
							"hasWall": self.has_wall
						}))                  
					except Exception as e:
						pass				
			# await asyncio.sleep(self.send_delay)

	async def sendFinalState(self):

		print(f"SEND FINAL STATE", flush=True)		

		self.state = State.end
		w_and_l = self.get_winner_and_looser()
		for p in self.users:
			try:					
				await p["socket"].send(text_data=json.dumps({
				"state": self.state.name,			
				"winnerId": w_and_l[0][0],
				"looserId": w_and_l[1][0],
				"names": self.names,
				"winnerName": w_and_l[0][1],
				"looserName": w_and_l[1][1],
				"score": self.score
				})) 
			except Exception as e:
				pass		
		print(f"BEFORE SEND MATCH RESULT", flush=True)
		await self.send_match_result(w_and_l[0], w_and_l[1])
		print(f"AFTER SEND MATCH RESULT", flush=True)
		# await asyncio.gather(*self.tasks, return_exceptions=True)
		# from match_app.views import del_pong
		# del_pong(self.id)

	def get_winner_and_looser(self):

		if not self.winner:
			return ((None, "None"), (None, "None"))
		return ((
			self.winner,
			self.names[0] if self.winner == self.plyIds[0] else self.names[1]			
		),
		(
			self.plyIds[0] if self.winner == self.plyIds[1] else self.plyIds[1],
			self.names[1] if self.winner == self.plyIds[0] else self.names[0]
		))

	async def send_match_result(self, winner, looser):

		async with aiohttp.ClientSession() as session:
			async with session.post(
				"http://tournament:8001/tournament/match-result/", json={
				"matchId": self.id,
				"winnerId": winner[0],
				"looserId": looser[0],
				"winnerName": winner[1],
				"looserName": looser[1],
				"p1Id": self.plyIds[0],
				"p2Id": self.plyIds[1],
				"score": self.score
			}) as response:				
				if response.status not in (200, 201):
					err = await response.text()
					print(f"Error HTTP {response.status}: {err}", flush=True)

Pong.pad_commands = physics.pad_commands
Pong.pad_command = physics.pad_command
Pong.bounces = physics.bounces
Pong.vert_bounce = physics.vert_bounce
Pong.horz_bounce = physics.horz_bounce
# Pong.are_pads_intersecting = physics.are_pads_intersecting
Pong.is_pad_intersecting = physics.is_pad_intersecting
Pong.segments_intersect = physics.segments_intersect
Pong.scale_vector = physics.scale_vector
Pong.get_magnitude = physics.get_magnitude
Pong.move_ball = physics.move_ball
Pong.get_random_vector = physics.get_random_vector

Pong.scores = scores.scores
Pong.score_point = scores.score_point
Pong.max_score_rise = scores.max_score_rise
