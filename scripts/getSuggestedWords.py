from pytrends.request import TrendReq
from threading import Thread
import json
import os, sys
import time
import numpy as np
import pandas as pd

input="games.csv"
output="games.csv"

df=pd.read_csv(input)

# Dynamic Programming implementation of Levenshtein distance (Edit Distance)
def levenshteinDistance(str1, str2):
    m = len(str1)
    n = len(str2)
    d = []           
    for i in range(m+1):
        d.append([i])        
    del d[0][0]    
    for j in range(n+1):
        d[0].append(j)       
    for j in range(1,n+1):
        for i in range(1,m+1):
            if str1[i-1] == str2[j-1]:
                d[i].insert(j,d[i-1][j-1])           
            else:
                minimum = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+2)         
                d[i].insert(j, minimum)
    return d[-1][-1]
	
# logging into Google with a legitimate account enables a higher rate limit
google_username = ""
google_password = ""

# connect to Google
pytrend = TrendReq(google_username, google_password, custom_useragent=None)

i=0
for game in df["Title"]:
	# skip the rows that are processed
	if pd.isnull(df["Type"][i]):
		keyword = game
		# strings with '/' will cause problems
		
		if "/" in keyword:
			keyword = game.replace("/", " ")
		print "Searching for",keyword+".."
		# start scraping
		while True:
			try:
				suggestions = pytrend.suggestions(keyword)
				suggestions = suggestions["default"]["topics"]
				jsonlist = []
				for suggestion in suggestions:
					# if suggestion type contains 'game', but not something like 'video game developer'
					if "game" in suggestion["type"].lower() and "develop" not in suggestion["type"].lower() and "company" not in suggestion["type"].lower():
						jsonlist.append(suggestion)
				
				# sort the list according to levenshtein distance with keyword
				jsonlist.sort(key=lambda x: levenshteinDistance(x["title"], keyword))
				if jsonlist:
					# get the best suggestion (least edit distance)
					suggestion = jsonlist[0]
					df.loc[i, "Type"]=suggestion["type"]
					df.loc[i, "Mid"]=suggestion["mid"]
					df.loc[i, "New Title"]=suggestion["title"]
					print "Found",suggestion["title"],suggestion["type"],suggestion["mid"]
					
					# do this in a thread to prevent KeyboardInterrupt from ruining everything
					a = Thread(target=df.to_csv(output, index=False, encoding="utf-8"))
					a.start()
					a.join()
				else:
					print "No suggestions found for",keyword+"."
				print
			except KeyboardInterrupt:
				# so that you can still stop the program!
				print 'Interrupted'
				try:
					sys.exit(0)
				except SystemExit:
					os._exit(0)
			except Exception, e:
				# retry when fail after 5 seconds
				print "Fail to find suggestions for",keyword,"retrying in 5 seconds."
				print "Error:",e
				time.sleep(5)
				continue
			break
	i+=1