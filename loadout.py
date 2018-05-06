import random
import collections

import config


def generateLoadout(all_rooms, all_doors, layout):
	description = []
	crew, crew_count = pickCrew(layout)
	if crew_count > 4:
		description.append("Zomg overstaffed!")


	#these might be helpful in determining what drones and augments to give
	path_points, venting_points = getLayoutPoints(all_rooms, all_doors, crew)
	boarder_defence_points, repair_points, firefight_points, airless_points, anaerobic, crew_scrap = getCrewPoints(crew)

	boarding_points, crew_synergies = getBoardingPoints(all_rooms, crew)

	viable_drones = collections.defaultdict(int)
	viable_augments = collections.defaultdict(int)
	viable_support_weapons = collections.defaultdict(int)
	viable_systems = collections.defaultdict(int)
	viable_subsystems = collections.defaultdict(int)

	viable_augments["O2_MASKS"] += 1/(2*(airless_points**2) *boarder_defence_points*firefight_points)
	viable_augments["NANO_MEDBAY"] += 1/(airless_points*boarder_defence_points)

	viable_augments["FIRE_EXTINGUISHERS"] += 1/((firefight_points**2)*(venting_points**2))

	viable_drones["REPAIR"] += 1/(repair_points) + 1/(airless_points*repair_points*firefight_points)
	viable_support_weapons["BOMB_HEAL_SYSTEM"] += 1/(repair_points**2)

	viable_drones["BATTLE"] += 1/(boarder_defence_points)


	viable_augments["ROCK_ARMOR"] += 1 * (layout == "rock_cruiser")
	viable_augments["CRYSTAL_SHARDS"] += 1 * (layout == "crystal_cruiser")
	viable_augments["ENERGY_SHIELD"] += 1 * (layout == "energy_cruiser")
	viable_augments["NANO_MEDBAY"] += 1 * (layout == "circle_cruiser")
	viable_augments["SLUG_GEL"] += 1 * (layout == "jelly_cruiser")
	viable_augments["CREW_STIMS"] += 1 * (layout == "mantis_cruiser")
	#viable_augments["DRONE_SPEED"] += 1 * (layout == "circle_cruiser") #do this later when we know if we have drone control
	viable_augments["SYSTEM_CASING"] += 1 * (layout == "stealth")
	viable_augments["ADV_SCANNERS"] += 1 * (layout == "stealth")


	#pilot, engines, weapons are guaranteed
	viable_systems["oxygen"] += 1 + 150/(airless_points**2) + 30 * (1 - anaerobic) - 10 * (layout == "anaerobic_cruiser")
	viable_systems["teleporter"] += boarding_points + 10 * (layout == "mantis_cruiser")
	viable_systems["cloaking"] += 1 + 50 * (layout == "stealth")
	viable_systems["shields"] += 100 - 99 * (layout == "stealth") - 20 * (layout == "energy_cruiser")
	viable_systems["hacking"] += 10 + 5 * (layout == "jelly_cruiser")
	viable_systems["mind"] += 10 + 5 * (layout == "jelly_cruiser")
	viable_systems["drones"] += 3 + 10 * (layout == "circle_cruiser") + 4 * len(viable_drones)

	viable_subsystems["sensors"] += 15 - 10 * (layout == "jelly_cruiser")
	viable_subsystems["doors"] += 20 - 5 * (layout == "rock_cruiser" or layout == "anaerobic_cruiser")
	viable_subsystems["battery"] += 2 + 10 * (layout == "energy_cruiser")

	systems, viable_systems, viable_subsystems = pickSystems(viable_systems, viable_subsystems)

	heal_system = None
	hs = random.random()
	if hs < 0.48:
		heal_system = "medbay"
		if "oxygen" not in systems:
			viable_augments["NANO_MEDBAY"] += 1
	elif hs < 0.95:
		heal_system = "clonebay"
		boarding_points += crew_synergies["clonebay"]
	if heal_system is not None:
		systems.append(heal_system)
	else:
		print("lol no healing system for you")
		description.append("No healing system for you.")
		#TODO: actually pick some weapons from this dict if appropriate
		viable_support_weapons["BOMB_HEAL"] += 1
		if "teleporter" in systems:
			viable_augments["TELEPORT_HEAL"] += 2
		if "oxygen" not in systems:
			description.append("Enjoy losing crew!")
			viable_augments["O2_MASKS"] += 2
	if heal_system != "medbay":
		viable_augments["NANO_MEDBAY"] = 0

	drone_power = 0
	if "drones" in systems:
		drones, viable_drones = pickDrones(viable_drones)
		max_power, total_power = 0,0
		for drone in drones:
			power = config.drone_points[drone]["power"]
			total_power += power
			max_power = max(power, max_power)
		if total_power > 3:
			drone_power = max_power
		else:
			drone_power = total_power
	else:
		drones = []

	if "REPAIR" in drones:
		viable_augments["FIRE_EXTINGUISHERS"] /= 2
		viable_support_weapons["BOMB_HEAL_SYSTEM"] /= 8

	#remember that the system levels are yet to be set
	sys_defence_points, sys_offence_points, sys_support_points, sys_scrap, sys_crewkill_points, sys_shield_drop = getSystemPoints(systems)
	drone_defence_points, drone_offence_points, drone_support_points, drone_scrap, drone_crewkill_points, drone_shield_drop = getDronePoints(drones)

	defence_points = sys_defence_points + drone_defence_points
	offence_points = sys_offence_points + drone_offence_points
	support_points = sys_support_points + drone_support_points + boarder_defence_points + repair_points
	shield_drop = sys_shield_drop + drone_shield_drop
	scrap = crew_scrap + sys_scrap + drone_scrap

	if "teleporter" not in systems:
		boarding_points = 0
	if "sensors" not in systems and "slug" not in crew:
		boarding_points *= 0.8
		sys_crewkill_points *= 0.5

	droneSlots = 2
	drone3chance = 0.1 + 0.2 * ("drones" in systems) + 1.0 * (len(drones) == 3)
	if random.random() < drone3chance:
		description.append("This one has three drone slots.")
		droneSlots = 3
	weaponSlots = 3
	weapon4chance = 0.6 - 0.2 * (layout in ("circle_cruiser", "stealth", "mantis_cruiser"))
	if droneSlots == 2 and random.random() < weapon4chance:
		weaponSlots = 4

	#now for the weapons.......
	crewkill_points = sys_crewkill_points + boarding_points
	weapons, viable_weapons, weapon_power = pickWeapons(layout, defence_points, offence_points, support_points, shield_drop, crewkill_points, crew_synergies, systems)
	weapon_offence_points, weapon_crewkill_points, weapon_slowness, req_shield_drop = getWeaponPoints(weapons, systems, offence_points, shield_drop, crew_synergies)

	#I don't account for drones because I haven't looked at their shield_drop and offence combo enough
	if crewkill_points + weapon_crewkill_points + boarding_points < 8 and weapon_offence_points < 2:
		weapon = pickWeapon(viable_weapons, req_shield_drop, weapons)
		if weapon is not None:
			weapons.append(weapon)
			weapon_power += config.weapon_points[weapon]["power"]
		else:
			print("did not find a suitable third weapon", weapons, viable_weapons, req_shield_drop)

	#print("[DEBUG] Pre-drop weapons", weapons, weapon_power)
	weapons, power_drop = dropRedundantWeapon(weapons, systems)
	weapon_power -= power_drop
	support_weapon_weight = sum([a[1] for a in viable_support_weapons.items()])
	if len(weapons) < weaponSlots and support_weapon_weight > random.random() + 1:
		support_weapon = weighted_chance(viable_support_weapons)
		viable_support_weapons[support_weapon] = 0
		weapons.append(support_weapon)
		if support_weapon_weight > 1 and weapon_power < 4:
			weapon_power += 1
	#print("[DEBUG] Final? weapons", weapons, weapon_power)
	weapon_offence_points, weapon_crewkill_points, weapon_slowness, req_shield_drop = getWeaponPoints(weapons, systems, offence_points, shield_drop, crew_synergies)


	if weapon_power > 3:
		#the old system caused a 2+2+1 setup to get 2 power even though I'd prefer 3 - as this new should give
		power_list = []
		for weapon in weapons:
			power_list.append(config.weapon_points[weapon]["power"])
		weapon_power = max(power_list)
		if sum(power_list) > weapon_power + 2:
			weapon_power += 1

	missiles = 0
	for weapon in weapons:
		missiles += config.weapon_points[weapon].get("missiles",0) * random.randint(8, 16)
	drone_parts = 0
	for drone in drones:
		bonus = config.drone_points[drone]
		drone_parts += random.randint(4,6) * bonus.get("support",0) + random.randint(1,2) * bonus.get("defence",0) + random.randint(12,20) * bonus.get("offence",0)

	system_levels = collections.defaultdict(int)
	for system in systems:
		if system == "weapons":
			system_levels["weapons"] = max(weapon_power, 1)
		elif system == "drones":
			system_levels["drones"] = drone_power
		elif system == "shields":
			system_levels[system] = 2
		else:
			system_levels[system] = 1

	augments = []
	slowness = 0

	if (crewkill_points + weapon_crewkill_points + boarding_points) > offence_points + weapon_offence_points:
		slowness += 200 / (crewkill_points + weapon_crewkill_points + boarding_points)
		description.append("Crewkiller?")
	else:
		slowness += weapon_slowness
		description.append("Gunship?")

	def_ratio = defence_points / slowness
	if def_ratio < 0.5:
		print("[DEBUG] Raising defences because def_ratio is %f because"%def_ratio, defence_points, slowness)
		dm = random.random()
		if dm < 0.4:
			system_levels["shields"] += 2
		elif dm < 0.5:
			augments.append("ENERGY_SHIELD")
		elif dm < 0.8:
			if "cloaking" in system_levels:
				if "hacking" in system_levels or random.random() < 0.5:
					system_levels["cloaking"] += 1
				else:
					system_levels["hacking"] += 1
			else:
				system_levels["cloaking"] += 1
		else:
			if "drones" not in system_levels:
				system_levels["drones"] = 2
			dd = random.random() + 0.2 * ("shields" not in system_levels)
			if dd < 0.5:
				drones.append("DEFENSE_1")
			elif dd < 0.8:
				if len(drones) == 0:
					system_levels["drones"] = 3
				drones.append("DEFENSE_2")
			elif dd < 0.95:
				drones.append("DRONE_SHIELD_PLAYER")
			else:
				if len(drones) == 0:
					system_levels["drones"] = 1
				drones.append("ANTI_DRONE")

	elif def_ratio > 5:
		print("[DEBUG] Dropping defences because def_ratio is %f"%def_ratio)
		#lol as if they could reach such a high defense ratio without shields
		#ok I think it's possible but extremely unlikely
		if "shields" in system_levels:
			system_levels["shields"] = 1

	if system_levels["mind"] > 0 and "slug" not in crew and system_levels["sensors"] < 2:
		visibility_req = 2.0
		for weapon in weapons:
			if "BOMB" in weapon:
				visibility_req /= 2.0
		if system_levels["teleporter"] > 0:
			visibility_req /= 3.0
		if random.random() < 0.3 * visibility_req:
			system_levels["sensors"] = 2
		else:
			viable_augments["LIFE_SCANNER"] += visibility_req

	#print("[DEBUG] Picking augments, system_levels, viable_augments:", augments, system_levels, viable_augments)
	augments, viable_augments = pickAugments(augments, viable_augments)
	#print("[DEBUG] Picked augments:", augments)

	if system_levels["oxygen"] < 1 and "O2_MASKS" not in augments and system_levels["medbay"] > 0 and airless_points < 1:
		system_levels["medbay"] += 1

	reactor_power, description = getReactor(system_levels, crew, description)

	if "hacking" in system_levels:
		drone_parts += random.randint(12,16)

	#yeah we're not done yet, balancing is out the whazoo but too eager to test
	misc = {
		"missiles":missiles, "drone_parts":drone_parts, "reactor_power":reactor_power,
		"droneSlots":droneSlots, "weaponSlots":weaponSlots, "description":" ".join(description)
	}

	if system_levels["oxygen"] < 1:
		description.append("Breathing is a privilege.")

	#misc contains weapon/drone slot count, starting drone parts/missiles, reactor power, etc
	return system_levels, crew, weapons, drones, augments, misc


