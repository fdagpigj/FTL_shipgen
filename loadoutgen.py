import random
import collections
import math

import config
from config import SYSTEMS, SUBSYSTEMS, AUGMENTS, RACES, LAYOUTS


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
		must('crew_count'),

		#  TODO
		# should('mindcontrol_usefulness'),#
		should('breathableness', ignore_chance=0.05),
		# should('intruder_defense'),#
		should('fair_system_levels'),
		should('fair_reactor_power'),
		should('fair_crew_count', ignore_chance=0.1),
		should('missile_count', ignore_chance=0),
		should('drone_part_count', ignore_chance=0),
		should('no_shield_buffer', ignore_chance=0.3),
		should('no_useless_augments'),
		should('no_useless_drones'),
		should('no_useless_drone_system'),
		should('reasonable_weapons'),
		should('no_useless_lasers'),
		should('basic_defence', ignore_chance=0.2),
	]

MANDATORY_SYSTEMS = (SYSTEMS.pilot, SYSTEMS.engines)
OFFENSIVE_SYSTEMS = (SYSTEMS.weapons, SYSTEMS.teleporter, SYSTEMS.hacking, SYSTEMS.drones, SYSTEMS.mind)
DEFENSIVE_SYSTEMS = (SYSTEMS.engines, SYSTEMS.shields, SYSTEMS.cloaking, SYSTEMS.drones, SYSTEMS.pilot)
CREW_SYSTEMS = (SYSTEMS.oxygen, SYSTEMS.medbay, SYSTEMS.clonebay, SYSTEMS.drones, SYSTEMS.doors, SYSTEMS.mind)

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

	warnings = 0
	errors = 0

	clean_run = False
	turns_till_panic = 300
	# Two levels of looping here to make sure we really checked every constraint since we're not always checking each one
	while not clean_run:
		clean_run = True
		fail_recency = collections.defaultdict(int)
		unsatisfied_constraints = True
		while unsatisfied_constraints:
			unsatisfied_constraints = False
			turns_till_panic -= 1
			if turns_till_panic == 30:
				print(f'[WARNING] Entering pre-panic mode!')
				warnings += 1
			if turns_till_panic <= 0:
				print(f'[ERROR] Panicking after {warnings} warnings and {errors} errors')
				print(loadout)
				raise Panic()
			for constraint in constraints:
				cname = constraint['name']
				fail_recency[cname] += 1
				# Check constraints that failed recently on every pass, only check periodically after OK 3 times
				if (fail_recency[cname] <= 3 or fail_recency[cname] % 8 == 0) and (constraint['panic'] or turns_till_panic > 30):
					satisfied = constraint['check'](loadout)
					if satisfied is None:
						print(f'[ERROR] Constraint {cname} returned None')
						errors += 1
					if not satisfied:
						if turns_till_panic < 40:
							print(f'[DEBUG] Attempting to satisfy constraint {cname}')
						unsatisfied_constraints = True
						constraint['alleviate'](loadout)
						fail_recency[cname] = 0
						clean_run = False

	print('[DEBUG]', turns_till_panic, loadout)
	loadout['warnings'] = warnings
	loadout['errors'] = errors

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
	options = { 'drop_random_weapon': 1 }
	if SYSTEMS.weapons not in loadout['starting_systems']:
		options['add_weapons_system'] = 1
	elif loadout['weapon_slots'] < 4:
		options['add_weapon_slot'] = 0.5 if loadout['layout'] in (LAYOUTS.circle_cruiser, LAYOUTS.stealth, LAYOUTS.mantis_cruiser) else 1

	choice = weighted_chance(options)
	if choice == 'drop_random_weapon':
		drop_random_weapon(loadout)
	elif choice == 'add_weapons_system':
		loadout['starting_systems'].append(SYSTEMS.weapons)
	elif choice == 'add_weapon_slot':
		loadout['weapon_slots'] += 1


def check_drone_count(loadout):
	if SYSTEMS.drones not in loadout['starting_systems'] and len(loadout['drones']) > 0:
		return False
	return len(loadout['drones']) <= loadout['drone_slots']

def alleviate_drone_count(loadout):
	options = { 'drop_random_drone': 1 }
	if SYSTEMS.drones not in loadout['starting_systems']:
		options['add_drone_control'] = 1
	elif loadout['drone_slots'] < 3:
		options['add_drone_slot'] = 1 if loadout['layout'] == LAYOUTS.circle_cruiser else 0.4

	choice = weighted_chance(options)
	if choice == 'drop_random_drone':
		drop_random_drone(loadout)
	elif choice == 'add_drone_control':
		loadout['starting_systems'].append(SYSTEMS.drones)
	elif choice == 'add_drone_slot':
		loadout['drone_slots'] += 1


