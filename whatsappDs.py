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
print('Conversation between '+str(len(users))+' users:' + str(users))

ind=[]
for u in range(0,len(users)):
    indt=[]
    for n in sender:
        indt.append(True) if n==users[u] else indt.append(False)
    ind.append(indt)

# hoe many individual messages from users
letter_counts = Counter(sender)
df = pandas.DataFrame.from_dict(letter_counts, orient='index')
df.plot(kind='bar')

#

NoWrdsUsr=[]
bodyUsr=[]
for u in range(0,len(users)):
    bodyUsr.append([body[i] for i, x in enumerate(ind[u]) if x])
    NoWrdsUsr.append(len(''.join([body[i] for i, x in enumerate(ind[u]) if x]).split(' ')))

print('TF-IDF Analysis')
vec = TfidfVectorizer(min_df=1, stop_words='english')
X = vec.fit_transform(bodyUsr[0])
idf = vec.idf_
res_dic = dict(zip(vec.get_feature_names(), idf))
st = sorted(res_dic.items(), key=lambda x: x[1])
#print(dict(zip(vec.get_feature_names(), idf)))
print(st[-20:-1])

print('TF-IDF Analysis')
vec2 = TfidfVectorizer(min_df=1, stop_words='english')
X = vec2.fit_transform(bodyUsr[1])
idf2 = vec2.idf_
res_dic2 = dict(zip(vec2.get_feature_names(), idf2))
st2 = sorted(res_dic2.items(), key=lambda x: x[1])
#print(dict(zip(vec.get_feature_names(), idf)))
print(st2[-20:-1])
