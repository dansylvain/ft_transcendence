import asyncio
import operator as op

async def scores(self):
	
	await self.score_point(op.ge, limit=100, score_idx=0)
	await self.score_point(op.le, limit=0, score_idx=1)
	await self.max_score_rise(ply_idx=0)
	await self.max_score_rise(ply_idx=1)
	
async def score_point(self, cmp, limit, score_idx):

	if cmp(self.ball[0], limit):
		self.score[score_idx] += 1
		self.ball = self.ball_rst.copy()
		self.vect = self.get_random_vector()
		await self.send_start(0)
		self.tasks.append(
			self.myEventLoop.create_task(self.watch_cat(self.point_delay)))

async def max_score_rise(self, ply_idx):
	
	from match_app.services.pong import State
	
	if self.max_score == self.score[ply_idx]: 
		self.winner = self.plyIds[ply_idx]		
		await self.sendFinalState()