def dropRedundantWeapon(weapons, systems):
	#ok fuck this can drop a dual laser instead of two beams...
	drop_need = 2 - 0.95*("teleporter" in systems) - 2*("hacking" in systems)
	power_drop = 0
	redundancies = []

	can_penetrate = False
	sd_sum, sp_sum, dmg_sum,  lethal_sum, crewkill_sum, missile_sum = getWeaponSums(-1, weapons)
	if sd_sum + sp_sum > drop_need and ((dmg_sum > 0 and crewkill_sum > 0) or (lethal_sum > 0 and dmg_sum > 1)):
		can_penetrate = True
	
	for index, drop in enumerate(weapons):
		sd_sum, sp_sum, dmg_sum,  lethal_sum, crewkill_sum, missile_sum = getWeaponSums(index, weapons)
		if (
			(not can_penetrate and dmg_sum + crewkill_sum + lethal_sum > 1)
			or (sd_sum + sp_sum > drop_need and ((dmg_sum > 0 and crewkill_sum > 0)
			or (lethal_sum > 0 and dmg_sum > 1)))
			):
			redundancies.append(index)
	if len(redundancies) > 0:
		dropper = random_from(redundancies)
		drop = weapons.pop(dropper)
		power_drop = config.weapon_points[drop].get("power",0)
		print("[DEBUG] Dropping", drop, power_drop)
	return weapons, power_drop


