import random
import math


import layoutinfo
from config import SYSTEMS

#idk these are arbitrary but they need to be large enough to fit all ships
GRID_WIDTH = 30
GRID_HEIGHT = 20

all_rooms = []
all_doors = []

# How many blocked wall pieces the system art requires
SYSTEM_GRUMPINESS = {
	0: [
		SYSTEMS.clonebay,
		SYSTEMS.mind,
		SYSTEMS.teleporter,
		],
	1: [
		SYSTEMS.artillery,
		SYSTEMS.battery,
		SYSTEMS.cloaking,
		SYSTEMS.doors,
		SYSTEMS.drones,
		SYSTEMS.medbay,
		SYSTEMS.oxygen,
		SYSTEMS.pilot,
		SYSTEMS.hacking,
		],
	#should I just make sensors into a 1?
	2: [
		SYSTEMS.engines,
		SYSTEMS.weapons,
		SYSTEMS.sensors,
		SYSTEMS.shields,
		]
}


def generateLayout(layout):
	all_rooms.clear()
	all_doors.clear()

	makeRooms(layout)

	#print("[INFO] Created %i rooms in total"%len(all_rooms))
	if len(all_rooms) < 14:
		#print("[ERROR] Placed less than 14 rooms!")
		return 1

	for i, room in enumerate(all_rooms):
		#this will be used in the XML as well as as keys to find connections
		#it is also handy because it gives the index of a room in this list
		room.room_id = i

	findDoorPositions()

	connectAllRooms()

	calculateShortestPaths()
	reducePathLength()

	#this function currently does nothing except print the result
	#calculateAveragePathLength()

	createAirlocks()

	#should I put this before airlocks?
	#for the time being let's not worry about artillery 
	systems_to_place = tuple(filter(lambda s: s not in (SYSTEMS.clonebay, SYSTEMS.artillery), SYSTEMS))
	placeSystems(systems_to_place)

	return all_rooms, all_doors


def makeRooms(layout):
	size = layoutinfo.info.get(layout, (GRID_WIDTH, GRID_HEIGHT, 14))
	next_coords = [size[0]//2, size[1]//2]
	next_dimensions = [2, 2]
	fail_count = 0
	ATTEMPTS = 200
	#all vanilla ships are restricted to 14-20 rooms
	room_count = random.randint(size[2],20)
	while len(all_rooms) < room_count:
		fail_count += 1
		if fail_count > ATTEMPTS:
			#print("[WARN] failed to place %i rooms in %i attempts"%(room_count, ATTEMPTS))
			break
		if canPlace(*next_coords, next_dimensions, layout):
			#print("[DEBUG] placing %i by %i room at x%i y%i"%(*next_dimensions, *next_coords))
			Room(next_coords, next_dimensions)
		else:
			jumped_room = random_from(all_rooms)
			if jumped_room == None:
				next_coords = [ random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1) ]
				next_dimensions = random_from(([1,2], [2,2], [2,1]))
			else:
				next_coords = list(jumped_room.coords)
				next_dimensions = list(jumped_room.dimensions)

		old_dimensions = list(next_dimensions)
		next_dimensions = random_from(([1,2], [2,2], [2,1]))
		coords_mod = [random.randint(-1, 0), random.randint(-1, 0)]
		free_direction = random.randint(0, 1)
		coords_mod[free_direction] = random.randint(1-next_dimensions[free_direction], old_dimensions[free_direction]-1)
		if coords_mod[1-free_direction] == 0:
			coords_mod[1-free_direction] = old_dimensions[1-free_direction]
		else:
			coords_mod[1-free_direction] = -next_dimensions[1-free_direction]
		for i in (0, 1):
			next_coords[i] += coords_mod[i]
		#print("afterwards, old_dimensions %s, free_direction %s"%(old_dimensions, free_direction))


def random_from(arr):
	l = len(arr)-1
	if l == -1:
		return None
	return arr[random.randint(0,l)]

"""def weighted_choice(choices):
	if len(choices) == 0:
		return None
	total = sum(w for c, w in choices)
	r = random.uniform(0, total)
	upto = 0
	for c, w in choices:
		if upto + w > r:
			return c
		upto += w
	return None"""


