import os, re
for filename in os.listdir('.'):
	a = re.sub('acc', 'acm', filename)
	a = re.sub('-', '_', a)
	os.rename(filename, a)