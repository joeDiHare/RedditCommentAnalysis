# Look at average score for swearwords, slang and control

# import time, csv, re, random
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cross_validation import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.metrics import accuracy_score
# from scipy.sparse import csr_matrix
import sqlite3
import pandas as pd
import pickle
import time


# Parameters
# srs_lmt = 10000#30100  # serious posts to train on
# sar_lmt = 100#30100  # sarcastic posts to train on
# top_k = 30  # features to display
# num_ex = 20  # examples displayed per feature
# min_ex = 0  # shortest example displayed
# max_ex = 120  # longest example displayed
# ovr_ex = True  # display longer/shorter examples if we run out


# import csv
# # script to read-in list of words
# filename = 'short_acronyms.txt';#filename = 'slang.txt';filename = 'swearwords.txt';
# results = []
# with open(filename, newline='') as inputfile:
#     for row in csv.reader(inputfile):
#         results.append(row[0])
# acron, along = [], []
# for item in results:
#     tmp = item.split(' ')
#     print(tmp)
#     acron.append(tmp[0])
#     along.append(' '.join(tmp[1:]).strip())
# slangs=['unreal', 'props', 'kudos', 'bottom line', 'dig', 'ace', 'all right?', 'full of beans', 'blatant', 'pear shaped', 'piece of cake', 'blimey', 'botch', 'cheers', 'smashing', 'chin wag', 'chuffed', 'cram', 'nice one', 'crikey', 'dear', 'faff', 'do', 'flog', 'fortnight', 'gobsmacked', 'splash out', 'grub ', 'nosh', 'bee’s knees', 'gutted', 'peanuts', 'haggle', 'jolly', 'throw a spanner in the works', 'kip', 'wind up', 'mate', 'not my cup of tea', 'porkies', 'row', 'donkey’s years', 'easy peasy', 'sorted', 'strop', 'cheerio', 'wangle', 'blinding', 'wonky', 'zonked', 'dodgy', 'leg it']
# swords=['shit', 'fuck', 'damn', 'bitch', 'crap', 'piss', 'dick', 'darn', 'pussy', 'cock', 'fag', 'asshole', 'bastard', 'slut', 'douche']
#  Script below to create queries
# i = 1
# for word in slangs:
#     if i == 1:
#         whereClause = " body LIKE '%" +word + "%'"
#     else:
#         whereClause += " OR body LIKE '%" +word + "%'"
#     i += 1

sar_lmt = 1000
startt = time.time()
slangs_query=" body LIKE '%unreal%' OR body LIKE '%props%' OR body LIKE '%kudos%' OR body LIKE '%bottom line%' OR body LIKE '%dig%' OR body LIKE '%ace%' OR body LIKE '%all right?%' OR body LIKE '%full of beans%' OR body LIKE '%blatant%' OR body LIKE '%pear shaped%' OR body LIKE '%piece of cake%' OR body LIKE '%blimey%' OR body LIKE '%botch%' OR body LIKE '%cheers%' OR body LIKE '%smashing%' OR body LIKE '%chin wag%' OR body LIKE '%chuffed%' OR body LIKE '%cram%' OR body LIKE '%nice one%' OR body LIKE '%crikey%' OR body LIKE '%dear%' OR body LIKE '%faff%' OR body LIKE '%do%' OR body LIKE '%flog%' OR body LIKE '%fortnight%' OR body LIKE '%gobsmacked%' OR body LIKE '%splash out%' OR body LIKE '%grub %' OR body LIKE '%nosh%' OR body LIKE '%bee’s knees%' OR body LIKE '%gutted%' OR body LIKE '%peanuts%' OR body LIKE '%haggle%' OR body LIKE '%jolly%' OR body LIKE '%throw a spanner in the works%' OR body LIKE '%kip%' OR body LIKE '%wind up%' OR body LIKE '%mate%' OR body LIKE '%not my cup of tea%' OR body LIKE '%porkies%' OR body LIKE '%row%' OR body LIKE '%donkey’s years%' OR body LIKE '%easy peasy%' OR body LIKE '%sorted%' OR body LIKE '%strop%' OR body LIKE '%cheerio%' OR body LIKE '%wangle%' OR body LIKE '%blinding%' OR body LIKE '%wonky%' OR body LIKE '%zonked%' OR body LIKE '%dodgy%' OR body LIKE '%leg it%'"
swords_query=" body LIKE '%shit%' OR body LIKE '%fuck%' OR body LIKE '%damn%' OR body LIKE '%bitch%' OR body LIKE '%crap%' OR body LIKE '%piss%' OR body LIKE '%dick%' OR body LIKE '%darn%' OR body LIKE '%pussy%' OR body LIKE '%cock%' OR body LIKE '%fag%' OR body LIKE '%asshole%' OR body LIKE '%bastard%' OR body LIKE '%slut%' OR body LIKE '%douche%'"

conn = sqlite3.connect("C:/Users/Stefano/Documents/reddit.sqlite")
c = conn.cursor()
print('Querying the DB:')
db_slang_query = pd.read_sql_query("""SELECT body, score FROM May2015\
                                   WHERE """+ slangs_query + """ ORDER BY RANDOM() LIMIT """ + str(sar_lmt), conn)
print('Finished with Slang words...')
db_swear_query = pd.read_sql_query("""SELECT body, score FROM May2015\
                                   WHERE """+ swords_query + """ ORDER BY RANDOM() LIMIT """ + str(sar_lmt), conn)
print('Finished with Swear words...')
db_contr_query = pd.read_sql_query("""SELECT body, score FROM May2015\
                                   ORDER BY RANDOM() LIMIT """ + str(sar_lmt), conn)
print('Finished with Control words...')
conn.close()

print('Estimate average score per category:')
res1, res2, res3 = 0, 0 ,0
for n in (db_slang_query.values):
    res1=res1+n[1]
for n in (db_swear_query.values):
    res2=res2+n[1]
for n in (db_contr_query.values):
    res3=res3+n[1]
slang_score = res1 / len(db_slang_query.values)
swear_score = res2 / len(db_swear_query.values)
contr_score = res3 / len(db_contr_query.values)
print("Swear: " + str(swear_score) + "\nSlang: " + str(slang_score)+ "\nControl: " + str(contr_score))

with open('saved_slang', 'wb') as f:  # Python 3: open(..., 'wb')
    pickle.dump(db_slang_query, f)
with open('saved_swear', 'wb') as f:  # Python 3: open(..., 'wb')
    pickle.dump(db_swear_query, f)
with open('saved_contr', 'wb') as f:  # Python 3: open(..., 'wb')
    pickle.dump(db_contr_query, f)

endt = time.time()
print("(Elapsed time:" + str(round((endt - startt)/60,1)) + " min.")
