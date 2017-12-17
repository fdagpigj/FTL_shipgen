
#each cruiser type has a list of blocked areas - no rooms can generate in the rectangles defined by the [x, y, w, h] coordinates below
blocked = {
	"anaerobic_cruiser": [
		[0, 0, 2, 1],
		[6, 0, 3, 1],
		[7, 0, 2, 2],
		[8, 3, 1, 4],
		[7, 8, 2, 2],
		[6, 9, 3, 1],
		[0, 9, 2, 1],
		[0, 3, 3, 4]
	],
	"circle_cruiser": [
		[0, 0, 1, 5],
		[7, 0, 99, 1],
		[9, 0, 99, 6],
		[4, 2, 3, 1],
		[4, 3, 1, 1],
	],
	"crystal_cruiser": [
		[10, 6, 5, 2],
		[0, 3, 1, 5],
		[7, 0, 5, 1]
	],
	"energy_cruiser": [
		[0, 0, 1, 5],
		[0, 2, 3, 3],
		[0, 3, 4, 3],
		[4, 0, 99, 1],
		[4, 0, 3, 2],
		[12, 1, 1, 1],
		[11, 5, 2, 2],
		[8, 5, 1, 2],
		[8, 6, 99, 1]
	],
	"fed_cruiser": [
		[3, 0, 2, 2],
		[5, 0, 6, 3],
		[11, 0, 4, 2],
		[14, 2, 1, 1],
		[0, 2, 1, 4],
		[3, 6, 2, 2],
		[5, 5, 6, 3],
		[11, 6, 4, 2],
		[14, 5, 1, 1]
	],
	"jelly_cruiser": [
		[0, 0, 3, 3],
		[0, 7, 3, 3],
		[3, 0, 2, 1],
		[3, 9, 2, 1],
		[8, 0, 3, 2],
		[8, 8, 3, 2],
		[10, 2, 1, 1],
		[10, 7, 1, 1]
	],
	"kestral": [
		[0, 0, 1, 2],
		[0, 4, 1, 2],
		[0, 0, 4, 1],
		[0, 5, 4, 1],
		[8, 0, 7, 1],
		[8, 5, 7, 1],
		[10, 0, 5, 2],
		[10, 4, 5, 2]
	],
	"mantis_cruiser": [
		[0, 2, 1, 6],
		[4, 0, 8, 2],
		[4, 8, 8, 2],
		[4, 2, 4, 1],
		[4, 7, 4, 1],
		[10, 2, 2, 1],
		[10, 7, 2, 1]
	],
	"rock_cruiser": [
		[8, 2, 1, 2]
	],
	"stealth": [
		[0, 0, 2, 2],
		[0, 4, 2, 2],
		[6, 0, 7, 1],
		[6, 5, 7, 1],
		[8, 0, 5, 2],
		[8, 4, 5, 2]
	]
}
info = {
	#(max_width, max_height, min_rooms)
	"anaerobic_cruiser": (9, 10, 16),
	"circle_cruiser": (10, 7, 14),
	"crystal_cruiser": (15, 8, 16),
	"energy_cruiser": (13, 7, 19),
	"fed_cruiser": (15, 8, 19),
	"jelly_cruiser": (11, 10, 16),
	"kestral": (15, 6, 17),
	"mantis_cruiser": (12, 10, 19),
	"rock_cruiser": (9, 6, 3),
	"stealth": (13, 6, 14)
}

txt = {
	#min X_OFFSET, min Y_OFFSET, ellipse size string, vanilla ellipse offset (x,y), vanilla layout (w,h), vanilla (X_OFFSET, Y_OFFSET)
	"anaerobic_cruiser": (3,0, "ELLIPSE\n341\n281", (-30,0), (9,10), (3,1)),
	"circle_cruiser": (2,2, "ELLIPSE\n245\n220", (-10,0), (9,7), (3,2)),
	"crystal_cruiser": (0,2, "ELLIPSE\n385\n242", (22,-40), (15,8), (0,2)),
	"energy_cruiser": (1,1, "ELLIPSE\n320\n200", (-20,20), (13,7), (1,1)),
	"fed_cruiser": (1,1, "ELLIPSE\n402\n253", (-63,-3), (15,8), (1,1)),
	"jelly_cruiser": (3,0, "ELLIPSE\n327\n218", (-56,0), (8,8), (5,1)),
	"kestral": (0,2, "ELLIPSE\n350\n220", (-30,0), (15,6), (0,2)),
	"mantis_cruiser": (3,0, "ELLIPSE\n350\n220", (-83,3), (12,10), (3,0)),
	"rock_cruiser": (4,2, "ELLIPSE\n327\n218", (-42,0), (9,6), (4,2)),
	"stealth": (2,2, "ELLIPSE\n350\n245", (-70,0), (13,6), (2,2))
}

floor_offset = {
	#how much empty space there is to the left and up of the vanilla type A floor images
	"anaerobic_cruiser": (3,3),
	"circle_cruiser": (2,2),
	"crystal_cruiser": (4,6),
	"energy_cruiser": (4,3),
	"fed_cruiser": (8,6),
	"jelly_cruiser": (3,3),
	"kestral": (8,4),
	"mantis_cruiser": (2,3),
	"rock_cruiser": (4,4),
	"stealth": (3,3)
}

blueprint = {
	"anaerobic_cruiser": ("PLAYER_SHIP_ANAEROBIC", "Lanius Cruiser"),
	"circle_cruiser": ("PLAYER_SHIP_CIRCLE", "Engi Cruiser"),
	"crystal_cruiser": ("PLAYER_SHIP_CRYSTAL", "Crystal Cruiser"),
	"energy_cruiser": ("PLAYER_SHIP_ENERGY", "Zoltan Cruiser"),
	"fed_cruiser": ("PLAYER_SHIP_FED", "Federation Cruiser"),
	"jelly_cruiser": ("PLAYER_SHIP_JELLY", "Slug Cruiser"),
	"kestral": ("PLAYER_SHIP_HARD", "Kestrel Cruiser"),
	"mantis_cruiser": ("PLAYER_SHIP_MANTIS", "Mantis Cruiser"),
	"rock_cruiser": ("PLAYER_SHIP_ROCK", "Rock Cruiser"),
	"stealth": ("PLAYER_SHIP_STEALTH", "Stealth Cruiser")
}