def check_drone_slots(loadout):
	return loadout['drone_slots'] < 3 or loadout['weapon_slots'] < 4

def alleviate_drone_slots(loadout):
	options = {
		'drop_drone_slot': 1 if loadout['layout'] == LAYOUTS.circle_cruiser else 3,
		'drop_weapon_slot': 2,
	}
	choice = weighted_chance(options)
	if choice == 'drop_drone_slot':
		loadout['drone_slots'] -= 1
	else:
		loadout['weapon_slots'] -= 1


def check_system_count(loadout):
	return len(tuple(filter(lambda s: s not in SUBSYSTEMS, loadout['starting_systems']))) <= 8

def alleviate_system_count(loadout):
	drop_random_system(loadout)


def check_augment_count(loadout):
	return len(loadout['augments']) < 3

def alleviate_augment_count(loadout):
	drop_random_augment(loadout)


def check_crew_count(loadout):
	if len(loadout['crew']) > 8:
		return False
	# TODO: Add support for auto ships
	elif len(loadout['crew']) == 0:
		return False
	return True

def alleviate_crew_count(loadout):
	if len(loadout['crew']) > 8:
		drop_random_crew(loadout)
	elif len(loadout['crew']) == 0:
		add_crew(loadout)


def check_fair_crew_count(loadout):
	if len(loadout['crew']) > 4:
		return False
	return True

def alleviate_fair_crew_count(loadout):
	drop_random_crew(loadout)


def check_missile_count(loadout):
	min_missiles = 0
	for weapon in loadout['weapons']:
		min_missiles += 8 * config.weapon_points[weapon].get('missiles', 0)
	if loadout['missiles'] < min_missiles:
		return False
	if loadout['missiles'] > min_missiles * 2 + 5:
		return False
	return True

def alleviate_missile_count(loadout):
	min_missiles = 0
	for weapon in loadout['weapons']:
		min_missiles += 8 * config.weapon_points[weapon].get('missiles', 0)
	max_missiles = 2 * min_missiles + 5
	loadout['missiles'] = random.randint(min_missiles, max_missiles)


def check_drone_part_count(loadout):
	min_parts = 0
	for drone in loadout['drones']:
		if config.drone_points[drone].get('onboard', 0) == 1:
			min_parts += 2
		if config.drone_points[drone].get('offence', 0) > 0:
			min_parts += 9
		else:
			min_parts += 7
	if SYSTEMS.hacking in loadout['starting_systems']:
		min_parts += 7
	if loadout['drone_parts'] < min_parts:
		return False
	if loadout['drone_parts'] > min_parts * 2 + 5:
		return False
	return True

def alleviate_drone_part_count(loadout):
	min_parts = 0
	for drone in loadout['drones']:
		if config.drone_points[drone].get('onboard', 0) == 1:
			min_parts += 2
		if config.drone_points[drone].get('offence', 0) > 0:
			min_parts += 9
		else:
			min_parts += 7
	if SYSTEMS.hacking in loadout['starting_systems']:
		min_parts += 7
	max_parts = min_parts * 2 + 5
	loadout['drone_parts'] = random.randint(min_parts, max_parts)


def check_no_shield_buffer(loadout):
	return loadout['system_levels'][SYSTEMS.shields] != 3

def alleviate_no_shield_buffer(loadout):
	if random.random() < 0.9:
		loadout['system_levels'][SYSTEMS.shields] -= 1
	else:
		loadout['system_levels'][SYSTEMS.shields] += 1


def check_offensive_capability(loadout):
	return check_gunship_ability(loadout) or check_crewkill_ability(loadout)

def alleviate_offensive_capability(loadout):
	alleviations = {
		# Get weights from available options
		"add_weapon": 5 * sum(get_weapon_options(loadout).values()),
		"add_drone": sum(get_drone_options(loadout).values()) / 3,
		"add_system": sum(get_system_options(loadout).values()),
		"add_crew": loadout['teleporter_size'] if SYSTEMS.teleporter in loadout['starting_systems'] else 0,
		"alleviate_healing_capability": 1,
		"upgrade_random_offensive_system": 8,
		"upgrade_random_system": 5,
	}
	func = weighted_chance(alleviations)
	globals()[func](loadout)


def alleviate_defensive_capability(loadout):
	alleviations = {
		"add_drone": sum(get_drone_options(loadout).values()) / 3,
		"add_system": sum(get_system_options(loadout).values()),
		"add_crew": 1,
		"alleviate_healing_capability": 1,
		"upgrade_random_defensive_system": 20,
		"upgrade_random_system": 4,
		"add_augment": sum(get_augment_options(loadout).values()),
		"upgrade_engines": 5,
		# "upgrade_shields": 5,
	}
	func = weighted_chance(alleviations)
	globals()[func](loadout)


