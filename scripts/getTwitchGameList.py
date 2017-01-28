import json
import time
import urllib.request
import csv

output="games.csv"
url="https://api.twitch.tv/kraken/games/top?limit=100" # twitch api limits to 100 per call

with open(output, 'w') as fp:
	a = csv.writer(fp)
	
	# prepare header
	a.writerow(['Title', 'Popularity', 'Type', 'Mid', 'New Title'])
	count=0
	while True:
		response = urllib.request.urlopen(url).read().decode()
		data=json.loads(response) # load json
		url=data["_links"]["next"] # next offset url
		
		games=data["top"]
		if len(games)==0:
			break
			
		count+=len(games)
		print ("Writing %d rows into file. (Total=%d)" % (len(games), count))
		for game in games:
			details = game["game"]
			title = details["name"]
			popularity = details["popularity"]
			a.writerow([title, popularity])