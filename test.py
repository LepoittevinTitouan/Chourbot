import json
from collections import Counter

competmaps = ["mirage","inferno","overpass","vertigo","nuke","train","dust2","cache"]
results = ["win","loose","tie"]


#for m in data['maps']:
with open('csgo.json') as f:
  cstats = json.load(f)

class Players:
	def __init__(self, name, wins, losses, ties, mvps):
		self.name = name
		self.wins = wins
		self.losses = losses
		self.ties = ties
		self.mvps = mvps

class Maps:
	def __init__(self, name, wins, losses, ties, mvps):
		self.name = name
		self.wins = wins
		self.losses = losses
		self.ties = ties
		self.mvps = mvps

for m in competmaps:
	if m in cstats["maps"].keys() :
		wins = cstats['maps'][m]['wins']
		ties = cstats['maps'][m]['ties']
		losses = cstats['maps'][m]['losses']
		mvps = cstats['maps'][m]['mvps']
		number_of_game = len(wins+ties+losses)

		#get the winrate
		winrate = int(round((len(wins)/(number_of_game))*100))

		#get the player(s) with the most mvps
		unique_mvps = list(set(mvps))
		mvp_rate = [0]*len(unique_mvps)
		for mvp in mvps:
			i=0
			for um in unique_mvps:
				if mvp == um:
					mvp_rate[i]+=1
				i+=1

		max_mvps = max(mvp_rate)
		mmvp = ''
		for i in range(len(unique_mvps)):
			if mvp_rate[i] == max_mvps:
				if len(mmvp) > 0:
					mmvp += ', '
				mmvp += unique_mvps[i]

		#display
		print(m)
		print("  " + str(winrate) + "% de winrate",sep = '')
		print('  MVP: ' + mmvp + ' (' + str(int(round((max_mvps/number_of_game)*100))) + '%)')
