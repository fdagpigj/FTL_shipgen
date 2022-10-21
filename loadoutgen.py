import random
import collections
import math

import config
from config import SYSTEMS, SUBSYSTEMS, AUGMENTS, RACES


class Panic(Exception):
	pass


CONSTRAINTS = None
def init():
	global CONSTRAINTS
	CONSTRAINTS = [
		must('funk_disabled'),
		must('weapon_count'),
		must('drone_count'),
		must('drone_slots'),
		must('system_count'),
		must('offensive_capability'),
		must('crew_sustainability'),
		must('healing_capability'),
		must('augment_count'),
		must('s1_survivability'),
		must('system_levels'),
		must('weapons_power'),
		must('drones_power'),
		must('reactor_power'),

		#  TODO
		# should('mindcontrol_usefulness'),#
		# should('breathableness'),#
		# should('intruder_defense'),#
		should('fair_system_levels'),
		should('fair_reactor_power'),
		# should('missile_count', ignore_chance=0),
		# should('drone_part_count', ignore_chance=0),
	]

MANDATORY_SYSTEMS = (SYSTEMS.pilot, SYSTEMS.engines)

fair_system_levels = {
	SYSTEMS.oxygen: [1, 2],
	SYSTEMS.teleporter: [1, 2],
	SYSTEMS.cloaking: [1, 2],
	SYSTEMS.pilot: [1, 3],
	SYSTEMS.medbay: [1, 3],
	SYSTEMS.shields: [1, 4],
	SYSTEMS.artillery: [1, 2],
	SYSTEMS.engines: [1, 4],
	SYSTEMS.weapons: [1, 4],
	SYSTEMS.drones: [1, 4],
	SYSTEMS.sensors: [1, 3],
	SYSTEMS.doors: [1, 2],
	SYSTEMS.clonebay: [1, 2],
	SYSTEMS.hacking: [1, 2],
	SYSTEMS.battery: [1, 2],
	SYSTEMS.mind: [1, 2]
}


def generateLoadout(all_rooms, all_doors, layout):
	loadout = {
		'starting_systems': list(MANDATORY_SYSTEMS),
		'system_levels': collections.defaultdict(lambda: 1),
		'crew': pickCrew(layout),
		'weapons': [],
		'weapon_slots': random.randint(3,4),
		'drone_slots': random.randint(2,3),
		'drones': [],
		'augments': [],
		'description': '',
		'name': 'RANDOM SHIP',
		'reactor_power': 2,
		'missiles': 0,
		'drone_parts': 0,
		'teleporter_size': 0, # only present for calculating crewkill capability
		'layout': layout, # only present for getting ship class preferences
	}

	for room in all_rooms:
		if room.system == "teleporter":
			loadout['teleporter_size'] = room.dimensions[0] * room.dimensions[1]
			break

	constraints = tuple(filter(lambda c: c['ignore_chance'] <= random.random(), CONSTRAINTS))

	clean_run = False
	turns_till_panic = 200
	# Two levels of looping here to make sure we really checked every constraint since we're not always checking each one
	while not clean_run:
		clean_run = True
		fail_recency = collections.defaultdict(int)
		unsatisfied_constraints = True
		while unsatisfied_constraints:
			unsatisfied_constraints = False
			turns_till_panic -= 1
			if turns_till_panic <= 0:
				print(loadout)
				raise Panic()
			for constraint in constraints:
				cname = constraint['name']
				fail_recency[cname] += 1
				# Check constraints that failed recently on every pass, only check periodically after OK 3 times
				if (fail_recency[cname] <= 3 or fail_recency[cname] % 8 == 0) and (constraint['panic'] or turns_till_panic > 30):
					if not constraint['check'](loadout):
						print(f'[DEBUG] Attempting to satisfy constraint {cname}')
						unsatisfied_constraints = True
						constraint['alleviate'](loadout)
						fail_recency[cname] = 0
						clean_run = False

	print(turns_till_panic, loadout)

	return loadout







