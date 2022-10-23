import random
import collections
import math
import time

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
		should('fair_system_count', ignore_chance=0.2),
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
		# Only for displaying a summary at the end
		'warnings': [],
		'errors': [],
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
				warn(loadout, f'[WARNING] Entering pre-panic mode!')
			if turns_till_panic <= 0:
				print(f'[ERROR] Panicking after {warnings} warnings and {errors} errors')
				print(loadout)
				raise Panic()
			for constraint in constraints:
				cname = constraint['name']
				fail_recency[cname] += 1
				# Check constraints that failed recently on every pass, only check periodically after OK 3 times
				if (fail_recency[cname] <= 3 or fail_recency[cname] % 3 == 0) and (constraint['panic'] or turns_till_panic > 30):
					satisfied = constraint['check'](loadout)
					if satisfied is None:
						error(loadout, f'Constraint {cname} returned None')
					if not satisfied:
						if turns_till_panic < 40:
							print(f'[DEBUG] Attempting to satisfy constraint {cname}')
						unsatisfied_constraints = True
						constraint['alleviate'](loadout)
						fail_recency[cname] = 0
						clean_run = False

	print('[DEBUG]', turns_till_panic, loadout)

	return loadout


def warn(loadout, message):
	print(f'[WARNING] {message}')
	loadout['warnings'].append(message)

def error(loadout, message):
	print(f'[ERROR] {message}')
	loadout['errors'].append(message)






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
	return loadout['drone_slots'] + loadout['weapon_slots'] <= 6

def alleviate_drone_slots(loadout):
	if loadout['weapon_slots'] > 4:
		loadout['weapon_slots'] = 4
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


def check_fair_system_count(loadout):
	if len(tuple(filter(lambda s: s not in SUBSYSTEMS, loadout['starting_systems']))) > 7:
		return False
	if not 7 <= len(loadout['starting_systems']) <= 10:
		return False
	return True

def alleviate_fair_system_count(loadout):
	if len(loadout['starting_systems']) < 7:
		add_system(loadout)
	else:
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
	# Check that we can damage systems
	if get_guns_speed(loadout)[1] <= 0:
		return False
	# Check that we can damage hull without the use of missiles
	if get_guns_speed(loadout, hull=True, needed_shield_drop=0, allow_missiles=False)[1] <= 0:
		return False
	return True

def check_crewkill_ability(loadout):
	crewkill_speed, lethal = get_crewkill_speed(loadout)
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
		'bomb_heal': 5 if SYSTEMS.weapons in loadout['starting_systems'] else 0,
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
	reactor_power, zoltan_power, battery_power, total_system_power = get_reactor_levels(loadout)
	if reactor_power < 2 or reactor_power > 25:
		return False
	if reactor_power + zoltan_power + min(1, battery_power) > total_system_power:
		return False
	# Hard limit of 2 power less than necessary
	if reactor_power + zoltan_power + battery_power + 2 < total_system_power:
		return False
	return True

def alleviate_reactor_power(loadout):
	options = {}
	reactor_power, zoltan_power, battery_power, total_system_power = get_reactor_levels(loadout)
	if reactor_power < 2:
		loadout['reactor_power'] = 2
		return
	if reactor_power > 25:
		loadout['reactor_power'] = 25
		return
	if reactor_power + zoltan_power + min(1, battery_power) > total_system_power:
		options = {
			'drop_reactor_power': 1,
		}
	if reactor_power + zoltan_power + battery_power + 2 < total_system_power:
		options = {
			'add_reactor_power': 1,
			'downgrade_random_system': 2,
		}
	choice = weighted_chance(options)
	if choice == 'drop_reactor_power':
		drop_reactor_power(loadout, zoltan_power, battery_power)
	elif choice == 'add_reactor_power':
		add_reactor_power(loadout, zoltan_power, battery_power)
	elif choice == 'downgrade_random_system':
		downgrade_random_system(loadout)


def check_fair_reactor_power(loadout):
	reactor_power, zoltan_power, battery_power, total_system_power = get_reactor_levels(loadout)
	if reactor_power + zoltan_power > 11 or reactor_power + zoltan_power + battery_power > 12:
		return False
	if reactor_power + zoltan_power + battery_power + 1 < total_system_power:
		return False
	return True

