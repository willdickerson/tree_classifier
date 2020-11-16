import requests
import json
from pandas.io.json import json_normalize
import pandas as pd
import urllib.request
import os
import ssl

# turn certificate verification off (insecure)
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
	ssl._create_default_https_context = ssl._create_unverified_context

outputFolder = "trees"
if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)

# Texas Live Oak, Bur Oak, Cedar Elm, Bald Cypress, Sassafras, Texas Ash, Pecan, American Sycamore, Texas Mountain Laurel, American Holly, Yaupon Holly, Wax Myrtle, Crape Myrtle, Southern Red Oak
speciesIdList = ["167647", "54781", "128823", "49666", "54795", "636177", "67593", "49662", "499559", "60749", "119955", "119956", "135394", "61324"]

for speciesId in speciesIdList:
	df = pd.DataFrame([])
	dataSize = 1

	# First 5 pages, 200 observations / page, 1000 images
	for pageNum in range(1,6):
		# REST endpoint for retrieving observations, consult https://www.inaturalist.org/pages/api+reference for parameters
		url = "https://api.inaturalist.org/v1/observations?identified=true&photos=true&quality_grade=research&order=desc&order_by=created_at&taxon_id="+speciesId+"&place_id=1&per_page=200&page="+str(pageNum)
		response = requests.get(url)
		dictr = response.json()
		recs = dictr['results']
		dataSize = len(recs)
		data = pd.json_normalize(recs)
		if dataSize > 0:
		    df = df.append(data)
		else:
			break

	# Save images to the folder
	for x in range(0, len(df)):
		id = df['id'].values[x]
		commonName = df['taxon.preferred_common_name'].values[x]
		imageURL = pd.json_normalize(df['photos'].values[x])['url'].values[0]
		imageURLM = imageURL.replace("square", "medium")
		speciesFolder = outputFolder+'/'+ commonName + '/'
		if not os.path.exists(speciesFolder):
			os.makedirs(speciesFolder)
		urllib.request.urlretrieve(imageURLM, speciesFolder + str(id)+'.jpg')