def check_funk_disabled(loadout):
	if SYSTEMS.weapons not in loadout['starting_systems']:
		return False
	if SYSTEMS.medbay in loadout['starting_systems'] and SYSTEMS.clonebay in loadout['starting_systems']:
		return False
	for system in SYSTEMS:
		if system not in loadout['starting_systems']:
			initial_power = config.system_points[system].get('initial_power', 1)
			if loadout['system_levels'][system] != initial_power:
				return False
	return True

def alleviate_funk_disabled(loadout):
	if SYSTEMS.weapons not in loadout['starting_systems']:
		loadout['starting_systems'].append(SYSTEMS.weapons)
	if SYSTEMS.medbay in loadout['starting_systems'] and SYSTEMS.clonebay in loadout['starting_systems']:
		loadout['starting_systems'].remove(SYSTEMS.medbay if random.random() < 0.5 else SYSTEMS.clonebay)
	for system in SYSTEMS:
		if system not in loadout['starting_systems']:
			initial_power = config.system_points[system].get('initial_power', 1)
			if loadout['system_levels'][system] != initial_power:
				loadout['system_levels'][system] = initial_power


def check_weapon_count(loadout):
	if SYSTEMS.weapons not in loadout['starting_systems'] and len(loadout['weapons']) > 0:
		return False
	return len(loadout['weapons']) <= loadout['weapon_slots']

def alleviate_weapon_count(loadout):
	if SYSTEMS.weapons not in loadout['starting_systems']:
		loadout['starting_systems'].append(SYSTEMS.weapons)
		return
	if loadout['weapon_slots'] < 4 and random.random() < 0.5:
		loadout['weapon_slots'] += 1
	else:
		drop_random_weapon(loadout)


def check_drone_count(loadout):
	if SYSTEMS.drones not in loadout['starting_systems'] and len(loadout['drones']) > 0:
		return False
	return len(loadout['drones']) <= loadout['drone_slots']

def alleviate_drone_count(loadout):
	if SYSTEMS.drones not in loadout['starting_systems']:
		loadout['starting_systems'].append(SYSTEMS.drones)
		return
	if loadout['drone_slots'] < 3 and random.random() < 0.5:
		loadout['drone_slots'] += 1
	else:
		drop_random_drone(loadout)


def check_drone_slots(loadout):
	return loadout['drone_slots'] < 3 or loadout['weapon_slots'] < 4

def alleviate_drone_slots(loadout):
	loadout['drone_slots'] -= 1
	if len(loadout['drones']) > loadout['drone_slots']:
		drop_random_drone(loadout)


def check_system_count(loadout):
	return len(tuple(filter(lambda s: s not in SUBSYSTEMS, loadout['starting_systems']))) <= 8

def alleviate_system_count(loadout):
	eligible = tuple(filter(lambda s: s not in SUBSYSTEMS and s not in MANDATORY_SYSTEMS, loadout['starting_systems']))
	loadout['starting_systems'].remove(random_from(eligible))


def check_augment_count(loadout):
	return len(loadout['augments']) < 3

def alleviate_augment_count(loadout):
	drop_random_augment(loadout)


def check_offensive_capability(loadout):
	return check_gunship_ability(loadout) or check_crewkill_ability(loadout)

def alleviate_offensive_capability(loadout):
	alleviations = {
		# Get weights from available options
		"add_weapon": sum(get_weapon_options(loadout).values()),
		"add_drone": sum(get_drone_options(loadout).values()),
		"add_system": sum(get_system_options(loadout).values()),
		"add_crew": loadout['teleporter_size'] if SYSTEMS.teleporter in loadout['starting_systems'] else 0,
		"alleviate_healing_capability": 1,
		"upgrade_random_system": 20,
	}
	func = weighted_chance(alleviations)
	globals()[func](loadout)


def alleviate_defensive_capability(loadout):
	alleviations = {
		"add_drone": sum(get_drone_options(loadout).values()),
		"add_system": sum(get_system_options(loadout).values()),
		"add_crew": 4,
		"alleviate_healing_capability": 1,
		"upgrade_random_system": 20,
	}
	func = weighted_chance(alleviations)
	globals()[func](loadout)