# Must be able to deal with 2 shield layers
def check_gunship_ability(loadout):
	return get_guns_speed(loadout, hull=True)[1] > 0

def check_crewkill_ability(loadout):
	crewkill_speed = 0
	lethal = False
	if SYSTEMS.teleporter in loadout['starting_systems'] and check_healing_capability(loadout):
		boarding = 0
		for crew_member in loadout['crew']:
			boarding += config.race_bonus[crew_member]['tp']
		crewkill_speed += max(len(loadout['crew']), loadout['teleporter_size']) * boarding
		lethal = True
	if 'BOARDER' in loadout['drones']:
		crewkill_speed += 2
	if SYSTEMS.mind in loadout['starting_systems']:
		crewkill_speed += loadout['system_levels'][SYSTEMS.mind]
	gun_slowness, gun_damage, _ = get_guns_speed(loadout, crewkill=True)
	if gun_damage > 0:
		crewkill_speed += gun_damage / gun_slowness / 10
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
	options = {
		'medbay': 55,
		'clonebay': 50,
		'teleport_heal': 15 if SYSTEMS.teleporter in loadout['starting_systems'] else 0,
		'bomb_heal': 3 if SYSTEMS.weapons in loadout['starting_systems'] else 0,
	}
	choice = weighted_chance(options)
	if choice == 'medbay':
		add_or_upgrade_system(loadout, SYSTEMS.medbay)
	elif choice == 'clonebay':
		add_or_upgrade_system(loadout, SYSTEMS.clonebay)
	elif choice == 'teleport_heal':
		loadout['augments'].append(AUGMENTS.TELEPORT_HEAL)
	elif choice == 'bomb_heal':
		loadout['weapons'].append('BOMB_HEAL')



# Must be able to heal crew faster than they suffocate or have backup DNA bank
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
		medbay_level = max(1, min(3, loadout['system_levels'][SYSTEMS.medbay] ))
		healing_rate = config.system_points[SYSTEMS.medbay]['healing_rate'][medbay_level - 1]
		return healing_rate > suffocation_rate
	elif SYSTEMS.clonebay in loadout['starting_systems']:
		return AUGMENTS.BACKUP_DNA in loadout['augments']
	return False

def alleviate_crew_sustainability(loadout):
	options = { 'oxygen': 1, 'upgrade_random_crew_system': 2 }
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
	elif choice == 'upgrade_random_crew_system':
		upgrade_random_crew_system(loadout)
	elif choice == 'remove_crew':
		drop_random_crew(loadout)
	elif choice == 'backup_dna':
		loadout['augments'].append(AUGMENTS.BACKUP_DNA)
	elif choice == 'medbay':
		add_or_upgrade_system(loadout, SYSTEMS.medbay)
	elif choice == 'o2_masks':
		loadout['augments'].append(AUGMENTS.O2_MASKS)


def check_breathableness(loadout):
	if SYSTEMS.oxygen in loadout['starting_systems']:
		return True
	for crew_member in loadout['crew']:
		if crew_member != RACES.anaerobic:
			return False
	return True

def alleviate_breathableness(loadout):
	options = { 'add_oxygen': 1 }
	if RACES.anaerobic in loadout['crew']:
		options['remove_crew'] = 1
	choice = weighted_chance(options)
	if choice == 'add_oxygen':
		loadout['starting_systems'].append(SYSTEMS.oxygen)
	elif choice == 'remove_crew':
		drop_random_crew(loadout)


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
		min_level, max_level = fair_system_levels[system]
		if power < min_level:
			loadout['system_levels'][system] = min_level
		else:
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
	options = {}
	quip_key = 'weapons' if system == SYSTEMS.weapons else 'drones'
	points = config.weapon_points if system == SYSTEMS.weapons else config.drone_points
	power = loadout['system_levels'][system]
	total_quip_power = 0
	for quip in tuple(loadout[quip_key]):
		quip_power = points[quip]['power']
		total_quip_power += quip_power
		if power < quip_power:
			if random.random() < 0.8:
				power = quip_power
				loadout['system_levels'][system] = power
				return
			else:
				loadout[quip_key].remove(quip)
				return
	if power + 1 < total_quip_power:
		options['add_power'] = 2 if power < 8 else 0
		options['drop_quip'] = len(loadout[quip_key])
	elif power - random.randint(0, 1) > total_quip_power:
		options['drop_power'] = 2
		options['add_quip'] = max(0, 4 - len(loadout[quip_key]))

	choice = weighted_chance(options)
	if choice == 'add_power':
		loadout['system_levels'][system] += 1
	elif choice == 'drop_power':
		loadout['system_levels'][system] -= 1
	elif choice == 'drop_quip':
		drop_random_weapon(loadout) if system == SYSTEMS.weapons else drop_random_drone(loadout)
	elif choice == 'add_quip':
		add_weapon(loadout) if system == SYSTEMS.weapons else add_drone(loadout)


