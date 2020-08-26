import pygame
import sys
import threading
import time
import os

import color

# Inits that are run before variables

pygame.init()


# Data structures

class keys():
	A = 0
	B = 0
	C = 0
	D = 0
	E = 0
	F = 0
	G = 0
	H = 0
	I = 0
	J = 0
	K = 0
	L = 0
	M = 0
	N = 0
	O = 0
	P = 0
	Q = 0
	R = 0
	S = 0
	T = 0
	U = 0
	V = 0
	W = 0
	X = 0
	Y = 0
	Z = 0
	UP = 0
	DOWN = 0
	RIGHT = 0
	LEFT = 0
	NUM_1 = 0
	NUM_2 = 0
	NUM_3 = 0
	NUM_4 = 0
	NUM_5 = 0
	NUM_6 = 0
	NUM_7 = 0
	NUM_8 = 0
	NUM_9 = 0
	NUM_0 = 0
	SPACE = 0

# Local variables

updateAvailable = True
updateAvailableLock = threading.Lock()

screenWidth = 800
screenHeight = 600

renderThread = None

_objects = {"Type_Origin":[]}
_objectsLock = threading.Lock()

_display = pygame.display.set_mode((screenWidth, screenHeight))
_displayLock = threading.Lock()

gameStartTime = 0
_gameTimeLock = threading.Lock()

_lastTick = 0
_lastTickLock = threading.Lock()

_isPlaying = True
_isPlayingLock = threading.Lock()

frameRate = 1/60

_key = keys()
_keyLock = threading.Lock()

_tickTime = 0
_tickLock = threading.Lock()

# Game classes


class Camera:
	_Pos = [0, 0]

	@property
	def x(self):
		return self._Pos[0]

	@x.setter
	def x(self, value):
		self._Pos[0] = value

	@property
	def y(self):
		return self._Pos[1]

	@y.setter
	def y(self, value):
		self._Pos[1] = value


class Object:

	def __init__(self):

		# Private variables (Can only be accessed via function call)
		self._Pos = [0, 0]
		self._PosLock = threading.Lock()

		self._Dimensions = [1, 1]
		self._DimensionLock = threading.Lock()

		self.tag = None

		self.forceX = 0
		self.forceY = 0

	# User Interface

	def isCollidingWith(self, obj):
		if self is obj:
			return False

		if obj.x + obj.width >= self.x:
			if obj.x <= self.x + self.width:
				if obj.y + obj.height >= self.y:
					if obj.y <= self.y + self.height:
						return True

	def setPosition(self, pos, prohibitCollision=False):
		with self._PosLock:
			self._Pos[0] = pos[0]
			self._Pos[1] = pos[1]

	def destroy(self):
		self.Remove()
		with _objectsLock:
			if self in _objects[self.tag]:
				_objects[self.tag].remove(self)
		del self
	# Dimension property call methods
	# region
	@property
	def x(self):
		with self._PosLock:
			return self._Pos[0]

	@x.setter
	def x(self, value):
		self.setPosition((value, self.y))

	@property
	def y(self):
		with self._PosLock:
			return self._Pos[1]

	@y.setter
	def y(self, value):
		self.setPosition((self.x, value))
	

	@property
	def width(self):
		with self._DimensionLock:
			return self._Dimensions[0]
	

	@width.setter
	def width(self, value):
		with self._DimensionLock:
			self._Dimensions[0] = value
	

	@property
	def height(self):
		with self._DimensionLock:
			return self._Dimensions[1]
	

	@height.setter
	def height(self, value):
		with self._DimensionLock:
			self._Dimensions[1] = value
	
	# endregion

	# Overidables (To be overriden by user)

	def Remove(self):
		pass

	def Tick(self):
		pass

	def Render(self):
		pass

	# Inner Methods

	def tick(self):
		self.x += self.forceX * tickTime()
		self.y += self.forceY * tickTime()
		self.Tick()

	def render(self):
		self.Render()

# Inner Game functions/methods

def isPlaying():
	with _isPlayingLock:
		return _isPlaying

