from enum import Enum


class LAYOUTS(Enum):
	anaerobic_cruiser = "anaerobic_cruiser"
	circle_cruiser = "circle_cruiser"
	crystal_cruiser = "crystal_cruiser"
	energy_cruiser = "energy_cruiser"
	fed_cruiser = "fed_cruiser"
	jelly_cruiser = "jelly_cruiser"
	kestral = "kestral"
	mantis_cruiser = "mantis_cruiser"
	rock_cruiser = "rock_cruiser"
	stealth = "stealth"


class RACES(Enum):
	human = "human"
	engi = "engi"
	mantis = "mantis"
	rock = "rock"
	energy = "energy"
	slug = "slug"
	anaerobic = "anaerobic"
	crystal = "crystal"


class SYSTEMS(Enum):
	oxygen = "oxygen"
	teleporter = "teleporter"
	cloaking = "cloaking"
	pilot = "pilot"
	medbay = "medbay"
	shields = "shields"
	artillery = "artillery"
	engines = "engines"
	weapons = "weapons"
	drones = "drones"
	sensors = "sensors"
	doors = "doors"
	clonebay = "clonebay"
	hacking = "hacking"
	battery = "battery"
	mind = "mind"

class SUBSYSTEMS(Enum):
	pilot = SYSTEMS.pilot
	doors = SYSTEMS.doors
	sensors = SYSTEMS.sensors
	battery = SYSTEMS.battery


# Most are not eligible to be chosen
class AUGMENTS(Enum):
	TELEPORT_HEAL = 'TELEPORT_HEAL'
	O2_MASKS = 'O2_MASKS'
	NANO_MEDBAY = 'NANO_MEDBAY'
	FIRE_EXTINGUISHERS = 'FIRE_EXTINGUISHERS'
	ROCK_ARMOR = 'ROCK_ARMOR'
	CRYSTAL_SHARDS = 'CRYSTAL_SHARDS'
	ENERGY_SHIELD = 'ENERGY_SHIELD'
	SLUG_GEL = 'SLUG_GEL'
	CREW_STIMS = 'CREW_STIMS'
	DRONE_SPEED = 'DRONE_SPEED'
	SYSTEM_CASING = 'SYSTEM_CASING'
	ADV_SCANNERS = 'ADV_SCANNERS'
	LIFE_SCANNER = 'LIFE_SCANNER'
	BACKUP_DNA = 'BACKUP_DNA'
	EXPLOSIVE_REPLICATOR = 'EXPLOSIVE_REPLICATOR'
	# FLEET_DISTRACTION = 'FLEET_DISTRACTION'
	BATTERY_BOOSTER = 'BATTERY_BOOSTER'
	DEFENSE_SCRAMBLER = 'DEFENSE_SCRAMBLER'
	HACKING_STUN = 'HACKING_STUN'
	ZOLTAN_BYPASS = 'ZOLTAN_BYPASS'
	ION_ARMOR = 'ION_ARMOR'
	# CLOAK_FIRE = 'CLOAK_FIRE'
	# REPAIR_ARM = 'REPAIR_ARM'
	# SCRAP_COLLECTOR = 'SCRAP_COLLECTOR'
	AUTO_COOLDOWN = 'AUTO_COOLDOWN'
	# SHIELD_RECHARGE = 'SHIELD_RECHARGE'
	# WEAPON_PREIGNITE = 'WEAPON_PREIGNITE'
	# FTL_BOOSTER = 'FTL_BOOSTER'
	FTL_JUMPER = 'FTL_JUMPER'
	DRONE_RECOVERY = 'DRONE_RECOVERY'
	FTL_JAMMER = 'FTL_JAMMER'