# Must be able to deal with 2 shield layers
def check_gunship_ability(loadout):
	return get_guns_speed(loadout) < math.inf

def check_crewkill_ability(loadout):
	crewkill_speed = 0
	lethal = False
	if SYSTEMS.teleporter in loadout['starting_systems'] and check_healing_capability(loadout):
		boarding = 0
		for crew_member in loadout['crew']:
			boarding += config.race_bonus[crew_member]['tp']
		crewkill_speed += max(len(loadout['crew']), loadout['teleporter_size']) * boarding
		lethal = True
	if SYSTEMS.mind in loadout['starting_systems']:
		crewkill_speed += loadout['system_levels'][SYSTEMS.mind]
	guns = get_guns_speed(loadout, crewkill=True)
	if guns < math.inf and guns > 0:
		crewkill_speed += 10 / guns
		lethal = True
	return lethal and crewkill_speed >= 2.0


def check_healing_capability(loadout):
	if SYSTEMS.medbay in loadout['starting_systems'] or SYSTEMS.clonebay in loadout['starting_systems']:
		return True
	if SYSTEMS.teleporter in loadout['starting_systems'] and AUGMENTS.TELEPORT_HEAL in loadout['augments']:
		return True
	if 'BOMB_HEAL' in loadout['weapons']:
		return True
	return False

def alleviate_healing_capability(loadout):
	if random.random() < 0.95:
		loadout['starting_systems'].append(SYSTEMS.medbay if random.random() < 0.55 else SYSTEMS.clonebay)
	elif SYSTEMS.teleporter in loadout['starting_systems']:
		loadout['augments'].append(AUGMENTS.TELEPORT_HEAL)
	elif SYSTEMS.weapons in loadout['starting_systems']:
		loadout['weapons'].append('BOMB_HEAL')


# Must have medbay lvl 2 or backup DNA bank if oxygenless with normal crew
def check_crew_sustainability(loadout):
	if SYSTEMS.oxygen in loadout['starting_systems']:
		return True
	suffocation_rate = 0.0
	for crew_member in loadout['crew']:
		if crew_member != RACES.anaerobic:
			if crew_member == RACES.crystal:
				suffocation_rate = max(0.5, suffocation_rate)
			else:
				suffocation_rate = max(1.0, suffocation_rate)
				break
	if AUGMENTS.O2_MASKS in loadout['augments']:
		suffocation_rate *= 0.5
	if SYSTEMS.medbay in loadout['starting_systems']:
		healing_rate = config.system_points[SYSTEMS.medbay]['healing_rate'][loadout['system_levels'][SYSTEMS.medbay] - 1]
		return healing_rate > suffocation_rate
	elif SYSTEMS.clonebay in loadout['starting_systems']:
		return AUGMENTS.BACKUP_DNA in loadout['augments']
	return False

def alleviate_crew_sustainability(loadout):
	options = { 'oxygen': 1 }
	if len(loadout['crew']) > 1:
		options['remove_crew'] = 0.5
	if SYSTEMS.clonebay in loadout['starting_systems']:
		options['backup_dna'] = 1
	elif SYSTEMS.medbay in loadout['starting_systems']:
		if loadout['system_levels'][SYSTEMS.medbay] < 3:
			options['medbay'] = 1
		if AUGMENTS.O2_MASKS not in loadout['augments']:
			options['o2_masks'] = 1
	else:
		options['medbay'] = 1

	choice = weighted_chance(options)
	if choice == 'oxygen':
		add_or_upgrade_system(loadout, SYSTEMS.oxygen)
	elif choice == 'remove_crew':
		drop_random_crew(loadout)
	elif choice == 'backup_dna':
		loadout['augments'].append(AUGMENTS.BACKUP_DNA)
	elif choice == 'medbay':
		add_or_upgrade_system(loadout, SYSTEMS.medbay)
	elif choice == 'o2_masks':
		loadout['augments'].append(AUGMENTS.O2_MASKS)