def check_reactor_power(loadout):
	reactor_power = loadout['reactor_power']
	if reactor_power < 2 or reactor_power > 25:
		return False
	zoltan_power = 0
	for crew_member in loadout['crew']:
		if crew_member == RACES.energy:
			zoltan_power += 1
	total_system_power = get_total_system_power(loadout)
	battery_power = loadout['system_levels'][SYSTEMS.battery] * 2 if SYSTEMS.battery in loadout['starting_systems'] else 0
	if reactor_power + zoltan_power + min(1, battery_power) > total_system_power:
		return False
	# Hard limit of 2 power less than necessary
	if reactor_power + zoltan_power + battery_power + 2 < total_system_power:
		return False
	return True

def alleviate_reactor_power(loadout):
	options = {}
	reactor_power = loadout['reactor_power']
	if reactor_power < 2:
		loadout['reactor_power'] = 2
		return
	if reactor_power > 25:
		loadout['reactor_power'] = 25
		return
	reactor_power = loadout['reactor_power']
	zoltan_power = 0
	for crew_member in loadout['crew']:
		if crew_member == RACES.energy:
			zoltan_power += 1
	total_system_power = get_total_system_power(loadout)
	battery_power = loadout['system_levels'][SYSTEMS.battery] * 2 if SYSTEMS.battery in loadout['starting_systems'] else 0
	if reactor_power + zoltan_power + min(1, battery_power) > total_system_power:
		options = {
			'drop_reactor_power': 1,
			# 'fast_drop_reactor_power': 1,
		}
	if reactor_power + zoltan_power + battery_power + 2 < total_system_power:
		options = {
			'add_reactor_power': 1,
			# 'fast_add_reactor_power': 1,
			'downgrade_random_system': 2,
		}
	choice = weighted_chance(options)
	if choice == 'drop_reactor_power':
		drop_reactor_power(loadout, zoltan_power, battery_power)
	elif choice == 'add_reactor_power':
		add_reactor_power(loadout, zoltan_power, battery_power)
	elif choice == 'fast_drop_reactor_power':
		target = total_system_power - reactor_power - zoltan_power - min(1, battery_power)
		loadout['reactor_power'] = target
	elif choice == 'fast_add_reactor_power':
		target = total_system_power - reactor_power - zoltan_power - battery_power - 2
		loadout['reactor_power'] = target
	elif choice == 'downgrade_random_system':
		downgrade_random_system(loadout)


def check_fair_reactor_power(loadout):
	reactor_power = loadout['reactor_power']
	zoltan_power = 0
	for crew_member in loadout['crew']:
		if crew_member == RACES.energy:
			zoltan_power += 1
	total_system_power = get_total_system_power(loadout)
	battery_power = loadout['system_levels'][SYSTEMS.battery] * 2 if SYSTEMS.battery in loadout['starting_systems'] else 0
	if reactor_power + zoltan_power > 11 or reactor_power + zoltan_power + battery_power > 12:
		return False
	if reactor_power + zoltan_power + battery_power + 1 < total_system_power:
		return False
	return True

def alleviate_fair_reactor_power(loadout):
	options = {}
	reactor_power = loadout['reactor_power']
	zoltan_power = 0
	for crew_member in loadout['crew']:
		if crew_member == RACES.energy:
			zoltan_power += 1
	total_system_power = get_total_system_power(loadout)
	battery_power = loadout['system_levels'][SYSTEMS.battery] * 2 if SYSTEMS.battery in loadout['starting_systems'] else 0
	if reactor_power + zoltan_power + min(1, battery_power) > 11:
		options = {
			'drop_reactor_power': 2,
			# 'fast_drop_reactor_power': 2,
		}
	elif reactor_power + zoltan_power + battery_power + 1 < total_system_power:
		options = {
			'add_reactor_power': 2,
			# 'fast_add_reactor_power': 1,
			'downgrade_random_system': 2,
		}
	choice = weighted_chance(options)
	if choice == 'drop_reactor_power':
		drop_reactor_power(loadout, zoltan_power, battery_power)
	elif choice == 'add_reactor_power':
		add_reactor_power(loadout, zoltan_power, battery_power)
	elif choice == 'fast_drop_reactor_power':
		target = 11 - reactor_power - zoltan_power - min(1, battery_power)
		loadout['reactor_power'] = target
	elif choice == 'fast_add_reactor_power':
		target = total_system_power - reactor_power - zoltan_power - battery_power - 1
		loadout['reactor_power'] = target
	elif choice == 'downgrade_random_system':
		downgrade_random_system(loadout)



