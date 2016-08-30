import csv
import time
import datetime
import collections

filename = 'OutputScore.txt'; target = 'Trump'
filename = 'OutputTimesCameron.txt'; target = 'Caneron'
filename = 'OutputTimesCuba.txt'; target = 'Cuba'
filename = 'OutputTimesFaggot.txt'; target = 'Faggot'

results = []
with open(filename, newline='') as inputfile:
    for row in csv.reader(inputfile):
        results.append(row)
res = results[0][0].split(" ")
res = res[:-1]

TRG=['faggot', 'poof', 'dyke', 'fag']
TRG=['gay']
for target in TRG:
    ###############
    import pickle
    with open('saved_'+target,'rb') as f:  # Python 3: open(..., 'rb')
        res = pickle.load(f)
    res = [item[1] for item in res.values]
    ###############


    res.sort()

    ress=[]
    for item in res:
        tmp = time.ctime(int(item))
        ress.append(tmp[8:-14])

    d = dict((x, ress.count(x)) for x in ress)
    d = collections.OrderedDict(sorted(d.items()))

    import matplotlib.pyplot as plt
    import numpy as np

    X = np.arange(len(d))
    plt.bar(range(len(d)), d.values(), align="center",width=1)
    plt.xticks(range(len(d)), list(d.keys()))#,rotation='vertical'
    plt.xlabel('Days in May 2015')
    plt.ylabel('Mentions for ' + target)
    ymax = max(d.values()) + 1
    plt.ylim(0, ymax)
    plt.show()