crew_weights = {
	"default": {
		RACES.human: 2,
		RACES.engi: 2,
		RACES.mantis: 2,
		RACES.rock: 2,
		RACES.energy: 2,
		RACES.slug: 2,
		RACES.anaerobic: 1,
		RACES.crystal: 1
	},
	LAYOUTS.anaerobic_cruiser:	{ RACES.anaerobic: 16, RACES.crystal: 2 },
	LAYOUTS.circle_cruiser:		{ RACES.engi: 12 },
	LAYOUTS.crystal_cruiser:	{ RACES.crystal: 16, RACES.anaerobic: 2 },
	LAYOUTS.energy_cruiser:		{ RACES.energy: 12 },
	LAYOUTS.fed_cruiser:		{},
	LAYOUTS.jelly_cruiser:		{ RACES.slug: 12 },
	LAYOUTS.kestral:			{ RACES.human: 4 },
	LAYOUTS.mantis_cruiser:		{ RACES.mantis: 16, RACES.engi: 6 },
	LAYOUTS.rock_cruiser:		{ RACES.rock: 16, RACES.crystal: 2 },
	LAYOUTS.stealth:			{ RACES.engi: 4 }
}

race_bonus = {
	RACES.human: {"tp":1.0, "airlock_need":1.0, "scrap":45},
	RACES.engi: {"tp":0.6, "airlock_need":0.7, "repair":2.0, "scrap":50},
	RACES.mantis: {"tp":1.6, "speed":1.2, "airlock_need":1.5, "repair":0.5, "scrap":55},
	RACES.rock: {"tp":1.4, "tp_synergies":{"fire":1.0}, "speed":0.5, "airlock_need":0.4, "health":150, "scrap":55},
	RACES.energy: {"tp":0.7, "tp_synergies":{"clonebay":0.3}, "airlock_need":1.5, "health":70, "scrap":60},
	RACES.slug: {"tp":1.0, "airlock_need":1.0, "scrap":45},
	RACES.anaerobic: {"tp":1.5, "tp_synergies":{"breach":1.0, "stun":0.5}, "speed":0.8, "airlock_need":0.1, "scrap":50},
	RACES.crystal: {"tp":2.0, "tp_synergies":{"breach":0.4}, "speed":0.8, "airlock_need":0.8, "health":125, "scrap":60}
}

system_points = {
	SYSTEMS.oxygen: {"support":10, "scrap":[30,25,50]},
	SYSTEMS.teleporter: {"scrap":[90,30,60]},
	SYSTEMS.cloaking: {"defence":15, "scrap":[150,30,50], "cooldown": 20},
	SYSTEMS.pilot: {"scrap":[0,20,50]},
	SYSTEMS.medbay: {"support":10, "scrap":[50,35,45], "healing_rate": [1.0, 1.5, 3.0]},
	# Notice: If shields is not a starting system, it should start at level 2. Hence level 1 cost is really only 25? (Drone Control too)
	SYSTEMS.shields: {"defence":25, "scrap":[125,100,20,30,40,60,80,100], "initial_power": 2},
	SYSTEMS.artillery: {"scrap":[0,30,50,80]},
	SYSTEMS.engines: {"scrap":[0,10,15,30,40,60,80,120]},
	SYSTEMS.weapons: {"scrap":[50,40,25,35,50,75,90,100]},
	SYSTEMS.drones: {"defence":1, "scrap":[60,10,20,30,45,60,80,100], "initial_power": 2},
	SYSTEMS.sensors: {"support":5, "scrap":[40,25,40]},
	SYSTEMS.doors: {"support":10, "scrap":[60,35,50]},
	SYSTEMS.clonebay: {"support":10, "scrap":[50,35,45]},
	SYSTEMS.hacking: {"support":10, "defence":5, "crewkill":2, "scrap":[80,35,60], "shield_drop": [1, 3, 4]},
	SYSTEMS.battery: {"support":5, "scrap":[35,50]},
	SYSTEMS.mind: {"support":7, "crewkill":[1,2,3], "scrap":[75,30,60]}
}