def check_s1_survivability(loadout):
	time_to_disarm, time_to_survive, _ = get_survival_times(loadout)
	# print(f"[DEBUG] Time to disarm {time_to_disarm:.1f}, Time to survive {time_to_survive:.1f}")
	return time_to_disarm + 1 < time_to_survive

def alleviate_s1_survivability(loadout):
	time_to_disarm, time_to_survive, unused = get_survival_times(loadout)
	if len(unused) > 0:
		to_drop = random_from(unused)
		if to_drop['type'] == 'weapon':
			loadout['weapons'].remove(to_drop['name'])
		elif to_drop['type'] == 'drone':
			loadout['drones'].remove(to_drop['name'])
	options = {
		'alleviate_offensive_capability': time_to_disarm / 20,
		'alleviate_defensive_capability': 60 / max(1, time_to_survive),
	}

	choice = weighted_chance(options)
	if choice == 'alleviate_offensive_capability':
		alleviate_offensive_capability(loadout)
	else:
		alleviate_defensive_capability(loadout)


def check_no_useless_augments(loadout):
	return len(get_useless_augments(loadout)) == 0

def alleviate_no_useless_augments(loadout):
	for augment in get_useless_augments(loadout):
		loadout['augments'].remove(augment)


def check_no_useless_drones(loadout):
	return len(get_useless_drones(loadout)) == 0

def alleviate_no_useless_drones(loadout):
	for drone in get_useless_drones(loadout):
		loadout['drones'].remove(drone)


def check_no_useless_drone_system(loadout):
	if SYSTEMS.drones in loadout['starting_systems'] and len(loadout['drones']) == 0:
		return False
	return True

def alleviate_no_useless_drone_system(loadout):
	if random.random() < 0.9:
		loadout['starting_systems'].remove(SYSTEMS.drones)
	else:
		add_drone(loadout)


def check_no_useless_lasers(loadout):
	return len(get_useless_lasers(loadout)) == 0

def alleviate_no_useless_lasers(loadout):
	for weapon in get_useless_lasers(loadout):
		loadout['weapons'].remove(weapon)


def check_reasonable_weapons(loadout):
	gun_slowness, gun_damage, _ = get_guns_speed(loadout)
	if gun_damage > 0 and gun_slowness / gun_damage < 4:
		return False
	return True

def alleviate_reasonable_weapons(loadout):
	drop_random_weapon(loadout)


def check_basic_defence(loadout):
	if SYSTEMS.shields in loadout['starting_systems'] and loadout['system_levels'][SYSTEMS.shields] > 1:
		return True
	if SYSTEMS.cloaking in loadout['starting_systems']:
		return True
	return False

def alleviate_basic_defence(loadout):
	system = weighted_chance(get_system_options(loadout, subset=(SYSTEMS.shields, SYSTEMS.cloaking), avoid_duplicates=False))
	add_or_upgrade_system(loadout, system)















##########
# Helpers
##########


def get_total_system_power(loadout):
	total_system_power = 0
	for system in loadout['starting_systems']:
		if system not in SUBSYSTEMS:
			total_system_power += loadout['system_levels'][system]
	return total_system_power


def get_survival_times(loadout):
	MAGIC = 2.0
	gun_slowness, gun_damage, unused = get_guns_speed(loadout)
	time_to_disarm = math.inf if gun_damage <= 0 else gun_slowness * MAGIC / min(MAGIC, gun_damage)
	if check_crewkill_ability(loadout):
		time_to_disarm = min(time_to_disarm, get_sp_disarm_speed(loadout))
	time_to_survive = get_survival_time(loadout)
	return time_to_disarm, time_to_survive, unused


