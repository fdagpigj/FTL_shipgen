#room image details

#  #56#
#  1  3
#  2  4
#  #78#

room_images = {
	"artillery": [
		#filename, w,h, blocked, station pos/rot (if relevant), console glow pos
		("", 2,1, [5]),
		("alt1", 2,1, [1])
	],
	"battery": [
		("alt1", 2,1, [5]),
		("2", 2,1, [1]),
		("", 2,1, [5,6,3]),
		("3", 2,1, [5,6]),
		("7", 2,1, [1,3]),
		("9", 2,1, [1,7,8]),
		("12", 2,1, [6,3]),
		("13", 2,1, [6,8]),
		("14", 2,1, [7,8]),
		("4", 2,2, [5,3,4,7]),
		("5", 1,2, [5,3,4]),
		("6", 1,2, [1,2]),
		("8", 1,2, [2,3]),
		("10", 1,2, [3,4]),
		("11", 1,2, [2,7]),
		("15", 1,2, [4]),
		("17", 1,2, [1,3])
	],
	"cloaking": [
		("alt1", 2,1, [5]),
		("alt2", 2,1, [1]),
		("", 2,2, [6,3]),
		("2", 2,2, [4,8]),
		("3", 2,1, [5,6]),
		("4", 1,2, [5,3]),
		("5", 2,1, [3,8]),
		("6", 2,1, [6,3]),
		("7", 2,1, [1,7]),
		("8", 1,2, [2,7]),
		("9", 1,2, [1,4]),
		("10", 2,2, [1,5]),
		("11", 2,2, [2,7]),
	],
	"doors": [
		("alt1", 2,1, [5], 0,"up"),
		("alt2", 2,1, [1], 0,"left"),
		("", 2,1, [5,6], 1,"up"),
		("2", 2,1, [7,8], 0,"down"),
		("3", 2,1, [7,8,3], 1,"right"),
		("4", 1,2, [3,4], 0,"right"),
		("5", 1,2, [5,3], 0,"right"),
		("6", 1,2, [2,4], 1,"right"),
		("7", 2,1, [6,8], 1,"up"),
		("8", 1,2, [1,2], 0,"left"),
		("9", 2,1, [6,8,3], 1,"right"),
	],
	"drones": [
		("alt1", 2,1, [1]),
		("alt2", 2,1, [5]),
		("", 2,2, [6,3,7]),
		("2", 1,2, [5,7,2,3]),
		("3", 2,1, [8,3]),
		("4", 2,2, [1,8,4]),
		("5", 2,2, [7,8,4]),
		("6", 2,2, [1,7,5]),
		("7", 2,2, [1,5,6]),
		("8", 2,2, [5,6,7,8,3,4]),
		("9", 2,2, [1,2,7]),
		("10", 2,2, [6,3,4]),
		("11", 2,2, [1,2,5,6,7,8]),
		("12", 2,2, [2,3,7]),
		("13", 2,2, [1,2,6,8]),
		("14", 1,2, [1,2]),
		("15", 2,1, [5,6,7,8])
	],
	"engines": [
		("3", 2,1, [1,3], 1,"right", 53,7),
		("8", 1,2, [1,2], 1,"left", 0,44),
		("alt1", 2,1, [3,7], 1,"right", 53,7),
		("alt2", 2,1, [3,8], 1,"right", 53,2),
		("alt3", 2,1, [6,7], 1,"up", 42,1),
		("alt4", 2,1, [6,8], 1,"up", 42,1),
		("alt5", 2,2, [6,7], 1,"up", 42,1),
		("alt6", 2,2, [6,2], 1,"up", 42,1),
		("", 2,2, [5,7,3,4], 2,"down", 5,53),
		("2", 2,2, [5,7,1,2], 2,"down", 5,53),
		("4", 2,2, [7,6,3], 2,"down", 5,53),
		("5", 1,2, [1,2,5], 0,"up", 5,1),
		("6", 2,2, [8,3,4], 3,"down", 43,53),
		("7", 2,2, [3,4], 3,"right", 54,44),
		("9", 2,2, [6,8,4], 1,"up", 43,1)
	],
	"hacking": [
		("4", 2,1, [5]),
		("3", 2,1, [1]),
		("", 2,1, [7,8,3]),
		("2", 2,1, [7,8]),
		("5", 1,2, [5,3]),
		("6", 2,2, [5]),
		("7", 1,2, [1,2]),
		("8", 2,2, [7,8]),
		("9", 2,1, [5,6,3])
	],
	"medbay": [
		("alt1", 2,1, [5], -2),
		("5", 2,1, [3], -2),
		("", 2,2, [6,3], 1),
		("2", 2,1, [6,3], -2),
		("3", 2,2, [3,4], -2),
		("4", 2,2, [1,5], 0),
		("6", 1,2, [3,4], -2),
		("7", 2,2, [2,7], 2),
		("8", 2,2, [7,8,6], 1),
		("9", 2,1, [5,6], -2)
	],
	"mind": [
		("9", 2,1, []),
		("alt1", 2,2, []),
		("", 2,2, [7,8,4]),
		("1", 2,1, [7,3]),
		("2", 1,2, [2]),
		("3", 2,1, [7,8]),
		("4", 2,2, [1,2]),
		("5", 2,1, [5,6]),
		("6", 1,2, [5,7]),
		("7", 2,1, [6,8]),
		("8", 2,1, [1,5,8,3]),
		("10", 2,2, [2,7,5,3]),
		("11", 1,2, [1,2]),
		("12", 1,2, [1,3])
	],
	"oxygen": [
		("alt1", 2,1, [1]),
		("alt2", 2,1, [5]),
		("", 2,1, [1,7,5,6]),
		("2", 2,1, [5,6]),
		("3", 2,2, [2,7,8]),
		("4", 1,2, [1,5,7,4]),
		("5", 2,1, [1,5,7,8]),
		("6", 1,2, [3,4]),
		("7", 1,2, [1,2,7]),
		("8", 1,2, [1,3,7]),
		("9", 2,1, [1,6,8]),
		("11", 2,2, [6,3,4]),
		("12", 1,2, [1,4]),
		("13", 1,2, [1,2])
	],
	"pilot": [
		("alt1", 2,1, [5], 0,"up", 8,0),
		("3", 2,1, [3], 1,"right", 54,8),
		("", 1,2, [5,7,3,4], 0,"right", 19,9),
		("2", 2,1, [6,3,8], 1,"right", 54,8),
		("4", 1,2, [3,4], 0,"right", 19,9)
	],
	"sensors": [
		("alt5", 2,1, [1,3], 1,"right"),
		("alt6", 2,1, [5], 0,"up"),
		("alt7", 2,1, [1], 0,"left"),
		("", 2,1, [7,8], 1,"down"),
		("2", 2,1, [5,6], 0,"up"),
		("3", 2,1, [3,6,8], 1,"right"),
		("4", 1,2, [1,2], 1,"left"),
		("6", 1,2, [3,4], 1,"right")
	],
	"shields": [
		("alt1", 2,2, [1,5], 0,"left", 1,8),
		("alt2", 2,2, [7,6], 1,"up", 36,1),
		("alt3", 2,2, [8,6], 1,"up", 36,1),
		("alt4", 2,2, [2,6], 1,"up", 36,1),
		("alt5", 2,2, [1,6], 1,"up", 36,1),
		("alt6", 2,2, [5,6], 1,"up", 36,1),
		("alt7", 2,1, [5,6], 1,"up", 36,1),
		("alt8", 2,1, [1,5], 0,"left", 1,8),
		("alt9", 1,2, [5,7], 0,"up", 39,1),
		("alt10", 2,1, [1,6], 1,"up", 36,1),
		("alt11", 2,1, [7,6], 1,"up", 36,1),
		("alt12", 2,1, [8,6], 1,"up", 36,1),
		("", 2,2, [1,7,8,4], 0,"left", 1,8),
		("2", 2,2, [1,5,4], 0,"left", 1,8),
		("3", 2,2, [2,6,3], 2,"left", 1,41),
		("4", 2,2, [1,5,6], 0,"left", 1,8),
		("5", 2,2, [2,5,7], 0,"up", 10,1),
		("6", 2,2, [1,5,8], 0,"left", 1,8),
		("7", 2,2, [6,7,8], 1,"up", 36,1),
		("8", 2,2, [1,3,4], 0,"left", 1,12),
		("9", 2,2, [6,8,4], 1,"up", 38,1),
		("10", 2,2, [6,8,4], 3,"down", 35,53),
		("11", 2,1, [7,8,3], 1,"down", 35,18)
	],
	"weapons": [
		("8", 2,1, [5,6], 1,"up", 40,0),
		("11", 1,2, [3,4], 1,"right", 19,41),
		("alt1", 1,2, [5,7], 0,"up", 9,0),
		("alt2", 1,2, [5,1], 0,"up", 9,0),
		("alt3", 1,2, [5,2], 0,"up", 9,0),
		("alt4", 1,2, [3,1], 0,"right", 19,7),
		("alt5", 1,2, [3,2], 0,"right", 19,7),
		("alt6", 2,2, [5,4], 0,"up", 8,0),
		("alt6", 2,2, [2,3], 1,"right", 54,7),
		("", 2,2, [6,8], 1,"up", 40,0),
		("2", 2,2, [6,8,1], 1,"up", 40,0),
		("3", 2,2, [5,6], 1,"up", 40,0),
		("4", 2,2, [5,7,4], 0,"up", 8,0),
		("5", 2,2, [8,3], 1,"right", 54,7),
		("6", 2,2, [1,6,7], 1,"up", 40,0),
		("7", 2,2, [5,6,8], 1,"up", 40,0),
		("9", 2,2, [6,8], 1,"up", 40,0),
		("10", 2,2, [1,5,8], 0,"up", 8,0)
	]
}
