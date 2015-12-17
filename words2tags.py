# -!- encoding: utf-8 -!-

import datetime
import json
from os import listdir
from os.path import isfile, join
import re
import sys
import codecs
import datetime

import pprint

# Linguisics
from nltk.stem.snowball import RussianStemmer
from nltk.stem.snowball import EnglishStemmer

pp = pprint.PrettyPrinter(depth=6)

timestamps = []
timestamps.append(datetime.datetime.now())

inp_file = 'test2-cleaned.txt'

with codecs.open(inp_file, 'r', encoding='utf-8') as f:
    queries_raw = f.readlines()
for i in range(len(queries_raw)):
    #queries_raw[i] = re.sub('\n', '', queries_raw[i], flags=re.UNICODE)
    queries_raw[i] = queries_raw[i].strip('\n')

def tokenize(line):
    #tokens = line.split()
    tokens = re.findall('[\w*]+', line, flags=re.UNICODE)
    return(tokens)

stemmed = {}
def normalize(tokens):
    stems = []
    for token in tokens:
        a = token.lower()
        if a not in stemmed:
            if ord(a[0]) <= 127:
                stems.append(EnglishStemmer(ignore_stopwords=False).stem(a))
                stemmed[a] = stems[-1]
            else:
                stems.append(RussianStemmer(ignore_stopwords=False).stem(a))
                stemmed[a] = stems[-1]
        else:
            stems.append(stemmed[a])
            #print('from cache')
    return stems

# Parsing and stemming queries
queries_parsed = []
for query in queries_raw:
    if len(queries_parsed) % 1000 == 0:
        print len(queries_parsed)
    tokenized = tokenize(query)
    #pp.pprint(tokenized)
    stems = normalize(tokenized)
    queries_parsed.append(stems)

#pp.pprint(queries_parsed[0:10])

tags_one_word = {}
tags_many_words = []
# Parsing tags dictionaries
tag_files = [f for f in listdir('./tags/') if isfile(join('./tags/',f)) ]
for tag_file in tag_files:
    if tag_file.endswith('.txt'):
        print 'processing tag file \'%s\'' % tag_file
        with codecs.open('./tags/' + tag_file, 'r', encoding='utf-8') as tf:
            current_tag = tag_file[:-4]
            tags_many_words.append([current_tag, []])
            for line in tf:
                tokenized = tokenize(line)
                stems = normalize(tokenized)
                if len(stems) == 1:
                    tags_one_word[stems[0]] = current_tag
                else:
                    tags_many_words[-1][1].append(stems)
#print tags_one_word

# Приписывание тегов
# Сначала проверяем на многословные теги
queries_tagged = []
n = 0
for ii in queries_parsed:
    queries_tagged.append([set(), set(), len(ii), False])
    #print ii
    n += 1

# Структура. 0 - множество тегов, 1 - множество номеров разобранных токенов, 2 - длина запроса в токенах, 3 - полностью ли распаршен запрос
for tag in tags_many_words:
    n = 0
    print 'pass 1, tag %d of %d (%s)' % (tags_many_words.index(tag), len(tags_many_words), tag[0])
    for query in queries_parsed:
        #if n % 1000 == 0:
        #    print 'pass 1, query %d' % n
        for i in range(len(query)):
            if len(tag[1]) > 0:
                for k in tag[1]:
                    if query[i] == k[0] and query[i:i + len(k)] == k:
                        queries_tagged[n][1].update(range(i, i + len(k)))
                        queries_tagged[n][0].add(tag[0])
        n += 1
n = 0
for query in queries_parsed:
    if n % 1000 == 0:
        print 'pass 2, query %d' % n
    for i in range(len(query)):
        if not i in queries_tagged[n][1]:
            try:
                if tags_one_word[query[i]] != 'stopword':
                    queries_tagged[n][0].add(tags_one_word[query[i]])
                queries_tagged[n][1].add(i)
            except KeyError:
                pass
    n += 1
parsed_number = 0
for i in queries_tagged:
    if len(i[1]) == i[2]:
        i[3] = True
        parsed_number += 1
n = 0
for i in queries_tagged:
    i.append(queries_raw[n])
    n +=1
#pp.pprint(queries_tagged)

# Вывод
print('Parsed %d queries (%s%%)' % (parsed_number, format((parsed_number * 100 / len(queries_tagged)), '.3f')))
with codecs.open('new_out.csv', 'w', encoding='utf-8') as out:
    out.write('query\ttags\tparsed\n')
    for query in queries_tagged:
        out.write('%s\t%s\t%s\n' % (query[4], query[0], query[3]))
timestamps.append(datetime.datetime.now())
print(timestamps[1] - timestamps[0])

tag_sets = {}
tags_freq = {}
for query in queries_tagged:
    if query[3] == True:
        if str(sorted(query[0])) in tag_sets:
            tag_sets[str(sorted(query[0]))].append(query[4])
        else:
            tag_sets[str(sorted(query[0]))] = [query[4]]
        if str(sorted(query[0])) in tags_freq:
            tags_freq[str(sorted(query[0]))] += 1
        else:
            tags_freq[str(sorted(query[0]))] = 1