def getWeaponSums(ban_index, weapons):
	sd_sum, sp_sum, dmg_sum,  lethal_sum, crewkill_sum, missile_sum = 0,0,0, 0,0,0
	for i, weapon in enumerate(weapons):
		if i == ban_index:
			continue
		reusability = 1- 0.9* config.weapon_points[weapon].get("missiles",0)
		sd_sum += config.weapon_points[weapon].get("shield_drop",0) * reusability
		sp_sum += config.weapon_points[weapon].get("sp",0) * reusability
		dmg_sum += config.weapon_points[weapon].get("offence",0) + config.weapon_points[weapon].get("nonlethal",0)
		lethal_sum += config.weapon_points[weapon].get("offence",0) * reusability
		crewkill_sum += (config.weapon_points[weapon].get("crewkill",0) + config.weapon_points[weapon].get("fire",0)) * reusability
	return sd_sum, sp_sum, dmg_sum, lethal_sum, crewkill_sum, missile_sum


def getReactor(system_levels, crew, description):
	total_power = 0
	for system, power in system_levels.items():
		if system not in ("pilot", "doors", "sensors", "battery"):
			total_power += power
		if system == "battery":
			total_power -= power * 2
	total_power -= crew.get("energy",0)

	reducted_power = 0
	if total_power > 9:
		reducted_power = total_power - 9
		total_power = 9
	if total_power > 5:
		if random.random() < 0.5:
			reducted_power += 1
			total_power -= 1
	if total_power < 2:
		total_power = 2

	if reducted_power > random.randint(1,3) and system_levels["battery"] < 2:
		system_levels["battery"] += 1
		reducted_power -= 2
	if reducted_power > 1:
		description.append("Power shortage?")
	if total_power < 4:
		description.append("Tiny reactor.")

	return total_power, description