system_weights = {
	"default": {
		# The mandatory systems are here for upgrade weights
		SYSTEMS.engines: 12,
		SYSTEMS.pilot: 2,
		SYSTEMS.oxygen: 8,
		SYSTEMS.teleporter: 3,
		SYSTEMS.cloaking: 2,
		SYSTEMS.medbay: 5,
		SYSTEMS.shields: 8,
		SYSTEMS.artillery: 0,
		SYSTEMS.weapons: 8,
		SYSTEMS.drones: 1,
		SYSTEMS.sensors: 3,
		SYSTEMS.doors: 4,
		SYSTEMS.clonebay: 4,
		SYSTEMS.hacking: 2,
		SYSTEMS.battery: 1,
		SYSTEMS.mind: 2,
	},
	LAYOUTS.anaerobic_cruiser:	{ SYSTEMS.oxygen: 1 },
	LAYOUTS.circle_cruiser:		{ SYSTEMS.drones: 8 },
	LAYOUTS.crystal_cruiser:	{ SYSTEMS.oxygen: 4, SYSTEMS.teleporter: 4 },
	LAYOUTS.energy_cruiser:		{ SYSTEMS.battery: 3, SYSTEMS.shields: 6 },
	LAYOUTS.fed_cruiser:		{}, # TODO: artillery
	LAYOUTS.jelly_cruiser:		{ SYSTEMS.sensors: 1, SYSTEMS.mind: 5, SYSTEMS.hacking: 4 },
	LAYOUTS.kestral:			{},
	LAYOUTS.mantis_cruiser:		{ SYSTEMS.teleporter: 8 },
	LAYOUTS.rock_cruiser:		{ SYSTEMS.teleporter: 4 },
	LAYOUTS.stealth:			{ SYSTEMS.cloaking: 8, SYSTEMS.shields: 2, SYSTEMS.engines: 12 }
}

augment_weights = {
	"default": {
		AUGMENTS.TELEPORT_HEAL: 0.1,
		AUGMENTS.O2_MASKS: 0.1,
		AUGMENTS.NANO_MEDBAY: 0.1,
		AUGMENTS.FIRE_EXTINGUISHERS: 0.1,
		AUGMENTS.ROCK_ARMOR: 0.1,
		AUGMENTS.CRYSTAL_SHARDS: 0,
		AUGMENTS.ENERGY_SHIELD: 0.05,
		AUGMENTS.SLUG_GEL: 0.05,
		AUGMENTS.CREW_STIMS: 0.1,
		AUGMENTS.DRONE_SPEED: 0.1,
		AUGMENTS.SYSTEM_CASING: 0.1,
		AUGMENTS.ADV_SCANNERS: 0.1,
		AUGMENTS.LIFE_SCANNER: 0.1,
		AUGMENTS.BACKUP_DNA: 0.1,
		AUGMENTS.EXPLOSIVE_REPLICATOR: 0.1,
		AUGMENTS.BATTERY_BOOSTER: 0.1,
		AUGMENTS.DEFENSE_SCRAMBLER: 0.1,
		AUGMENTS.HACKING_STUN: 0.1,
		AUGMENTS.ZOLTAN_BYPASS: 0.1,
		AUGMENTS.DRONE_RECOVERY: 0,
		AUGMENTS.ION_ARMOR: 0.1,
		AUGMENTS.FTL_JAMMER: 0,
		AUGMENTS.FTL_JUMPER: 0.1,
		AUGMENTS.AUTO_COOLDOWN: 0.1,
	},
	LAYOUTS.anaerobic_cruiser: {
		AUGMENTS.LIFE_SCANNER: 0.3,
		AUGMENTS.BACKUP_DNA: 0.3,
		AUGMENTS.HACKING_STUN: 0.3,
	},
	LAYOUTS.circle_cruiser: {
		AUGMENTS.NANO_MEDBAY: 1,
		AUGMENTS.DRONE_SPEED: 0.4,
		AUGMENTS.DRONE_RECOVERY: 0.4,
	},
	LAYOUTS.crystal_cruiser: {
		AUGMENTS.CRYSTAL_SHARDS: 1,
		AUGMENTS.BACKUP_DNA: 0.2,
		AUGMENTS.DEFENSE_SCRAMBLER: 0.8,
	},
	LAYOUTS.energy_cruiser: {
		AUGMENTS.ENERGY_SHIELD: 8,
		AUGMENTS.ION_ARMOR: 0.5,
		AUGMENTS.BATTERY_BOOSTER: 0.5,
	},
	LAYOUTS.fed_cruiser: {
		AUGMENTS.O2_MASKS: 0.3,
		AUGMENTS.BACKUP_DNA: 0.2,
	},
	LAYOUTS.jelly_cruiser: {
		AUGMENTS.SLUG_GEL: 1,
		AUGMENTS.LIFE_SCANNER: 0,
		AUGMENTS.DEFENSE_SCRAMBLER: 0.2,
		AUGMENTS.HACKING_STUN: 0.5,
		AUGMENTS.FTL_JAMMER: 0.1,
		AUGMENTS.ZOLTAN_BYPASS: 0.2,
	},
	LAYOUTS.kestral: {
		AUGMENTS.AUTO_COOLDOWN: 0.3,
	},
	LAYOUTS.mantis_cruiser: {
		AUGMENTS.CREW_STIMS: 0.4,
		AUGMENTS.FIRE_EXTINGUISHERS: 0.2,
		AUGMENTS.ZOLTAN_BYPASS: 0.5,
	},
	LAYOUTS.rock_cruiser: {
		AUGMENTS.ROCK_ARMOR: 1,
		AUGMENTS.EXPLOSIVE_REPLICATOR: 0.8,
		AUGMENTS.DEFENSE_SCRAMBLER: 0.8,
	},
	LAYOUTS.stealth: {
		AUGMENTS.ADV_SCANNERS: 8,
		AUGMENTS.SYSTEM_CASING: 0.8,
		AUGMENTS.ION_ARMOR: 0.3,
		AUGMENTS.ZOLTAN_BYPASS: 0.1,
	 }
}


