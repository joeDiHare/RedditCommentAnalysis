import csv
import re
import datetime
import time
import numpy as np
import pandas
from collections import Counter
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import difflib
from datetime import date, timedelta

# script to read-in list of words
filename = "C:/Users/Stefano/Documents/chat.txt"
MsgErr1 = 'Messages you send to this chat and calls are now secured with end-to-end encryption. Tap for more info.'
print("Reading chat conversation & data validation...      ", end="")
results = []
with open(filename, newline='',encoding='UTF8') as inputfile:
    for row in csv.reader(inputfile):
        if row!=[]:
            if re.search(r'(\d+/\d+/\d+)', row[0]) is None:
                results[-1][-1] = results[-1][-1] + ' ' + row[0]
            elif row[1].partition('-')[-1].partition(':')[0].strip()!= MsgErr1:
                results.append(row)
print('[done]')

print("Create lists...      ", end="")
bodyraw, dates, body, datesLong, message, tm, sender = [],[],[],[],[],[],[]
for item in results:
    match_date = re.search(r'(\d+/\d+/\d+)', ''.join(item))
    match_time = re.search(r'(\d+:\d+)', item[1])
    datesLong.append(datetime.datetime.strptime(match_date.group(1) +' '+ match_time.group(1), "%d/%m/%Y %H:%M"))
    dates.append(item[0])
    tm.append(match_time.group(1))
    sender.append(item[1].partition('-')[-1].partition(':')[0].strip())
    message.append(''.join(item))
    bodyraw.append(item[1])
    body.append(item[1].partition(':')[-1].partition(':')[-1].strip())
print('[done]')

print('DATA ANALYSIS')
users = list(set(sender))
print('Conversations between '+str(len(users))+' users:' + str(users))

ind=[]
for u in range(0,len(users)):
    indt=[]
    for n in sender:
        indt.append(True) if n==users[u] else indt.append(False)
    ind.append(indt)

# how many individual messages from users
letter_counts = Counter(sender)
df = pandas.DataFrame.from_dict(letter_counts, orient='index')
df.plot(kind='bar')

# MOST COMMON 20 WORDS PER USER
# script to read-in strop words
filename = 'stopwords.txt'; stopwords = []
with open(filename, newline='',encoding='UTF8') as inputfile:
    for row in csv.reader(inputfile):
        stopwords.append(row[0].lower())
NoWrdsUsr, bodyUsr, count =[],[],[]
for u in range(0,len(users)):
    bodyUsr.append([body[i] for i, x in enumerate(ind[u]) if x])
    NoWrdsUsr.append(len(''.join([body[i] for i, x in enumerate(ind[u]) if x]).split(' ')))

    print('\nTF-IDF Analysis for user: ' + users[u] )
    count.append(Counter(word for word in ' '.join(bodyUsr[u]).lower().split() if word not in stopwords).most_common(20))
    print(count[u])

# HOW MANY JINX?
jinxNo = []
for u in range(0,len(users)):
    jinxNo.append(len(difflib.get_close_matches('jinx', ' '.join(bodyUsr[u]).lower().split(), n=100, cutoff=.8)))
    print('User: ' + users[u] + ' jinxed ' + str(jinxNo[u]) + ' times.')

# 0000000000000000000000000000000000000000000000000000000000000000000000
# TIME ANALYSIS
# find unique dates
Duniq=['initialize']
for n in dates:
    Duniq.append(n) if Duniq[-1]!=n else ''
Duniq.pop(0)
# noDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, \
#           31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
# noMsgPerDay=[]
# for n in Duniq:
#     noMsgPerDay.append(dates.count(n))

# a list containing all of the dates
d1 = date(int(dates[0][-4:10]),int(dates[0][3:5]),int(dates[0][0:2]))
d2 = date(int(dates[-1][-4:10]),int(dates[-1][3:5]),int(dates[-1][0:2]))
dd = [d1 + timedelta(days=x) for x in range((d2-d1).days + 1)]
noMsgPerDay=[]
for d in dd:
    noMsgPerDay.append(dates.count(d.strftime('%d/%m/%Y')))
    # print(d.strftime('%d/%m/%y'))
# how many messages per day?
# df = pandas.DataFrame.from_dict(noMsgPerDay)
# df.plot(kind='bar')
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 9))
ax = plt.subplot(111)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.get_xaxis().tick_bottom(); ax.get_yaxis().tick_left()
plt.xticks(fontsize=14);
plt.yticks(range(5000, 30001, 5000), fontsize=14)
plt.xlabel("days", fontsize=16);
plt.ylabel("Number of messages", fontsize=16)

df = pandas.DataFrame.from_dict(dict(zip(Duniq,noMsgPerDay)), orient='index')
df.plot(kind='bar')
#plt.show()

# Always include your data source(s) and copyright notice! And for your
# data sources, tell your viewers exactly where the data came from,
# preferably with a direct link to the data. Just telling your viewers
# that you used data from the "U.S. Census Bureau" is completely useless:
# the U.S. Census Bureau provides all kinds of data, so how are your
# viewers supposed to know which data set you used?
plt.text(1300, -5000, "Showing something cool about the convos"
                      "Author: SC", fontsize=10)