def pickAugments(augments, viable_augments):
	for i in range(2):
		total_weight = sum([a[1] for a in viable_augments.items()])
		if len(augments) >= 2 or total_weight < random.randrange(5):
			break
		augment = weighted_chance(viable_augments)
		augments.append(augment)
		viable_augments[augment] = 0
	return augments, viable_augments


def pickWeapon(viable_weapons, req_shield_drop, weapons):
	#let's just pick the most viable weapon from viable_weapons
	most_viable = []
	max_viability = 0
	for weapon, viability in viable_weapons.items():
		if config.weapon_points[weapon].get("shield_drop", 0) >= req_shield_drop:
			if viability > max_viability:
				max_viability = viability
				most_viable.clear()
				most_viable.append(weapon)
			elif viability == max_viability:
				most_viable.append(weapon)
	weapon = random_from(most_viable)
	return weapon


def getWeaponPoints(weapons, systems, offence_points, shield_drop, crew_synergies):
	#print("[DEBUG] getting weapon_points for", weapons)
	req_shield_drop = max(0, 2 - shield_drop)
	if len(weapons) == 0:
		return 0, 0, 0, req_shield_drop
	# this should work with an arbitrary number of weapons... but it's not gonna
	shield_droppers, hitters, crewkillers, lone_wolves = getWeaponSynergies(weapons, crew_synergies, systems)
	#I'm gonna half-ass this for now because my brain has melted by now
	used_weapons = []
	damage = 0
	crewkill = 0
	max_slowness = 0
	drop_need = req_shield_drop
	tp_synergies = crew_synergies if "teleporter" in systems else {}
	while drop_need > 0 and len(used_weapons) < len(weapons):
		best_shield_dropper = (None, 0)
		best_lone_wolf = (None, 0)
		for weapon in weapons:
			if weapon is None:
				print("[ERROR] weapon is None")
				continue
			if used_weapons.count(weapon) == weapons.count(weapon):
				continue
			sd = shield_droppers[weapon] * (1 + (1/(hitters[weapon]+crewkillers[weapon]) if hitters[weapon] > 0 or crewkillers[weapon] > 0 else 10000)) - lone_wolves[weapon]
			if best_shield_dropper[0] is None or best_shield_dropper[1] < sd:
				best_shield_dropper = (weapon, sd)
			if not best_shield_dropper[0]:
				print("[ERROR] uh oh", weapon, best_shield_dropper)
			if best_lone_wolf[0] is None or best_lone_wolf[1] < lone_wolves[weapon]:
				best_lone_wolf = (weapon, lone_wolves[weapon])
			#print("wtf", weapon, best_shield_dropper)
		weapon = best_shield_dropper[0]
		if weapon is None:
			weapon = best_lone_wolf[0]
		if weapon is None:
			print("[ERROR] WHAT THE FUCKING FUCK")
		sd = shield_droppers[weapon]
		drop_need = max(0, drop_need - sd)
		remaining_dmg = (sd - drop_need) / sd if sd > 0 else 0
		damage += hitters[weapon] * remaining_dmg
		crewkill += crewkillers[weapon] * remaining_dmg
		for effect in ("fire","breach","stun"):
			if weapon is None:
				print("304: weapon", weapon, weapons, best_shield_dropper)
			amount = config.weapon_points[weapon].get(effect,0) * remaining_dmg
			crewkill += amount * (1 + tp_synergies.get(effect,0))
		used_weapons.append(weapon)
	for weapon in weapons:
		max_slowness = max(config.weapon_points[weapon]["slowness"] / max(1, lone_wolves[weapon]), max_slowness)
		if weapon in used_weapons:
			continue
		damage += hitters[weapon]
		crewkill += crewkillers[weapon]
		for effect in ("fire","breach","stun"):
			amount = config.weapon_points[weapon].get(effect,0)
			crewkill += amount * (1 + tp_synergies.get(effect,0))

	return damage, crewkill, max_slowness, drop_need