drone_points = {
	"COMBAT_1": {"offence":1, "scrap":50, "shield_drop":1, "power":2, "slowness": 15},
	"COMBAT_2": {"offence":2, "scrap":75, "shield_drop":2, "power":4, "slowness": 13},
	"COMBAT_BEAM": {"offence":1, "scrap":50, "power":2, "slowness": 16},
	"COMBAT_BEAM_2": {"offence":2, "scrap":60, "power":3, "slowness": 14},
	"COMBAT_FIRE": {"offence":1, "crewkill":1, "fire":1, "scrap":50, "power":3, "slowness": 21},
	"DEFENSE_1": {"defence":12, "scrap":50, "power":2},
	"DEFENSE_2": {"defence":8, "scrap":70, "power":3, "laser_defence": 0.2},
	"REPAIR": {"support":5, "scrap":30, "power":1, "onboard": 1},
	"BATTLE": {"support":5, "scrap":35, "power":2, "onboard": 1},
	"BOARDER": {"crewkill":2, "scrap":70, "power":3, "breach": 1},
	"BOARDER_ION": {"offence":1, "scrap":65, "power":3, "breach": 1, "stun": 1},
	"ANTI_DRONE": {"defence":2, "scrap":35, "power":1},
	"DRONE_SHIELD_PLAYER": {"defence":6, "scrap":60, "power":2, "layer_times":[8,10,13,16,20]}
}

drone_categories = {
	"COMBAT": {
		"weights": {
			"default": 1,
			LAYOUTS.circle_cruiser: 3,
		},
		"included": [
			"COMBAT_1",
			"COMBAT_2",
			"COMBAT_BEAM",
			"COMBAT_BEAM_2",
		]
	},
	"CREW": {
		"weights": {
			"default": 1,
			LAYOUTS.circle_cruiser: 2,
		},
		"included": [
			"REPAIR",
			"BATTLE",
			"BOARDER",
			"BOARDER_ION",
		]
	},
	"DEFENSE": {
		"weights": {
			"default": 1,
			LAYOUTS.energy_cruiser: 3,
			LAYOUTS.circle_cruiser: 3,
		},
		"included": [
			"DEFENSE_1",
			"DEFENSE_2",
			"ANTI_DRONE",
			"DRONE_SHIELD_PLAYER",
		]
	},
	"FIRE": {
		"weights": {
			"default": 0.5,
			LAYOUTS.jelly_cruiser: 1,
			LAYOUTS.rock_cruiser: 1.5,
		},
		"included": [
			"COMBAT_FIRE",
		]
	}
}

