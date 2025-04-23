import math
import asyncio
import operator as op
import random

def pad_commands(self, players):
	
	self.pad_command(players[0], pad_idx=0)
	self.pad_command(players[1], pad_idx=1)
	
def pad_command(self, player, pad_idx):

	if player.get("dir") is not None :
		if player["dir"] == 'up':					
			self.pads_y[pad_idx] = max(
				self.pads_y[pad_idx] - self.pad_speed,
				(self.pad_height / 2)
			)
			self.are_pads_hurt_ball('up')								
		elif player["dir"] == 'down':					
			self.pads_y[pad_idx] = min(
				self.pads_y[pad_idx] + self.pad_speed,
				100 - (self.pad_height / 2)
			)
			self.are_pads_hurt_ball('dn')				
		player["dir"] = None

def are_pads_hurt_ball(self, sense):

	self.is_pad_hurt_ball(sense, (self.x_left_pad_back, self.x_left_pad),
		side=-1, pad_idx=0)
	self.is_pad_hurt_ball(sense, (self.x_rght_pad, self.x_rght_pad_back),
		side=+1, pad_idx=1)	

def is_pad_hurt_ball(self, sense, x_limits, side, pad_idx):

	if x_limits[0] < self.ball[0] < x_limits[1] and \
		self.pads_y[pad_idx] - self.pads_half_h < \
		self.ball[1] < \
		self.pads_y[pad_idx] + self.pads_half_h:
		if sense == "up":
			self.ball[1] = self.pads_y[pad_idx] - self.pads_half_h
			self.vect[1] = abs(self.vect[1])
			if self.ball[1] < self.y_top:
				self.ball[1] = self.y_top 
				self.pads_y[pad_idx] = self.up_pads_stuck 
				self.vect[0] = abs(self.vect[0]) * side
				self.vect[1] = 0
		elif sense == "dn":
			self.ball[1] = self.pads_y[pad_idx] + self.pads_half_h
			self.vect[1] = -abs(self.vect[1])
			if self.ball[1] > self.y_bot:
				self.ball[1] = self.y_bot
				self.pads_y[pad_idx] = self.dn_pads_stuck
				self.vect[0] = abs(self.vect[0]) * side
				self.vect[1] = 0

async def bounces(self):

	if self.vect[0] < 0:
		await self.horz_bounce(
			op.le, limit=self.x_left_pad, pad_y_idx=0, dir=+1
		)
	if self.vect[0] > 0:
		await self.horz_bounce(
			op.ge, limit=self.x_rght_pad, pad_y_idx=1, dir=-1
		)	
	await self.side_pads_bounces()	
	if self.vect[1] > 0:
		await self.vert_bounce(op.ge, limit=self.y_bot)
	if self.vect[1] < 0:
		await self.vert_bounce(op.le, limit=self.y_top)

async def side_pads_bounces(self):
		
	if self.vect[1] < 0:
		if self.vect[0] < 0:
			await self.side_pad_bounce(
				op.le, self.pads_y[0] + self.pads_half_h,
				self.x_left_pad, self.x_left_pad_back
			)
		if self.vect[0] > 0:
			await self.side_pad_bounce(
				op.ge, self.pads_y[1] + self.pads_half_h,
				self.x_rght_pad, self.x_rght_pad_back
			)
	if self.vect[1] > 0:
		if self.vect[0] < 0:
			await self.side_pad_bounce(
				op.le, self.pads_y[0] - self.pads_half_h,
				self.x_left_pad, self.x_left_pad_back
			)
		if self.vect[0] > 0:
			await self.side_pad_bounce(
				op.ge, self.pads_y[1] - self.pads_half_h,
				self.x_rght_pad, self.x_rght_pad_back
			)
			
async def horz_bounce(self, cmp, limit, pad_y_idx, dir):

	if self.is_pad_horz_intersect(cmp, limit, pad_y_idx):			
		bounce_vect = [0, 0]
		bounce_vect[0] = limit - self.ball[0]
		bounce_vect[1] = self.scale_vector(
			bounce_vect[0], self.vect[1], self.vect[0])
		if self.is_overflow(bounce_vect):
			return			
		self.ball[0] += bounce_vect[0]				
		self.ball[1] += bounce_vect[1]
		self.has_wall = True
		await asyncio.sleep(self.bounce_delay)
		mag = self.get_magnitude(self.vect) 				
		y = (self.ball[1] - self.pads_y[pad_y_idx]) / (self.pad_height / 2) 
		y = max(min(y, 0.9), -0.9)
		y = y * mag
		x = (self.vect[0] ** 2) + (self.vect[1] ** 2) - (y ** 2)								
		x = math.sqrt(abs(x))	
		scl = 1
		if abs(self.vect[0]) < self.max_ball_speed and \
			abs(self.vect[1]) < self.max_ball_speed:
			scl = self.ball_acceleration
		self.vect[0] = scl * x * dir
		self.vect[1] = scl * y 				
		self.wall_flag = False