def get_guns_speed(loadout, crewkill=False, hull=False):
	# Note: Power use need not be considered too deeply as every weapon and drone is equivalent
	#  as there can only ever be 1 too litte power in each system
	weapons = []

	for weapon in loadout['weapons']:
		stats = config.weapon_points.get(weapon)
		weapon = {
			'type': 'weapon',
			'name': weapon,
			'slowness': stats['slowness'],
			'shield_drop': stats.get('shield_drop', 0),
			'sp': stats.get('sp', 0),
			'damage': stats.get('offence', 0) * stats.get('hull_multi', 1) + stats.get('fire', 0),
			'crewkill': stats.get('crewkill', 0) + stats.get('fire', 0),
			'system_damage': stats.get('offence', 0) + stats.get('nonlethal', 0) + stats.get('fire', 0),
			'missiles': stats.get('missiles', 0),
			'power': stats['power'],
			'drone_power': 0,
			'drone_parts': 0,
		}
		if stats.get('sp', 0) >= 5:
			weapon['shield_drop'] += (weapon['system_damage'] + 1) // 2
		# Beams are special
		if stats.get('beam_length'):
			weapon['damage'] = stats['beam_length'] * stats.get('beam_damage', 0) * stats.get('hull_multi', 1) + stats.get('fire', 0)
			weapon['crewkill'] = stats.get('crewkill', 0) + stats.get('fire', 0)
			weapon['system_damage'] = stats['beam_damage'] + stats.get('fire', 0)
			weapon['shield_drop'] = stats['beam_damage'] // 2
		weapons.append(weapon)

	for drone in loadout['drones']:
		stats = config.drone_points[drone]
		if not 'slowness' in stats:
			continue
		drone = {
			'type': 'drone',
			'name': drone,
			'slowness': stats['slowness'],
			'shield_drop': stats.get('shield_drop', 0),
			'sp': stats.get('sp', 0),
			'damage': stats.get('offence', 0) * stats.get('hull_multi', 1) + stats.get('fire', 0),
			'crewkill': stats.get('crewkill', 0) + stats.get('fire', 0),
			'system_damage': stats.get('offence', 0) + stats.get('nonlethal', 0) + stats.get('fire', 0),
			'missiles': 0,
			'power': 0,
			'drone_power': stats['power'],
			'drone_parts': 1,
		}
		weapons.append(drone)

	if SYSTEMS.hacking in loadout['starting_systems']:
		hacking_level = max(1, min(3, loadout['system_levels'][SYSTEMS.hacking] ))
		hacking = {
			'type': 'hacking',
			'name': 'hacking',
			'slowness': 8,
			'shield_drop': config.system_points[SYSTEMS.hacking]['shield_drop'][hacking_level - 1],
			'sp': 0,
			'damage': 0,
			'crewkill': 0,
			'system_damage': 0,
			'missiles': 0,
			'power': 0,
			'drone_power': 0,
			'drone_parts': 1,
		}
		weapons.append(hacking)

	weapons_by_shield_drop = sorted(weapons,
		key=lambda w: w['shield_drop'] / w['slowness']
	)
	damage_key = 'damage' if hull else ('crewkill' if crewkill else 'system_damage')
	weapons_by_damage = sorted(weapons,
		key=lambda w: w[damage_key] / w['slowness'] / (w['missiles'] + 1)
	)

	needed_shield_drop = 2
	remaining_power = loadout['system_levels'][SYSTEMS.weapons]
	remaining_drone_power = loadout['system_levels'][SYSTEMS.drones]
	damage = 0
	slowness = 0
	used_drone_parts = 0
	used_missiles = 0
	unused = []
	while len(weapons) > 0:
		if needed_shield_drop > 0:
			weapon = weapons_by_shield_drop.pop()
			shield_drop = True
			weapons_by_damage.remove(weapon)
		else:
			weapon = weapons_by_damage.pop()
			shield_drop = False
			weapons_by_shield_drop.remove(weapon)
		weapons.remove(weapon)
		if weapon['power'] > remaining_power or weapon['drone_power'] > remaining_drone_power:
			unused.append(weapon)
			continue
		if weapon['missiles'] > 0 and (damage >= 3 or used_missiles > 2):
			unused.append(weapon)
			continue
		if weapon['drone_parts'] > 0 and (damage >= 3 or used_drone_parts > 2):
			unused.append(weapon)
			continue
		if (weapon['slowness'] > slowness + 1 and damage >= 3) or (weapon['slowness'] >= 2 * slowness and damage > 1):
			unused.append(weapon)
			continue
		if not shield_drop and weapon[damage_key] <= 0:
			unused.append(weapon)
			continue
		used_missiles += weapon['missiles']
		used_drone_parts += weapon['drone_parts']
		remaining_power -= weapon['power']
		remaining_drone_power -= weapon['drone_power']
		slowness = max(slowness, weapon['slowness'])
		if shield_drop:
			sd = weapon['shield_drop']
			unspent_shield_drop = sd - needed_shield_drop
			needed_shield_drop -= sd
			if unspent_shield_drop > 0:
				damage += weapon[damage_key] * unspent_shield_drop / sd
		else:
			damage += weapon[damage_key]

	if damage <= 0 or slowness <= 0:
		return math.inf, 0, unused
	if len(loadout['crew']) > 2:
		slowness *= 0.9
	for augment in loadout['augments']:
		if augment == AUGMENTS.AUTO_COOLDOWN:
			slowness *= 0.9

	return slowness, damage, unused



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
		extra_time += avg_enemy_slowness / 2 + loadout['system_levels'][SYSTEMS.cloaking] * 5
	zshield_time = avg_enemy_slowness / (
		avg_enemy_damage_lasers +
		avg_enemy_damage_missiles +
		avg_enemy_damage_ion * 2 / (2 if AUGMENTS.ION_ARMOR in loadout['augments'] else 1) +
		avg_enemy_damage_beams * 2 +
		avg_enemy_damage_bombs
	)
	if AUGMENTS.ENERGY_SHIELD in loadout['augments']:
		extra_time += zshield_time
	if 'DRONE_SHIELD_PLAYER' in loadout['drones']:
		extra_time += zshield_time * 0.2
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
	return max(0, min(1, evasion + shield_bonus + drone_bonus))

