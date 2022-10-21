from config import LAYOUTS


#each cruiser type has a list of blocked areas - no rooms can generate in the rectangles defined by the [x, y, w, h] coordinates below
blocked = {
	LAYOUTS.anaerobic_cruiser: [
		[0, 0, 2, 1],
		[6, 0, 3, 1],
		[7, 0, 2, 2],
		[8, 3, 1, 4],
		[7, 8, 2, 2],
		[6, 9, 3, 1],
		[0, 9, 2, 1],
		[0, 3, 3, 4]
	],
	LAYOUTS.circle_cruiser: [
		[0, 0, 1, 5],
		[7, 0, 99, 1],
		[9, 0, 99, 6],
		[4, 2, 3, 1],
		[4, 3, 1, 1],
	],
	LAYOUTS.crystal_cruiser: [
		[10, 6, 5, 2],
		[0, 3, 1, 5],
		[7, 0, 5, 1]
	],
	LAYOUTS.energy_cruiser: [
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
	LAYOUTS.fed_cruiser: [
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
	LAYOUTS.jelly_cruiser: [
		[0, 0, 3, 3],
		[0, 7, 3, 3],
		[3, 0, 2, 1],
		[3, 9, 2, 1],
		[8, 0, 3, 2],
		[8, 8, 3, 2],
		[10, 2, 1, 1],
		[10, 7, 1, 1]
	],
	LAYOUTS.kestral: [
		[0, 0, 1, 2],
		[0, 4, 1, 2],
		[0, 0, 4, 1],
		[0, 5, 4, 1],
		[8, 0, 7, 1],
		[8, 5, 7, 1],
		[10, 0, 5, 2],
		[10, 4, 5, 2]
	],
	LAYOUTS.mantis_cruiser: [
		[0, 2, 1, 6],
		[4, 0, 8, 2],
		[4, 8, 8, 2],
		[4, 2, 4, 1],
		[4, 7, 4, 1],
		[10, 2, 2, 1],
		[10, 7, 2, 1]
	],
	LAYOUTS.rock_cruiser: [
		[8, 2, 1, 2]
	],
	LAYOUTS.stealth: [
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
	LAYOUTS.anaerobic_cruiser: (9, 10, 16),
	LAYOUTS.circle_cruiser: (10, 7, 14),
	LAYOUTS.crystal_cruiser: (15, 8, 16),
	LAYOUTS.energy_cruiser: (13, 7, 19),
	LAYOUTS.fed_cruiser: (15, 8, 19),
	LAYOUTS.jelly_cruiser: (11, 10, 16),
	LAYOUTS.kestral: (15, 6, 17),
	LAYOUTS.mantis_cruiser: (12, 10, 19),
	LAYOUTS.rock_cruiser: (9, 6, 14),
	LAYOUTS.stealth: (13, 6, 14)
}

txt = {
	#min X_OFFSET, min Y_OFFSET, ellipse size string, vanilla ellipse offset (x,y), vanilla layout (w,h), vanilla (X_OFFSET, Y_OFFSET)
	LAYOUTS.anaerobic_cruiser: (3,0, "ELLIPSE\n341\n281", (-30,0), (9,10), (3,1)),
	LAYOUTS.circle_cruiser: (2,2, "ELLIPSE\n245\n220", (-10,0), (9,7), (3,2)),
	LAYOUTS.crystal_cruiser: (0,2, "ELLIPSE\n385\n242", (22,-40), (15,8), (0,2)),
	LAYOUTS.energy_cruiser: (1,1, "ELLIPSE\n320\n200", (-20,20), (13,7), (1,1)),
	LAYOUTS.fed_cruiser: (1,1, "ELLIPSE\n402\n253", (-63,-3), (15,8), (1,1)),
	LAYOUTS.jelly_cruiser: (3,0, "ELLIPSE\n327\n218", (-56,0), (8,8), (5,1)),
	LAYOUTS.kestral: (0,2, "ELLIPSE\n350\n220", (-30,0), (15,6), (0,2)),
	LAYOUTS.mantis_cruiser: (3,0, "ELLIPSE\n350\n220", (-83,3), (12,10), (3,0)),
	LAYOUTS.rock_cruiser: (4,2, "ELLIPSE\n327\n218", (-42,0), (9,6), (4,2)),
	LAYOUTS.stealth: (2,2, "ELLIPSE\n350\n245", (-70,0), (13,6), (2,2))
}

floor_offset = {
	#how much empty space there is to the left and up of the vanilla type A floor images
	LAYOUTS.anaerobic_cruiser: (3,3),
	LAYOUTS.circle_cruiser: (2,2),
	LAYOUTS.crystal_cruiser: (4,6),
	LAYOUTS.energy_cruiser: (4,3),
	LAYOUTS.fed_cruiser: (8,6),
	LAYOUTS.jelly_cruiser: (3,3),
	LAYOUTS.kestral: (8,4),
	LAYOUTS.mantis_cruiser: (2,3),
	LAYOUTS.rock_cruiser: (4,4),
	LAYOUTS.stealth: (3,3)
}

blueprint = {
	LAYOUTS.anaerobic_cruiser: ("PLAYER_SHIP_ANAEROBIC", "Lanius Cruiser"),
	LAYOUTS.circle_cruiser: ("PLAYER_SHIP_CIRCLE", "Engi Cruiser"),
	LAYOUTS.crystal_cruiser: ("PLAYER_SHIP_CRYSTAL", "Crystal Cruiser"),
	LAYOUTS.energy_cruiser: ("PLAYER_SHIP_ENERGY", "Zoltan Cruiser"),
	LAYOUTS.fed_cruiser: ("PLAYER_SHIP_FED", "Federation Cruiser"),
	LAYOUTS.jelly_cruiser: ("PLAYER_SHIP_JELLY", "Slug Cruiser"),
	LAYOUTS.kestral: ("PLAYER_SHIP_HARD", "Kestrel Cruiser"),
	LAYOUTS.mantis_cruiser: ("PLAYER_SHIP_MANTIS", "Mantis Cruiser"),
	LAYOUTS.rock_cruiser: ("PLAYER_SHIP_ROCK", "Rock Cruiser"),
	LAYOUTS.stealth: ("PLAYER_SHIP_STEALTH", "Stealth Cruiser")
}
