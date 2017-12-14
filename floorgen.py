from PIL import Image, ImageDraw
import os

GRID_WIDTH = 30
GRID_HEIGHT = 20

GRID_SIZE = 35
floorMargin = 4
borderWidth = 2
cornerSize = 2
floorColor = (100,105,111)
borderColor = (0,0,0)
offset = floorMargin + borderWidth

#this is kinda horrible but oh well... this global is set whenever a new floor image is generated
all_doors = None


def generateFloorImage(all_rooms, doors, out_path):
	global all_doors
	all_doors = doors
	#print("got %i doors"%len(all_doors))

	#tiles = a matrix which I guess has null if there is no room with a tile at this spot? I'm gonna make it True/False
	tiles = []
	for x in range(GRID_WIDTH):
		tiles.append([False] * GRID_HEIGHT)
	for room in all_rooms:
		for x in range(room.dimensions[0]):
			for y in range(room.dimensions[1]):
				tiles[x + room.coords[0]][y + room.coords[1]] = True

	"""print("Before cropping:")
	for y, _ in enumerate(tiles[0]):
		print([int(col[y]) for col in tiles])"""

	#let's trim the grid to not have extra rows
	x_off = 0
	for x, col in list(enumerate(tiles)):
		broken = True
		for y, tile in enumerate(col):
			if tile is True:
				break
		else:
			broken = False
			tiles.pop(0)
			x_off += 1
		if broken:
			break
	for x, col in reversed(list(enumerate(tiles))):
		broken = True
		for y, tile in enumerate(col):
			if tile is True:
				break
		else:
			broken = False
			tiles.pop()
		if broken:
			break
	y_off = 0
	for y, _ in enumerate(tiles[0]):
		broken = True
		for x, col in enumerate(tiles):
			if col[0] is True:
				break
		else:
			broken = False
			for col in tiles:
				col.pop(0)
			y_off += 1
		if broken:
			break
	for y, _ in reversed(list(enumerate(tiles[0]))):
		broken = True
		for x, col in enumerate(tiles):
			if col[-1] is True:
				break
		else:
			broken = False
			for col in tiles:
				col.pop()
		if broken:
			break

	"""print("After cropping:")
	for y, _ in enumerate(tiles[0]):
		print([int(col[y]) for col in tiles])"""

	#add back one layer of padding in every direction to make life easier
	for col in tiles:
		col.insert(0, False)
		col.append(False)
	tiles.append([False]*len(tiles[0]))
	tiles.insert(0, [False]*len(tiles[0]))

	#gc = a new image filled with transparency
	img = Image.new("RGBA", (len(tiles)*GRID_SIZE + 2*offset, len(tiles[0])*GRID_SIZE + 2*offset), (0,0,0,0))
	gc = ImageDraw.Draw(img)

	for x, col in enumerate(tiles):
		for y, tile in enumerate(col):
			if tile is False:
				continue
			x_tot, y_tot = x+x_off - 1, y+y_off - 1
			xy = (x*GRID_SIZE, y*GRID_SIZE, (x+1)*GRID_SIZE, (y+1)*GRID_SIZE)
			gc.rectangle(xy, fill=floorColor)

			if y > 0 and not tiles[x][y-1]:
				if hasAirlockAt((x_tot, y_tot, False)):
					#has airlock above
					cx, cy = x * GRID_SIZE, y * GRID_SIZE
					if x > 0 and tiles[x-1][y-1]:
						cx += floorMargin
					if isDoubleDent(tiles, x,y) or not hasAirlockAt((x_tot-1, y_tot, False)):
					#if not (isDent(tiles, x,y) or isDoubleDent(tiles, x,y) or hasAirlockAt((x_tot-1, y_tot, False))):
						#corner = not (isDent(tiles, x,y) or isDoubleDent(tiles, x,y))
						drawTopRightCorner(gc, cx, cy)

					cx = (x+1) * GRID_SIZE
					if x+1 < len(tiles) and tiles[x+1][y-1]:
						cx -= floorMargin
					if isDoubleDent(tiles, x+1,y) or not hasAirlockAt((x_tot+1, y_tot, False)):
					#if not (isDent(tiles, x+1,y) or isDoubleDent(tiles, x+1,y) or hasAirlockAt((x_tot+1, y_tot, False))):
						#corner = not (isDent(tiles, x+1,y) or isDoubleDent(tiles, x+1,y))
						drawTopLeftCorner(gc, cx, cy)
				else:
					if isDent(tiles, x,y) or isDoubleDent(tiles, x,y):
						rect(gc, (x*GRID_SIZE + floorMargin + 1, y*GRID_SIZE - floorMargin - borderWidth,
										GRID_SIZE - floorMargin - 2, floorMargin + borderWidth), fill=borderColor)
					else:
						rect(gc, (x*GRID_SIZE, y*GRID_SIZE - floorMargin - borderWidth,
										GRID_SIZE, floorMargin + borderWidth), fill=borderColor)
					rect(gc, (x*GRID_SIZE, y*GRID_SIZE - floorMargin, GRID_SIZE, floorMargin), fill=floorColor)

			if x > 0 and not tiles[x-1][y]:
				if hasAirlockAt((x_tot, y_tot, True)):
					#has airlock to the left
					cx, cy = x * GRID_SIZE, y * GRID_SIZE
					if hasAirlockAt((x_tot-1, y_tot, False)):
						rect(gc, (cx - floorMargin, cy, floorMargin, floorMargin), fill=floorColor)
					if hasAirlockAt((x_tot-1, y_tot+1, False)):
						rect(gc, (cx - floorMargin, cy + GRID_SIZE - floorMargin, floorMargin, floorMargin), fill=floorColor)

					if y > 0 and tiles[x-1][y-1]:
						cy += floorMargin
					if isDoubleDent(tiles, x,y) or not hasAirlockAt((x_tot, y_tot-1, True)):
					#if not (isDent(tiles, x,y) or isDoubleDent(tiles, x,y) or hasAirlockAt((x_tot, y_tot-1, True))):
						#corner = not (isDent(tiles, x,y) or isDoubleDent(tiles, x,y))
						drawBottomLeftCorner(gc, cx, cy)

					cy = (y+1) * GRID_SIZE
					if y < len(tiles[0])-1 and tiles[x-1][y+1]:
						cy -= floorMargin
					if isDoubleDent(tiles, x,y+1) or not hasAirlockAt((x_tot, y_tot+1, True)):
					#if not (isDent(tiles, x,y+1) or isDoubleDent(tiles, x,y+1) or hasAirlockAt((x_tot, y_tot+1, True))):
						special = isDent(tiles, x,y+1) or isDoubleDent(tiles, x,y+1)
						drawTopLeftCorner(gc, cx, cy, special)
				else:
					dent = isDent(tiles, x,y) or isDoubleDent(tiles, x,y)
					lowerDent = isDent(tiles, x,y+1) or isDoubleDent(tiles, x,y+1)
					if dent and lowerDent:
						rect(gc, (x*GRID_SIZE - floorMargin - borderWidth, y*GRID_SIZE + floorMargin +1,
										floorMargin + borderWidth, GRID_SIZE - floorMargin*2 -2), fill=borderColor)
					elif dent:
						rect(gc, (x*GRID_SIZE - floorMargin - borderWidth, y*GRID_SIZE + floorMargin +1,
										floorMargin + borderWidth, GRID_SIZE - floorMargin -2), fill=borderColor)
					elif lowerDent:
						rect(gc, (x*GRID_SIZE - floorMargin - borderWidth, y*GRID_SIZE,
										floorMargin + borderWidth, GRID_SIZE - floorMargin -1), fill=borderColor)
					else:
						rect(gc, (x*GRID_SIZE - floorMargin - borderWidth, y*GRID_SIZE -1,
										floorMargin + borderWidth, GRID_SIZE +2), fill=borderColor)
					rect(gc, (x*GRID_SIZE - floorMargin, y*GRID_SIZE -1, floorMargin, GRID_SIZE +2), fill=floorColor)

			if y < len(tiles[0])-1 and not tiles[x][y+1]:
				if hasAirlockAt((x_tot, y_tot+1, False)):
					#has airlock below
					cx, cy = x * GRID_SIZE, (y+1) * GRID_SIZE
					if x > 0 and tiles[x-1][y+1]:
						cx += floorMargin
					if isDoubleDent(tiles, x,y+1) or not hasAirlockAt((x_tot-1, y_tot+1, False)):
					#if not (isDent(tiles, x,y+1) or isDoubleDent(tiles, x,y+1) or hasAirlockAt((x_tot-1, y_tot+1, False))):
						#corner = not (isDent(tiles, x,y+1) or isDoubleDent(tiles, x,y+1))
						drawBottomRightCorner(gc, cx, cy)

					cx = (x+1) * GRID_SIZE
					if x+1 < len(tiles) and tiles[x+1][y+1]:
						cx -= floorMargin
					if isDoubleDent(tiles, x+1,y+1) or not hasAirlockAt((x_tot+1, y_tot+1, False)):
					#if not (isDent(tiles, x+1,y+1) or isDoubleDent(tiles, x+1,y+1) or hasAirlockAt((x_tot+1, y_tot+1, False))):
						#corner = not (isDent(tiles, x+1,y+1) or isDoubleDent(tiles, x+1,y+1))
						drawBottomLeftCorner(gc, cx, cy)
				else:
					if isDent(tiles, x,y+1) or isDoubleDent(tiles, x,y+1):
						rect(gc, (x*GRID_SIZE + floorMargin + 1 -1, (y+1)*GRID_SIZE -1,
										GRID_SIZE - floorMargin - 2 +1, floorMargin + borderWidth), fill=borderColor)
					else:
						rect(gc, (x*GRID_SIZE, (y+1)*GRID_SIZE -1,
										GRID_SIZE, floorMargin + borderWidth), fill=borderColor)
					rect(gc, (x*GRID_SIZE, (y+1)*GRID_SIZE -1, GRID_SIZE, floorMargin), fill=floorColor)

			if x < len(tiles)-1 and not tiles[x+1][y]:
				if hasAirlockAt((x_tot+1, y_tot, True)):
					#has airlock to the right
					cx, cy = (x+1) * GRID_SIZE, y * GRID_SIZE
					if hasAirlockAt((x_tot+1, y_tot, False)):
						rect(gc, (cx, cy, floorMargin, floorMargin), fill=floorColor)
					if hasAirlockAt((x_tot+1, y_tot+1, False)):
						rect(gc, (cx, cy + GRID_SIZE - floorMargin, floorMargin, floorMargin), fill=floorColor)

					if y > 0 and tiles[x+1][y-1]:
						cy += floorMargin
					if isDoubleDent(tiles, x+1,y) or not hasAirlockAt((x_tot+1, y_tot-1, True)):
					#if not (isDent(tiles, x+1,y) or isDoubleDent(tiles, x+1,y) or hasAirlockAt((x_tot+1, y_tot-1, True))):
						#corner = not (isDent(tiles, x+1,y) or isDoubleDent(tiles, x+1,y))
						drawBottomRightCorner(gc, cx, cy)

					cy = (y+1) * GRID_SIZE
					if y < len(tiles[0])-1 and tiles[x+1][y+1]:
						cy -= floorMargin
					if isDoubleDent(tiles, x+1,y+1) or not hasAirlockAt((x_tot+1, y_tot+1, True)):
					#if not (isDent(tiles, x+1,y+1) or isDoubleDent(tiles, x+1,y+1) or hasAirlockAt((x_tot+1, y_tot+1, True))):
						#corner = not (isDent(tiles, x+1,y+1) or isDoubleDent(tiles, x+1,y+1))
						drawTopRightCorner(gc, cx, cy)
					#elif isDent(tiles, x+1, y+1):
					#	print("HELLO WTF")
					#	rect(gc, (cx, cy-2, 4, 1), (255,0,0))
				else:
					rect(gc, ( (x+1)*GRID_SIZE -1, y*GRID_SIZE, floorMargin + borderWidth, GRID_SIZE), fill=borderColor)
					rect(gc, ( (x+1)*GRID_SIZE -1, y*GRID_SIZE, floorMargin, GRID_SIZE), fill=floorColor)

			if isCorner(tiles, x,y):
				drawTopLeftCorner(gc, x*GRID_SIZE, y*GRID_SIZE)
			if isCorner(tiles, x+1,y):
				drawTopRightCorner(gc, (x+1)*GRID_SIZE, y*GRID_SIZE)
			if isCorner(tiles, x,y+1):
				drawBottomLeftCorner(gc, x*GRID_SIZE, (y+1)*GRID_SIZE)
			if isCorner(tiles, x+1,y+1):
				drawBottomRightCorner(gc, (x+1)*GRID_SIZE, (y+1)*GRID_SIZE)

			#gc.rectangle(xy, fill=(0,0,100))

	img = img.crop(box=(GRID_SIZE - offset, GRID_SIZE - offset, img.size[0] - GRID_SIZE - offset, img.size[1] - GRID_SIZE - offset))

	del gc
	if os.path.exists(out_path):
		os.remove(out_path)
	img.save(out_path, "PNG")

	return x_off, y_off