def get_missile_resistance(loadout):
	evasion = get_evasion(loadout)
	drone_bonus = 0
	for drone in loadout['drones']:
		stats = config.drone_points[drone]
		defence = stats.get('defence', 0)
		if defence > 0:
			drone_bonus += 1 - 1 / defence
	return max(0, min(1, 1 - (1 - evasion) * (1 - drone_bonus)))

def get_ion_resistance(loadout):
	return max(0, min(1, 1 - (1 - get_laser_resistance(loadout)) * (1 - 0.5 * (AUGMENTS.ION_ARMOR in loadout['augments'])) ))

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
	return max(0, min(1, 1 - (1 - shield_bonus) * (1 - drone_bonus)))


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
	return max(0, min(1, base * autopilot_multi))


def get_useless_augments(loadout):
	useless = []
	if AUGMENTS.TELEPORT_HEAL in loadout['augments'] and SYSTEMS.teleporter not in loadout['starting_systems']:
		useless.append(AUGMENTS.TELEPORT_HEAL)
	if AUGMENTS.BACKUP_DNA in loadout['augments'] and SYSTEMS.clonebay not in loadout['starting_systems']:
		useless.append(AUGMENTS.BACKUP_DNA)
	if AUGMENTS.NANO_MEDBAY in loadout['augments'] and SYSTEMS.medbay not in loadout['starting_systems']:
		useless.append(AUGMENTS.NANO_MEDBAY)
	if AUGMENTS.DRONE_SPEED in loadout['augments']:
		for drone in loadout['drones']:
			if config.drone_points[drone].get('onboard', 0) == 1:
				break
		else:
			useless.append(AUGMENTS.DRONE_SPEED)
	if AUGMENTS.LIFE_SCANNER in loadout['augments'] and RACES.slug in loadout['crew']:
		useless.append(AUGMENTS.LIFE_SCANNER)
	if AUGMENTS.EXPLOSIVE_REPLICATOR in loadout['augments']:
		for weapon in loadout['weapons']:
			if config.weapon_points[weapon].get('missiles', 0) > 0:
				break
		else:
			useless.append(AUGMENTS.EXPLOSIVE_REPLICATOR)
	if AUGMENTS.BATTERY_BOOSTER in loadout['augments'] and SYSTEMS.battery not in loadout['starting_systems']:
		useless.append(AUGMENTS.BATTERY_BOOSTER)
	if AUGMENTS.HACKING_STUN in loadout['augments'] and SYSTEMS.hacking not in loadout['starting_systems']:
		useless.append(AUGMENTS.HACKING_STUN)
	if AUGMENTS.DRONE_RECOVERY in loadout['augments'] and SYSTEMS.teleporter not in loadout['starting_systems']:
		for drone in loadout['drones']:
			if config.drone_points[drone].get('defence', 0) > 0:
				break
		else:
			useless.append(AUGMENTS.DRONE_RECOVERY)
	return useless


def get_useless_drones(loadout):
	useless = []
	if 'BATTLE' in loadout['drones'] and len(loadout['crew']) > 3:
		useless.append('BATTLE')
	if 'REPAIR' in loadout['drones']:
		repair_speed = 0
		for crew_member in loadout['crew']:
			repair_speed += config.race_bonus[crew_member].get('repair', 1)
		if repair_speed > 5:
			useless.append('REPAIR')
	_, _, unused = get_guns_speed(loadout)
	for w in unused:
		if w['type'] == 'drone':
			useless.append(w['name'])
	return useless


