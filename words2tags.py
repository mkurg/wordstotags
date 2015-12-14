# -!- encoding: utf-8 -!-

import datetime
import json
from os import listdir
from os.path import isfile, join
import re
import sys

import pprint
import pymorphy2

pp = pprint.PrettyPrinter(depth=6)

timestamps = []
timestamps.append(datetime.datetime.now())

inp_file = 'test2-cleaned.txt'

with open('test1001.txt', 'r') as f:
    queriesRaw = f.readlines()
for query in queriesRaw:
    #query = query.strip('\n')
    query = re.sub('\n', '', query)

class CacheMorchAnalyzer:
    def __init__(self):
        self.ma = pymorphy2.MorphAnalyzer()
        self.parsed_words = {}

    def parse(self, word):
        if word not in self.parsed_words:
            parsed_result = self.ma.parse(word)
            if parsed_result:
                self.parsed_words[word] = parsed_result[0]
        return self.parsed_words[word]

morph = CacheMorchAnalyzer()

def Splitter(line):
    tokens = line.split()
    for token in tokens:
        token = token.strip('\n')
        token = re.sub('\n', '', token)
    return(tokens)

with open('out3.txt', 'w') as out:
    out.write(str(queriesRaw[0:10]))