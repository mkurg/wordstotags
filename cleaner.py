# -!- encoding: utf-8 -!-
import re

a = []
with open('test2-cleaned.txt', 'r') as inp:
    for line in inp:
        a.append(line)
'''
for line in a:
    line = re.sub('\t\d+\t/.*$', '', line)
'''
freqDict = {}

for line in a:
    z = re.findall('\w+і\w+', line)
    if len(z) > 0:
        for l in z:
                if l in freqDict:
                    freqDict[l] += 1
                else:
                    freqDict[l] = 1
with open('poi.txt', 'w') as out:
    for word in sorted(freqDict, key = lambda x: freqDict[x], reverse=True):
        out.write(word + ':' + str(freqDict[word]) + '\n')