def is_overflow(self, new_vect):	

	if self.x_left_pad_back < self.ball[0] + new_vect[0] < self.x_left_pad and \
		self.pads_y[0] - self.pads_half_h < \
		self.ball[1] + new_vect[1] < \
		self.pads_y[0] + self.pads_half_h:
		return True
	if self.x_rght_pad < self.ball[0] + new_vect[0] < self.x_rght_pad_back and \
		self.pads_y[1] - self.pads_half_h < \
		self.ball[1] + new_vect[1] < \
		self.pads_y[1] + self.pads_half_h:
		return True	
	if not self.y_top  <= self.ball[1] + new_vect[1] <= self.y_bot:
		return True
	return False

def touch_test(self):
	
	print(f"\033[37m{self.ball[0]}\033[0m" , flush=True)
	if self.ball[0] != self.x_left_pad and self.ball[0] != self.x_rght_pad: 
		print(f"\033[35m touch test horz: {self.ball[0]}\033[0m" , flush=True)
		
def speed_test(self, place, color):	

	if self.x_left_pad_back < self.ball[0] < self.x_left_pad and \
		self.pads_y[0] - self.pads_half_h < \
		self.ball[1] < \
		self.pads_y[0] + self.pads_half_h:
		print(
			f"\033[35m left horz \033[{color}m from {place} {self.ball}\033[0m"
			, flush=True
		)
	if self.x_rght_pad < self.ball[0] < self.x_rght_pad_back and \
		self.pads_y[1] - self.pads_half_h < \
		self.ball[1] < \
		self.pads_y[1] + self.pads_half_h:
		print(
			f"\033[35m rght horz \033[{color}m from {place} {self.ball}\033[0m"
			, flush=True
		)	
	if not self.y_top  <= self.ball[1] <= self.y_bot:
		print(
			f"\033[36m vert \033[{color}m from {place} {self.ball}\033[0m"
			, flush=True)

async def vert_bounce(self, cmp, limit):
	
	if self.wall_flag and cmp(self.ball[1] + self.vect[1], limit):
		await self.bounce(limit)

async def side_pad_bounce(self, cmp, y_side, x_side, x_side_back):

	if self.is_pad_vert_intersect(cmp, x_side,
		((x_side, y_side), (x_side_back, y_side))):
		await self.bounce(y_side)

async def bounce(self, limit):

	bounce_vect = [0, 0]
	bounce_vect[1] = limit - self.ball[1]
	bounce_vect[0] = self.scale_vector(
		bounce_vect[1], self.vect[0], self.vect[1])		
	if self.is_overflow(bounce_vect):
		return
	self.ball[0] += bounce_vect[0]				
	self.ball[1] += bounce_vect[1]
	self.has_wall = True
	await asyncio.sleep(self.bounce_delay)
	self.vect[1] = -self.vect[1]		
	self.wall_flag = False

def is_pad_vert_intersect(self, cmp, limit, segment):

	return cmp(self.ball[0] + self.vect[0], limit) and \
		self.segments_intersect(
			(self.ball[0], self.ball[1]),
			(self.ball[0] + self.vect[0], self.ball[1] + self.vect[1]),
			segment[0],
			segment[1]
		)

def is_pad_horz_intersect(self, cmp, limit, pad_y_idx): 

	return cmp(self.ball[0] + self.vect[0], limit) and \
		self.segments_intersect(
			(self.ball[0], self.ball[1]),
			(self.ball[0] + self.vect[0], self.ball[1] + self.vect[1]),
			(limit, self.pads_y[pad_y_idx] - self.pads_half_h),
			(limit, self.pads_y[pad_y_idx] + self.pads_half_h))
	
def segments_intersect(self, A, B, C, D, eps=1e-9):

	def orientation(p, q, r):

		val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
		if abs(val) < eps:
			return 0  
		return 1 if val > 0 else 2  
	
	def on_segment(p, q, r):	

		return (
			min(p[0], r[0]) - eps <= q[0] <= max(p[0], r[0]) + eps and
			min(p[1], r[1]) - eps <= q[1] <= max(p[1], r[1]) + eps
		)
	
	o1 = orientation(A, B, C)
	o2 = orientation(A, B, D)
	o3 = orientation(C, D, A)
	o4 = orientation(C, D, B)
	if o1 != o2 and o3 != o4:
		return True
	if o1 == 0 and on_segment(A, C, B): return True
	if o2 == 0 and on_segment(A, D, B): return True
	if o3 == 0 and on_segment(C, A, D): return True
	if o4 == 0 and on_segment(C, B, D): return True
	return False

def scale_vector(self, m1, m2, div):
	if div == 0:
		return m2
	return m1 * m2 / div

def get_magnitude(self, vect):
	return math.sqrt(vect[0] ** 2 + vect[1] ** 2)

def move_ball(self):

	if (self.wall_flag):			
		self.ball[0] += self.vect[0]				
		self.ball[1] += self.vect[1]	

def get_random_vector(self):

	neg_x = random.uniform(-self.ball_speed, -self.ball_speed / 2)
	pos_x = random.uniform(+self.ball_speed, +self.ball_speed / 2)
	x = random.choice([neg_x, pos_x])
	y = math.sqrt(abs(self.ball_speed ** 2 - x **2))
	y = random.choice([y, -y])
	return [x, y]
