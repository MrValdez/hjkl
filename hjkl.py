import pygame
import sys
import random
import math

import pygame._view 

pygame.init()
clock = pygame.time.Clock()
resolution = [800, 600]
window = pygame.display.set_mode(resolution)
pygame.display.set_caption("HJKL shooter")

font = pygame.font.Font("freesansbold.ttf", 30)
font_mode = pygame.font.Font("freesansbold.ttf", 20)

msg = ["123", "The quick brown fox jumps over the lazy dog"]
current_msg = "hello world"
currentBuffer = ""

currentMode = "Movement"

class Player:
	def __init__(self):
		self.img = pygame.image.load("eyelander.png")
		self.img = pygame.transform.scale2x(self.img)
		self.x, self.y = [resolution[0] / 2, resolution[1] / 2]
		self.speed = 5
	def draw(self, window):
		window.blit(self.img, [self.x, self.y])
	def updateInput(self, keys, prevkeys):
		if keys[pygame.K_h]: self.x -= self.speed
		if keys[pygame.K_j]: self.y += self.speed
		if keys[pygame.K_k]: self.y -= self.speed
		if keys[pygame.K_l]: self.x += self.speed

		if self.x < -5: self.x = -5
		if self.x + self.img.get_width() > resolution[0] + 5: 
			self.x = resolution[0] - self.img.get_width() + 5
		if self.y < -5: self.y = -5
		if self.y + self.img.get_height() > resolution[1] + 5: 
			self.y = resolution[1] - self.img.get_height() + 5
	def update(self, clock):
		pass

class Bullet():
	def __init__(self, player, target):
		self.img = pygame.image.load("air006.png")
		self.img.set_colorkey(self.img.get_at((0,0)))
		self.x, self.y = player.x, player.y
		self.img = pygame.transform.rotate(self.img, -40)
		self.img.set_alpha(205)
		self.target = target
		self.delta = [self.x - self.target.x, self.y - self.target.y]
		if self.delta[0] < -10: self.delta[0] = -10
		if self.delta[1] < -10: self.delta[1] = -10
		if self.delta[0] > +10: self.delta[0] = +10	
		if self.delta[1] > +10: self.delta[1] = +10	
		self.timer = 0
	def draw(self, window):
		window.blit(self.img, [self.x, self.y])
	def update(self, clock):
		self.timer += clock.get_time()
		speed = 30
		if self.timer > speed:
			self.timer -= speed
			self.x -= self.delta[0]
			self.y -= self.delta[1]
		
		for troll in trollList:
			if checkCollision(self, troll):
				troll.kill()
class Troll:
	def __init__(self, x, y):
		self.img = pygame.image.load("grob.png")
		self.img.set_colorkey(self.img.get_at((0,0)))
		self.x, self.y = x, y
		self.speed = random.randint(3, 5)
		self.cos = 0
		self.cos_direction = 1
		self.mirror = False
		self.moveDelta = 0
		self.moveTime = 300
		self.target = None
		self.touchingTroll = []
	def draw(self, window):
		img = pygame.transform.rotate(self.img, self.cos)
		if self.mirror:
			img = pygame.transform.flip(img, True, False)	
		window.blit(img, [self.x, self.y])
	def updatePlayerPos(self, player):
		diff = player.x - self.x
		self.mirror = diff > 0
		self.target = player
	def update(self, clock):
		self.cos += self.cos_direction
		if self.cos > +10 or \
		   self.cos < -10: 
			self.cos_direction *= -1 
		if len(self.touchingTroll) <= 0:
			self.moveDelta += clock.get_time()
			if self.moveDelta > self.moveTime:
				self.moveDelta -= self.moveTime
				self.move()
		for troll in self.touchingTroll:
			delta_x = troll.x - self.x
			delta_y = troll.y - self.y
			if delta_x > 0: 
				self.x -= 1
			else:
				self.x += 1
			if delta_y > 0: 
				self.y -= 1
			else:
				self.y += 1

		self.touchingTroll = []

		self.updateTouchTarget()	
	def move(self):
		if self.target is None: return

		delta_x = self.target.x - self.x
		delta_y = self.target.y - self.y

		if delta_x < 0: 
			self.x -= self.speed
		else:
			self.x += self.speed
		if delta_y < 0: 
			self.y -= self.speed
		else:
			self.y += self.speed
	def updateTouchTarget(self):
		if self.target is None: return

		collide = checkCollision(self, self.target)
		if collide:
			self.kill()

	def kill(self):
		global trollList
		trollList.remove(self)
		global deadTrollList
		deadTrollList.append(DeadTroll(self))			

class DeadTroll():
	def __init__(self, troll):
		self.img = pygame.image.load("grob.png")
		self.img.set_colorkey(self.img.get_at((0,0)))
		self.x, self.y = troll.x, troll.y
		self.img = pygame.transform.rotate(self.img, -40)
		self.mirror = troll.mirror
		if self.mirror:
			self.img = pygame.transform.flip(self.img, True, False)
		self.img.set_alpha(155)
	
		global deadTrollList
		deadTrollList.append(self)
		self.upForce = 40 
	def draw(self, window):
		window.blit(self.img, [self.x, self.y])
	def update(self, clock):
		if self.upForce > 0:
			self.y -= 1
			self.x += math.cos(self.upForce + 60) * \
					  (self.mirror if 1 else -1)
			self.upForce -= 1
		else:
			self.y += 1
		alpha = self.img.get_alpha()
		self.img.set_alpha(alpha - 1)

		if alpha == 30:
			createTroll()
		if alpha <= 10:
			global deadTrollList
			deadTrollList.remove(self)