def alleviate_fair_reactor_power(loadout):
	options = {}
	reactor_power, zoltan_power, battery_power, total_system_power = get_reactor_levels(loadout)
	if reactor_power + zoltan_power > 11 or reactor_power + zoltan_power + battery_power > 12:
		options = {
			'drop_reactor_power': 2,
		}
	elif reactor_power + zoltan_power + battery_power + 1 < total_system_power:
		options = {
			'add_reactor_power': 2,
			'downgrade_random_system': 2,
		}
	choice = weighted_chance(options)
	if choice == 'drop_reactor_power':
		drop_reactor_power(loadout, zoltan_power, battery_power)
	elif choice == 'add_reactor_power':
		add_reactor_power(loadout, zoltan_power, battery_power)
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
	if gun_damage > 0 and gun_slowness < 3 * gun_damage:
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


def get_reactor_levels(loadout):
	reactor_power = loadout['reactor_power']
	zoltan_power = 0
	for crew_member in loadout['crew']:
		if crew_member == RACES.energy:
			zoltan_power += 1
	total_system_power = get_total_system_power(loadout)
	battery_power = loadout['system_levels'][SYSTEMS.battery] * 2 if SYSTEMS.battery in loadout['starting_systems'] else 0
	return reactor_power, zoltan_power, battery_power, total_system_power


def get_total_system_power(loadout):
	total_system_power = 0
	for system in loadout['starting_systems']:
		if system not in SUBSYSTEMS:
			system_power = loadout['system_levels'][system]
			if system == SYSTEMS.shields and system_power % 2 != 0:
				system_power -= 1
			elif system in (SYSTEMS.weapons, SYSTEMS.drones):
				system_power = min(system_power, get_weapon_or_drones_total_power(loadout, system))
			total_system_power += system_power
	return total_system_power


def get_weapon_or_drones_total_power(loadout, system):
	quip_key = 'weapons' if system == SYSTEMS.weapons else 'drones'
	points = config.weapon_points if system == SYSTEMS.weapons else config.drone_points
	total_quip_power = 0
	for quip in loadout[quip_key]:
		quip_power = points[quip]['power']
		total_quip_power += quip_power
	return total_quip_power


def get_survival_times(loadout):
	MAGIC = 2.0
	time_to_survive = get_survival_time(loadout)
	gun_slowness, gun_damage, unused = get_guns_speed(loadout, preferred_sort='highest_damage', max_slowness=time_to_survive)
	time_to_disarm = math.inf if gun_damage <= 0 else gun_slowness * MAGIC / min(MAGIC, gun_damage)
	crewkill_speed, can_crewkill = get_crewkill_speed(loadout)
	if check_crewkill_ability(loadout):
		time_to_disarm = min(time_to_disarm, get_sp_disarm_speed(loadout))
	return time_to_disarm, time_to_survive, unused



def get_crewkill_speed(loadout):
	crewkill_damage = 0
	can_crewkill = False
	synergies = get_guns_bonuses(loadout)

	if 'BOARDER' in loadout['drones']:
		crewkill_damage += 2
		can_crewkill = True

	if SYSTEMS.teleporter in loadout['starting_systems'] and check_healing_capability(loadout):
		boarders = []
		for crew_member in loadout['crew']:
			# TODO: Include synergies
			base = config.race_bonus[crew_member]['tp']
			boarders.append(config.race_bonus[crew_member]['tp'])
		boarders.sort(reverse=True)
		crewkill_damage += sum(boarders[:loadout['teleporter_size']])
		can_crewkill = True

	if SYSTEMS.mind in loadout['starting_systems']:
		mc_level = min(3, max(1, loadout['system_levels'][SYSTEMS.mind]))
		crewkill_damage += config.system_points[SYSTEMS.mind]['crewkill'][mc_level - 1]

	gun_slowness, gun_damage, _ = get_guns_speed(loadout, crewkill=True, preferred_sort='highest_damage')
	if gun_damage > 0:
		crewkill_damage += gun_damage * 0.15
		can_crewkill = True

	return crewkill_damage, can_crewkill


def get_guns_bonuses(loadout):
	bonuses = {'fire': 0, 'breach': 0, 'stun': 0}

	for quip_key in ('weapons', 'drones'):
		points = config.weapon_points if quip_key == 'weapons' else config.drone_points
		for quip in loadout[quip_key]:
			stats = points[quip]
			for bonus in bonuses:
				bonuses[bonus] += stats.get(bonus, 0)

	return bonuses



