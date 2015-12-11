# -!- encoding: utf-8 -!-
"""wordstotags converts search engine queries to sets of semantic tags."""

import re
import sys
from os import listdir
from os.path import isfile, join
import pymorphy2
import pprint
import json
import datetime

timestamps = []
timestamps.append(datetime.datetime.now())
    

with open('test.txt', 'r') as f:
    queriesRaw = f.readlines()
for query in queriesRaw:
    query = query.strip('\n')
    query = re.sub('\n', '', query)

inFile = 'test.txt'

pp = pprint.PrettyPrinter(depth=6)

#morph = pymorphy2.MorphAnalyzer()
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


pp = pprint.PrettyPrinter(depth=6)

def Splitter(line):
    tokens = line.split()
    for token in tokens:
        token = token.strip('\n')
        token = re.sub('\n', '', token)
    return(tokens)

def normalizer(queries):
    result_queries = []
    # за каждую итерацию цикла значение index увеличивается на 1, начиная с 0; query = queries[index]
    for index, query in enumerate(queries):
        if index % 100 == 0:
            # print можно использовать без скобок
            print 'normalizing query %d' % index

        query_normal_form = []
        for token in query:
            query_normal_form.append(morph.parse(token.decode('utf-8')).normal_form)
        result_queries.append(query_normal_form)
    print result_queries
    return result_queries

def ProcessFile(inFile):
    n = 0
    queries = []
    with open(inFile) as inFile:
        for line in inFile:
            print('parsing line %d' % n)
            line.strip('\n')
            line = Splitter(line)
            queries.append(line)
            n+=1
    queries = normalizer(queries)
    #print(queries)
    #pp.pprint(queries)
    return(queries)



queriesParsed = ProcessFile(inFile)
queriesParsed2 = []
for query in queriesParsed:
    queriesParsed2.append([query])
queriesParsed = queriesParsed2

# обрабатываем слова для тегов
tagFiles = [ f for f in listdir('./tags/') if isfile(join('./tags/',f)) ]
tags = []
keyWordsOriginal = []
for tagFile in tagFiles:
    if tagFile[-4:] == '.txt':
        print('processing tag file \'%s\'' % tagFile)
        keyWordsOriginal.append([[tagFile[:-4]]])
        keyWordsOriginal[-1].append([])
        with open('./tags/' + tagFile, 'r') as tf:
            tags.append([tagFile[:-4]])
            for line in tf:
                keyWordsOriginal[-1][1].append(line.strip('\n'))
                #tags[-1].append([])
                line = line.split()
                tags[-1].append([])
                for token in line:
                    token = token.strip('!.,?:;\'\"\(\)<>[]\ufeff\n\r')
                    token = token.lower()
                    #tags[-1][-1].append([morph.parse(token)[0].normal_form, morph.parse(token)[0].tag.case, morph.parse(token)[0].tag.number])
                    #tags[-1][-1].append([morph.parse(token.decode('utf-8'))[0].normal_form])
                    tags[-1][-1].append([morph.parse(token.decode('utf-8'))[0]])



# превращаем список слов запроса в список (пригодится для обратной задачи) тегов
def Tagger(query): # сравниваем лишь нормалиованные формы, без числа и падежа
"""Логика работы: берём нормализованные формы токенов запроса по порядку и
    сравниваем со всеми первыми токенами элементов словаря. Если каждый
    следующий токен, присутствующий в единице словаря, есть и в запросе,
    приписывай соответствующий тег."""
    queryTokens = []
    matched = 0
    queryLemmas = []
    for queryToken in query[0]:
        queryLemmas.append(queryToken)
    ifCounted = []
    for i in range(len(queryLemmas)):
        ifCounted.append(False)
    #print(ifCounted)
    #print(queryLemmas)
    for tag in tags:
        for tagToken in tag:
            if tag.index(tagToken) != 0:
                tagLemmas = []
                for tagToken2 in tagToken:
                    tagLemmas.append(tagToken2[0])
                #print(tagLemmas)
                for i in range(len(queryLemmas)):
                    if queryLemmas[i] == tagLemmas[0] and queryLemmas[i:i + len(tagLemmas)] == tagLemmas:
                         #print(tagLemmas)
                         #print(tags[tags.index(tag)][0])
                         #print(queryLemmas)
                         if tags[tags.index(tag)][0] != u'stopword':
                            queryTokens.append(tags[tags.index(tag)][0])
                         numbersOfMatched = []
                         for j in range(i, i + len(tagLemmas)):
                            numbersOfMatched.append(j)
                            ifCounted[j] = True
                         #print(numbersOfMatched)
                         #print('\n')
    print(ifCounted)
    #if matched == len(query): # проверяем, все ли токены "ушли" на теги
    if not False in ifCounted:
        queryTokens.append(u'full')
    print(set(queryTokens))
    return(set(queryTokens))


