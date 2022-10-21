from PIL import Image
import os
from pathlib import Path
import random

import imgdefs
from config import SYSTEMS


GRID_SIZE = 35
GLOW_SIZE = (22,16)
PILOT_GLOW_SIZE = (19,16)


#  #56#
#  1  3
#  2  4
#  #78#

def imgClockwise(station, size, img):
	if station and station[0] != -2:
		if station[0] not in (0,1,2,3):
			print("[ERROR] station is", station)
		if size[0] == 1:
			station[0] = [1,0][station[0]]
		elif size[1] == 1:
			station[0] = [0,1][station[0]]
		else:
			station[0] = [1,3,0,2][station[0]]
		if station[1] != "no":
			station[1] = {"up":"right","right":"down","down":"left","left":"up"}[station[1]]
	size.reverse()
	img = img.transpose(Image.ROTATE_270)
	return station, size, img

def imgY(station, size, img):
	if station and station[0] != -2:
		if size[1] > 1:
			station[0] = ( station[0] + size[0] ) % (size[0]*size[1])
		if station[1] != "no":
			station[1] = {"up":"down","right":"right","down":"up","left":"left"}[station[1]]
		if len(station) > 2:
			station[2][0] = GRID_SIZE - (station[2][0] + station[3][0])
	img = img.transpose(Image.FLIP_TOP_BOTTOM)
	return station, size, img

def imgExtend(station, size, img):
	bg = Image.new("RGBA", (img.width, 2*img.height), (0,0,0,0))
	bg.paste(img, (0,0), img)
	size[1] += 1
	return station, size, bg

def rotateClockwise(walls, size):
	if size[0] == size[1] == 2:
		spins = {1:6,2:5,3:8,4:7,5:3,6:4,7:1,8:2}
	elif size[1] == 1:
		spins = {1:5,3:7,5:3,6:4,7:1,8:2}
	elif size[0] == 1:
		spins = {1:6,2:5,3:8,4:7,5:3,7:1}
	new_walls = []
	for wall in walls:
		try:
			new_walls.append(spins[wall])
		except KeyError:
			print(walls, size)
	size[0], size[1] = size[1], size[0]
	return new_walls, size

def mirrorY(walls, size):
	new_walls = []
	for wall in walls:
		if wall in (1,3):
			if size[1] > 1:
				wall += 1
		elif wall in (2,4):
			wall -= 1
		elif wall in (5,6):
			wall += 2
		elif wall in (7,8):
			wall -= 2
		new_walls.append(wall)
	return new_walls, size

def extend(walls, size):
	size[1] += 1
	return walls, size