def check_system_levels(loadout):
	for system in SYSTEMS:
		power = loadout['system_levels'][system]
		if power < 1:
			return False
		else:
			max_level = len(config.system_points[system]['scrap'])
			if power > max_level:
				return False
	return True

def alleviate_system_levels(loadout):
	for system in SYSTEMS:
		power = loadout['system_levels'][system]
		if power < 1:
			loadout['system_levels'][system] = 1
		else:
			max_level = len(config.system_points[system]['scrap'])
			if power > max_level:
				loadout['system_levels'][system] = max_level


def check_fair_system_levels(loadout):
	for system in loadout['starting_systems']:
		power = loadout['system_levels'][system]
		if power < fair_system_levels[system][0]:
			return False
		else:
			if power > fair_system_levels[system][1]:
				return False
	return True

def alleviate_fair_system_levels(loadout):
	for system in loadout['starting_systems']:
		power = loadout['system_levels'][system]
		if power < 1:
			loadout['system_levels'][system] = 1
		else:
			max_level = len(config.system_points[system]['scrap'])
			if power > max_level:
				loadout['system_levels'][system] = max_level


def check_weapons_power(loadout):
	return check_weapon_or_drones_power(loadout, SYSTEMS.weapons)

def alleviate_weapons_power(loadout):
	alleviate_weapons_or_drones_power(loadout, SYSTEMS.weapons)


def check_drones_power(loadout):
	return check_weapon_or_drones_power(loadout, SYSTEMS.drones)

def alleviate_drones_power(loadout):
	alleviate_weapons_or_drones_power(loadout, SYSTEMS.drones)


def check_weapon_or_drones_power(loadout, system):
	quip_key = 'weapons' if system == SYSTEMS.weapons else 'drones'
	points = config.weapon_points if system == SYSTEMS.weapons else config.drone_points
	if system in loadout['starting_systems']:
		power = loadout['system_levels'][system]
		total_quip_power = 0
		for quip in loadout[quip_key]:
			quip_power = points[quip]['power']
			total_quip_power += quip_power
			if power < quip_power:
				return False
		if power + 1 < total_quip_power or power - 1 > total_quip_power:
			return False
	return True

def alleviate_weapons_or_drones_power(loadout, system):
	quip_key = 'weapons' if system == SYSTEMS.weapons else 'drones'
	points = config.weapon_points if system == SYSTEMS.weapons else config.drone_points
	if system in loadout['starting_systems']:
		power = loadout['system_levels'][system]
		total_quip_power = 0
		for quip in tuple(loadout[quip_key]):
			quip_power = points[quip]['power']
			total_quip_power += quip_power
			if power < quip_power:
				if random.random() < 0.8:
					power = quip_power
					loadout['system_levels'][system] = power
				else:
					loadout[quip_key].remove(quip)
		if power + 1 < total_quip_power:
			if random.random() < 0.6:
				loadout['system_levels'][system] += 1
			else:
				drop_random_weapon(loadout) if system == SYSTEMS.weapons else drop_random_drone(loadout)
		elif power - 1 > total_quip_power:
			if random.random() < 0.6:
				loadout['system_levels'][system] -= 1
			else:
				add_weapon(loadout) if system == SYSTEMS.weapons else add_drone(loadout)


def check_reactor_power(loadout):
	reactor_power = loadout['reactor_power']
	if reactor_power < 2 or reactor_power > 25:
		return False
	effective_reactor_power = reactor_power
	for crew_member in loadout['crew']:
		if crew_member == RACES.energy:
			effective_reactor_power += 1
	total_system_power = 0
	for system in loadout['starting_systems']:
		total_system_power += loadout['system_levels'][system]
	if total_system_power < effective_reactor_power:
		return False
	battery_power = loadout['system_levels'][SYSTEMS.battery] * 2 if SYSTEMS.battery in loadout['starting_systems'] else 0
	# Hard limit of 2 power less than necessary
	if effective_reactor_power + 2 + battery_power < total_system_power:
		return False
	return True