parsed = 0
processed = 0
tagsFreq = {} # частотность данного множества тегов для полностью распаршенного запроса
tagsQueries = [] # это будет список с запросами в виде тегов, соответствующий списку запросов
queryCache = {}
outTableAll = open('queries-tagged.csv', 'w')
outTableFull = open('queries-good-tagged.csv', 'w')
for query in queriesParsed:
    print "this is query: %s" % query
    if processed % 100 == 0:
        print('processing query %d' % processed)
#   print(query)
#   print(Tagger(query))
    if not str(query) in queryCache:
        tagged = Tagger(query)
        queryCache[str(query)] = tagged
    else:
        tagged = queryCache[str(query)]
    #tagged = Tagger(query)

    if u'full' in tagged:
        taggedWithoutFull = set(tagged)
        #taggedWithoutFull.remove(u'full')
        #print(tagged)
        parsed +=1
        #tagged.remove(u'full')
        if  str(sorted(set(taggedWithoutFull))) in tagsFreq:
            tagsFreq[str(sorted(set(taggedWithoutFull)))] += 1
        else:
            tagsFreq[str(sorted(set(taggedWithoutFull)))] = 1
        #outTableAll.write('%s\t%s\n' % (queriesRaw[nn].strip('\n'), str(sorted(set(tagged)))))
        #nn += 1
#for query in queriesParsed:
#   if u'full' in tagged:
#       tagged.remove(u'full') # чтобы потом находилось в словаре для статистики популярных запросов
    #print(tagged)
    processed += 1
    tagsQueries.append(tagged) 
tagsFreq2 = {}
tagsFreq['total'] = parsed
for i, k in tagsFreq.items():
    tagsFreq2[i + '_%'] = k * 100 / len(queriesParsed)
#for i, k in tagsFreq.items():
#   tagsFreq2[i] += k * 100 / len(queriesParsed)
#tagsFreqAll = tagsFreq.copy()
#tagsFreqAll.update(tagsFreq2)
tagsFreqList = []
tagsFreq2List = []
for k, v in tagsFreq.items():
    tagsFreqList.append([k,v])
for k, v in tagsFreq2.items():
    tagsFreq2List.append([k,v])
tagsFreqList = sorted(tagsFreqList, key=lambda setOfTags: setOfTags[1], reverse=True)
tagsFreq2List = sorted(tagsFreq2List, key=lambda setOfTags: setOfTags[1], reverse=True)
tagsFreq2List = list(enumerate(tagsFreq2List))
#pp.pprint(tagsFreq2List)

# вывод

allStatistics = []
allStatistics.append(tagsFreq2List)
allStatistics.append(tagsFreqList)
'''
with open('out.json', 'w') as outfile:
    json.dump(tagsQueries, outfile)
with open('statistics.json', 'w') as statisticsfile:
    json.dump(allStatistics, statisticsfile)
'''
print(parsed / len(queriesParsed))

# новый вывод

tags.sort()

yetAnotherDictOfTags = {}

keyWordsOriginal.sort(key = lambda s: len(s[1]))
oi = 0
for tagSet in tagsQueries:
    #print(tagSet)
    #if u'full' in tagSet:
#       tagSet.remove(u'full') # чтобы в этом списке теперь тоже было без фулл, список нужен для отображения статистики самого популярного запроса
    #if str(tagSet) in yetAnotherDictOfTags:
    #   yetAnotherDictOfTags[str(tagSet)].append([queriesRaw[tagsQueries.index(tagSet)], tagsQueries.index(tagSet)])
    #else:
    #   yetAnotherDictOfTags[str(tagSet)] = [[queriesRaw[tagsQueries.index(tagSet)], tagsQueries.index(tagSet)]]
    #tagSet = set(tagSet)
    #tagSet.sort()
    if str(sorted(set(tagSet))) in yetAnotherDictOfTags:
        yetAnotherDictOfTags[str(sorted(set(tagSet)))].append([queriesRaw[oi], oi])
    else:
        yetAnotherDictOfTags[str(sorted(set(tagSet)))] = [[queriesRaw[oi], oi]]
    oi += 1
