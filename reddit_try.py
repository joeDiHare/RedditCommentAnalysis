import numpy as np
import sqlite3
import pandas as pd
import time
import pickle

startt = time.time()

conn = sqlite3.connect("C:/Users/Stefano/PycharmProjects/redditMay2015/reddit.sqlite")
c = conn.cursor()

TRG=['faggot', 'poof', 'bum', 'dyke', 'fag', 'gay']
TRG=['gay']
# target = 'Faggot' # poof' 'bum' 'dyke' 'fag'
for target in TRG:
    res = pd.read_sql_query("SELECT score,created_utc "
                            "FROM May2015 "
                            "WHERE LENGTH(body)<555 AND LENGTH(body)>1 "
                            # "AND score>0 "
                            #"AND body LIKE '% Trump %' " # COLLATE utf8_bin
                            "AND body LIKE '%" + target + "%' "
                            "LIMIT 50000",conn)
    print(res)

    # Saving the objects:
    with open('saved_'+target, 'wb') as f:  # Python 3: open(..., 'wb')
        pickle.dump(res, f)

# # Getting back the objects:
# with open('saved','rb') as f:  # Python 3: open(..., 'rb')
#     res = pickle.load(f)

endt = time.time()
print((endt - startt)/60)

conn.close()


# text_file1 = open("OutputTweet" + target + ".txt", "w")
# text_file2 = open("OutputTimes" + target + ".txt", "w")
# for item in res.values:
#     print("XXX: "+item[0])
#     text_file1.write("%s " % item[0])
#     text_file2.write("%s " % item[1])
# text_file1.close()
# text_file2.close()