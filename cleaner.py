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
with open('test2-words-2.txt', 'w') as out:
	for line in a:
		z = re.findall('\w+\.\w+', line)
		if len(z) > 0:
			for l in z:
				out.write(l)
				out.write('\n')