class Door(object):
	def __init__(self, roomA, roomB=None, position=(0,0), vertical=True):
		global all_doors
		super(Door, self).__init__()
		all_doors.append(self)
		self.roomA = roomA
		self.roomB = roomB
		self.position = position #absolute (x, y)
		self.vertical = vertical

		roomA.doors[doorPosToWall(self, roomA)] = self
		if roomB is not None:
			roomB.doors[doorPosToWall(self, roomB)] = self
		"""else:
			print(roomA.doors, self)"""


	def getRenderCoords(self):
		shape = (6, 20)
		if self.vertical:
			w, h = shape
			x = self.position[0]*GRID_SIZE - w/2.0
			y = self.position[1]*GRID_SIZE + (GRID_SIZE - h)/2.0
		else:
			h, w = shape
			x = self.position[0]*GRID_SIZE + (GRID_SIZE - w)/2.0
			y = self.position[1]*GRID_SIZE - h/2.0
		return (x, y, w, h)

	def getColour(self):
		#return (255, 200, 150)
		return (255, 100, 0)

#  #56#
#  1  3
#  2  4
#  #78#

class Room(object):
	def __init__(self, coords, dimensions):
		global all_rooms
		super(Room, self).__init__()
		all_rooms.append(self)
		self.coords = tuple(coords) #coords on the grid, not screen
		self.dimensions = tuple(dimensions)
		self.oxygen = 100.0
		self.breaches = 0
		#a dict with room ids as keys and a list of wall pieces leading to that room as values
		self.neighbours = {}
		#a dict with room ids as keys and distance (in tiles) to that room
		self.shortestPaths = {}
		#room_id is set later
		self.room_id = None

		#a dict with wall pieces as keys and any door present there as value (else None)
		# - the keys are also handy for looping over all present wall pieces
		self.doors = {}
		walls = [1,3,5,7]
		if self.dimensions[0] == 2:
			walls.extend((6,8))
		if self.dimensions[1] == 2:
			walls.extend((2,4))
		for wall in walls:
			self.doors[wall] = None

		self.system = None


	def getColour(self):
		if self.oxygen < 5.0:
			return (round(self.oxygen*50), 0, 255)
		return (255,round(2.55*self.oxygen),round(2.55*self.oxygen))

	def getTileCount(self):
		return self.dimensions[0] * self.dimensions[1]

	def getCPD(self, dimension):
		#coord plus dimension
		return self.coords[dimension] + self.dimensions[dimension]


#def distance_between(x1,y1,x2,y2):
#	d = math.sqrt( abs(x1-x2)**2 + abs(y1-y2)**2 )
#	return d


def placeSystems(systems_to_place):
	grumpies = {}
	for key, item in SYSTEM_GRUMPINESS.items():
		grumpies[key] = []
		for system in item:
			if system in systems_to_place:
				grumpies[key].append(system)
	rooms_with_walls = {}
	max_walls = max(grumpies)
	i = 0
	for room in all_rooms:
		wall_count = 0
		for wall_piece, other_room in room.doors.items():
			if other_room is None:
				wall_count += 1
				#cap at the max required for systems
				if wall_count == max_walls:
					break
		if wall_count not in rooms_with_walls:
			rooms_with_walls[wall_count] = []
		rooms_with_walls[wall_count].append(room)
		i += 1
	considered_rooms = []
	considered_systems = []
	for wall_count in sorted(grumpies, reverse=True):
		considered_systems += grumpies[wall_count]
		considered_rooms += rooms_with_walls.get(wall_count, [])
		if len(considered_rooms) < len(considered_systems):
			print("[ERROR] Trying to put %i systems in only %i rooms!" % (len(considered_systems), len(considered_rooms)))
		while len(considered_systems) > 0:
			room, system = random_from(considered_rooms), random_from(considered_systems)
			#print("[DEBUG] Placing %s in room id %i"%(system,all_rooms.index(room)))
			considered_systems.remove(system)
			considered_rooms.remove(room)
			room.system = system

#def getOverlap(range1, range2):
#	return min(max(range1), max(range2)) - max(min(range2), min(range1))

def getRange(min, offset):
	return (min, min+offset)

def findCommonWalls(roomA, roomB):
	#print("finding common walls for %s room at %s and %s at %s"%(roomA.dimensions, roomA.coords, roomB.dimensions, roomB.coords))
	common_walls = []
	for mirrored in (0, 1):
		if mirrored:
			room1, room2 = roomA, roomB
		else:
			room1, room2 = roomB, roomA
		for direction in (0, 1):
			if room1.getCPD(direction) == room2.coords[direction]:
				for i in range(roomA.dimensions[1-direction]):
					if roomB.coords[1-direction] <= roomA.coords[1-direction] + i < roomB.getCPD(1-direction):
						common_walls.append(direction*4 + mirrored*2 + 1 + i)
	#print(common_walls)
	return common_walls

