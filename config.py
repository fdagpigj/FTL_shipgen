LAYOUTS = ("anaerobic_cruiser", "circle_cruiser", "crystal_cruiser", "energy_cruiser",
	"fed_cruiser", "jelly_cruiser", "kestral", "mantis_cruiser", "rock_cruiser", "stealth")


crew_weights = {
	"default": {"human":1,"engi":1,"mantis":1,"rock":1,"energy":1,"slug":1,"anaerobic":1,"crystal":1},
	"anaerobic_cruiser": {"anaerobic":4},
	"circle_cruiser": {"engi":4},
	"crystal_cruiser": {"crystal":4},
	"energy_cruiser": {"energy":4},
	"fed_cruiser": {},
	"jelly_cruiser": {"slug":4},
	"kestral": {"human":2},
	"mantis_cruiser": {"mantis":4,"engi":2},
	"rock_cruiser": {"rock":4},
	"stealth": {"engi":2}
}

race_bonus = {
	"human":{"tp":1.0, "airlock_need":1.0, "scrap":45},
	"engi":{"tp":0.6, "airlock_need":0.7, "repair":2.0, "scrap":50},
	"mantis":{"tp":1.6, "speed":1.2, "airlock_need":1.5, "repair":0.5, "scrap":55},
	"rock":{"tp":1.3, "tp_synergies":{"fire":1.0}, "speed":0.5, "airlock_need":0.4, "health":150, "scrap":55},
	"energy":{"tp":0.7, "tp_synergies":{"clonebay":0.3}, "airlock_need":1.5, "health":70, "scrap":60},
	"slug":{"tp":1.0, "airlock_need":1.0, "scrap":45},
	"anaerobic":{"tp":1.5, "tp_synergies":{"breach":1.0, "stun":0.5}, "speed":0.8, "airlock_need":0.1, "scrap":50},
	"crystal":{"tp":2.0, "tp_synergies":{"breach":0.4}, "speed":0.8, "airlock_need":0.8, "health":125, "scrap":60}
}

system_points = {
	"oxygen": {"support":10, "scrap":[30,25,50]},
	"teleporter": {"scrap":[90,30,60]},
	"cloaking": {"defence":15, "scrap":[150,30,50]},
	"pilot": {"scrap":[0,20,50]},
	"medbay": {"support":10, "scrap":[50,35,45]},
	"shields": {"defence":20, "scrap":[125,100,20,30,40,60,80,100]},
	"artillery": {"scrap":[0,30,50,80]},
	"engines": {"scrap":[0,10,15,30,40,60,80,120]},
	"weapons": {"scrap":[50,40,25,35,50,75,90,100]},
	"drones": {"scrap":[60,10,20,30,45,60,80,100]},
	"sensors": {"support":5, "scrap":[40,25,40]},
	"doors": {"support":10, "scrap":[60,35,50]},
	"clonebay": {"support":10, "scrap":[50,35,45]},
	"hacking": {"support":10, "defence":5, "crewkill":2, "scrap":[80,35,60], "shield_drop":4},
	"battery": {"support":5, "scrap":[35,50]},
	"mind": {"support":7, "crewkill":3, "scrap":[75,30,60]}
}

drone_points = {
	"COMBAT_1": {"offence":1, "scrap":50, "shield_drop":1, "power":2},
	"COMBAT_2": {"offence":2, "scrap":75, "shield_drop":2, "power":4},
	"COMBAT_BEAM": {"offence":1, "scrap":50, "power":2},
	"COMBAT_BEAM_2": {"offence":2, "scrap":60, "power":3},
	"COMBAT_FIRE": {"offence":1, "crewkill":1, "fire":1, "scrap":50, "power":3},
	"DEFENSE_1": {"defence":12, "scrap":50, "power":2},
	"DEFENSE_2": {"defence":8, "scrap":70, "power":3},
	"REPAIR": {"support":5, "scrap":30, "power":1},
	"BATTLE": {"support":5, "scrap":35, "power":2},
	"BOARDER": {"crewkill":2, "scrap":70, "power":3},
	"BOARDER_ION": {"offence":1, "scrap":65, "power":3},
	"ANTI_DRONE": {"defence":2, "scrap":35, "power":1},
	"DRONE_SHIELD_PLAYER": {"defence":6, "scrap":60, "power":2}
}

