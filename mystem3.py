from pymystem3 import Mystem
a = []
with open('test2-cleaned.txt', 'r') as f:
    for line in f:
        a.append(line)
for line in a:
    text = line
    m = Mystem()
    lemmas = m.lemmatize(text)
    print(''.join(lemmas))