def alleviate_reactor_power(loadout):
	reactor_power = loadout['reactor_power']
	if reactor_power < 2:
		loadout['reactor_power'] = 2
	if reactor_power > 25:
		loadout['reactor_power'] = 25
	reactor_power = loadout['reactor_power']
	effective_reactor_power = reactor_power
	for crew_member in loadout['crew']:
		if crew_member == RACES.energy:
			effective_reactor_power += 1
	total_system_power = 0
	for system in loadout['starting_systems']:
		total_system_power += loadout['system_levels'][system]
	battery_power = loadout['system_levels'][SYSTEMS.battery] * 2 if SYSTEMS.battery in loadout['starting_systems'] else 0
	if total_system_power < effective_reactor_power:
		drop_reactor_power(loadout, effective_reactor_power, reactor_power, battery_power)
	if effective_reactor_power + 2 + battery_power < total_system_power:
		add_reactor_power(loadout, effective_reactor_power, reactor_power, battery_power)


def check_fair_reactor_power(loadout):
	reactor_power = loadout['reactor_power']
	effective_reactor_power = reactor_power
	for crew_member in loadout['crew']:
		if crew_member == RACES.energy:
			effective_reactor_power += 1
	total_system_power = 0
	for system in loadout['starting_systems']:
		total_system_power += loadout['system_levels'][system]
	battery_power = loadout['system_levels'][SYSTEMS.battery] * 2 if SYSTEMS.battery in loadout['starting_systems'] else 0
	if effective_reactor_power > 11 or effective_reactor_power + battery_power > 12:
		return False
	if effective_reactor_power + 1 + battery_power < total_system_power:
		return False
	return True

def alleviate_fair_reactor_power(loadout):
	reactor_power = loadout['reactor_power']
	effective_reactor_power = reactor_power
	for crew_member in loadout['crew']:
		if crew_member == RACES.energy:
			effective_reactor_power += 1
	total_system_power = 0
	for system in loadout['starting_systems']:
		total_system_power += loadout['system_levels'][system]
	battery_power = loadout['system_levels'][SYSTEMS.battery] * 2 if SYSTEMS.battery in loadout['starting_systems'] else 0
	if effective_reactor_power > 11 or effective_reactor_power + battery_power > 12:
		drop_reactor_power(loadout, effective_reactor_power, reactor_power, battery_power)
	elif effective_reactor_power + 1 + battery_power < total_system_power:
		add_reactor_power(loadout, effective_reactor_power, reactor_power, battery_power)


def check_s1_survivability(loadout):
	time_to_disarm = get_guns_speed(loadout)
	if check_crewkill_ability(loadout):
		time_to_disarm = min(time_to_disarm, get_sp_disarm_speed(loadout))
	time_to_survive = get_survival_time(loadout)
	print(f"[DEBUG] Time to disarm {time_to_disarm:.1f}, Time to survive {time_to_survive:.1f}")
	return time_to_disarm < time_to_survive

def alleviate_s1_survivability(loadout):
	if random.random() < 0.5:
		alleviate_offensive_capability(loadout)
	else:
		alleviate_defensive_capability(loadout)





##########
# Helpers
##########


def get_guns_speed(loadout, crewkill=False):
	# TODO: make this get the shield drop, damage ability, speed and power use of each weapon
	#  and intelligently order them by which purpose it should be used for
	#  and then only use each weapon for at most one purpose
	total_shield_drop = 0
	slowness = -1
	for weapon in loadout['weapons'] + loadout['drones']:
		stats = config.weapon_points.get(weapon) or config.drone_points[weapon]
		if not 'slowness' in stats:
			continue
		slowness = max(slowness, stats['slowness'])
		total_shield_drop += stats.get('shield_drop', 0)
		if stats.get('sp', 0) >= 5:
			total_shield_drop += (stats.get('nonlethal', 0) + 1) // 2
			total_shield_drop += stats.get('fire', 0)
	if SYSTEMS.hacking in loadout['starting_systems']:
		total_shield_drop += loadout['system_levels'][SYSTEMS.hacking]
	damage = 0
	for weapon in loadout['weapons'] + loadout['drones']:
		stats = config.weapon_points.get(weapon) or config.drone_points[weapon]
		if stats.get('sp', 0) >= 2 - total_shield_drop:
			if stats.get('missiles', 0) == 0 or crewkill or AUGMENTS.EXPLOSIVE_REPLICATOR in loadout['augments']:
				damage += stats.get('offence', 0)
				damage += stats.get('crewkill', 0) if crewkill else 0
	if damage == 0 or slowness <= 0:
		return math.inf
	if len(loadout['crew']) > 2:
		slowness *= 0.9
	return slowness * 3 / min(3, damage)