weapon_points = {
	"MISSILES_1": {"offence":1, "sp":5, "missiles":1, "power":1, "scrap":20, "fire":0.1, "breach":0.1, "stun":0.1, "slowness":9},
	"MISSILES_2_PLAYER": {"offence":2, "sp":5, "missiles":1, "power":1, "scrap":38, "fire":0.1, "breach":0.1, "stun":0.1, "slowness":11},
	"MISSILES_3": {"offence":3, "sp":5, "missiles":1, "power":3, "scrap":45, "fire":0.3, "breach":0.2, "stun":0.1, "slowness":14},
	"MISSILES_BURST": {"offence":4, "shots": 2, "sp":5, "missiles":1, "power":3, "scrap":60, "fire":0.6, "breach":0.4, "stun":0.2, "slowness":20},
	"MISSILES_BREACH": {"offence":4, "sp":5, "missiles":1, "power":3, "scrap":65, "fire":0.3, "breach":0.8, "stun":0.1, "slowness":22},
	"MISSILES_HULL": {"offence":2, "hull_multi": 2, "sp":5, "missiles":1, "power":2, "scrap":65, "fire":0.1, "breach":0.3, "stun":0.1, "slowness":17},
	"MISSILE_CHARGEGUN": {"offence":1, "charges":3, "shots": 1, "sp":5, "missiles":1, "power":2, "scrap":65, "fire":0.1, "breach":0.09, "slowness":7},

	"LASER_BURST_1": {"offence":1, "shield_drop":1, "power":1, "scrap":20, "fire":0.1, "slowness":10},
	"LASER_BURST_2": {"offence":2, "shots": 2, "shield_drop":2, "power":1, "scrap":25, "fire":0.2, "slowness":10, "rarity": 2},
	"LASER_BURST_2_A": {"offence":2, "shots": 2, "shield_drop":2, "power":2, "scrap":50, "fire":0.2, "slowness":11},
	"LASER_BURST_3": {"offence":3, "shots": 3, "shield_drop":3, "power":2, "scrap":80, "fire":0.3, "slowness":12, "rarity": 3},
	"LASER_BURST_5": {"offence":5, "shots": 5, "shield_drop":5, "power":4, "scrap":95, "slowness":19},
	"LASER_HEAVY_1": {"offence":2, "shield_drop":1, "power":1, "scrap":55, "fire":0.3, "breach":0.21, "stun":0.2, "slowness":9},
	"LASER_HEAVY_2": {"offence":4, "shots": 2, "shield_drop":2, "power":3, "scrap":65, "fire":0.6, "breach":0.42, "stun":0.2, "slowness":13},
	"LASER_HEAVY_1_SP": {"offence":2, "sp":1, "shield_drop":1, "power":2, "scrap":55, "fire":0.3, "breach":0.21, "slowness":10, "rarity": 2},
	"LASER_HULL_1": {"offence":2, "shots": 2, "hull_multi":2, "shield_drop":2, "power":2, "scrap":55, "breach":0.4, "slowness":14},
	"LASER_HULL_2": {"offence":3, "shots": 3, "hull_multi":2, "shield_drop":3, "power":3, "scrap":75, "breach":0.9, "slowness":15},
	# Chain guns are weird...
	"LASER_CHAINGUN": {"offence":3, "shots": 2, "shield_drop":2, "power":2, "scrap":65, "fire":0.2, "slowness":16},
	"LASER_CHAINGUN_2": {"offence":10, "shots": 5, "crewkill":-5, "shield_drop":5, "power":4, "scrap":95, "fire":0.1, "slowness":37},
	"LASER_CHARGEGUN_PLAYER": {"offence":1, "charges": 2, "shots": 1, "shield_drop":1, "power":1, "scrap":30, "slowness":5.5, "rarity": 2},
	"LASER_CHARGEGUN_2": {"offence":1, "charges": 4, "shots": 1, "shield_drop":1, "power":3, "scrap":70, "fire":0.1, "slowness":5},

	"SHOTGUN_PLAYER": {"offence":3, "shots": 3, "shield_drop":3, "power":1, "scrap":60, "slowness":8, "rarity": 3},
	"SHOTGUN": {"offence":2, "shots": 3, "shield_drop":3, "power":2, "scrap":65, "slowness":10},
	"SHOTGUN_2": {"offence":5, "shots": 7, "crewkill":-1, "shield_drop":5, "power":3, "scrap":80, "slowness":21},

	"BEAM_1": {"beam_damage":1, "beam_length": 4, "power":1, "scrap":20, "fire":0.4, "slowness":12},
	"BEAM_LONG": {"beam_damage":1, "beam_length": 6, "crewkill":-0.6, "power":2, "scrap":55, "slowness":16},
	"BEAM_2": {"beam_damage":2, "beam_length": 4, "crewkill":-0.4, "power":3, "scrap":65, "slowness":17},
	"BEAM_3": {"beam_damage":3, "beam_length": 4, "crewkill":-0.4, "power":4, "scrap":95, "slowness":25},
	"BEAM_FIRE": {"beam_damage":0, "beam_length": 5, "power":2, "scrap":50, "fire":4, "slowness":20, "rarity": 2},
	"BEAM_BIO": {"beam_damage":0, "beam_length": 5, "crewkill":4, "power":2, "scrap":50, "slowness":16},
	"BEAM_HULL": {"beam_damage":1, "beam_length": 4, "hull_multi": 2, "crewkill":-1, "power":2, "scrap":70, "slowness":14},

	"ION_1": {"nonlethal":1, "shield_drop":1, "power":1, "scrap":30, "stun":0.1, "slowness":8},
	"ION_2": {"nonlethal":2, "shield_drop":1, "power":2, "scrap":45, "stun":0.2, "slowness":13},
	# stats for 4 blasts because it's so good at stacking. Once the algorithm is improved for ion weapons, use the stats of one blast
	"ION_4": {"nonlethal":3, "shots": 4, "shield_drop":2, "power":3, "scrap":70, "stun":0.3, "slowness":16},
	"ION_STUN": {"nonlethal":1, "shield_drop":1, "power":1, "scrap":35, "stun":1.7, "slowness":10},
	"ION_CHARGEGUN": {"nonlethal":1, "charges": 3, "shots": 1, "shield_drop":0.7, "power":2, "scrap":50, "slowness":6},
	"ION_CHAINGUN": {"nonlethal":1, "shield_drop":1, "power":3, "scrap":55, "slowness":14, "rarity": 3},

	"BOMB_1": {"nonlethal":2, "crewkill":2, "sp":5, "missiles":1, "power":1, "scrap":45, "fire":0.1, "slowness":13},
	"BOMB_BREACH_1": {"nonlethal":1, "crewkill":1, "crewkill":0.2, "sp":5, "missiles":1, "power":1, "scrap":50, "breach":1, "slowness":9},
	"BOMB_BREACH_2": {"nonlethal":3, "crewkill":3, "sp":5, "missiles":1, "power":2, "scrap":60, "breach":1, "slowness":17},
	"BOMB_FIRE": {"crewkill":0.5, "sp":5, "missiles":1, "power":2, "scrap":50, "fire":1, "slowness":15},
	"BOMB_ION": {"nonlethal":4, "sp":5, "missiles":1, "power":1, "scrap":55, "stun":0.2, "slowness":22},
	"BOMB_LOCK": {"support":1, "sp":5, "missiles":1, "power":1, "scrap":45, "slowness":15, "rarity": 4},
	"BOMB_STUN": {"nonlethal":1, "sp":5, "missiles":1, "power":1, "scrap":45, "stun":5, "slowness":17},

	"BOMB_HEAL": {"support":4, "sp":5, "missiles":1, "power":1, "scrap":40, "slowness":18},
	"BOMB_HEAL_SYSTEM": {"support":3, "sp":5, "missiles":1, "power":1, "scrap":40, "slowness":14},

	"CRYSTAL_BURST_1": {"offence":2, "shield_drop":2, "sp":1, "power":2, "scrap":20, "breach":0.2, "stun":0.2, "slowness":15},
	"CRYSTAL_BURST_2": {"offence":3, "shield_drop":3, "sp":1, "power":3, "scrap":20, "breach":0.3, "stun":0.3, "slowness":17},
	"CRYSTAL_HEAVY_1": {"offence":2, "shield_drop":1, "sp":1, "power":1, "scrap":20, "breach":0.1, "stun":0.2, "slowness":13},
	"CRYSTAL_HEAVY_2": {"offence":4, "shield_drop":1, "sp":1, "power":3, "scrap":20, "breach":1, "stun":0.2, "slowness":19}
}

