# -!- encoding: utf-8 -!-
import re
import sys

data = open('queries-tagged-2015-11-24.csv')
queries = []
for line in data:
	a = line
	a = re.sub('\n', '', a)
	a = a.split('\t')
	if not '\'full\'' in a[1]:
		queries.append([a[0], a[1]])
print(queries[3])
queriesDict = {}
for query in queries:
	if not query[0] in queriesDict:
		queriesDict[query[0]] = [1, query[1]]
	else:
		queriesDict[query[0]][0] += 1
print(queriesDict['гостиницы в энгельсе цены'])
queriesList = []
for k, v in queriesDict.items():
	queriesList.append([k, v[0], v[1]])
print(queriesList[3])
queriesList.sort(key = lambda s: s[1], reverse=True)
for i in range(15):
	print(queriesList[i])
with open('unparsed.csv', 'w') as unparsed:
	for i in queriesList:
		unparsed.write(i[0] + '\t' + str(i[1]) + '\t' + i[2] + '\n')