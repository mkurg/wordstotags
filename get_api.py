import urllib, urllib.request, urllib.parse, codecs, json, time

data = {}
numbers = []
for line in open('rus_cities_numbers.txt', 'r'):
	time.sleep(0.2)
	print(line)
	numbers.append(line)
	f = urllib.request.urlopen('http://gis.ostrovok.ru/api/v0.2/region/synonyms/' + line)
	data[line] = json.loads(str(f.read(f.length).decode('utf-8')))

with open('synonyms.csv', 'w') as synonyms:
	for line in numbers:
		synonyms.write(line + '\t' + str(data[line]))