def get_guns_speed(loadout, crewkill=False, hull=False,
		needed_shield_drop=2, allow_missiles=True,
		max_slowness=math.inf, preferred_sort='highest_dps'):
	# TODO: Split into initial and followup volleys, the latter not using missiles
	# TODO: Account for drone use in defense
	# TODO: Account for ion stacking
	# TODO: Consider followup and interluding volleys
	weapons = []

	# For debugging
	# loadout['weapons'] = ['BOMB_ION', 'BEAM_HULL']



	for weapon in loadout['weapons']:
		stats = config.weapon_points[weapon]
		weapon = {
			'type': 'weapon',
			'name': weapon,
			'slowness': stats['slowness'],
			'shield_drop': stats.get('shield_drop', 0),
			'sp': stats.get('sp', 0),
			'charges': stats.get('charges', 1),
			'damage': stats.get('offence', 0) * stats.get('hull_multi', 1) + stats.get('fire', 0),
			'crewkill': stats.get('crewkill', 0) + stats.get('fire', 0) + stats.get('offence', 0) * 0.1,
			'system_damage': stats.get('offence', 0) + stats.get('nonlethal', 0) + stats.get('fire', 0),
			'missiles': stats.get('missiles', 0) / (2 if AUGMENTS.EXPLOSIVE_REPLICATOR in loadout['augments'] else 1),
			'power': stats['power'],
			'drone_power': 0,
			'drone_parts': 0,
		}
		# bombs and missiles
		if stats.get('sp', 0) >= 5:
			weapon['shield_drop'] = (weapon['system_damage'] + 1) // 2
		# Beams are special
		if stats.get('beam_length'):
			weapon['damage'] = stats['beam_length'] * stats.get('beam_damage', 0) * stats.get('hull_multi', 1) + stats.get('fire', 0)
			weapon['crewkill'] = stats.get('crewkill', 0) + stats.get('fire', 0) + stats.get('beam_damage', 0) * 0.2
			weapon['system_damage'] = stats['beam_damage'] + stats.get('fire', 0)
			weapon['shield_drop'] = stats['beam_damage'] // 2
		if allow_missiles or weapon['missiles'] == 0:
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
			'charges': 1,
			'damage': stats.get('offence', 0) * stats.get('hull_multi', 1) + stats.get('fire', 0),
			'crewkill': stats.get('crewkill', 0) + stats.get('fire', 0) - stats.get('offence', 0),
			'system_damage': stats.get('offence', 0) + stats.get('nonlethal', 0) + stats.get('fire', 0),
			'missiles': 0,
			'power': 0,
			'drone_power': stats['power'],
			'drone_parts': 0.5 if AUGMENTS.DRONE_RECOVERY in loadout['augments'] else 1,
		}
		weapons.append(drone)

	if SYSTEMS.hacking in loadout['starting_systems']:
		hacking_level = max(1, min(3, loadout['system_levels'][SYSTEMS.hacking] ))
		hacking = {
			'type': 'hacking',
			'name': 'hacking',
			'slowness': 8,
			'shield_drop': config.system_points[SYSTEMS.hacking]['shield_drop'][hacking_level - 1],
			'sp': 5,
			'charges': 1,
			'damage': 0,
			# Pseudo damage
			'crewkill': 0.5 * (hacking_level - 1), # oxygen/medbay/clonebay
			'system_damage': hacking_level,
			'missiles': 0,
			'power': 0,
			'drone_power': 0,
			'drone_parts': 1,
		}
		weapons.append(hacking)

	# Illegal setup, skip expensive calculation
	if len(weapons) > 7:
		return 1, 99, weapons

	damage_key = 'damage' if hull else ('crewkill' if crewkill else 'system_damage')

	weapons_power = loadout['system_levels'][SYSTEMS.weapons]
	drones_power = loadout['system_levels'][SYSTEMS.drones]
	# There can only be at most 7 "weapons" (4w2d1h or 3w3d1h). That's "only" 7! = 5040 permutations.
	# Fortunately, this can be limited:
	# - use at most 2 total drone parts + missiles (for UX reasons)
	# - beams with less than 2 normal damage can always be checked last
	# - sp 5 weapons can always be checked first,
	#    however then we must check targetting the shields system vs the desired target (as well as the usual option of not using the weapon).
	# - if system power is limited.
	#    (eg. it's very unlikely for the program to allow >4 system power which means max 2 offensive drones)
	# - the order of duplicates doesn't matter.
	# - weapons which deal no damage of the desired type can be ignored once shields are down
	# - weapons which neither deal damage of the desired type nor can drop shields can be ignored outright
	#    (eg. bio beam for non-crew damage, stun bomb, ...)
	weapons_by_priority = {
		"high": [],
		"normal": [],
		"low": [],
	}
	for weapon in weapons:
		if weapon['shield_drop'] <= 0:
			if weapon[damage_key] > 0:
				weapons_by_priority['low'].append(weapon)
			continue
		if weapon['sp'] >= 5:
			weapons_by_priority['high'].append(weapon)
			continue
		weapons_by_priority['normal'].append(weapon)

	remaining = {
		"weapons": weapons_by_priority,
		"weapons_power": weapons_power,
		"drones_power": drones_power,
		"shields": needed_shield_drop,
		"ammo": 2,
	}
	DEBUG = False
	if DEBUG and len(weapons) > 1:
		print(f"[DEBUG] Getting options for {len(weapons)} \"weapons\"")
		for i in range(10):
			print('')
	start = time.time()
	options = recursively_find_weapon_options(remaining, damage_key)
	end = time.time()

	real_options = list(filter(lambda o: o['damage'] > 0 and o['slowness'] < max_slowness, options))
	best = {}
	if len(real_options) > 0:
		best['highest_damage'] = max(real_options, key=lambda o: o['damage'])
		best['highest_dps'] = max(real_options, key=lambda o: o['damage'] / o['slowness'] if o['damage'] > 0 else -1)
		# best['fastest_to_3'] = min(real_options, key=lambda o: o['slowness'] if o['damage'] >= 3 else math.inf)
		best['fastest'] = min(real_options, key=lambda o: o['slowness'] if o['damage'] > 0 else math.inf)
		# best['cheapest'] = min(real_options, key=lambda o: o['ammo'] * 1000 + o['slowness'] if o['damage'] > 0 else math.inf)

	def print_option(o, comment=''):
		print(f"{comment} - {o['damage']}dmg {o['slowness']}s {o['missiles']}m {o['drone_parts']}dr {len(o['weapons_used'])}w {o['__shields']}sh")


	### REMOVE ME
	unused = weapons.copy()
	damage = 0
	slowness = 0
	used_drone_parts = 0
	used_missiles = 0
	remaining_power = weapons_power
	remaining_drone_power = drones_power
	weapons_by_shield_drop = sorted(unused,
		key=lambda w: w['shield_drop'] / w['slowness']
	)
	weapons_by_damage = sorted(unused,
		key=lambda w: w[damage_key] / w['slowness'] / (w['missiles'] + 1)
	)
	while len(unused) > 0:
		if needed_shield_drop > 0:
			weapon = weapons_by_shield_drop.pop()
			shield_drop = True
			weapons_by_damage.remove(weapon)
		else:
			weapon = weapons_by_damage.pop()
			shield_drop = False
			weapons_by_shield_drop.remove(weapon)
		unused.remove(weapon)
		if weapon['power'] > remaining_power or weapon['drone_power'] > remaining_drone_power:
			continue
		if weapon['missiles'] > 0 and (damage >= 3 or used_missiles > 2):
			continue
		if weapon['drone_parts'] > 0 and (damage >= 3 or used_drone_parts > 2):
			continue
		if (weapon['slowness'] > slowness + 1 and damage >= 3) or (weapon['slowness'] >= 2 * slowness and damage > 1):
			continue
		if not shield_drop and weapon[damage_key] <= 0:
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
			if unspent_shield_drop > 0 and weapon['sp'] == 0:
				damage += weapon[damage_key] * unspent_shield_drop / sd
		else:
			damage += weapon[damage_key]

	# if damage <= 0 or slowness <= 0:
	# 	return math.inf, 0, unused

	warning = False
	if damage > 0 and used_missiles + used_drone_parts <= 2 and slowness <= max_slowness:
		if len(best) > 0:
			if damage > best['highest_damage']['damage']:
				error(loadout, "Oh noes! Old algo found a better raw damage output.")
				warning = True
			if damage / slowness > best['highest_dps']['damage'] / best['highest_dps']['slowness']:
				error(loadout, "Oh noes! Old algo found a better DPS.")
				warning = True
			if slowness < best['fastest']['slowness']:
				error(loadout, "Oh noes! Old algo found a faster option.")
				warning = True
		else:
			error(loadout, "Oh noes! Old algo found a solution where new did not.")
			warning = True
	if end - start > 0.1:
		warn(loadout, f'Took too long to find guns speed')
		warning = True
	if warning:
		total_weapons_power = sum(map(lambda w: w['power'], weapons))
		total_drones_power = sum(map(lambda w: w['drone_power'], weapons))
		print(f"{damage_key}, {weapons_power} weapon power ({total_weapons_power} needed), {drones_power} drone power ({total_drones_power} needed)")
		print('weapons:', list(map(lambda w: w['name'], weapons)))
		print(f"Old algo got {damage}dmg {slowness}s {used_missiles}m {used_drone_parts}dr {len(weapons) - len(unused)}w")
		print(f"Got {len(real_options)} ways to use available weapons in {end - start} seconds")
		for k in best:
			print_option(best[k], comment=k)
		if len(real_options) < 10:
			for o in real_options:
				print_option(o)
		print(loadout)
		raise Exception()
	### END REMOVE ME

	if len(real_options) == 0:
		return math.inf, 0, []

	best_option = best[preferred_sort]
	damage, slowness = best_option['damage'], best_option['slowness']
	weapons_by_name = {}
	for w in weapons:
		weapons_by_name[w['name']] = w
	unused = weapons
	for weapon_name in best_option['weapons_used']:
		unused.remove(weapons_by_name[weapon_name])

	if len(loadout['crew']) > 2:
		slowness *= 0.9
	for augment in loadout['augments']:
		if augment == AUGMENTS.AUTO_COOLDOWN:
			slowness *= 0.9

	return slowness, damage, unused