weapon_points = {
	"MISSILES_1": {"offence":1, "sp":5, "missiles":1, "power":1, "scrap":20, "fire":0.1, "breach":0.1, "stun":0.1, "slowness":9},
	"MISSILES_2_PLAYER": {"offence":2, "sp":5, "missiles":1, "power":1, "scrap":38, "fire":0.1, "breach":0.1, "stun":0.1, "slowness":11},
	"MISSILES_3": {"offence":3, "sp":5, "missiles":1, "power":3, "scrap":45, "fire":0.3, "breach":0.2, "stun":0.1, "slowness":14},
	"MISSILES_BURST": {"offence":4, "sp":5, "missiles":1, "power":3, "scrap":60, "fire":0.6, "breach":0.4, "stun":0.2, "slowness":20},
	"MISSILES_BREACH": {"offence":4, "sp":5, "missiles":1, "power":3, "scrap":65, "fire":0.3, "breach":0.8, "stun":0.1, "slowness":22},
	"MISSILES_HULL": {"offence":3, "crewkill":-0.6, "sp":5, "missiles":1, "power":2, "scrap":65, "fire":0.1, "breach":0.3, "stun":0.1, "slowness":17},
	"MISSILE_CHARGEGUN": {"offence":2, "sp":5, "missiles":1, "power":2, "scrap":65, "fire":0.2, "breach":0.2, "slowness":14},

	"LASER_BURST_1": {"offence":1, "shield_drop":1, "power":1, "scrap":20, "fire":0.1, "slowness":10},
	"LASER_BURST_2": {"offence":2, "shield_drop":2, "power":1, "scrap":25, "fire":0.2, "slowness":10},
	"LASER_BURST_2_A": {"offence":2, "shield_drop":2, "power":2, "scrap":50, "fire":0.2, "slowness":11},
	"LASER_BURST_3": {"offence":3, "shield_drop":3, "power":2, "scrap":80, "fire":0.3, "slowness":12},
	"LASER_BURST_5": {"offence":3, "shield_drop":5, "power":4, "scrap":95, "slowness":19},
	"LASER_HEAVY_1": {"offence":2, "shield_drop":1, "power":1, "scrap":55, "fire":0.3, "breach":0.3, "stun":0.2, "slowness":9},
	"LASER_HEAVY_2": {"offence":4, "shield_drop":2, "power":3, "scrap":65, "fire":0.6, "breach":0.6, "stun":0.4, "slowness":13},
	"LASER_HEAVY_1_SP": {"offence":2, "sp":1, "shield_drop":1, "power":2, "scrap":55, "fire":0.3, "breach":0.3, "slowness":10},
	"LASER_HULL_1": {"offence":3, "crewkill":-0.2, "shield_drop":2, "power":2, "scrap":55, "breach":0.4, "slowness":14},
	"LASER_HULL_2": {"offence":5, "crewkill":-0.3, "shield_drop":3, "power":3, "scrap":75, "breach":0.9, "slowness":15},
	"LASER_CHAINGUN": {"offence":3, "shield_drop":2, "power":2, "scrap":65, "fire":0.2, "slowness":46},
	"LASER_CHAINGUN_2": {"offence":10, "crewkill":-5, "shield_drop":5, "power":4, "scrap":95, "fire":0.1, "slowness":37},
	"LASER_CHARGEGUN_PLAYER": {"offence":2, "shield_drop":2, "power":1, "scrap":30, "slowness":11},
	"LASER_CHARGEGUN_2": {"offence":2, "shield_drop":4, "power":3, "scrap":70, "fire":0.1, "slowness":10},

	"SHOTGUN_PLAYER": {"offence":3, "shield_drop":3, "power":1, "scrap":60, "slowness":8},
	"SHOTGUN": {"offence":2, "shield_drop":3, "power":2, "scrap":65, "slowness":10},
	"SHOTGUN_2": {"offence":4, "crewkill":-1, "shield_drop":5, "power":3, "scrap":80, "slowness":21},

	"BEAM_1": {"offence":4, "power":1, "scrap":20, "fire":0.4, "slowness":12},
	"BEAM_LONG": {"offence":5, "crewkill":-0.6, "power":2, "scrap":55, "slowness":16},
	"BEAM_2": {"offence":8, "crewkill":-0.4, "sp":1, "power":3, "scrap":65, "slowness":17},
	"BEAM_3": {"offence":12, "crewkill":-0.4, "sp":2, "power":4, "scrap":95, "slowness":25},
	"BEAM_FIRE": {"offence":1, "power":2, "scrap":50, "fire":4, "slowness":20},
	"BEAM_BIO": {"crewkill":4, "power":2, "scrap":50, "slowness":16},
	"BEAM_HULL": {"offence":6, "crewkill":-1, "power":2, "scrap":70, "slowness":14},

	"ION_1": {"nonlethal":1, "shield_drop":1, "power":1, "scrap":30, "stun":0.1, "slowness":8},
	"ION_2": {"nonlethal":2, "shield_drop":1, "power":2, "scrap":45, "stun":0.2, "slowness":13},
	"ION_4": {"nonlethal":1, "shield_drop":3, "power":3, "scrap":70, "stun":0.5, "slowness":20},
	"ION_STUN": {"nonlethal":1, "shield_drop":1, "power":1, "scrap":35, "stun":1.7, "slowness":10},
	"ION_CHARGEGUN": {"nonlethal":1, "shield_drop":2, "power":2, "scrap":50, "slowness":18},
	"ION_CHAINGUN": {"nonlethal":3, "shield_drop":2, "power":3, "scrap":55, "slowness":42},

	"BOMB_1": {"nonlethal":2, "sp":5, "missiles":1, "power":1, "scrap":45, "fire":0.1, "slowness":13},
	"BOMB_BREACH_1": {"nonlethal":1, "crewkill":0.2, "sp":5, "missiles":1, "power":1, "scrap":50, "breach":1, "slowness":9},
	"BOMB_BREACH_2": {"nonlethal":3, "sp":5, "missiles":1, "power":2, "scrap":60, "breach":1, "slowness":17},
	"BOMB_FIRE": {"crewkill":0.5, "sp":5, "missiles":1, "power":2, "scrap":50, "fire":1, "slowness":15},
	"BOMB_ION": {"nonlethal":4, "sp":5, "missiles":1, "power":1, "scrap":55, "stun":0.2, "slowness":22},
	"BOMB_LOCK": {"support":1, "sp":5, "missiles":1, "power":1, "scrap":45, "slowness":15},
	"BOMB_STUN": {"nonlethal":1, "sp":5, "missiles":1, "power":1, "scrap":45, "stun":5, "slowness":17},

	"BOMB_HEAL": {"support":4, "sp":5, "missiles":1, "power":1, "scrap":40, "slowness":18},
	"BOMB_HEAL_SYSTEM": {"support":3, "sp":5, "missiles":1, "power":1, "scrap":40, "slowness":14},

	"CRYSTAL_BURST_1": {"offence":2, "shield_drop":2, "sp":1, "power":2, "scrap":20, "breach":0.2, "stun":0.2, "slowness":15},
	"CRYSTAL_BURST_2": {"offence":3, "shield_drop":3, "sp":1, "power":3, "scrap":20, "breach":0.3, "stun":0.3, "slowness":17},
	"CRYSTAL_HEAVY_1": {"offence":2, "shield_drop":1, "sp":1, "power":1, "scrap":20, "breach":0.1, "stun":0.2, "slowness":13},
	"CRYSTAL_HEAVY_2": {"offence":4, "shield_drop":1, "sp":1, "power":3, "scrap":20, "breach":1, "stun":0.2, "slowness":19}
}

