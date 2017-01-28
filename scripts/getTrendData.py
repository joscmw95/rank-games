from pytrends.request import TrendReq
from threading import Thread
import json
import os, sys
import time
import numpy as np
import pandas as pd

# use the same input and output for resumeable work
input="games.csv"
output="games.csv"
# the item used as relative benchmark
ref_query="book"
col_avg_search_pop="Average Search Popularity"
col_normalized="Normalized"
google_username = ""
google_password = ""

# connect to Google
pytrend = TrendReq(google_username, google_password, None)

df=pd.read_csv(input)

for i in range(len(df)):
	if "2016-05-01" in df and df["2016-05-01"][i] != -1:
		continue
	gameTitle=df["Title"][i]
	if "/" in gameTitle:
		gameTitle = gameTitle.replace("/", " ")
	if pd.isnull(df["Mid"][i]):
		keyword = gameTitle
	else:
		keyword = df["Mid"][i]
	
	q = []
	qstring = ref_query+','
	qstring+=keyword
	q.append(qstring)
		
	# let the scrapping begin
	while True:
		try:
			print "Getting trend data for",gameTitle+".."
			trend_payload = {'q': q, 'cat': '8', 'date': '05/2016 4m'}
			retdf = pytrend.trend(trend_payload, return_type='dataframe')
		except KeyboardInterrupt:
			# so that you can still stop the program!
			print 'Interrupted'
			try:
				sys.exit(0)
			except SystemExit:
				os._exit(0)
		except Exception, e:
			print "Fail to scrap data for",gameTitle,"retrying in 10 seconds."
			print "Error:",e
			time.sleep(10)
			continue
		break
	
	for cols in retdf:
		if cols != "book":
			colname=cols
			break
	retdf["Normalized"]=0.0
	for j in range(len(retdf)):
		if retdf[ref_query][j]==0:
			retdf[col_normalized][j]=retdf[colname][j]
		else:
			retdf[col_normalized][j]=retdf[colname][j]/retdf[ref_query][j]
	a = Thread(target=retdf.to_csv("output/"+gameTitle+".csv", encoding="utf-8"))
	a.start()
	a.join()	
	retdf=pd.read_csv("output/"+gameTitle+".csv")
	for j in range(len(retdf)):
		date = retdf["Date"][j]
		if date not in df:
			df[date]=-1.0
		df.loc[i, date]=retdf[col_normalized][j]
	if col_avg_search_pop not in df:
		df[col_avg_search_pop]=0.0
	df.loc[i, col_avg_search_pop]=retdf[col_normalized].mean()
	a = Thread(target=df.to_csv(output, index=False))
	a.start()
	a.join()
	print(retdf)
	print "Average Search Popularity:",retdf[col_normalized].mean()
	i+=1