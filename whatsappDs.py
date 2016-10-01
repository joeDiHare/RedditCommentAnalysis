import csv
import re
import datetime
import pandas
from collections import Counter
import difflib
from datetime import date, timedelta
import matplotlib.pyplot as plt
import string
from itertools import groupby
from collections import OrderedDict
import numpy as np

# script to read-in list of words
filename = "/Users/joeDiHare/Documents/chat.txt"#"C:/Users/Stefano/Documents/chat.txt"
MsgErr1 = 'Messages you send to this chat and calls are now secured with end-to-end encryption. Tap for more info.'
MsgErr2 = '<Media omitted>'
print("Reading chat conversation & data validation... ", end="")
results, mediaSender, mediaCaption = [], [], []
with open(filename, newline='',encoding='UTF8') as inputfile:
    for row in csv.reader(inputfile):
        if row!=[]:#ignore empty lines
            if re.search(r'(\d+/\d+/\d+)', row[0]) is None: #if not a new sender, attach to previous
                results[-1][-1] = results[-1][-1] + ' ' + row[0]
            elif row[1].partition('-')[-1].partition(':')[0].strip()!= MsgErr1: #remove error messages
                if row[1].partition(':')[-1].partition(':')[-1].strip()[:15]== MsgErr2: #count <Media omitted> and remove
                    mediaSender.append(row[1].partition('-')[-1].partition(':')[0].strip())
                    mediaCaption.append(row[1].partition(':')[-1].partition(':')[-1].strip())
                else:
                    results.append(row)
print('[done]')

print("Create full message lists... ", end="")
bodyraw, dates, body, datesLong, message, tm, sender = [],[],[],[],[],[],[]
for item in results:
    match_date = re.search(r'(\d+/\d+/\d+)', ''.join(item))
    match_time = re.search(r'(\d+:\d+)', item[1])
    datesLong.append(datetime.datetime.strptime(match_date.group(1) + ' ' + match_time.group(1), "%d/%m/%Y %H:%M"))
    dates.append(item[0])
    tm.append(match_time.group(1))
    sender.append(item[1].partition('-')[-1].partition(':')[0].strip())
    message.append(''.join(item))
    bodyraw.append(item[1])
    body.append(item[1].partition(':')[-1].partition(':')[-1].strip())
print('[done]')

users = list(set(sender))

print("Create conversation lists... ", end="")
# if the previous message is within LONG_BREAK_CON seconds and it is from the same sender, combine them in the same conversation
# initialise
ConvBody = [body[0]]; ConvSender = [sender[0]]; ConvDates = [dates[0]]; ConvDatesLong = [datesLong[0]]
ConvMessage = [message[0]]; ConvTime = [tm[0]]; ConvTimeEnd = [tm[0]]
Conversations = []
bodylast = '(' + sender[0] + ') ' + body[0]
RT = [-1]
LONG_BREAK_CONV = 20 * 60 # time constant to consider a message as belonging to a new conversation
LM = [],[]
for n in range(1,len(tm)):
    if (datetime.datetime.strptime(tm[n], "%H:%M") - datetime.datetime.strptime(tm[n-1], "%H:%M")).seconds < LONG_BREAK_CONV \
    and sender[n]==sender[n-1]: # same sender, add to last message
        ConvBody[-1] = ConvBody[-1] + '. ' + body[n]
        ConvTimeEnd[-1] = tm[n]
        bodylast = bodylast + '. ' + body[n]
    else: # break and start new msg in conversation
        ConvBody.append(body[n])
        ConvSender.append(sender[n])
        ConvTimeEnd.append(tm[n])
        ConvTime.append(tm[n])
        ConvDates.append(dates[n])
        ConvMessage.append(message[n])
        ConvDatesLong.append(datesLong[n])
        bodylast = bodylast + ' (' + sender[n] + ') ' +ConvBody[-1]
        RT.append(round((datetime.datetime.strptime(tm[n],"%H:%M")-datetime.datetime.strptime(ConvTimeEnd[-2],"%H:%M")).seconds/60)) \
            if sender[n] != ConvSender[-2] else RT.append(-1)
        if (datetime.datetime.strptime(tm[n], "%H:%M") - datetime.datetime.strptime(tm[n-1], "%H:%M")).seconds >= LONG_BREAK_CONV:
            Conversations.append(bodylast)
            bodylast=''
print('[done]')


# Find first mover (FM) occurrences
users_search = "|".join(users)
FM = []
for item in Conversations:
    FM.append(re.search(users_search, item).group())
FM_counts = Counter(FM)

print('DATA ANALYSIS')
print('Conversations between '+str(len(users))+' users:' + str(users))

