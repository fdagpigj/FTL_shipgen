#ideally we'll do all randomisation before this file - well, except maybe picking of interior images
import random

import layoutinfo
import roomimggen
import loadout


def generateBlueprint(all_rooms, layout, variant, layout_string, out_dir, all_doors):
	systems, crew, weapons, drones, augments, misc = loadout.generateLoadout(all_rooms, all_doors, layout)
	return_string = ""
	blueprint_info = layoutinfo.blueprint[layout]
	blueprintName = blueprint_info[0]
	if variant > 0:
		blueprintName += "_%i"%(variant+1)

	return_string += '<shipBlueprint name="%s" layout="%s" img="%s">\n'%(blueprintName, layout_string, layout_string)
	return_string += '\t<class>%s</class>\n'%blueprint_info[1]
	return_string += '\t<name>%s</name>\n'%"RANDOM SHIP"
	#return_string += '\t<unlock>%s</unlock>\n'%"fuck if I know :DDDD"
	return_string += '\t<desc>%s</desc>\n'%"Dude it's a procedurally generated ship what do you expect me to say?"
	return_string += '\t<systemList>\n'
	for i, room in enumerate(all_rooms):
		if room.system is not None:
			#for the time being we'll just omit the slot and img info and have ships start fully decked out
			room_img, station = roomimggen.findRoomImage(room)
			img_str = ""
			if room_img is not None:
				img_str = 'img="room_%s"'%room_img
			power = systems.get(room.system, None)
			if power is not None:
				starts = "true"
			else:
				starts = "false"
				if room.system in ("drones","shields"):
					power = 2
				else:
					power = 1
			if station is not None:
				return_string += '\t\t<%s power="%i" room="%i" start="%s" %s>\n'%(room.system, power, i, starts, img_str)
				return_string += '\t\t\t<slot>\n'
				if station[1] is not "no":
					return_string += '\t\t\t\t<direction>%s</direction>\n'%station[1]
				#print("creating station", station)
				return_string += '\t\t\t\t<number>%i</number>\n'%station[0]
				return_string += '\t\t\t</slot>\n\t\t</%s>\n'%room.system
			else:
				return_string += '\t\t<%s power="%i" room="%i" start="%s" %s/>\n'%(room.system, power, i, starts, img_str)
	return_string += '\t</systemList>\n'
	return_string += '\t<weaponSlots>%i</weaponSlots>\n'%misc["weaponSlots"]
	return_string += '\t<droneSlots>%i</droneSlots>\n'%misc["droneSlots"]
	return_string += '\t<weaponList count="%i" missiles="%i">\n'%(len(weapons), misc["missiles"])
	for weapon in weapons:
		return_string += '\t\t<weapon name="%s" />'%weapon
	return_string += '\t</weaponList>'
	return_string += '\t<droneList count="%i" drones="%i">\n'%(len(drones), misc["drone_parts"])
	for drone in drones:
		return_string += '\t\t<drone name="%s" />'%drone
	return_string += '\t</droneList>'
	return_string += '\t<health amount="30"/>\n'
	return_string += '\t<maxPower amount="%i"/>\n'%misc["reactor_power"]
	for race, amount in crew.items():
		return_string += '\t<crewCount amount="%i" class="%s" />\n'%(amount, race)
	for augment in augments:
		return_string += '\t<aug name="%s" />\n'%augment
	return_string += '\t<shieldImage>%s</shieldImage>\n'%layout
	return_string += '\t<cloakImage>%s</cloakImage>\n'%layout
	return_string += '\t<floorImage>%s</floorImage>\n'%layout_string
	return_string += '</shipBlueprint>\n\n\n'

	filename = "blueprints.xml.append"
	if layout == "anaerobic_cruiser":
		filename = "dlcBlueprints.xml.append"
	elif variant == 2:
		filename = "dlcBlueprintsOverwrite.xml.append"
	with open("%s/%s"%(out_dir, filename), "a") as f:
		f.write(return_string)