def findDoorPositions():
	#this creates the dict of neighbours for each room
	for room in all_rooms:
		#list of all wall pieces that may connect to space
		airlock_walls = list(room.doors)
		for other_room in all_rooms:
			if room is other_room:
				continue
			common_walls = findCommonWalls(room, other_room)
			if len(common_walls) > 0:
				room.neighbours[other_room.room_id] = common_walls
			for wall_piece in common_walls:
				#obviously not connected to space
				airlock_walls.remove(wall_piece)
		room.neighbours[-1] = airlock_walls


def findDoorAt(pos):
	x, y, vertical = pos
	for door in all_doors:
		if door.position[0] == x and door.position[1] == y and door.vertical == vertical:
			return door


def wallToDoorPos(room, wall):
	vertical = wall < 5
	x = 0 if wall in (1,2,5,7) else room.dimensions[0] - 1 + int(vertical)
	y = 0 if wall in (1,5,6,3) else room.dimensions[1] - int(vertical)
	return (x + room.coords[0] , y + room.coords[1] , vertical)

def doorPosToWall(door, room):
	x = door.position[0] - room.coords[0]
	y = door.position[1] - room.coords[1]
	pos = 1
	if door.vertical:
		#blarg
		a, b = y, x
	else:
		pos += 4
		a, b = x, y
	if a != 0:
		pos += 1
	if b != 0:
		pos += 2
	return pos


def getDoorDistance(door1, door2):
	#returns minimum distance required to walk from one door to the other
	x1, y1 = door1.position[0], door1.position[1]
	x2, y2 = door2.position[0], door2.position[1]
	if door1.vertical:
		xr1 = (x1 - 1, x1)
		yr1 = (y1, )
	else:
		xr1 = (x1, )
		yr1 = (y1 - 1, y1)
	if door2.vertical:
		xr2 = (x2 - 1, x2)
		yr2 = (y2, )
	else:
		xr2 = (x2, )
		yr2 = (y2 - 1, y2)

	x_dis = y_dis = None
	#any overlap in coords
	if any(x in xr2 for x in xr1):
		#this special case is needed because else the one-liner below gives 1 if the ranges are the same
		x_dis = 0
	else:
		x_dis = min( abs( min(xr1) - max(xr2) ), abs( min(xr2) - max(xr1) ) )
	if any(y in yr2 for y in yr1):
		y_dis = 0
	else:
		y_dis = min( abs( min(yr1) - max(yr2) ), abs( min(yr2) - max(yr1) ) )
	
	distance = math.sqrt( y_dis**2 + x_dis**2 )
	return distance


def connectAllRooms():
	#function to create doors between rooms in a way that ensures every room can be reached from all others
	#first, a list to keep track of rooms connected thus far - starting out with the first room
	connected_rooms = [ all_rooms[0] ]
	while len(connected_rooms) < len(all_rooms):
		#TODO: put a failsafe here so it doesn't freeze if there's an error and all rooms can't be connected for some reason
		room = random_from(connected_rooms)
		#make a list of the keys of the dict and pick randomly from that
		room_to_connect = random_from(list(room.neighbours))
		if room_to_connect == -1:
			#don't connect to space. Is this retarded?
			continue
		other_room = all_rooms[room_to_connect]
		if other_room in connected_rooms:
			#prevent all doors which are not strictly required - we'll add extra ones later?
			continue
		wall_to_doorify = random_from(room.neighbours[room_to_connect])
		if room.doors[wall_to_doorify] is None:
			door_pos = wallToDoorPos(room, wall_to_doorify)
			#do stuff eg. create door, append connected_rooms, etc.
			Door(room, other_room, (door_pos[0], door_pos[1]), door_pos[2])
			if other_room not in connected_rooms:
				connected_rooms.append(other_room)