ind=[]
for u in range(0,len(users)):
    indt=[]
    for n in sender:
        indt.append(True) if n==users[u] else indt.append(False)
    ind.append(indt)

# WHO MESSAGED THE MOST?
message_counts = Counter(sender)
df = pandas.DataFrame.from_dict(message_counts, orient='index')
df.plot(kind='bar')

# WHO SENT MORE MEDIA?
mediaSender_counts = Counter(mediaSender)
df2 = pandas.DataFrame.from_dict(mediaSender_counts, orient='index')
df2.plot(kind='bar')

for u in users:
    print(u+' sent ' +str(message_counts[u])+' messages and '+str(mediaSender_counts[u])+' images/videos.')

# MOST COMMON 20 WORDS PER USER
# script to read-in strop words
filename = 'stopwords.txt'; stopwords = []
with open(filename, newline='',encoding='UTF8') as inputfile:
    for row in csv.reader(inputfile):
        stopwords.append(row[0].lower())
NoWrdsUsr, bodyUsr, bodyCompact, count =[],[],[],[]
punctuation = set(string.punctuation)
for u in range(0,len(users)):
    bodyUsr.append([body[i] for i, x in enumerate(ind[u]) if x])
    NoWrdsUsr.append(len(''.join([body[i] for i, x in enumerate(ind[u]) if x]).split(' ')))

    print('\nTF-IDF Analysis for user: ' + users[u] )
    count.append(Counter(word for word in ' '.join(bodyUsr[u]).lower().split() if word not in stopwords).most_common(20))
    print(count[u])
    s = ''.join(ch for ch in ' '.join(bodyUsr[u]).lower() if ch not in punctuation)
    bodyCompact.append(s.split()) #compact version of body, all in one string


# HOW MANY JINX?
jinxNo = []
for u in range(0,len(users)):
    jinxNo.append(len(difflib.get_close_matches('jinx', ' '.join(bodyUsr[u]).lower().split(), n=100, cutoff=.8)))
    print(users[u] + ' jinxed ' + str(jinxNo[u]) + ' times.')

# HOW MANY 'LOVE' or 'I LOVE YOU'?
noLove, noWhy = [],[]; noHateU, noIloveU = [0]*len(users),[0]*len(users)
for u in range(0,len(users)):
    noLove.append(bodyCompact[u].count('love'))
    noWhy.append(bodyCompact[u].count('why'))
    for i in range(0,len(bodyCompact[u])-3):
        if bodyCompact[u][i] + ' ' + bodyCompact[u][i + 1] == "love you" \
                or bodyCompact[u][i] + ' ' + bodyCompact[u][i + 1] == "luv you":
            noIloveU[u] += 1
        if bodyCompact[u][i] + ' ' + bodyCompact[u][i + 1] == "hate you":
            noHateU[u] += 1
    print(users[u] + " used the word 'love' " + str(noLove[u]) + " times, and said 'I love you' "+str(noIloveU[u]) +
          " times, but also 'I hate you' "+str(noHateU[u])+" times.")

# 0000000000000000000000000000000000000000000000000000000000000000000000
# TIME ANALYSIS
# find unique dates with messages
Duniq=['initialize']
for n in dates:
    Duniq.append(n) if Duniq[-1]!=n else ''
Duniq.pop(0)

#Dates for user
datesUser=[]
for u in range(0,len(users)):
    tmp = [dates[n] for n in range(0, len(dates)) if ind[u][n]]
    datesUser.append(tmp)

# a list containing all uniques days of the dates from
d1 = date(int(dates[0][-4:10]),int(dates[0][3:5]),int(dates[0][0:2]))
d2 = date(int(dates[-1][-4:10]),int(dates[-1][3:5]),int(dates[-1][0:2]))
dd = [d1 + timedelta(days=x) for x in range((d2-d1).days + 1)]
noMsgPerDay = []
for u in range(0, len(users)):
    tmp = []
    for d in dd:
        tmp.append(dates.count(d.strftime('%d/%m/%Y')))
    noMsgPerDay.append(tmp)