queriesPopularity = {}
#pp.pprint(yetAnotherDictOfTags)
#def GetListofQueriesByTag:
for tagSet in yetAnotherDictOfTags.items():
    #pp.pprint(tagSet[0])
    ddict = {}
    llist = []
    for qquery in tagSet[1]:
        #pp.pprint(qquery[0])
        if str(qquery[0]) in ddict:
            ddict[str(qquery[0])] += 1
        else:
            #pp.pprint(qquery[0])
            ddict[str(qquery[0])] = 1
    #pp.pprint(ddict)
    for k, v in ddict.items():
        llist.append([ k, v])
    #pp.pprint(tagSet[0])
    llist.sort(key = lambda s: s[1], reverse=True)
    #pp.pprint(llist)
    #for a in llist:
    #   queriesPopularity[a[0]] = a[1]
    queriesPopularity[tagSet[0]] = llist
#pp.pprint(queriesPopularity)




with open('prettyStatistics.txt', 'w') as prettyStatistics:
    #prettyStatistics.write('total: %f%%' % tagsFreq2List[0][1])
    prettyStatistics.write('Queries processed: %d. For all parsed queries see file \'queries-tagged.csv\', for fully parsed queries see file \'queries-good-tagged.csv\' (separator - tabulation).\n\n' % len(queriesParsed))
    prettyStatistics.write('Tags:\n\n(\'full\' is a marker for fully parsed queries.)\n')
    keyWordsTotal = 0
    for k in tags:
        prettyStatistics.write('%s - %d\n' % (k[0], len(k)))
        keyWordsTotal += len(k)
    prettyStatistics.write('\nTotal number of keywords: %d. Full list of keywords see below\n' % keyWordsTotal)
    prettyStatistics.write('\nTag sets statistics:\n\n')
    for i in tagsFreq2List:
        try:
            #prettyStatistics.write('%d. %s - %s%%, most popular query: %s\n' % (i[0], i[1][0][:-2], format(i[1][1],'.3f'), queriesPopularity[i[1][0][:-2]][0]))
            unist = str(queriesPopularity[i[1][0][:-2]][0][0])
            unist.decode('utf-8')
            prettyStatistics.write('%d. %s - %s%%, most popular query: %s, %s\n' % (i[0], i[1][0][:-2], format(i[1][1],'.3f'), unist, queriesPopularity[i[1][0][:-2]][0][1]))
        except KeyError:
            prettyStatistics.write('%d. %s - %s%%\n' % (i[0], i[1][0][:-2], format(i[1][1],'.3f')))
    prettyStatistics.write('\nList of keywords (sorted by length):')
    for tag in keyWordsOriginal:
        prettyStatistics.write('\n\n%s' % tag[0][0])
        for line in tag[1]:
            prettyStatistics.write('\n\t%s' % line)


with open('newStatistics.csv', 'w') as newStatistics:
    for i in tagsFreq2List:
        try:
            newStatistics.write('%d\t%s\t%s%%\t%s\t%s\n' % (i[0], i[1][0][:-2], format(i[1][1],'.3f'), re.sub('\n', '', queriesPopularity[i[1][0][:-2]][0][0]), queriesPopularity[i[1][0][:-2]][0][1]))
        except KeyError:
            newStatistics.write('%d\t%s\t%s%%\n' % (i[0], i[1][0][:-2], format(i[1][1],'.3f')))
with open('new2Statistics.csv', 'w') as new2Statistics:
    for tag in keyWordsOriginal:
        new2Statistics.write('%s' % tag[0][0])
        for line in tag[1]:
            new2Statistics.write('\t%s\n' % line)

# вывод найденных запросов
'''
print(queriesParsed[31]) # запрос разбит на списки: [нормальная форма слов, падеж, число]
print(queriesRaw[31]) # запрос как есть
print(tagsQueries[31]) # теги данного запроса (если среди прочих есть u'full', скрипт считает, что запрос разобран полностью)
'''

for i in range(len(queriesRaw)):
    outTableAll.write('%s\t%s\n' % (queriesRaw[i].strip('\n'), tagsQueries[i]))
    for q in tagsQueries[i]:
        if u'full' in q:
            outTableFull.write('%s\t%s\n' % (queriesRaw[i].strip('\n'), tagsQueries[i]))

timestamps.append(datetime.datetime.now())
print(timestamps[1] - timestamps[0])
print(parsed)
print('see file \'prettyStatistics.txt\'')
#pp.pprint(queriesPopularity)