def pickWeapons(layout, defence_points, offence_points, support_points, shield_drop, crewkill_points, crew_synergies, systems):
	weapons = []
	weapon_power = 0
	viable_weapons = collections.defaultdict(int)
	for weapon, bonus in config.weapon_points.items():
		if weapon[:7] == "MISSILE":
			viable_weapons[weapon] += 1 + 2 * (layout == "rock_cruiser") - 0.2 * bonus["power"]
		if weapon[:5] == "LASER":
			viable_weapons[weapon] += 5 - bonus["power"]
		if weapon[:7] == "SHOTGUN":
			viable_weapons[weapon] += 1 + 1 * (layout == "anaerobic_cruiser") - 0.2 * bonus["power"]
		if weapon[:4] == "BEAM":
			viable_weapons[weapon] += 1 + 1 * (layout == "jelly_cruiser")
			if weapon != "BEAM_BIO":
				viable_weapons[weapon] += 2 * (layout in ("stealth", "energy_cruiser"))
		if weapon[:3] == "ION":
			viable_weapons[weapon] += 1 + 2 * (layout in ("circle_cruiser", "energy_cruiser")) - 0.33 * bonus["power"]
		if weapon[:4] == "BOMB":
			if weapon not in ("BOMB_HEAL", "BOMB_HEAL_SYSTEM"):
				viable_weapons[weapon] += 1 + 1 * (layout in ("jelly_cruiser", "mantis_cruiser"))
		if weapon[:7] == "CRYSTAL":
			viable_weapons[weapon] += 0.1 + 2 * (layout == "crystal_cruiser")

	shield_droppers, hitters, crewkillers, lone_wolves = getWeaponSynergies(viable_weapons, crew_synergies, systems)
	req_shield_drop = max(0, 2 - shield_drop)

	#pick one weapon to start us out with... unless the boarding or drone setup is real good in which case shh bby is ok
	if ((crewkill_points > 8 and defence_points > 20) or (offence_points > 5 and shield_drop > 1)) and random.random() < 0.5:
		#do nothing
		pass
	else:
		weapon = weighted_chance(viable_weapons)
		#viable_weapons[weapon] /= 3
		weapons.append(weapon)
		weapon_power += config.weapon_points[weapon]["power"]

	if len(weapons) > 0 and crewkill_points + offence_points < 40:
		for weapon in tuple(viable_weapons):
			bonus = config.weapon_points[weapon]
			if bonus["power"] > 4 - weapon_power:
				del viable_weapons[weapon]
				continue
			max_dmg_synergy = 0
			max_ck_synergy = 0
			max_slowness = max(config.weapon_points[weapons[0]]["slowness"], bonus["slowness"])
			if req_shield_drop > 0:
				for w1, w2 in ((weapon, weapons[0]), (weapons[0], weapon)):
					shield_drop_need = req_shield_drop - lone_wolves[w2]
					if shield_droppers[w1] >= shield_drop_need:
						w1remaining = (shield_droppers[w1] - shield_drop_need) / shield_droppers[w1] if shield_droppers[w1] > 0 else 0
						if hitters[w2] > max_dmg_synergy:
							max_dmg_synergy = hitters[w2] + hitters[w1] * w1remaining
						if crewkillers[w2] > max_ck_synergy:
							max_ck_synergy = crewkillers[w1] + crewkillers[w1] * w1remaining
			else:
				max_dmg_synergy = hitters[weapon] + hitters[weapons[0]]
				max_ck_synergy = crewkillers[weapon] + crewkillers[weapons[0]]
			#should this be += or *= ?
			viable_weapons[weapon] += (max_dmg_synergy + max_ck_synergy + lone_wolves[weapon]) / max_slowness

		if len(viable_weapons) > 0:
			weapon = weighted_chance(viable_weapons)
			weapons.append(weapon)
			weapon_power += config.weapon_points[weapon]["power"]

	return weapons, viable_weapons, weapon_power


