#!/bin/env python
import json,sys
import dateutil.parser,pandas,requests
p=type('',(),{'__pow__':lambda _,x:print(x)or x})()

if len(sys.argv) == 3:
	zipcode,radius = sys.argv[1:3]
else:
	print('usage: find <zipcode> <radius>')
	sys.exit(1)


def fetch(resource,json):
	return requests.post(
		'https://tools.usps.com/UspsToolsRestServices/rest/'+resource,
		headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0',
			'Accept': 'application/json, text/javascript, */*; q=0.01',
			'Content-Type': 'application/json;charset=utf-8',
		},
		json= json
	).json()



locations = fetch(
	'POLocator/findLocations',
	{
		'maxDistance': radius,
		'lbro': '',
		'requestType': 'po',
		'requestServices': '',
		'requestRefineTypes': '',
		'requestRefineHours': '',
		'requestZipCode': str(zipcode),
		'requestZipPlusFour': '',
	}
)


def get_dates(location_id):
	return fetch(
		'v2/appointmentDateSearch',
		{
			'numberOfAdults': '1',
			'numberOfMinors': '0',
			'fdbId': str(location_id),
			'productType': 'PASSPORT',
		}
	)


def load_jsonfile(filename):
	with open(filename,'r') as jsonfile:
		return json.load(jsonfile)

location_names = {
	int(location['locationID']):
	location['locationName']
	for location
	in locations['locations']
}
dates = {
	id:
	list(map(dateutil.parser.parse,get_dates(id)['dates'] or []))
	for id in location_names.keys()
}


options = pandas.DataFrame(
	[
		(location_names[id],date)
		for id,id_dates in dates.items()
		for date in id_dates
	],
	columns=['location','date']
)

print(options.sort_values('date').to_string(index=False))
