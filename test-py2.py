# -!- encoding: utf-8 -!-
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

token = u'стали'

#token.encode('utf-8')

morphology = [morph.parse(token)[0].normal_form, morph.parse(token)[0].tag.case, morph.parse(token)[0].tag.number]

print(morphology)