# WHAT DAYS OF THE WEEK DO WE MESSAGE LESS or MORE?
# subplot(1) LESS
#  extract days with 0 messages
week=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
plt.figure(figsize=(10, 9))
f, ax1 = plt.subplots(2, sharex=True)
cols = [[.5,.5,.8,.3],[.5,.6,.1,.3],'b','y','r','g']
ddaysCount = []
for u in range(0, len(users)):
    grouped_L = [[k, sum(1 for i in g)] for k,g in groupby(noMsgPerDay[u])] #sum occurrences of consecutive numbers
    count_noMsg = [grouped_L[n][1] for n in range(0,len(grouped_L)) if grouped_L[n][0] is 0] # only looks at zeros
    ddays = [dd[n].strftime('%a') for n in range(0,len(noMsgPerDay[u])) if noMsgPerDay[u][n] is 0]
    ddaysCount.append(OrderedDict((w, ddays.count(w)) for w in week)) #ddaysCount = {w:ddays.count(w) for w in week}
    # plot
    ax1[0].bar(range(len(ddaysCount[u])), ddaysCount[u].values(), color=cols[u],  width=.5, bottom=ddaysCount[u].values()
    if u > 0 else [0]*7)
    plt.xticks(range(len(ddaysCount[u])), ddaysCount[u].keys())
plt.ylabel('Occurrence'); plt.title('Number of times there were ZERO :( messages on a specific day of the week')
plt.legend(users)
# subplot(2) MORE
#  WHAT DAYS OF THE WEEK DO WE MESSAGE MORE?
noMsgPerWeekday=[]
for u in range(0, len(users)):
    ddays = [[dd[n].strftime('%a'),noMsgPerDay[u][n]] for n in range(0,len(noMsgPerDay[u])) if noMsgPerDay[u][n] > 0]
    ddaysCount = OrderedDict((w, 0) for w in week)
    for d in ddays:
        ddaysCount[d[0]]=ddaysCount[d[0]]+d[1]
    noMsgPerWeekday.append(ddaysCount)
    ax1[1].bar(range(len(noMsgPerWeekday[u])), noMsgPerWeekday[u].values(), color=cols[u],
               width=.5,bottom=noMsgPerWeekday[u].values() if u > 0 else [0] * 7)
    plt.xticks(range(len(noMsgPerWeekday[u])), noMsgPerWeekday[u].keys())
plt.ylabel('Occurrence'); plt.title('Messaging during the week')
plt.show()

# WHAT HOUR OF THE DAY WE MESSAGE MORE?
hours=['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
# plt.figure(figsize=(10, 9))
ax2 = plt.subplot(111)
noMsgPerHour=[]
width=.3
for u in range(0, len(users)):
    tmp = []
    for t in hours:
        tmp.append(sum([tm[n][:2].count(t) for n in range(0,len(tm)) if ind[u][n]]))
    noMsgPerHour.append(tmp)
    ax2.bar(u*width+np.arange(0,len(noMsgPerHour[u])), noMsgPerHour[u], color=cols[u], width=width)
    plt.xticks(np.arange(0,len(noMsgPerHour[u])), hours)
plt.ylabel('Occurrence'); plt.xlabel('Hour of the day'); plt.title('Messaging during the day')
plt.legend(users)
plt.show()

## PLOT Message Distribution over period
plt.figure(figsize=(12, 9))
ax = plt.subplot(111)
ax.spines["top"].set_visible(False);ax.spines["right"].set_visible(False)
ax.get_xaxis().tick_bottom();ax.get_yaxis().tick_left()
for u in range(0,len(users)):
    xdata = range(0,len(dd))
    ydata1 = noMsgPerDay[u-1] if u>0 else [0]*len(dd)
    ydata2 = [sum(x) for x in zip(noMsgPerDay[u], noMsgPerDay[u-1])] if u>0 else noMsgPerDay[u]
    l = ax.fill_between(xdata,  ydata1, ydata2, facecolor=cols[u], alpha=0.5)
    # change the fill color, edge color and thickness
    # l.set_facecolors([[.5,.5,.8,.3]])
    l.set_edgecolors([[0, 0, .5, .3]])
    l.set_linewidths([.1])
ax.set_xlabel('Day posting', fontsize=16)
ax.set_ylabel('Number of messages', fontsize=16)
ax.set_title('Message Distribution', fontsize=18)
# set the limits
ax.set_xlim(0, len(dd))
ax.set_ylim(0, max(ydata2) + 5)
# add more ticks
ax.set_xticks(range(0,len(dd),30))
# remove tick marks
ax.xaxis.set_tick_params(size=0)
ax.yaxis.set_tick_params(size=0)
# change the color of the top and right spines to opaque gray
ax.spines['right'].set_color((1,1,1))
ax.spines['top'].set_color((1,1,1))
# tweak the axis labels
xlab = ax.xaxis.get_label()
ylab = ax.yaxis.get_label()
xlab.set_style('italic')
xlab.set_size(10)
ylab.set_style('italic')
ylab.set_size(10)
# tweak the title
ttl = ax.title
ttl.set_weight('bold')