def recursively_find_weapon_options(remaining, damage_key, depth=1):
	options_list = []
	weapon = None
	DEBUG = False

	weapon_options = tuple()
	for priority in ('high', 'normal', 'low'):
		if len(remaining['weapons'][priority]) > 0:
			weapon_options = remaining['weapons'][priority]
			break

	if DEBUG:
		print('-' * depth, remaining)
	if len(weapon_options) == 0:
		# print('-' * depth, 'no more weapons!')
		return [{
			'weapons_used': [],
			'damage': 0,
			'slowness': 0,
			'missiles': 0,
			'drone_parts': 0,
			'ammo': 0,
			'__shields': remaining['shields'],
		}]

	checked_weapons = set()
	for i, weapon in enumerate(weapon_options):
		# don't re-check duplicates
		if weapon['name'] in checked_weapons:
			continue
		checked_weapons.add(weapon['name'])
		new_weapon_options = tuple(w for j, w in enumerate(weapon_options) if j != i)

		choices = [('pass', 0)]
		weapon_ammo = weapon['missiles'] + weapon['drone_parts']
		can_afford = remaining['ammo'] >= weapon_ammo
		can_power = remaining['weapons_power'] >= weapon['power'] and remaining['drones_power'] >= weapon['drone_power']
		if can_afford and can_power:
			if remaining['shields'] > weapon['sp']:
				for c in range(weapon['charges']):
					choices.append(('shields', c+1))
			else:
				# if shield-piercing weapon should choose to hit shield system
				if remaining['shields'] > 0 and weapon['system_damage'] > 0:
					for c in range(weapon['charges']):
						choices.append(('shields', c+1))
				if weapon[damage_key] > 0:
					for c in range(weapon['charges']):
						choices.append(('damage', c+1))
		elif DEBUG:
			print('-' * depth, can_afford, can_power, remaining, weapon)

		if DEBUG:
			print('-' * depth, weapon['name'], choices)

		for choice, charges in choices:
			if DEBUG:
				print('-' * depth, choice)
			new_remaining = remaining.copy()
			new_remaining['weapons'] = remaining['weapons'].copy()
			new_remaining['weapons'][priority] = new_weapon_options
			if choice == 'pass':
				pass
			else:
				new_remaining['weapons_power'] -= weapon['power']
				new_remaining['drones_power'] -= weapon['drone_power']
				# print('-' * depth, f"subtracting {weapon_ammo} ammo from {new_remaining['ammo']}")
				new_remaining['ammo'] -= weapon_ammo
				if choice == 'shields':
					new_remaining['shields'] = max(0, remaining['shields'] - weapon['shield_drop'] * charges)

			sub_options = recursively_find_weapon_options(new_remaining, damage_key, depth+1)
			for option in sub_options:
				# print('-' * depth, option)
				if choice != 'pass':
					option['weapons_used'].append(weapon['name'])
					option['slowness'] = max(option['slowness'], weapon['slowness'] * charges)
					option['ammo'] += weapon_ammo
					option['missiles'] += weapon['missiles']
					option['drone_parts'] += weapon['drone_parts']

					if choice == 'damage':
						option['damage'] += weapon[damage_key] * charges

					else:
						# First shot(s) hit shields, remaining ones hit targetted room
						if choice == 'shields' and new_remaining['shields'] == 0 and weapon['shield_drop'] * charges > 1 and weapon['sp'] == 0:
							unspent_shots = weapon['shield_drop'] * charges - remaining['shields']
							if unspent_shots > 0:
								option['damage'] += weapon[damage_key] * unspent_shots / weapon['shield_drop']

				if DEBUG:
					print('-' * depth, option)
				# If the decision tree is returning and the last weapon used wasn't able to deal damage, it's dead weight
				if choice == 'pass' or option['damage'] > 0:
					options_list.append(option)
				elif DEBUG:
					print('-' * depth, 'discarding option')

	# Remove any options that are strictly worse than (or equal to) any other
	for other_option in reversed(options_list):
		for option in reversed(options_list):
			if option is other_option:
				continue
			weaker = option['damage'] <= other_option['damage']
			slower = option['slowness'] >= other_option['slowness']
			costlier_m = option['missiles'] >= other_option['missiles']
			costlier_d = option['drone_parts'] >= other_option['drone_parts']
			if weaker and slower and costlier_m and costlier_d:
				if DEBUG:
					print('-' * depth, 'discarding weak option', option)
					print('-' * depth, f'because {other_option} is better')
				options_list.remove(option)

	return options_list


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
	# Note: This does not consider boarders, hazards etc.
	# TODO: instead of calculating based on averages (with average values drawn out of my arse),
	#  use several real s1 enemy ships and take the median of the results
	avg_enemy_slowness = 13.0
	avg_enemy_damage_lasers = 2.0
	avg_enemy_damage_missiles = 0.8
	avg_enemy_damage_ion = 0.5
	avg_enemy_damage_beams = 0.8
	avg_enemy_damage_bombs = 0.5
	avg_enemy_damage_drones = 0.2

	volley_damage = (
		avg_enemy_damage_lasers * (1 - get_laser_resistance(loadout)) +
		avg_enemy_damage_missiles * (1 - get_missile_resistance(loadout)) +
		avg_enemy_damage_ion * (1 - get_ion_resistance(loadout)) +
		avg_enemy_damage_beams * (1 - get_beam_resistance(loadout)) +
		avg_enemy_damage_bombs * (1 - get_bomb_resistance(loadout)) +
		avg_enemy_damage_drones * (1 - get_drone_resistance(loadout))
	)
	pain_time = avg_enemy_slowness / volley_damage
	time = pain_time * 5
	extra_time = 0
	cloak_rate = 0
	cloaked_evasion = 0

	if SYSTEMS.cloaking in loadout['starting_systems']:
		cloak_time = loadout['system_levels'][SYSTEMS.cloaking] * 5
		cloak_rate = cloak_time / (cloak_time + config.system_points[SYSTEMS.cloaking]['cooldown'])
		cloaked_evasion = min(1, get_evasion(loadout) + 0.6)
		# Let's say you cloak the first volley and after that the biggest benefit is slowing enemy weapon recharge
		extra_time += avg_enemy_slowness * cloaked_evasion + time * cloak_rate

	zshield_damage = (
		avg_enemy_damage_lasers * (1 - get_laser_resistance(loadout, True)) +
		avg_enemy_damage_missiles * (1 - get_missile_resistance(loadout, True)) +
		avg_enemy_damage_ion * 2 * (1 - get_ion_resistance(loadout, True)) +
		avg_enemy_damage_beams +
		avg_enemy_damage_bombs * (1 - get_bomb_resistance(loadout)) +
		avg_enemy_damage_drones * (1 - get_drone_resistance(loadout, True))
	)
	zshield_layer_time = avg_enemy_slowness / zshield_damage * (1 - cloak_rate)
	# Let's assume you can cloak on average 15% of incoming supershield damage which you wouldn't have evaded otherwise
	#  (can't cloak beams, drones, desynced weapons)
	zshield_layer_time *= 1 - (0.15 * cloaked_evasion)
	assert(zshield_layer_time > 0)

	if AUGMENTS.ENERGY_SHIELD in loadout['augments']:
		extra_time += 5 * zshield_layer_time

	if 'DRONE_SHIELD_PLAYER' in loadout['drones']:
		drone_stats = config.drone_points['DRONE_SHIELD_PLAYER']
		# Time to recharge the first layer
		layer_charge_time = drone_stats['layer_times'][0]
		# It starts recharging already before the first layer is gone. Use the slowest rate for simplicity
		layer_charge_time *= (1 - zshield_layer_time / drone_stats['layer_times'][-1])
		# If the average enemy can't deal with the shields faster than they appear, your ship is OP
		if layer_charge_time <= 0:
			return math.inf
		# Ratio of time spent shielded vs. nakedly recharging
		r = zshield_layer_time / (layer_charge_time + zshield_layer_time)
		# Sum of a geometric series for -1 < r < 1
		time = time / (1 - r)

	return time + extra_time