def findRoomImage(room):
	#print("[DEBUG] Fetching image for %s"%room.system)
	if room.system == SYSTEMS.teleporter:
		return None, None
	elif room.system == SYSTEMS.clonebay:
		station = [random.randrange(room.dimensions[0] * room.dimensions[1]) , "no"]
		return None, station

	free_walls = []
	for wall, door in room.doors.items():
		if door is None:
			free_walls.append(wall)

	compatible_images = []
	for image in imgdefs.room_images[room.system]:
		if image[1] * image[2] > room.dimensions[0] * room.dimensions[1]:
			#this room image is too big
			continue
		#print("Testing image %s"%image[0])

		#this keeps track of how we've messed with the image so we can know the manning station
		transformations = []
		blocked_walls = image[3]
		station = None
		size = [image[1], image[2]]
		priority = 0
		if len(image) > 4:
			station = [image[4], "no"]
			if len(image) > 5:
				station[1] = image[5]
				if len(image) > 6:
					#convert glow positions to relative so rotating/mirroring doesn't affect them
					glow = GLOW_SIZE
					if room.system == SYSTEMS.pilot:
						glow = PILOT_GLOW_SIZE
					x = image[6] % GRID_SIZE
					y = image[7] % GRID_SIZE
					if station[1] == "up":
						station.append([x, y])
					elif station[1] == "right":
						station.append([y, GRID_SIZE - (x + glow[1])])
					elif station[1] == "down":
						station.append([GRID_SIZE - (x + glow[0]), GRID_SIZE - (y + glow[1])])
					elif station[1] == "left":
						station.append([GRID_SIZE - (y + glow[0]), x])
					#print("[abs] %s x%i y%i to relative %s"%(image[0], image[6],image[7],station))
					station.append(glow)

		if (room.dimensions[0] == 2 and size[0] == 1) or (room.dimensions[0] == 1 and size[1] == 1):
			#make the image lie horizontal if it's 1x2 and the room is 2x1 or 2x2
			#or make it stand up if the room is 1x2
			#print("Rotating bc room is %s whereas image is %s"%(room.dimensions, size))
			transformations.append("rot")
			blocked_walls, size = rotateClockwise(blocked_walls, size)

		if room.dimensions[0] == room.dimensions[1] == 2 and size[1] == 1:
			#extend the image vertically
			#print("Extending bc room is %s whereas image is %s"%(room.dimensions, size))
			#set priority really low because we want to avoid using extended images where possible
			priority -= 10
			if (7 not in blocked_walls and 8 not in blocked_walls):
				#extend it
				transformations.append("extend")
				blocked_walls, size = extend(blocked_walls, size)
			elif (5 not in blocked_walls and 6 not in blocked_walls):
				#mirror it, then extend
				transformations.append("mirrorY")
				blocked_walls, size = mirrorY(blocked_walls, size)
				transformations.append("extend")
				blocked_walls, size = extend(blocked_walls, size)
			else:
				#this image can't be extended
				continue

		#print("Checkpoint! :D")
		priority += len(blocked_walls)
		if len(blocked_walls) == 0:
			compatible_images.append([image[0], transformations, station, size, priority])
			continue
		#this'll just loop through all possible configurations of the room achievable via rotations and mirrors
		for i in range(2):
			#print("loop i",i)
			for j in range(4):
				#print("loop j",j)
				#if j%2 == 1 and room.dimensions[0] != room.dimensions[1]:
				#	continue
				if size[0] == room.dimensions[0] and size[1] == room.dimensions[1]:
					collides = False
					for wall in blocked_walls:
						if wall not in free_walls:
							#print("[DEBUG] room %s when transformed using %s has blocked walls %s which are not a subset of %s in %s"%(image[0], transformations, blocked_walls, free_walls, room.system))
							collides = True
							break
					else:
						#print("Found compatible image! Aww yeah! %s %s %s(c%s)"%(image[0], transformations, blocked_walls, free_walls))
						compatible_images.append([image[0], tuple(transformations), station, [image[1], image[2]], priority ])
				#else:
					#print("Wrong size", size, room.dimensions)
				transformations.append("rot")
				blocked_walls, size = rotateClockwise(blocked_walls, size)
			#since we just went a full revolution we can remove the last 4 rotations
			transformations = transformations[:-4]
			transformations.append("mirrorY")
			blocked_walls, size = mirrorY(blocked_walls, size)

	highest_priority_images = []
	highest_priority = None
	for image in compatible_images:
		if highest_priority is None or highest_priority < image[4]:
			highest_priority_images.clear()
			highest_priority = image[4]
			highest_priority_images.append(image)
		elif highest_priority == image[4]:
			highest_priority_images.append(image)
	image = random_from(highest_priority_images)

	if image is not None:
		transformations, station, size = image[1], image[2], image[3]
		imgname = room.system.value
		if len(image[0]) > 0:
			imgname = f"{imgname}_{image[0]}"
		pathname = f"ship/interior/room_{imgname}.png"
		for in_dir in ("img_extra", "img_originals"):
			if os.path.exists("%s/%s"%(in_dir, pathname)):
				pathname = "%s/%s"%(in_dir, pathname)
				break
		else:
			print("[ERROR] WTF no image file %s exists in img_originals or img_extra"%pathname)
			raise Exception

		img = Image.open(pathname)
		out_name = imgname
		for op in transformations:
			if op == "rot":
				#print("[DEBUG] Rotating image", station, size, out_name)
				station, size, img = imgClockwise(station, size, img)
				out_name += "r"
			elif op == "mirrorY":
				station, size, img = imgY(station, size, img)
				out_name += "y"
			elif op == "extend":
				station, size, img = imgExtend(station, size, img)
				out_name += "e"

		#stuff
		out_path = "img/ship/interior/room_%s.png"%out_name
		img.save(out_path)
		if room.system == "cloaking":
			glow_path = "img/ship/interior/room_%s_glow.png"%out_name
			if not os.path.exists(glow_path):
				glow_img = Image.open(pathname[:-4]+"_glow"+pathname[-4:])
				path = Path(glow_path)
				path.parent.mkdir(parents=True, exist_ok=True)
				glow_img.save(glow_path)

		if room.system in ("engines","shields","weapons","pilot"):
			with open("data/rooms.xml.append", "a") as f:
				x, y = 0, 0
				if len(station) > 2:
					if station[1] == "up":
						x, y = station[2]
					elif station[1] == "right":
						x, y = GRID_SIZE - (station[2][1] + station[3][1]), station[2][0]
					elif station[1] == "down":
						x, y = GRID_SIZE - (station[2][0] + station[3][0]), GRID_SIZE - (station[2][1] + station[3][1])
					elif station[1] == "left":
						x, y = station[2][1], GRID_SIZE - (station[2][0] + station[3][0])
						if room.system == "pilot":
							x += 1
							y += 1
					x_offset = GRID_SIZE * (station[0]%2) if size[0] > 1 else 0
					y_offset = GRID_SIZE * (station[0]//size[0]) if size[1] > 1 else 0
					x += x_offset
					y += y_offset
					#print("[DEBUG] Image %s"%out_name)
					#print("[DEBUG] Relative %s to absolute %i, %i"%(station, x, y))
				pilot_str = ""
				if room.system == "pilot":
					pilot_str = 'name="glow_pilot"'
				glow_str = '<computerGlow %s x="%i" y="%i" dir="%s" />'%(pilot_str, x, y, station[1].upper())
				room_str = '<roomLayout name="%s">\n\t%s\n</roomLayout>\n'%(out_name, glow_str)
				f.write(room_str)

		#print("Successfully found %s"%out_name)
		return out_name, station

		#TODO: append room.xml for glows

	print("[ERROR] No suitable image found for %s"%room.system)
	print(room.dimensions, room.doors)
	raise Exception
	return None, None



def random_from(arr):
	l = len(arr)-1
	if l == -1:
		return None
	return arr[random.randint(0,l)]

