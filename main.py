import random
import os

from pathlib import Path

import recolour
import layoutgen
import floorgen
import datafilegen
import blueprintgen
from config import LAYOUTS


PIECES = ("base", "gib1", "gib2", "gib3", "gib4", "gib5", "gib6")


def main():
	if not os.path.exists("data"):
		path = Path("data")
		path.parent.mkdir(parents=True, exist_ok=True)
	if not os.path.exists("img/customizeUI"):
		path = Path("data")
		path.parent.mkdir(parents=True, exist_ok=True)
	if not os.path.exists("img_originals/ship/interior"):
		print("[WARNING] Please copy extracted vanilla FTL img folder into a img_originals folder")
	if not os.path.exists("data_originals"):
		print("[WARNING] Please copy extracted vanilla FTL data folder into a data_originals folder")

	with open("data/blueprints.xml.append", "w+") as f:
		f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
	with open("data/dlcBlueprints.xml.append", "w+") as f:
		f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
	with open("data/dlcBlueprintsOverwrite.xml.append", "w+") as f:
		f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
	with open("data/rooms.xml.append", "w+") as f:
		f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')

	interior_dir = "img/ship/interior"
	if not os.path.exists(interior_dir):
		path = Path(interior_dir)
		path.parent.mkdir(parents=True, exist_ok=True)
	for file in os.listdir(interior_dir):
		file_path = os.path.join(interior_dir, file)
		if os.path.isfile(file_path):
			os.unlink(file_path)


	for layout in LAYOUTS:
		variants = 2 if layout in (LAYOUTS.anaerobic_cruiser, LAYOUTS.crystal_cruiser) else 3
		for variant in range(variants):
			layout_string = layout.value if variant == 0 else f"{layout.value}_{variant+1}"
			print("[INFO] Generating ship %s"%layout_string)
			tint = tuple(random.randint(0,255) for x in range(3))
			for piece in PIECES:
				piece_string = "%s_%s"%(layout_string, piece)
				recolour.auto_colorize("img_originals/ship/%s.png"%piece_string, "img/ship/%s.png"%piece_string, tint)
			recolour.auto_colorize("img_originals/customizeUI/miniship_%s.png"%layout_string, "img/customizeUI/miniship_%s.png"%layout_string, tint)
			out = 1
			while type(out) == int:
				out = layoutgen.generateLayout(layout)
			all_rooms, all_doors = out
			offset = floorgen.generateFloorImage(all_rooms, all_doors, "img/ship/%s_floor.png"%layout_string)
			for room in all_rooms:
				room.coords = room.coords[0] - offset[0], room.coords[1] - offset[1]
			for door in all_doors:
				door.position = door.position[0] - offset[0], door.position[1] - offset[1]
			datafilegen.generateDatafiles(all_rooms, all_doors, offset, layout, "data", layout_string)
			blueprintgen.generateBlueprint(all_rooms, layout, variant, layout_string, "data", all_doors)







main()