#pp.pprint(tag_sets)

tag_sets_list = []
for k, v in tag_sets.items():
    tag_sets_list.append([k, v])
queries_popularity = {}

for tag_set in tag_sets_list:
    ddict = {}
    llist = []
    for a in tag_sets[tag_set[0]]:
        #print a
        if a in ddict:
            ddict[a] += 1
        else:
            ddict[a] = 1
    for k, v in ddict.items():
        llist.append([k, v])
    llist.sort(key = lambda s: s[1], reverse=True)
    queries_popularity[tag_set[0]] = llist

tags_freq_list = []
for k, v in tags_freq.items():
    tags_freq_list.append([k, v])
tags_freq_list = sorted(tags_freq_list, key=lambda setOfTags: setOfTags[1], reverse=True)
tags_freq_list = list(enumerate(tags_freq_list))

with codecs.open('new_stat.csv', 'w', encoding='utf-8') as new_stat:
    for i in tags_freq_list:
        try:
            new_stat.write('%d\t%s\t%s%%\t%s\t%d\n' % (i[0], i[1][0], format(i[1][1] / float(len(queries_raw)) * 100, '.3f'), queries_popularity[i[1][0]][0][0], queries_popularity[i[1][0]][0][1]))
        except KeyError:
            new_stat.write()



# То же, но для нераспаршенных
tag_sets = {}
tags_freq = {}
for query in queries_tagged:
    if query[3] == False:
        if str(sorted(query[0])) in tag_sets:
            tag_sets[str(sorted(query[0]))].append(query[4])
        else:
            tag_sets[str(sorted(query[0]))] = [query[4]]
        if str(sorted(query[0])) in tags_freq:
            tags_freq[str(sorted(query[0]))] += 1
        else:
            tags_freq[str(sorted(query[0]))] = 1
#pp.pprint(tag_sets)

tag_sets_list = []
for k, v in tag_sets.items():
    tag_sets_list.append([k, v])
queries_popularity = {}

for tag_set in tag_sets_list:
    ddict = {}
    llist = []
    for a in tag_sets[tag_set[0]]:
        #print a
        if a in ddict:
            ddict[a] += 1
        else:
            ddict[a] = 1
    for k, v in ddict.items():
        llist.append([k, v])
    llist.sort(key = lambda s: s[1], reverse=True)
    queries_popularity[tag_set[0]] = llist

tags_freq_list = []
for k, v in tags_freq.items():
    tags_freq_list.append([k, v])
tags_freq_list = sorted(tags_freq_list, key=lambda setOfTags: setOfTags[1], reverse=True)
tags_freq_list = list(enumerate(tags_freq_list))

with codecs.open('new_stat_unparsed.csv', 'w', encoding='utf-8') as new_stat:
    for i in tags_freq_list:
        try:
            new_stat.write('%d\t%s\t%s%%\t%s\t%d\n' % (i[0], i[1][0], format(i[1][1] / float(len(queries_raw)) * 100, '.3f'), queries_popularity[i[1][0]][0][0], queries_popularity[i[1][0]][0][1]))
        except KeyError:
            new_stat.write()
'''
for tag_set in tag_sets.items():
    #pp.pprint(tag_set)
    ddict = {}
    for query in tag_set:
        #pp.pprint(query)
        #print
        if str(query) in ddict:
            ddict[str(query)] += 1
        else:
            ddict[str(query)] = 1
    #pp.pprint(ddict)

queries_popularity = {}
for tag_set in tag_sets.items():
    ddict = {}
    llist = []
    for qquery in tag_set:
        if str(qquery) in ddict:
            ddict[str(qquery)] += 1
        else:
            ddict[str(qquery)] = 1
    for k, v in ddict.items():
        llist.append([k, v])
    llist.sort(key = lambda s: s, reverse=True)
    queries_popularity[str(tag_set)] = llist

pp.pprint(queries_popularity)
# Отладочный вывод
'''
'''
test_queries = [u'в санкт-петербурге', u'Санкт-Петербург']
for i in test_queries:
    tokenized = tokenize(i)
    #pp.pprint(tokenized)
    stems = normalize(tokenized)
    for stem in stems:
        print stem

for query in queries_parsed:
    for token in query:
        print(token)
with codecs.open('out3.txt', 'w', encoding='utf-8') as out:
    out.write(unicode(str(queries_parsed), 'unicode-escape'))


for i in queries_parsed:
    print queries_parsed.index(i)
    for j in i:
        print j

for i in tags_many_words:
    if i[0] == 'city':
        for j in i[1]:
            print len(j)
            for k in j:
                print k

test = u'Это какая-то тестоввая строка-строчечка with some English words. 2* 3* двухзвёздочный островок.ру https://slovari.yandex.ru/tarball/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4/ перевірка Київ, Києва'
#test = tokenize(test)
#RussianStemmer(ignore_stopwords=False).stem()

a = tokenize(test)

for l in a:
    print l

'''