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
from matplotlib.backends.backend_pdf import PdfPages
from wordcloud import WordCloud
import pdfkit
from jinja2 import Template, Environment, FileSystemLoader

# script to read-in list of words
filename = "/Users/joeDiHare/Documents/chat.txt"#"C:/Users/Stefano/Documents/chat.txt"
MsgErr1 = 'Messages you send to this chat and calls are now secured with end-to-end encryption. Tap for more info.'
MsgErr2 = '<Media omitted>'
print("Reading chat conversation & first data validation... ", end="")
results, mediaSender, mediaCaption = [], [], []
with open(filename, newline='',encoding='UTF8') as inputfile:
    for row in csv.reader(inputfile):
        if row!=[]: #ignore empty lines
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

print("Create conversation lists... ", end="")
# if the previous message is within LONG_BREAK_CON seconds and it is from the same sender, combine them in the same conversation
ConvBody = [body[0]]; ConvSender = [sender[0]]; ConvDates = [dates[0]]; ConvDatesLong = [datesLong[0]]# initialise
ConvMessage = [message[0]]; ConvTime = [tm[0]]; ConvTimeEnd = [tm[0]]
Conversations, LM = [],[]; RT= [['user', -1]]; flag_new_conv=False
bodylast = '(' + sender[0] + ') ' + body[0]
LONG_BREAK_CONV = 30 * 60 # time constant to consider a message as belonging to a new conversation
for n in range(1,len(tm)):
    if (datetime.datetime.strptime(tm[n], "%H:%M") - datetime.datetime.strptime(tm[n-1], "%H:%M")).seconds < LONG_BREAK_CONV \
    and sender[n]==sender[n-1]: # same sender, add to last message
        ConvBody[-1] = ConvBody[-1] + '. ' + body[n]
        ConvTimeEnd[-1] = tm[n]
        bodylast = bodylast + '. ' + body[n] if bodylast!='' else  ' ('+sender[n]+') '+body[n]
    else: # break and start new msg in conversation
        ConvBody.append(body[n])
        ConvSender.append(sender[n])
        ConvTimeEnd.append(tm[n])
        ConvTime.append(tm[n])
        ConvDates.append(dates[n])
        ConvMessage.append(message[n])
        ConvDatesLong.append(datesLong[n])
        bodylast = bodylast + ' (' + sender[n] + ') ' +ConvBody[-1]
        if flag_new_conv:
            RT.append([sender[n],
                        round((datetime.datetime.strptime(tm[n],"%H:%M")-datetime.datetime.strptime(ConvTimeEnd[-2],"%H:%M")).seconds/60)])
            flag_new_conv = False
        if (datetime.datetime.strptime(tm[n], "%H:%M") - datetime.datetime.strptime(tm[n-1], "%H:%M")).seconds >= LONG_BREAK_CONV:
            Conversations.append(bodylast)
            bodylast=''
            flag_new_conv = True
print('[done]')


print('\n\n~~~~~~~~~~~~~~~~~~~ DATA ANALYSIS ~~~~~~~~~~~~~~~~~~~~\n')
do_stages = [1,2,3]
OutputPdf = PdfPages(filename='outputWA.pdf')
users = list(set(sender))
print('Conversations between '+str(len(users))+' users:' + str(users))

# Find first mover (FM) occurrences
users_search = "|".join(users)
FM = []
for item in Conversations:
    FM.append(re.search(users_search, item).group())
FM_counts = Counter(FM)
for user in users:
    print(user + " started a conversation " + str(round(100*FM_counts[user]/sum(Counter(FM_counts).values()))) + "% of the times.")

# Find users' reaction times to initial message in conversation
UsersRT, UsersRTall = [], []
for user in users:
    tmp=[]
    for item in RT:
        if item[0]==user:
            tmp.append(item[1])
    UsersRTall.append(np.asarray(tmp))
    UsersRT.append(sum(tmp)/len(tmp))
    print('The median reaction time for '+user+' is '+str(np.median(np.asarray(tmp)))+' minutes')
# plot histogram of reaction times
# a = np.hstack(UsersRTall[0])
# fig1 = plt.figure(figsize=(6,4))
# plt.hist(a, bins='auto')  # plt.hist passes it's arguments to np.histogram
# plt.show()
# fig1.savefig('RT.png')

ind=[]
for u in range(0,len(users)):
    indt=[]
    for n in ConvSender:
        indt.append(True) if n==users[u] else indt.append(False)
    ind.append(indt)

# WHO MESSAGED THE MOST?
if 1 in do_stages:
    message_counts = Counter(ConvSender)
    fig2a = plt.figure(0, figsize=(6,6))
    ax = plt.subplot(111)
    df = pandas.DataFrame.from_dict(message_counts, orient='index')
    df.plot.pie(subplots=True, ax=ax, rot=90)
    plt.title("Who Messaged the Most?")
    plt.xlabel("number of messages")
    ax.legend().set_visible(False)
    fig2a.savefig('WhoMessagedTheMost.png')
    OutputPdf.savefig(fig2a)
    plt.close()

# WHO SENT MORE MEDIA?
if 2 in do_stages:
    mediaSender_counts = Counter(mediaSender)
    fig2b = plt.figure(figsize=(6,4))
    ax = plt.subplot(111)
    df2 = pandas.DataFrame.from_dict(mediaSender_counts, orient='index')
    df2.plot(kind='bar', ax=ax, rot=0, color=['g','k'])
    plt.title("Who sent more media messages?")
    plt.xlabel("number of messages")
    ax.legend().set_visible(False)
    fig2b.savefig('WhoSentMoreMedia.png')
    OutputPdf.savefig(fig2b)
    plt.close()

    for u in users:
        print(u+' sent ' +str(message_counts[u])+' messages and '+str(mediaSender_counts[u])+' images/videos.')
        # OutputPdf.attach_note(text="hhhhhhhhhhhhhhh  <><hshshshs/b>   ksksksksks sjsjsnfskdb skbdskjf  a")