def get_laser_resistance(loadout, for_zshield=False):
	evasion = get_evasion(loadout)
	shield_bonus = 0
	drone_bonus = 0
	if SYSTEMS.shields in loadout['starting_systems'] and for_zshield:
		shield_layers = loadout['system_levels'][SYSTEMS.shields] // 2
		if shield_layers == 1:
			shield_bonus = 0.25
		elif shield_layers == 2:
			shield_bonus = 0.6
		elif shield_layers > 2:
			shield_bonus = 0.9
	for drone in loadout['drones']:
		stats = config.drone_points[drone]
		drone_bonus += stats.get('laser_defence', 0) * (0.5 if for_zshield else 1)
	return max(0, min(1, evasion + shield_bonus + drone_bonus))

def get_missile_resistance(loadout, for_zshield=False):
	evasion = get_evasion(loadout)
	drone_bonus = 0
	for drone in loadout['drones']:
		stats = config.drone_points[drone]
		defence = stats.get('defence', 0)
		if defence > 0:
			drone_bonus += 1 - 1 / defence * (0.5 if for_zshield else 1)
	return max(0, min(1, 1 - (1 - evasion) * (1 - drone_bonus)))

def get_ion_resistance(loadout, for_zshield=False):
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

def get_drone_resistance(loadout, for_zshield=False):
	shield_bonus = 0
	drone_bonus = 0
	if SYSTEMS.shields in loadout['starting_systems'] and not for_zshield:
		shield_layers = loadout['system_levels'][SYSTEMS.shields] // 2
		if shield_layers == 1:
			shield_bonus = 0.2
		elif shield_layers == 2:
			shield_bonus = 0.4
		elif shield_layers > 2:
			shield_bonus = 0.7
	for drone in loadout['drones']:
		if drone == 'ANTI_DRONE':
			drone_bonus = 1 - (1 - drone_bonus) * 0.15
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
		# if w['type'] == 'weapon' and w['name'][:5] == 'LASER':
		if w['type'] == 'weapon':
			useless.append(w['name'])
	return useless


def get_weapon_options(loadout):
	options = {}
	for category in config.weapon_categories.values():
		weight = category['weights'].get(loadout['layout']) or category['weights']['default']
		for weapon in category['included']:
			options[weapon] = weight / config.weapon_points[weapon]['power'] / config.weapon_points[weapon].get('rarity', 1)
	return options

def get_drone_options(loadout):
	options = {}
	for category in config.drone_categories.values():
		weight = category['weights'].get(loadout['layout']) or category['weights']['default']
		for drone in category['included']:
			existing_count = loadout['drones'].count(drone)
			# Slightly decreased chance for duplicates
			options[drone] = weight / (existing_count + 1) / config.drone_points[drone].get('rarity', 1)
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
		raise IndexError()
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