def get_useless_lasers(loadout):
	useless = []
	_, _, unused = get_guns_speed(loadout)
	for w in unused:
		if w['type'] == 'weapon' and w['name'][:5] == 'LASER':
			useless.append(w['name'])
	return useless


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

def get_system_options(loadout, subset=None, avoid_duplicates=True):
	options = {}
	fallback_options = {}
	weights = collections.ChainMap(config.system_weights[loadout['layout']], config.system_weights["default"])
	for system in SYSTEMS:
		fallback_weight = 0
		if avoid_duplicates and system in loadout['starting_systems']:
			weight = 0
		elif subset is not None and system not in subset:
			weight = 0
			fallback_weight = weights[system]
		else:
			weight = weights[system]
		options[system] = weight
		fallback_options[system] = max(fallback_weight, weight)

	if sum(options.values()) == 0:
		return fallback_options
	return options


def add_weapon(loadout):
	weapon = weighted_chance(get_weapon_options(loadout))
	loadout['weapons'].append(weapon)

def add_drone(loadout):
	drone = weighted_chance(get_drone_options(loadout))
	loadout['drones'].append(drone)

def add_augment(loadout):
	augment = weighted_chance(get_augment_options(loadout))
	loadout['augments'].append(augment)

def add_system(loadout):
	system = weighted_chance(get_system_options(loadout))
	loadout['starting_systems'].append(system)


def upgrade_random_offensive_system(loadout):
	system = weighted_chance(get_system_options(loadout, subset=OFFENSIVE_SYSTEMS, avoid_duplicates=False))
	add_or_upgrade_system(loadout, system)

def upgrade_random_defensive_system(loadout):
	system = weighted_chance(get_system_options(loadout, subset=DEFENSIVE_SYSTEMS, avoid_duplicates=False))
	add_or_upgrade_system(loadout, system)

def upgrade_random_crew_system(loadout):
	system = weighted_chance(get_system_options(loadout, subset=CREW_SYSTEMS, avoid_duplicates=False))
	add_or_upgrade_system(loadout, system)


def upgrade_random_system(loadout):
	system = random_from(loadout['starting_systems'])
	add_or_upgrade_system(loadout, system)

def downgrade_random_system(loadout):
	system = random_from(loadout['starting_systems'])
	downgrade_or_remove_system(loadout, system)


def downgrade_or_remove_system(loadout, system):
	if system not in loadout['starting_systems']:
		return
	if loadout['system_levels'][system] > 1:
		loadout['system_levels'][system] -= 1
	elif system not in MANDATORY_SYSTEMS:
		loadout['starting_systems'].remove(system)

def add_or_upgrade_system(loadout, system):
	if system not in SYSTEMS:
		return
	if system not in loadout['starting_systems']:
		loadout['starting_systems'].append(system)
	else:
		loadout['system_levels'][system] += 1


def upgrade_engines(loadout):
	add_or_upgrade_system(loadout, SYSTEMS.engines)

def upgrade_shields(loadout):
	add_or_upgrade_system(loadout, SYSTEMS.shields)


def drop_reactor_power(loadout, zoltan_power, battery_power):
	options = {
		'reactor_power': 8,
	}
	if battery_power > 0:
		options['remove_battery'] = 3
	if zoltan_power > 0:
		options['remove_zoltan'] = len(loadout['crew'])

	choice = weighted_chance(options)
	if choice == 'reactor_power':
		loadout['reactor_power'] -= 1
	elif choice == 'remove_zoltan':
		loadout['crew'].remove(RACES.energy)
	elif choice == 'remove_battery':
		downgrade_or_remove_system(loadout, SYSTEMS.battery)

def add_reactor_power(loadout, zoltan_power, battery_power):
	options = {
		'reactor_power': 2 if loadout['layout'] == LAYOUTS.energy_cruiser else 8,
	}
	if len(loadout['crew']) < 8 * random.random():
		options['add_zoltan'] = 1
	elif battery_power < 4 and random.random() < 0.4:
		options['add_battery'] = 1

	choice = weighted_chance(options)
	if choice == 'reactor_power':
		loadout['reactor_power'] += 1
	elif choice == 'add_zoltan':
		loadout['crew'].append(RACES.energy)
	elif choice == 'add_battery':
		add_or_upgrade_system(loadout, SYSTEMS.battery)


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

def drop_random_system(loadout):
	eligible = tuple(filter(lambda s: s not in SUBSYSTEMS and s not in MANDATORY_SYSTEMS, loadout['starting_systems']))
	loadout['starting_systems'].remove(random_from(eligible))

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

def random_from(things):
	l = len(things)
	if l == 0:
		return None
	return things[random.randrange(l)]


init()