def get_sp_disarm_speed(loadout):
	slowest_non_missile = 1
	fastest_missile = 99
	non_missile_damage = 0
	missile_damage = 0
	for weapon in loadout['weapons'] + loadout['drones']:
		stats = config.weapon_points.get(weapon) or config.drone_points[weapon]
		if stats.get('sp', 0) >= 2:
			damage = stats.get('nonlethal', 0) + stats.get('offence', 0) + stats.get('fire', 0) + stats.get('breach', 0)
			# TODO: use actual blueprint values in the beam configs and calculate the exact damages to avoid having to do this silliness
			if weapon[:4] == 'BEAM':
				damage = damage * 0.2
			speed = stats['slowness']
			if stats.get('missiles', 0) > 0:
				# Only consider one missile-consuming weapon
				if damage > missile_damage or (damage >= 2 and speed < fastest_missile):
					missile_damage = damage
					fastest_missile = speed
			else:
				non_missile_damage = non_missile_damage + damage
				slowest_non_missile = max(slowest_non_missile, speed)
	total_damage = non_missile_damage + missile_damage
	if total_damage <= 0:
		return math.inf
	slowness = max(slowest_non_missile if non_missile_damage > 0 else 0, fastest_missile if missile_damage > 0 else 0)
	if len(loadout['crew']) > 2:
		slowness *= 0.9
	return slowness * 3 / min(3, total_damage)


def get_weapon_charge_bonus(loadout):
	bonus = 1.0
	if len(loadout['crew']) > 2:
		bonus *= 0.9
	for augment in loadout['augments']:
		if augment == AUGMENTS.AUTO_COOLDOWN:
			# This is not exact but close enough
			bonus *= 0.9
	return bonus


def get_survival_time(loadout):
	avg_enemy_slowness = 13.0
	avg_enemy_damage_lasers = 2.0
	avg_enemy_damage_missiles = 0.8
	avg_enemy_damage_ion = 0.5
	avg_enemy_damage_beams = 0.5
	avg_enemy_damage_bombs = 0.5
	avg_enemy_damage_drones = 0.2
	time = 5 * avg_enemy_slowness / (
		avg_enemy_damage_lasers * (1 - get_laser_resistance(loadout)) +
		avg_enemy_damage_missiles * (1 - get_missile_resistance(loadout)) +
		avg_enemy_damage_ion * (1 - get_ion_resistance(loadout)) +
		avg_enemy_damage_beams * (1 - get_beam_resistance(loadout)) +
		avg_enemy_damage_bombs * (1 - get_bomb_resistance(loadout)) +
		avg_enemy_damage_drones * (1 - get_drone_resistance(loadout))
	)
	extra_time = 0
	if SYSTEMS.cloaking in loadout['starting_systems']:
		extra_time += avg_enemy_slowness + loadout['system_levels'][SYSTEMS.cloaking] * 5
	if AUGMENTS.ENERGY_SHIELD in loadout['augments']:
		zshield_time = avg_enemy_slowness / (
			avg_enemy_damage_lasers +
			avg_enemy_damage_missiles +
			avg_enemy_damage_ion * 2 / (2 if AUGMENTS.ION_ARMOR in loadout['augments'] else 1) +
			avg_enemy_damage_beams * 2 +
			avg_enemy_damage_bombs
		)
		extra_time += zshield_time
	return time + extra_time