def getWeaponSynergies(weapons, crew_synergies, systems):
	#how good each weapon is at each task
	shield_drop = collections.defaultdict(int)
	hitter = collections.defaultdict(int)
	crewkill = collections.defaultdict(int)
	lone_wolf = collections.defaultdict(int)
	for weapon in weapons:
		bonus = config.weapon_points[weapon]
		shield_drop[weapon] += bonus.get("shield_drop",0)
		hitter[weapon] += bonus.get("offence",0) + bonus.get("nonlethal",0)
		if "teleporter" in systems:
			tp_synergies = crew_synergies
		else:
			tp_synergies = collections.defaultdict(int)
		crewkill[weapon] += bonus.get("crewkill",0) + min(bonus.get("offence",0),4) + (bonus.get("fire",0) * (1+ tp_synergies["fire"]) + 
			bonus.get("breach",0) * (1+ tp_synergies["breach"]) + bonus.get("stun",0) * (1+ tp_synergies["stun"]))
		remaining_dmg = hitter[weapon]* (shield_drop[weapon]-2)/shield_drop[weapon] if shield_drop[weapon] > 0 else 0
		lone_wolf[weapon] += max( min(bonus.get("sp",0), hitter[weapon]),  remaining_dmg )
	return shield_drop, hitter, crewkill, lone_wolf


def getDronePoints(drones):
	def_points, off_points, supp_points,  scrap, crewkill, shield_drop = 0,0,0, 0,0,0
	for drone in drones:
		bonus = config.drone_points[drone]
		def_points += bonus.get("defence",0)
		off_points += bonus.get("offence",0)
		supp_points += bonus.get("support",0)
		crewkill += bonus.get("crewkill",0)
		shield_drop += bonus.get("shield_drop",0)
		scrap += bonus["scrap"]
	return def_points, off_points, supp_points, scrap, crewkill, shield_drop