def hasAirlockAt(pos):
	door = findDoorAt(pos)
	if door is None:
		return False
	return door.roomB is None

def findDoorAt(pos):
	x, y, vertical = pos
	for door in all_doors:
		if door.position[0] == x and door.position[1] == y and door.vertical == vertical:
			return door
	return None


def rect(gc, pos, fill):
	x, y, w, h = pos
	gc.rectangle((x, y, w+x, h+y), fill=fill)

def drawTopLeftCorner(gc, cx, cy, special=False):
	cx_, cy_ = (cx, cy) if not special else (cx-1, cy-1)
	gc.polygon([
		(cx_, cy_), 
		(cx - floorMargin - borderWidth, cy_), 
		(cx - floorMargin - borderWidth, cy - cornerSize), 
		(cx - cornerSize, cy - floorMargin - borderWidth), 
		(cx_, cy - floorMargin - borderWidth)], fill=borderColor);
	gc.polygon([
		(cx, cy), 
		(cx - floorMargin, cy), 
		(cx - floorMargin, cy - cornerSize +1), 
		(cx - cornerSize +1, cy - floorMargin), 
		(cx, cy - floorMargin)], fill=floorColor);

def drawTopRightCorner(gc, cx, cy):
	cx_, cy_ = (cx, cy)# if corner else (cx+1, cy-1)
	gc.polygon([
		(cx_, cy_), 
		(cx_, cy - floorMargin - borderWidth), 
		(cx -1 + cornerSize, cy - floorMargin - borderWidth), 
		(cx -1 + floorMargin + borderWidth, cy - cornerSize), 
		(cx -1 + floorMargin + borderWidth, cy_)], fill=borderColor);
	gc.polygon([
		(cx, cy), 
		(cx, cy - floorMargin), 
		(cx -1 + cornerSize -1, cy - floorMargin), 
		(cx -1 + floorMargin, cy - cornerSize +1), 
		(cx -1 + floorMargin, cy)], fill=floorColor);