def get_laser_resistance(loadout):
	evasion = get_evasion(loadout)
	shield_bonus = 0
	drone_bonus = 0
	if SYSTEMS.shields in loadout['starting_systems']:
		shield_layers = loadout['system_levels'][SYSTEMS.shields] // 2
		if shield_layers == 1:
			shield_bonus = 0.25
		elif shield_layers == 2:
			shield_bonus = 0.6
		elif shield_layers > 2:
			shield_bonus = 0.9
	for drone in loadout['drones']:
		stats = config.drone_points[drone]
		drone_bonus += stats.get('laser_defence', 0)
	return evasion + shield_bonus + drone_bonus

def get_missile_resistance(loadout):
	evasion = get_evasion(loadout)
	drone_bonus = 0
	for drone in loadout['drones']:
		stats = config.drone_points[drone]
		defence = stats.get('defence', 0)
		if defence > 0:
			drone_bonus += 1 - 1 / defence
	return 1 - (1 - evasion) * (1 - drone_bonus)

def get_ion_resistance(loadout):
	return 1 - (1 - get_laser_resistance(loadout)) * (1 - 0.5 * (AUGMENTS.ION_ARMOR in loadout['augments']))

def get_beam_resistance(loadout):
	if SYSTEMS.shields in loadout['starting_systems']:
		shield_layers = loadout['system_levels'][SYSTEMS.shields] // 2
		if shield_layers == 1:
			return 0.5
		elif shield_layers == 2:
			return 0.8
		elif shield_layers > 2:
			return 0.9
	return 0

def get_bomb_resistance(loadout):
	return get_evasion(loadout)

def get_drone_resistance(loadout):
	shield_bonus = 0
	drone_bonus = 0
	if SYSTEMS.shields in loadout['starting_systems']:
		shield_layers = loadout['system_levels'][SYSTEMS.shields] // 2
		if shield_layers == 1:
			shield_bonus = 0.2
		elif shield_layers == 2:
			shield_bonus = 0.4
		elif shield_layers > 2:
			shield_bonus = 0.7
	for drone in loadout['drones']:
		if drone == 'ANTI_DRONE':
			drone_bonus = 1 - (1 - drone_bonus) * 0.1
	return 1 - (1 - shield_bonus) * (1 - drone_bonus)


def get_evasion(loadout):
	engines = {
		1: 0.05,
		2: 0.10,
		3: 0.15,
		4: 0.20,
		5: 0.25,
		6: 0.28,
		7: 0.31,
		8: 0.35
	}
	base = engines.get(loadout['system_levels'][SYSTEMS.engines], 0)
	crew = len(loadout['crew'])
	base += 0.05 * min(2, crew)
	autopilot = { 1: 0, 2: 0.5, 3: 0.8 }
	autopilot_base = autopilot.get(loadout['system_levels'][SYSTEMS.pilot], 0)
	autopilot_need = 0.01
	if crew < 3:
		autopilot_need = 0.1
		if crew == 1:
			autopilot_need = 0.4 - 0.2 * ('REPAIR' in loadout['drones'])
	autopilot_multi = (autopilot_need * autopilot_base) + (1 - autopilot_need)
	return base * autopilot_multi



def get_weapon_options(loadout):
	options = {}
	for category in config.weapon_categories.values():
		weight = category['weights'].get(loadout['layout']) or category['weights']['default']
		for weapon in category['included']:
			options[weapon] = weight / config.weapon_points[weapon]['power']
	return options

def get_drone_options(loadout):
	options = {}
	for category in config.drone_categories.values():
		weight = category['weights'].get(loadout['layout']) or category['weights']['default']
		for drone in category['included']:
			existing_count = loadout['drones'].count(drone)
			# Slightly decreased chance for duplicates
			options[drone] = weight / (existing_count + 1)
	return options

def get_augment_options(loadout):
	options = {}
	weights = collections.ChainMap(config.augment_weights[loadout['layout']], config.augment_weights["default"])
	for augment in AUGMENTS:
		# No duplicate augments
		if augment in loadout['augments']:
			weight = 0
		else:
			weight = weights[augment]
		options[augment] = weight
	return options