def getSystemPoints(systems):
	def_points, off_points, supp_points,  scrap, crewkill, shield_drop = 0,0,0, 0,0,0
	for system in systems:
		bonus = config.system_points[system]
		def_points += bonus.get("defence",0)
		off_points += bonus.get("offence",0)
		supp_points += bonus.get("support",0)
		crewkill += bonus.get("crewkill",0)
		shield_drop += bonus.get("shield_drop",0)
		scrap += bonus["scrap"][0]
	return def_points, off_points, supp_points, scrap, crewkill, shield_drop


def pickDrones(viable_drones):
	#THESE ARE NOT FINAL, drones can still be added afterwards
	drones = []
	viable_drones["COMBAT_1"] += 4
	viable_drones["COMBAT_BEAM"] += 2
	viable_drones["COMBAT_2"] += 0.1
	viable_drones["DEFENSE_1"] += 9
	viable_drones["DEFENSE_2"] += 3
	viable_drones["REPAIR"] += 3
	viable_drones["BATTLE"] += 2
	viable_drones["BOARDER"] += 4
	viable_drones["BOARDER_ION"] += 2
	viable_drones["ANTI_DRONE"] += 2
	viable_drones["COMBAT_BEAM_2"] += 0.5
	viable_drones["COMBAT_FIRE"] += 2
	viable_drones["DRONE_SHIELD_PLAYER"] += 3
	for _ in range(3):
		drone = weighted_chance(viable_drones)
		drones.append(drone)
		viable_drones[drone] = 0
		total_weight = sum([a[1] for a in viable_drones.items()])
		if total_weight < random.randrange(50) or random.random() < 0.5:
			break
	return drones, viable_drones


def pickSystems(viable_systems, viable_subsystems):
	#THESE ARE NOT FINAL, systems can still be added afterwards
	#yeah I don't like having to make weapons guaranteed but UI issues and balancing is difficult
	systems = ["engines", "pilot", "weapons"]
	for _ in tuple(viable_systems):
		system = weighted_chance(viable_systems)
		systems.append(system)
		del viable_systems[system]
		total_weight = sum([a[1] for a in viable_systems.items()])
		if total_weight < random.randrange(100) or len(systems) > random.randint(4,5) or len(viable_systems) == 0:
			break
	for _ in tuple(viable_subsystems):
		total_weight = sum([a[1] for a in viable_subsystems.items()])
		if total_weight < random.randrange(60):
			break
		system = weighted_chance(viable_subsystems)
		systems.append(system)
		del viable_subsystems[system]
	return systems, viable_systems, viable_subsystems



def getCrewPoints(crew):
	boarder_defence_points, repair_points, firefight_points,  airless_points, crew_scrap, total_crew = 0,0,0, 0,0,0
	anaerobic = 1.0
	for race, count in crew.items():
		bonus = config.race_bonus[race]
		tp_synergies = bonus.get("tp_synergies",{})
		boarder_defence_points += count * (bonus.get("health",100)/100 * bonus.get("tp",1) * (1 + tp_synergies.get("fire",0) + tp_synergies.get("breach",0)) * bonus.get("speed",1))
		repair_points += count * (bonus.get("repair",1))
		firefight_points += count * (bonus.get("health",100)/100 * bonus.get("repair",1) * (1 + tp_synergies.get("fire",0) + tp_synergies.get("breach",0)) * bonus.get("speed",1))
		airless_points += count * (bonus.get("health",100)/100 * (bonus.get("repair",1)**0.5) * (1 + 10 * tp_synergies.get("breach",0)**2) * bonus.get("speed",1))
		anaerobic = min(anaerobic, tp_synergies.get("breach",0))
		crew_scrap += count * bonus["scrap"]
		total_crew += count
	airless_points /= total_crew
	return boarder_defence_points, repair_points, firefight_points, airless_points, anaerobic, crew_scrap