# MOST COMMON 20 WORDS PER USER
if 3 in do_stages:
    # script to read-in strop words
    filename = 'stopwords.txt'; stopwords = []
    with open(filename, newline='',encoding='UTF8') as inputfile:
        for row in csv.reader(inputfile):
            stopwords.append(row[0].lower())
    NoWrdsUsr, bodyUsr, bodyCompact, count = [], [], [], []
    punctuation = set(string.punctuation)
    for u in range(0,len(users)):
        bodyUsr.append([body[i] for i, x in enumerate(ind[u]) if x])
        NoWrdsUsr.append(len(''.join([body[i] for i, x in enumerate(ind[u]) if x]).split(' ')))

        print('\nWord frequency Analysis for user: ' + users[u] )
        count.append(Counter(word for word in ' '.join(bodyUsr[u]).lower().split() if word not in stopwords).most_common(20))
        print(count[u])
        s = ''.join(ch for ch in ' '.join(bodyUsr[u]).lower() if ch not in punctuation)
        bodyCompact.append(s.split()) #compact version of body, all in one string

        #Wordles
        text_user = ' '.join(bodyUsr[u]).lower()
        wordcloud = WordCloud(max_font_size=40, relative_scaling=.5).generate(text_user)
        fig3 = plt.figure(figsize=(6,2))
        plt.imshow(wordcloud)
        plt.axis("off")
        fig3.savefig(users[u] + '_wordle.png')
        OutputPdf.savefig(fig3)
        plt.close()

# HOW MANY JINX?
if 4 in do_stages:
    jinxNo = []
    for u in range(0,len(users)):
        jinxNo.append(len(difflib.get_close_matches('jinx', ' '.join(bodyUsr[u]).lower().split(), n=100, cutoff=.8)))
        print(users[u] + ' jinxed ' + str(jinxNo[u]) + ' times.')

# HOW MANY 'LOVE' or 'I LOVE YOU'?
if 5 in do_stages:
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

# TIME ANALYSIS
# find unique dates with messages
Duniq=['initialize']
for n in ConvDates:
    Duniq.append(n) if Duniq[-1]!=n else ''
Duniq.pop(0)

#Dates for user
datesUser=[]
for u in range(0,len(users)):
    tmp = [ConvDates[n] for n in range(0, len(ConvDates)) if ind[u][n]]
    datesUser.append(tmp)

# a list containing all uniques days of the dates from
d1 = date(int(ConvDates[0][-4:10]),int(ConvDates[0][3:5]),int(ConvDates[0][0:2]))
d2 = date(int(ConvDates[-1][-4:10]),int(ConvDates[-1][3:5]),int(ConvDates[-1][0:2]))
dd = [d1 + timedelta(days=x) for x in range((d2-d1).days + 1)]
noMsgPerDay = []
for u in range(0, len(users)):
    tmp = []
    for d in dd:
        tmp.append(ConvDates.count(d.strftime('%d/%m/%Y')))
    noMsgPerDay.append(tmp)

# WHAT DAYS OF THE WEEK DO WE MESSAGE LESS or MORE?
if 6 in do_stages:
    # subplot(1) LESS
    #  extract days with 0 messages
    week=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    fig4, ax1 = plt.subplots(2, figsize=(6,6), sharex=True)
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
    fig4.savefig('weekdays.png')
    OutputPdf.savefig(fig4)
    plt.close()

# WHAT HOUR OF THE DAY WE MESSAGE MORE?
hours=['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
if 7 in do_stages:
    fig5b = plt.figure(figsize=(6, 6))
    ax2 = plt.subplot(111)
    noMsgPerHour=[]
    width=.3
    for u in range(0, len(users)):
        tmp = []
        for t in hours:
            tmp.append(sum([ConvTime[n][:2].count(t) for n in range(0,len(ConvTime)) if ind[u][n]]))
        noMsgPerHour.append(tmp)
        ax2.bar(u*width+np.arange(0,len(noMsgPerHour[u])), noMsgPerHour[u], color=cols[u], width=width)
        plt.xticks(np.arange(0,len(noMsgPerHour[u])), hours)
    plt.ylabel('Occurrence'); plt.xlabel('Hour of the day'); plt.title('Messaging during the day')
    plt.legend(users)
    fig5b.savefig('dayshour.png')
    OutputPdf.savefig(fig5b)
    plt.close()

## PLOT Message Distribution over period
if 8 in do_stages:
    fig6 = plt.figure(figsize=(6, 5))
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
    fig6.savefig('message distribution.png')
    OutputPdf.savefig(fig6)
    plt.close()

# Time analysis over months


OutputPdf.close()

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')
output_from_parsed_template = template.render(no_users=len(users), users=users,a_variable='hay')

# to save the results
with open("OutputAnalysis.html", "w") as fh:
    fh.write(output_from_parsed_template)

with open('OutputAnalysis.html') as f:
    pdfkit.from_file(f, 'out.pdf')

# To do:
# Module to: Check how words are stretched as in informal conversations
# Module to: Find anniversaries by frequencies of "happy birthday"
# Module to: Swear words
# Module to: Implement detection block for US/EU pattern
# Module to: Add more stopwords
# Module to: