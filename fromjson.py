import sys, json
with open ('cities.json') as cities:
	for line in cities:
		data = json.loads(line)
for city in data:
	print(city['name_ru'])