def eventManager():

	# Runs for each registered event
	for event in pygame.event.get():

		# Check if quit button clicked
		if event.type == pygame.QUIT:
			with _isPlayingLock:
				_isPlaying = False
			sys.exit()

		# If keydown event update key input for key class
		if event.type == pygame.KEYDOWN:
			#print(event.key)
			UP = 273
			DOWN = 274
			RIGHT = 275
			LEFT = 276
			SPACE = 32

			if event.key == UP:
				setattr(getKey(), "UP", 1)
				continue
			if event.key == DOWN:
				setattr(getKey(), "DOWN", 1)
				continue
			if event.key == RIGHT:
				setattr(getKey(), "RIGHT", 1)
				continue
			if event.key == LEFT:
				setattr(getKey(), "LEFT", 1)
				continue
			if event.key == SPACE:
				setattr(getKey(), "SPACE", 1)
				continue


			# Set key based on char if not unique key
			setattr(getKey(), chr(event.key).upper(), 1)
			#print(chr(event.key))
		
		# Update key class for keyup event
		if event.type == pygame.KEYUP:

			UP = 273
			DOWN = 274
			RIGHT = 275
			LEFT = 276
			SPACE = 32

			if event.key == UP:
				setattr(getKey(), "UP", 0)
				continue
			if event.key == DOWN:
				setattr(getKey(), "DOWN", 0)
				continue
			if event.key == RIGHT:
				setattr(getKey(), "RIGHT", 0)
				continue
			if event.key == LEFT:
				setattr(getKey(), "LEFT", 0)
				continue
			if event.key == SPACE:
				setattr(getKey(), "SPACE", 0)
				continue
			
			setattr(getKey(), chr(event.key).upper(), 0)

def renderTick():
	tempObjects = None
	with _objectsLock:
		tempObjects = _objects
	
	for key in list(tempObjects):
		for obj in tempObjects[key]:
			obj.tick()
	
	global updateAvailable
	with updateAvailableLock:
		updateAvailable = True

def render():
	lastFrame = time.time()
	while isPlaying():

		if not time.time() - lastFrame >= frameRate:
			continue

		with updateAvailableLock:
			global updateAvailable
			if not updateAvailable:
				continue
			else:
				updateAvailable = False

		getScreen().fill((20, 20, 20))

		localObjects = None
		with _objectsLock:
			localObjects = _objects

		for key in list(localObjects):
			for obj in localObjects[key]:
				if obj:
					obj.render()
		
		pygame.display.update()

def gameLoop():
	global _lastTick

	tempTick = gameTime()

	eventManager()

	with _tickLock:
		global _tickTime
		_tickTime = gameTime() - lastTick()

	renderTick()

	with _lastTickLock:
		_lastTick = tempTick


# Exposed Game functions/methods


def addObject(obj, tag="Type_Origin"):
	if str(type(obj)) == "<class 'type'>":
		print("Error uninstatiated class")
		sys.exit()
	with _objectsLock:
		if not tag in _objects:
			_objects[tag] = []
		_objects[tag].append(obj)
	obj.tag = tag



def removeObject(obj):
	with _objectsLock:
		_objects[obj.tag].remove(obj)


def getObjectsWithTag(tag):
	with _objectsLock:
		if not tag in _objects:
			return []
		return _objects[tag]


def getObjectWithName(name):
	pass


def run():

	global gameStartTime
	with _gameTimeLock:
		gameStartTime = time.time()

	with _lastTickLock:
		_lastTick = gameTime()

	global renderThread
	renderThread = threading.Thread(target=render, daemon=True)
	renderThread.start()

	time.sleep(0.001)
	while isPlaying():
		gameLoop()


def gameTime():
	with _gameTimeLock:
		return time.time() - gameStartTime


def lastTick():
	with _lastTickLock:
		return _lastTick


def tickTime():
	with _tickLock:
		return _tickTime
	


def getKey():
	with _keyLock:
		return _key


# draw functions

def getScreen():
	with _displayLock:
		return _display


def drawRect(obj = None, x = 0, y = 0, width = 0, height = 0, color = (255, 255, 255), debug=False):
	if not obj == None:
		#if debug == True:
			#print("Draw data = " + str(obj.x) + " and " + str(obj.y))
		pygame.draw.rect(getScreen(), color, (obj.x, obj.y, obj.width, obj.height))
		return
	pygame.draw.rect(getScreen(), color, (x, y, width, height))

def loadImage(imagePath, width = None, height = None):
	path = os.path.dirname(os.path.abspath(__file__)) + imagePath
	image = pygame.image.load(r'{}'.format(path))
	if not width == None and not height == None:
		image = pygame.transform.scale(image, (width, height))
	image.convert_alpha()
	image.convert()
	return image

def drawImage(image, obj=None, x=None, y=None):
	if obj:
		x = obj.x
		y = obj.y
	getScreen().blit(image, (x, y))