def get_system_options(loadout):
	options = {}
	weights = collections.ChainMap(config.system_weights[loadout['layout']], config.system_weights["default"])
	for system in SYSTEMS:
		# No duplicate systems
		if system in loadout['starting_systems']:
			weight = 0
		else:
			weight = weights[system]
		options[system] = weight
	return options


def add_weapon(loadout):
	weapon = weighted_chance(get_weapon_options(loadout))
	loadout['weapons'].append(weapon)

def add_drone(loadout):
	drone = weighted_chance(get_drone_options(loadout))
	loadout['drones'].append(drone)

def add_augment(loadout):
	augment = weighted_chance(get_augment_options(loadout))
	loadout['augments'].append(drone)

def add_system(loadout):
	system = weighted_chance(get_system_options(loadout))
	loadout['starting_systems'].append(system)


def upgrade_random_system(loadout):
	system = random_from(loadout['starting_systems'])
	add_or_upgrade_system(loadout, system)


def downgrade_or_remove_system(loadout, system):
	if system not in loadout['starting_systems']:
		return
	if loadout['system_levels'][system] > 1:
		loadout['system_levels'][system] -= 1
	else:
		loadout['starting_systems'].remove(system)

def add_or_upgrade_system(loadout, system):
	if system not in loadout['starting_systems']:
		loadout['starting_systems'].append(system)
	else:
		loadout['system_levels'][system] += 1


def drop_reactor_power(loadout, effective_reactor_power, reactor_power, battery_power):
	if battery_power > 0 and random.random() < 0.5:
		downgrade_or_remove_system(loadout, SYSTEMS.battery)
	elif effective_reactor_power > reactor_power and len(loadout['crew']) > 1 and random.random() * 10 < len(loadout['crew']):
		loadout['crew'].remove(RACES.energy)
	else:
		loadout['reactor_power'] -= 1

def add_reactor_power(loadout, effective_reactor_power, reactor_power, battery_power):
	if len(loadout['crew']) < 8 * random.random() and (loadout['layout'] == config.LAYOUTS.energy_cruiser or random.random() < 0.5):
		loadout['crew'].append(RACES.energy)
	elif battery_power < 4 and random.random() < 0.4:
		add_or_upgrade_system(loadout, SYSTEMS.battery)
	else:
		loadout['reactor_power'] += 1


def add_crew(loadout):
	weights = collections.ChainMap(config.crew_weights[loadout['layout']], config.crew_weights["default"])
	race = weighted_chance(weights)
	loadout['crew'].append(race)


def drop_random_weapon(loadout):
	drop_random_from(loadout['weapons'])

def drop_random_drone(loadout):
	drop_random_from(loadout['drones'])

def drop_random_augment(loadout):
	drop_random_from(loadout['augments'])

def drop_random_crew(loadout):
	drop_random_from(loadout['crew'])

def drop_random_from(x):
	l = len(x)
	if l == 0:
		return None
	x.pop(random.randrange(l))




def must(name):
	return {
		'name': name,
		'check': globals()[f'check_{name}'],
		'alleviate': globals()[f'alleviate_{name}'],
		'panic': True,
		'ignore_chance': 0,
	}

def should(name, panic=False, ignore_chance=0.01):
	return {
		'name': name,
		'check': globals()[f'check_{name}'],
		'alleviate': globals()[f'alleviate_{name}'],
		'panic': panic,
		'ignore_chance': ignore_chance,
	}



def pickCrew(layout):
	#for now, let's not bother making auto ships because those have a few special practical requirements
	crew_count = weighted_chance({1: 0.06, 2: 0.29, 3: 0.45, 4: 0.19,  5: 0.02, 6: 0.01, 7: 0.005, 8: 0.0025})
	# crew = collections.defaultdict(int)
	crew = []
	crew_weights = collections.ChainMap(config.crew_weights[layout], config.crew_weights["default"])
	for i in range(crew_count):
		race = weighted_chance(crew_weights)
		# crew[race] += 1
		crew.append(race)
	# return crew, crew_count
	return crew


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


init()