import threading
import time
import match_app.services.match_consumer as match_consumer
import asyncio
import json
import aiohttp
from enum import Enum
import requests
import random
import match_app.services.pong_physics as physics
import match_app.services.pong_scores as scores

class State(Enum):
	waiting = "waiting"
	running = "running"
	end = "end"

class Pong:

	id = 0

	def __init__(self, p1, p2):

		Pong.id += 1
		self.id = Pong.id	
		self.plyIds = [p1[0], p2[0]]
		self.names = [p1[1], p2[1]]
		print("NAAAAAME", flush=True)
		print(self.names, flush=True)
		self.state = State.waiting
		self.start_flag = False
		self.winner = None
		self.score = [0, 0]

		self.has_wall = False
		self.max_score = 50
		self.max_wait_delay = 1500

		self.pad_height = 40	
		self.pads_y = [self.pad_height / 2, self.pad_height / 2]
		self.pad_width = 10
		self.ball_rst = [25, 5]
		self.ball = self.ball_rst.copy()
	
		self.vect_rst = lambda: random.uniform(-1, 1)
		self.vect = [self.vect_rst(), self.vect_rst()] 
		self.pad_speed = 4
		self.max_ball_speed = 10
		self.ball_acceleration = 1.1

		self.bounce_delay = 0.05
		self.send_delay = 0.05
		self.gear_delay = 0.05

		self.send_task = None
		self.watch_task = None

		self.users = None
		self.players = None
		# asyncio.run(self.end())
		threading.Thread(target=self.launchTask, daemon=True).start()

	# async def end(self):
	# 	print("end un", flush=True)
	# 	await self.two()
	# 	print("end deux", flush=True)
		
	# async def two(self):
	# 	print("two un", flush=True)
	# 	await self.three()
	# 	print("two deux", flush=True)
		
	# async def three(self):
	# 	print("three un", flush=True)
	# 	await asyncio.sleep(1)
	# 	print("three deux", flush=True)



	# async def stop_tasks(self):

	# 	tasks = [self.send_task, self.watch_task]
	# 	for task in tasks:
	# 		if task and not task.done() and not task.cancelled():
	# 			task.cancel()
	# 	await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)

	# def stop(self, playerId):
	# 	print(f"in stop PONG my id is : {self.id}", flush=True)
	# 	print(f"self.idP1: {self.idP1}, self.idP2: {self.idP2}, playerId: {playerId}", flush=True)

	# 	if playerId in (self.idP1, self.idP2):
	# 		print("Player is authorized to stop the match", flush=True)
	# 		self.state = State.end
	# 		print(f"Match {self.id} state updated to {self.state}", flush=True)
	# 		return True

	# 	print("Player not authorized to stop the match", flush=True)
	# 	return False
	# def launchTask(self):
	# 	self.start_flag = False
	# 	self.myEventLoop = asyncio.new_event_loop()
	# 	asyncio.set_event_loop(self.myEventLoop)
	# 	self.myEventLoop.create_task(self.launch())
	# 	# self.myEventLoop.run_forever()
	# 	# myEventLoop.run_until_complete(asyncio.Future())
	# 	self.myEventLoop.run_until_complete(self.launch())
	
	# 	self.myEventLoop.stop()
	# 	self.myEventLoop.close() 
	# 	print("in match after RUN", flush=True)
	
	# def launchTask(self):
		
	# 	self.myEventLoop = asyncio.new_event_loop()
	# 	asyncio.set_event_loop(self.myEventLoop)	
	# 	try:
	# 		# self.myEventLoop.create_task(self.launch_game())
	# 		# self.myEventLoop.run_forever()

	# 		self.myEventLoop.run_until_complete(self.launch())  
	# 	finally:
	# 		time.sleep(2)			
	# 		tasks = [
	# 			t for t in asyncio.all_tasks(self.myEventLoop) if not t.done()]
	# 		for task in tasks:
	# 			task.cancel()
	# 		self.myEventLoop.run_until_complete(
	# 			asyncio.gather(*tasks, return_exceptions=True))
	# 		self.myEventLoop.stop()
	# 		self.myEventLoop.close()
	# 		print(f"Event loop fermé proprement pour match {self.id}", flush=True)

		# self.launch_task = self.myEventLoop.create_task(self.launch_game())
		# self.send_task = self.myEventLoop.create_task(self.sendState())
		# self.watch_task = self.myEventLoop.create_task(self.watch_dog())

	def launchTask(self):

		myEventLoop = asyncio.new_event_loop()
		asyncio.set_event_loop(myEventLoop)
		tasks = [
			myEventLoop.create_task(self.launch_game()),
			myEventLoop.create_task(self.sendState()),
			myEventLoop.create_task(self.watch_dog()),	
		]
		try:
			myEventLoop.run_until_complete(
				asyncio.gather(*tasks, return_exceptions=True))
		finally:
			myEventLoop.close()
			print(f"Event loop fermé proprement pour match {self.id}", flush=True)

	async def launch_game(self):
			
		while self.state != State.end:		
			self.has_wall = False	
			self.get_users()		
			if None not in self.players:			
				await self.run_game()						
			else:
				self.set_waiting_state(self.players)							
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

	async def run_game(self):

		self.state = State.running
		self.winner = None
		self.start_flag = True
		self.wall_flag = True

		self.pad_commands(self.players)		
		await self.scores()
		await self.bounces()										
		self.move_ball()
						
	def set_waiting_state(self, players):

		if self.start_flag:
			if players[0]:
				self.winner = self.plyIds[0]
			elif players[1]:
				self.winner = self.plyIds[1]
		self.state = State.waiting

	async def watch_dog(self):
		
		delay = 0
		while self.state != State.end:			
			if self.state == State.running:
				delay = 0
			if (delay > self.max_wait_delay):
				print(f"stopped by wathdog", flush=True)
				await self.stop(self.plyIds[0])
				return
			delay += 1
			await asyncio.sleep(1.00)

	async def stop(self, playerId):

		print(f"STOP playerId: {playerId}", flush=True)
		print(self.plyIds, flush=True)
		if playerId in self.plyIds: 	
			print(f"le player est bien autorise a fermer le match", flush=True)
			# self.sendTask.cancel()
			# try:
			# 	await self.sendTask  # Attendre que l'annulation soit complète
			# except asyncio.CancelledError:
			# 	print("Tâche annulée avec succès")	 
			# self.state = State.end
			if self.winner is None and self.start_flag:
				self.winner = self.plyIds[0] \
					if playerId == self.plyIds[1] else self.plyIds[1]
			if self.winner is None and not self.start_flag:
				self.winner = self.plyIds[0] \
					if playerId == self.plyIds[1] else self.plyIds[1]
			# asyncio.run_coroutine_threadsafe(self.stop_tasks, self.myEventLoop)
			await self.sendFinalState()
			return True
		print(f"le player n'est pas bien autorise a fermer le match", flush=True)
		return False
	
	async def sendState(self):		
		
		while self.state != State.end:	
			# print(f"{self.ball}", flush=True)
			self.users = [p for p in match_consumer.players
				if self.id == p["matchId"]]
			for p in self.users:
				state = self.state
				if state != State.end:
					try:												
						await p["socket"].send(text_data=json.dumps({
							"state": state.name,
							"yp1": self.pads_y[0],
							"yp2": self.pads_y[1],
							"names": self.names,
							"ball": self.ball,
							"score": self.score,
							"hasWall": self.has_wall
						}))                  
					except Exception as e:
						pass				
			await asyncio.sleep(self.send_delay)

	async def sendFinalState(self):

		self.state = State.end
		print(f"SEND FINAL STATE", flush=True)		
		winner_id = self.winner
		looser_id = self.plyIds[0] \
			if self.winner == self.plyIds[1] else self.plyIds[1]
		winner_name = self.names[0] \
			if winner_id == self.plyIds[0] else self.names[1]
		looser_name = self.names[1] \
			if winner_id == self.plyIds[0] else self.names[0]	
		self.users = [p for p in match_consumer.players
			if self.id == p["matchId"]]
		for p in self.users:
			print(f"users {p}", flush=True)
			try:					
				await p["socket"].send(text_data=json.dumps({
				"state": self.state.name,			
				"winnerId": winner_id,
				"looserId": looser_id,
				"names": self.names,
				"winnerName": winner_name,
				"looserName": looser_name,
				"score": self.score
				}))
			except Exception as e:
				pass		
		print(f"BEFORE SEND MATCH RESULT", flush=True)


		# response = requests.post(
		# 	"http://tournament:8001/tournament/match-result/", json={
		# 	"matchId": self.id,
		# 	"winnerId": self.winner,
		# 	"looserId": self.idP1 if self.winner == self.idP2 else self.idP2,
		# 	"p1Id": self.idP1,
		# 	"p2Id": self.idP2,
		# 	"score": self.score
		# })

		# if response.status_code not in [200, 201]:
		# 	print(f"Error HTTP {response.status_code}: {response.text}")
	
		async with aiohttp.ClientSession() as session:
			async with session.post(
				"http://tournament:8001/tournament/match-result/", json={
				"matchId": self.id,
				"winnerId": winner_id,
				"looserId": looser_id,
				"winnerName": winner_name,
				"looserName": looser_name,
				"p1Id": self.plyIds[0],
				"p2Id": self.plyIds[1],
				"score": self.score
			}) as response:				
				if response.status != 200 and response.status != 201:
					err = await response.text()
					print(f"Error HTTP {response.status}: {err}", flush=True)
		print(f"AFTER SEND MATCH RESULT", flush=True)
		from match_app.views import del_pong
		del_pong(self.id)

Pong.pad_commands = physics.pad_commands
Pong.pad_command = physics.pad_command
Pong.bounces = physics.bounces
Pong.vert_bounce = physics.vert_bounce
Pong.horz_bounce = physics.horz_bounce
Pong.are_pads_intersecting = physics.are_pads_intersecting
Pong.is_pad_intersecting = physics.is_pad_intersecting
Pong.segments_intersect = physics.segments_intersect
Pong.scale_vector = physics.scale_vector
Pong.get_magnitude = physics.get_magnitude
Pong.move_ball = physics.move_ball

Pong.scores = scores.scores
Pong.score_point = scores.score_point
Pong.max_score_rise = scores.max_score_rise
