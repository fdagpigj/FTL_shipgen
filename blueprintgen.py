#ideally we'll do all randomisation before this file - well, except maybe picking of interior images
import random

import layoutinfo
import roomimggen
# import loadout
import loadoutgen
from config import LAYOUTS, SYSTEMS


def generateBlueprint(all_rooms, layout, variant, layout_string, out_dir, all_doors):
	# systems, crew, weapons, drones, augments, misc = loadout.generateLoadout(all_rooms, all_doors, layout)
	loadout = loadoutgen.generateLoadout(all_rooms, all_doors, layout)
	return_string = ""
	blueprint_info = layoutinfo.blueprint[layout]
	blueprintName = blueprint_info[0]
	if variant > 0:
		blueprintName += f"_{variant+1}"

	return_string += f'<shipBlueprint name="{blueprintName}" layout="{layout_string}" img="{layout_string}">\n'
	return_string += f'\t<class>{blueprint_info[1]}</class>\n'
	return_string += f'\t<name>{loadout["name"]}</name>\n'
	#return_string += '\t<unlock>%s</unlock>\n'%"fuck if I know :DDDD"
	return_string += f'\t<desc>{loadout["description"]}</desc>\n'

	return_string += '\t<systemList>\n'
	for i, room in enumerate(all_rooms):
		if room.system is not None:
			system_str = room.system.value
			#for the time being we'll just omit the slot and img info and have ships start fully decked out
			room_img, station = roomimggen.findRoomImage(room)
			img_str = ""
			if room_img is not None:
				img_str = f'img="room_{room_img}"'
			power = loadout['system_levels'][room.system]
			starts = 'true' if room.system in loadout['starting_systems'] else 'false'
			if station is not None:
				return_string += f'\t\t<{system_str} power="{power}" room="{i}" start="{starts}" {img_str}>\n'
				return_string += '\t\t\t<slot>\n'
				if station[1] != "no":
					return_string += f'\t\t\t\t<direction>{station[1]}</direction>\n'
				#print("creating station", station)
				return_string += f'\t\t\t\t<number>{station[0]}</number>\n'
				return_string += f'\t\t\t</slot>\n\t\t</{system_str}>\n'
			else:
				return_string += f'\t\t<{system_str} power="{power}" room="{i}" start="{starts}" {img_str}/>\n'

			# Generate clonebay data in medbay room
			if room.system == SYSTEMS.medbay:
				station = [random.randrange(room.dimensions[0] * room.dimensions[1]) , "no"]
				power = loadout['system_levels']['clonebay']
				starts = 'true' if SYSTEMS.clonebay in loadout['starting_systems'] else 'false'
				return_string += f'\t\t<clonebay power="1" room="{i}" start="{starts}">\n'
				return_string += '\t\t\t<slot>\n'
				return_string += f'\t\t\t\t<number>{station[0]}</number>\n'
				return_string += f'\t\t\t</slot>\n\t\t</{system_str}>\n'

	return_string += '\t</systemList>\n'
	return_string += f'\t<weaponSlots>{loadout["weapon_slots"]}</weaponSlots>\n'
	return_string += f'\t<droneSlots>{loadout["drone_slots"]}</droneSlots>\n'

	weapons = loadout['weapons']
	return_string += f'\t<weaponList count="{len(weapons)}" missiles="{loadout["missiles"]}">\n'
	for weapon in weapons:
		return_string += f'\t\t<weapon name="{weapon}" />'
	return_string += '\t</weaponList>'

	drones = loadout['drones']
	return_string += f'\t<droneList count="{len(drones)}" drones="{loadout["drone_parts"]}">\n'
	for drone in drones:
		return_string += f'\t\t<drone name="{drone}" />'
	return_string += '\t</droneList>'

	return_string += '\t<health amount="30"/>\n'
	return_string += f'\t<maxPower amount="{loadout["reactor_power"]}"/>\n'
	# for race, amount in crew.items():
	# 	return_string += '\t<crewCount amount="%i" class="%s" />\n'%(amount, race)
	for race in loadout['crew']:
		return_string += f'\t<crewCount amount="1" class="{race.value}" />\n'
	for augment in loadout['augments']:
		return_string += f'\t<aug name="{augment.value}" />\n'

	return_string += f'\t<shieldImage>{layout.value}</shieldImage>\n'
	return_string += f'\t<cloakImage>{layout.value}</cloakImage>\n'
	return_string += f'\t<floorImage>{layout_string}</floorImage>\n'
	return_string += '</shipBlueprint>\n\n\n'


	filename = "blueprints.xml.append"
	if layout == LAYOUTS.anaerobic_cruiser:
		filename = "dlcBlueprints.xml.append"
	elif variant == 2:
		filename = "dlcBlueprintsOverwrite.xml.append"
	with open(f"{out_dir}/{filename}", "a") as f:
		f.write(return_string)
	return loadout['warnings'], loadout['errors']