def checkCollision(a, b):
	rectA = a.img.get_rect()
	rectB = b.img.get_rect()
	rectA.move_ip(a.x, a.y)
	rectB.move_ip(b.x, b.y)
	return rectA.colliderect(rectB)

player = Player()
keys = pygame.key.get_pressed()

trollList = []

def createTroll():
	global trollList
	if random.randint(0, 1) == 0:
		x = random.randint(-100, resolution[0] / 2 - 100)
	else:
		x = random.randint(resolution[0] / 2 + 100, resolution[0] + 100)
	if random.randint(0, 1) == 0:
		y = random.randint(-100, resolution[1] / 2 - 100)
	else:
		y = random.randint(resolution[1] / 2 + 100, resolution[1] + 100)
	troll = Troll(x, y)
	trollList.append(troll)	

for i in range(12):
	createTroll()

deadTrollList = []
bulletList = []

while True:
	clock.tick(60)
	window.fill(pygame.Color(0, 0, 0))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
	
	prevkeys = keys
	keys = pygame.key.get_pressed()
	key_mod = pygame.key.get_mods()

	if keys[pygame.K_F4] and key_mod & pygame.K_ALT:
		pygame.quit()

	# mode change
	if keys[pygame.K_ESCAPE]:
		currentMode = "movement"
	if currentMode.lower() == "movement":
		if keys[pygame.K_i] or \
		   keys[pygame.K_a] or \
		   keys[pygame.K_o]:
			currentMode = "editing"
		elif keys[pygame.K_r]:
			currentMode = "replacing"

	if currentMode.lower() == "movement":
		player.updateInput(keys, prevkeys)
	else:
		# get the next character to type
		# if its a space, add space to buffer and
		# go to the next character
		# if the current message is complete, get
		# a new one
		correctKeys = False

		def EntrySuccess():
			global currentBuffer, current_msg

			currentBuffer = ""
			current_msg = random.choice(msg)
			
			global bulletList

			# find closest troll
			target = None
			smallestDistance = 99999.0
			for troll in trollList:
				x = player.x - troll.x
				y = player.y - troll.y
				d = math.sqrt(x * x + y * y)		
				if d < smallestDistance:
					smallestDistance = d
					target = troll	
			if not target is None:			
				bullet = Bullet(player, target)
				bulletList.append(bullet)
	
		while True:
			try:
				nextChar = current_msg[len(currentBuffer)]
			except IndexError:
				EntrySuccess()

			if not nextChar.isalnum():
				currentBuffer += nextChar
				continue	# not a character, so we try again

			ascii = ord(nextChar.lower()) # we lower the char as pygame only have constants for lowercase
			
			# This check if the key is held. If it is held,
			# we ignore the key. 
			# Example scenario without this code:
			# in "Hello", holding l would consider ll
			keypress_once = keys[ascii] and prevkeys[ascii] == False
			if not keypress_once:
				break
 
			# check non-numeric entries
			if nextChar.isalpha():
				# check lower case
				if nextChar.islower() and keys[ascii]:
					currentBuffer += nextChar
					correctKeys = True	
				# check upper case
				elif nextChar.isupper():
					mods = key_mod & pygame.KMOD_RSHIFT
					mods |= key_mod & pygame.KMOD_LSHIFT
					if mods & pygame.KMOD_SHIFT:
						if keys[ascii]:
							currentBuffer += nextChar
							correctKeys = True	
				if len(currentBuffer) >= len(current_msg):
					EntrySuccess()
			elif nextChar.isnumeric():
				if keys[ascii]:
					currentBuffer += nextChar
					correctKeys = True
				
			# if we get here, then the player typed the correct key
			break

		if correctKeys and currentMode.lower() == "replacing":
			currentMode = "movement"
	
	player.update(clock)
	for troll in trollList:
		troll.update(clock)
		troll.updatePlayerPos(player)
	for troll1 in trollList:
		for troll2 in trollList:
			if troll1 == troll2:
				continue
			collide = checkCollision(troll1, troll2)
			if collide:
				troll1.touchingTroll.append(troll2)
				troll2.touchingTroll.append(troll1)
	player.draw(window)
	for troll in trollList:
		troll.draw(window)

	for bullet in bulletList:
		bullet.update(clock)
		bullet.draw(window)
	
	for deadTroll in deadTrollList:
		deadTroll.update(clock)
		deadTroll.draw(window)

	text = font.render(current_msg, True, pygame.Color(255, 255, 255))	
	text_pos = [resolution[0] / 2 - text.get_width() / 2,
			    resolution[1] - text.get_height() - 60]
	window.blit(text, text_pos)

	text = font.render(currentBuffer, True, pygame.Color(0, 0, 255))	
	window.blit(text, text_pos)
	
	text = font_mode.render(currentMode.upper(), True, pygame.Color(0, 255, 0))	
	text_pos = [resolution[0] / 2 - text.get_width() / 2,
			    resolution[1] - text.get_height() - 20]
	window.blit(text, text_pos)
	
	pygame.display.update()
