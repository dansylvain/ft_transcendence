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
		elif player["dir"] == 'down':					
			self.pads_y[pad_idx] = min(
				self.pads_y[pad_idx] + self.pad_speed,
				100 - (self.pad_height / 2)
			)					
		player["dir"] = None

async def bounces(self):

	await self.horz_bounce(op.le, limit=self.x_left_pad, pad_y_idx=0, dir=+1)
	await self.horz_bounce(op.ge, limit=self.x_rght_pad, pad_y_idx=1, dir=-1)
	# await self.vert_bounce
	await self.vert_bounce(op.le, limit=self.y_top)
	await self.vert_bounce(op.ge, limit=self.y_bot)
		
async def horz_bounce(self, cmp, limit, pad_y_idx, dir):

	if self.is_pad_intersecting(cmp, limit, pad_y_idx):			
		new_vect = [0, 0]
		new_vect[0] = limit - self.ball[0]
		new_vect[1] = self.scale_vector(
			new_vect[0], self.vect[1], self.vect[0])
		self.ball[0] += new_vect[0]				
		self.ball[1] += new_vect[1]
		self.has_wall = True
		# await asyncio.sleep(self.bounce_delay)				
		await self.sendState();	
		mag = self.get_magnitude(self.vect) 				
		y = (self.ball[1] - self.pads_y[pad_y_idx]) / (self.pad_height / 2) 
		y = y * mag
		# y = max(min(y, 0.9), -0.9)
		x = (self.vect[0] ** 2) + (self.vect[1] ** 2) - (y ** 2)								
		x = math.sqrt(abs(x))	

		scl = 1
		if abs(self.vect[0]) < self.max_ball_speed and \
			abs(self.vect[1]) < self.max_ball_speed:
			scl = self.ball_acceleration
		self.vect[0] = scl * x * dir
		self.vect[1] = scl * y 				
		self.wall_flag = False

# def updown_side_pad_bounce(self):
# 	if self.is_updown_side_pad_intersecting()

	

async def vert_bounce(self, cmp, limit):
	
	# if self.are_pads_intersecting():
	# 	return
	if cmp(self.ball[1] + self.vect[1], limit) and self.wall_flag:
		bounce_vect = [0, 0]
		bounce_vect[1] = limit - self.ball[1]
		bounce_vect[0] = self.scale_vector(
			bounce_vect[1], self.vect[0], self.vect[1])		
		self.ball[0] += bounce_vect[0]				
		self.ball[1] += bounce_vect[1]
		self.has_wall = True
		# await asyncio.sleep(self.bounce_delay)	
		await self.sendState();	
		self.vect[1] = -self.vect[1]		
		self.wall_flag = False

# def are_pads_intersecting(self):

# 	return \
# 		self.is_pad_intersecting(op.ge, limit=self.x_rght_pad, pad_y_idx=1) or \
# 		self.is_pad_intersecting(op.le, limit=self.x_left_pad, pad_y_idx=0)

# def is_sidepad_intersecting(self, cmp, limit, pad_y_idx):

# 	return self.segments_intersect(
# 			(self.ball[0], self.ball[1]),
# 			(self.ball[0] + self.vect[0], self.ball[1] + self.vect[1]),
# 			(limit, self.pads_y[pad_y_idx] - (self.pad_height / 2)),
# 			(limit, self.pads_y[pad_y_idx] + (self.pad_height / 2)))

def is_pad_intersecting(self, cmp, limit, pad_y_idx): #opti cmp!!!!!

	return cmp(self.ball[0] + self.vect[0], limit) and \
		self.segments_intersect(
			(self.ball[0], self.ball[1]),
			(self.ball[0] + self.vect[0], self.ball[1] + self.vect[1]),
			(limit, self.pads_y[pad_y_idx] - (self.pad_height / 2)),
			(limit, self.pads_y[pad_y_idx] + (self.pad_height / 2)))
	
def segments_intersect(self, A, B, C, D, eps=1e-9):

	def orientation(p, q, r):
		# Déterminant orienté
		val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
		if abs(val) < eps:
			return 0  # colinéaire
		return 1 if val > 0 else 2  # 1: horaire, 2: anti-horaire

	def on_segment(p, q, r):
		# Vérifie si q est sur le segment [p, r]
		return (
			min(p[0], r[0]) - eps <= q[0] <= max(p[0], r[0]) + eps and
			min(p[1], r[1]) - eps <= q[1] <= max(p[1], r[1]) + eps
		)

	o1 = orientation(A, B, C)
	o2 = orientation(A, B, D)
	o3 = orientation(C, D, A)
	o4 = orientation(C, D, B)

	# Cas général
	if o1 != o2 and o3 != o4:
		return True

	# Cas particuliers (colinéaires)
	if o1 == 0 and on_segment(A, C, B): return True
	if o2 == 0 and on_segment(A, D, B): return True
	if o3 == 0 and on_segment(C, A, D): return True
	if o4 == 0 and on_segment(C, B, D): return True

	return False

def scale_vector(self, m1, m2, div):
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

# def substract_vect(self, vect_a, vect_b):
# 	new_vect = [0, 0]
# 	new_vect[0] = vect_a[0] - vect_b[0]
# 	new_vect[1] = vect_a[1] - vect_b[1]
# 	return new_vect