def getLayoutPoints(all_rooms, all_doors, crew):
	average_path_length = calculateAveragePathLength(all_rooms)
	ventability = getVentability(all_rooms, all_doors)
	total_crew, total_airlock_need, total_slowness = 0, 0, 0
	for race, count in crew.items():
		bonus = config.race_bonus[race]
		total_slowness += count / bonus.get("speed",1)
		total_airlock_need += count * bonus.get("airlock_need",1)
		total_crew += count
	path_points = 1 / (average_path_length * total_slowness / total_crew)
	venting_points = ventability / (total_airlock_need / total_crew)
	return path_points, venting_points


def getBoardingPoints(all_rooms, crew):
	points = 0
	synergies = {"breach":0, "fire":0, "stun":0, "clonebay":0}
	for race, count in crew.items():
		bonus = config.race_bonus[race]
		points += count * bonus.get("tp",1)
		for synergy, amount in bonus.get("tp_synergies", {}).items():
			synergies[synergy] += amount
	for room in all_rooms:
		if room.system == "teleporter":
			points *= room.dimensions[0] * room.dimensions[1]
			break
	return points, synergies


def pickCrew(layout):
	crew_count = 0
	number = random.random()
	#for now, let's not bother making auto ships because those have a few special practical requirements
	if number < 0.06: #6%
		crew_count = 1
	elif number < 0.35: #29%
		crew_count = 2
	elif number < 0.8: #45%
		crew_count = 3
	elif number < 0.99: #19%
		crew_count = 4
	else: #1% chance
		crew_count = random.randint(5,8)

	crew = collections.defaultdict(int)
	crew_weights = collections.ChainMap(config.crew_weights[layout], config.crew_weights["default"])
	for i in range(crew_count):
		race = weighted_chance(crew_weights)
		crew[race] += 1
	return crew, crew_count


def weighted_chance(thing):
	total_weight = sum([a[1] for a in thing.items()])
	if total_weight == 0:
		print("[ERROR] weighted_chance got thing with zero chance", thing)
	i = random.random() * total_weight
	for item, weight in thing.items():
		i -= weight
		if i <= 0 and weight > 0:
			return item
	print("...")

def random_from(things):
	l = len(things)
	if l == 0:
		return None
	return things[random.randrange(l)]


def getVentability(all_rooms, all_doors):
	#do a breadth-first-search to find the shortest path from each room to the nearest airlock
	# this algorithm unfortunately does not account for the number of doors connecting each room
	# nor the number of airlocks in airlock rooms
	ventability = 0
	for starting_room in all_rooms:
		is_airlock = False
		#list of tuples (door, distance)
		explored_doors = []
		for wall, door in starting_room.doors.items():
			if door is not None:
				if door.roomB is None:
					is_airlock = True
					break
				explored_doors.append((door, 0))
		if is_airlock:
			ventability += 1
			#no point checking other rooms when it vents instantly anyway
			continue
		no_changes = False
		room_frontier = []
		while no_changes == False:
			no_changes = True
			room_frontier.clear()
			for door, distance in explored_doors:
				for room in (door.roomA, door.roomB):
					if room is None:
						continue
					room_frontier.append(room)
					for wall, other_door in room.doors.items():
						if other_door is door or other_door is None:
							continue
						for index, door_ in enumerate(explored_doors):
							if door_[0] is other_door:
								break
						else:
							index = -1
						new_distance = distance + 1
						if index == -1 or new_distance < door_[1]:
							no_changes = False
							if index == -1:
								explored_doors.append((other_door, new_distance))
							else:
								explored_doors[index] = (other_door, new_distance)

		shortest_airlock_distance = None
		for door, distance in explored_doors:
			if door.roomB is None:
				if shortest_airlock_distance is None or shortest_airlock_distance > distance:
					shortest_airlock_distance = distance

		if shortest_airlock_distance == None:
			break

		ventability += 1 / (shortest_airlock_distance + 1)

	if len(all_rooms) == 0:
		average_ventability = 0
	else:
		#adding number of doors here because extra doors generally speaking help with venting no matter where they are
		average_ventability = (ventability + len(all_doors)) / len(all_rooms)

	return average_ventability


def calculateAveragePathLength(all_rooms):
	sum_ = 0
	for room in all_rooms:
		for other_room in all_rooms:
			if room is other_room:
				continue
			sum_ += room.shortestPaths[other_room.room_id]
	return sum_ / ( len(all_rooms) * (len(all_rooms) - 1) * 2 )