def calculateShortestPaths():
	#do a breadth-first-search to find the shortest path from each room to all other rooms
	#this can then be used to find adjacent rooms with long shortest paths and put doors inbetween
	#print("calculating paths")
	for starting_room in all_rooms:
		#keep in mind that room.shortestPaths might not be empty, in case we've called this function before
		#list of tuples (door, distance)
		explored_doors = []
		for wall, door in starting_room.doors.items():
			if door is not None: #I could check that it's not an airlock but I don't think it's required
				explored_doors.append((door, 0))
		no_changes = False
		while no_changes == False:
			no_changes = True
			for door, distance in explored_doors:
				for room in (door.roomA, door.roomB):
					if room is None:
						continue
					for wall, other_door in room.doors.items():
						if other_door is door or other_door is None:
							continue
						for index, door_ in enumerate(explored_doors):
							if door_[0] is other_door:
								break
						else:
							index = -1
						new_distance = distance + getDoorDistance(door, other_door) + 1
						if index == -1 or new_distance < door_[1]:
							no_changes = False
							if index == -1:
								explored_doors.append((other_door, new_distance))
							else:
								explored_doors[index] = (other_door, new_distance)

		#convert distances to doors -> distances to rooms
		#always add 1 more than the distance to the closest door, I guess?
		for door, distance in explored_doors:
			for room in (door.roomA, door.roomB):
				if room is None:
					continue
				new_distance = distance + 1
				old_distance = starting_room.shortestPaths.get(room.room_id, None)
				if old_distance is None or old_distance > new_distance:
					starting_room.shortestPaths[room.room_id] = new_distance
	#print("done calculating paths")


def reducePathLength():
	#add doors between adjacent rooms which have a long shortest path
	for room in all_rooms:
		for other_room, common_walls in room.neighbours.items():
			if other_room == -1:
				continue
			if room.shortestPaths[other_room] + random.randint(0,7) > 10 or random.randint(0,10) == 0:
				wall_to_doorify = random_from(common_walls)
				if room.doors[wall_to_doorify] is None:
					door_pos = wallToDoorPos(room, wall_to_doorify)
					Door(room, all_rooms[other_room], (door_pos[0], door_pos[1]), door_pos[2])
					calculateShortestPaths()


"""def calculateAveragePathLength():
	sum_ = 0
	for room in all_rooms:
		for other_room in all_rooms:
			if room is other_room:
				continue
			sum_ += room.shortestPaths[other_room.room_id]
	average = sum_ / ( len(all_rooms) * (len(all_rooms) - 1) * 2 )
	print("[INFO] Average distance between rooms is %f"%average)"""


def createAirlocks():
	#blarg
	airlock_rooms = []
	for i in range(random.randint(0,len(all_rooms))):
		room = random_from(all_rooms)
		wall_piece = random_from(room.neighbours[-1])
		if wall_piece is None:
			continue
		x, y, vertical = wallToDoorPos(room, wall_piece)
		if not findDoorAt((x,y,vertical)):
			other_room = random_from(airlock_rooms)
			if other_room is not room and other_room is not None and room.shortestPaths[other_room.room_id] < random.randint(0,4):
				continue
			Door(room, None, (x,y), vertical)
			if not room in airlock_rooms:
				airlock_rooms.append(room)


"""def createAllAirlocks():
	#test function for placing every possible airlock
	for room in all_rooms:
		for wall in room.neighbours[-1]:
			x, y, vertical = wallToDoorPos(room, wall)
			Door(room, None, (x, y), vertical)"""


def canPlace(x, y, dimensions, layout):
	w = dimensions[0]
	h = dimensions[1]
	if x+w > GRID_WIDTH or y+h > GRID_HEIGHT or x < 0 or y < 0:
		#print("Outside border")
		return False

	size = layoutinfo.info.get(layout, (GRID_WIDTH, GRID_HEIGHT))
	if x < 0 or y < 0 or x+w > size[0] or y+h > size[1]:
		return False
	#if (x < 2 and y < 6) or (x+w > 8 and y < 2) or (x+w > 10 and y < 8) or (x+w > 5 and x < 8 and y+h > 3 and y < 4) or (x+w > 5 and x < 6 and y+h > 3 and y < 5):
	#	return False
	for block in layoutinfo.blocked[layout]:
		if len(block) > 3 and (x < block[0]+block[2] and block[0] < x+w and y < block[1]+block[3] and block[1] < y+h):
			return False

	for room in all_rooms:
		if room.getCPD(0) > x and x+w > room.coords[0] and room.getCPD(1) > y and y+h > room.coords[1]:
			return False
	return True