# The weights here are per weapon, not per category. So a category with more weapons is more likely to be chosen.
weapon_categories = {
	"MISSILE": {
		"weights": {
			"default": 1,
			LAYOUTS.rock_cruiser: 3,
			LAYOUTS.energy_cruiser: 2,
			LAYOUTS.crystal_cruiser: 2,
		},
		"included": [
			"MISSILES_1",
			"MISSILES_2_PLAYER",
			"MISSILES_3",
			"MISSILES_BURST",
			"MISSILES_BREACH",
			"MISSILES_HULL",
			"MISSILE_CHARGEGUN",
		]
	},
	"LASER": {
		"weights": { "default": 4 },
		"included": [
			"LASER_BURST_1", 
			"LASER_BURST_2", 
			"LASER_BURST_2_A", 
			"LASER_BURST_3", 
			"LASER_BURST_5", 
			"LASER_HEAVY_1", 
			"LASER_HEAVY_2", 
			"LASER_HEAVY_1_SP", 
			"LASER_HULL_1", 
			"LASER_HULL_2", 
			"LASER_CHAINGUN", 
			"LASER_CHAINGUN_2", 
			"LASER_CHARGEGUN_PLAYER", 
			"LASER_CHARGEGUN_2", 
		]
	},
	"SHOTGUN": {
		"weights": {
			"default": 1,
			LAYOUTS.anaerobic_cruiser: 2,
		},
		"included": [
			"SHOTGUN_PLAYER",
			"SHOTGUN",
			"SHOTGUN_2",
		]
	},
	"BEAM": {
		"weights": {
			"default": 1.5,
			LAYOUTS.jelly_cruiser: 2,
			LAYOUTS.stealth: 3,
			LAYOUTS.energy_cruiser: 3,
		},
		"included": [
			"BEAM_1",
			"BEAM_LONG",
			"BEAM_2",
			"BEAM_3",
			"BEAM_HULL",
		]
	},
	"BEAM_BIO": {
		"weights": {
			"default": 0.2,
			LAYOUTS.jelly_cruiser: 2,
		},
		"included": ["BEAM_BIO"]
	},
	"ION": {
		"weights": {
			"default": 1.5,
			LAYOUTS.circle_cruiser: 3,
			LAYOUTS.energy_cruiser: 3,
		},
		"included": [
			"ION_1",
			"ION_2",
			"ION_4",
			"ION_STUN",
			"ION_CHARGEGUN",
			"ION_CHAINGUN",
		]
	},
	"BOMB": {
		"weights": {
			"default": 1,
			LAYOUTS.jelly_cruiser: 2,
			LAYOUTS.mantis_cruiser: 2,
		},
		"included": [
			"BOMB_1",
			"BOMB_BREACH_1",
			"BOMB_BREACH_2",
			"BOMB_ION",
			"BOMB_LOCK",
			"BOMB_STUN",
		]
	},
	"FIRE": {
		"weights": {
			"default": 0.5,
			LAYOUTS.jelly_cruiser: 1,
			LAYOUTS.rock_cruiser: 2,
		},
		"included": [
			"BEAM_FIRE",
			"BOMB_FIRE",
		]
	},
	"CRYSTAL": {
		"weights": {
			"default": 0.1,
			LAYOUTS.rock_cruiser: 0.2,
			LAYOUTS.crystal_cruiser: 5,
		},
		"included": [
			"CRYSTAL_BURST_1",
			"CRYSTAL_BURST_2",
			"CRYSTAL_HEAVY_1",
			"CRYSTAL_HEAVY_2",
		]
	}
}