def drawBottomLeftCorner(gc, cx, cy):
	cx_, cy_ = (cx, cy)# if corner else (cx-1, cy+1)
	gc.polygon([
		(cx_, cy_), 
		(cx_, cy + floorMargin + borderWidth -1), 
		(cx - cornerSize, cy + floorMargin + borderWidth -1), 
		(cx - floorMargin - borderWidth, cy + cornerSize -1), 
		(cx - floorMargin - borderWidth, cy_)], fill=borderColor);
	gc.polygon([
		(cx, cy), 
		(cx, cy + floorMargin -1), 
		(cx - cornerSize + 1, cy + floorMargin -1), 
		(cx - floorMargin, cy + cornerSize - 1 -1), 
		(cx - floorMargin, cy)], fill=floorColor);

def drawBottomRightCorner(gc, cx, cy):
	cx_, cy_ = (cx, cy)# if corner else (cx+1, cy+1)
	gc.polygon([
		(cx_, cy_), 
		(cx_, cy + floorMargin + borderWidth -1), 
		(cx -1 + cornerSize, cy + floorMargin + borderWidth -1), 
		(cx -1 + floorMargin + borderWidth, cy + cornerSize -1), 
		(cx -1 + floorMargin + borderWidth, cy_)], fill=borderColor);
	gc.polygon([
		(cx, cy), 
		(cx, cy + floorMargin -1), 
		(cx -1 + cornerSize - 1, cy + floorMargin -1), 
		(cx -1 + floorMargin, cy + cornerSize - 1 -1), 
		(cx -1 + floorMargin, cy)], fill=floorColor);	

def isCorner(tiles, x, y):
	# 10 or 01 or 00 or 00
	# 00    00    01    10
	lis = get4tiles(tiles, x, y)
	return sum(lis) == 1

def isDent(tiles, x, y):
	#x, y are the bottom right tile's coords
	# 10 or 01 or 11 or 11
	# 11    11    01    10
	#where 0 is space and 1 is any room
	lis = get4tiles(tiles, x, y)
	return sum(lis) == 3

def isDoubleDent(tiles, x, y):
	# 10 or 01
	# 01    10
	lis = get4tiles(tiles, x, y)
	return lis[0] == lis[1] != lis[2] == lis[3]

def get4tiles(tiles, x, y):
	lis = [False]*4
	if x < len(tiles) and y < len(tiles[0]):
		lis[0] = tiles[x][y]
	if 0 < x and 0 < y:
		lis[1] = tiles[x-1][y-1]
	if 0 < x and y < len(tiles[0]):
		lis[2] = tiles[x-1][y]
	if x < len(tiles) and 0 < y:
		lis[3] = tiles[x][y-1]
	return lis
