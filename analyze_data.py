import pickle
import matplotlib.pyplot as plt
import numpy as np

acron=['FYI', 'ETA', 'ASAP','AKA', 'ATM', 'TBA', 'RIP', 'PS', 'ESL', 'DIY', 'AFK', 'BRB', 'BBIAB', 'BBL', 'TTFN', 'BBS', 'BTW', 'KISS', 'KIT', 'EG', 'NYOB', 'OMG', 'PM', 'POS', 'TTYL', 'LTNS', 'SSDD', 'IDK', 'WTF','BS','LMK','LOL','ROFL','YOLO']
along=['For Your Information', 'Estimated Time of Arrival', 'As soon as possible','Also Known As', 'At the moment', 'To Be Announced', 'Rest in Peace', 'Post Script', 'English as a Second Language', 'Do it Yourself', 'Away From Keyboard', 'Be Right Back', 'Be Back In A Bit', 'Be Back Later', 'Ta Ta For Now', 'Be Back Soon', 'By The Way', 'Keep It Simple Stupid', 'Keep In Touch', 'Evil Grin', 'None of Your Business', 'Oh My God', 'Private Message', 'Parents Over Shoulder', 'Talk To You Later', 'Long Time No See', 'Same Shit Different Day', "I dont know", 'What the fuck','Bullshit', 'let me know', 'laughing out loud', 'Rolling On the Floor Laughing','you only live once']

with open('saved_acron_scores', 'rb') as f:  # Python 3: open(..., 'rb')
   Sacron = pickle.load(f)
with open('saved_along_scores', 'rb') as f:  # Python 3: open(..., 'rb')
   Along = pickle.load(f)

plt.bar(range(len(Along)), Along, align="center",width=1)
plt.xticks(range(len(Along)), list(Along))#,rotation='vertical'
plt.xlabel('Days in May 2015')
plt.ylabel('Mentions for ')
ymax = max(Along) + 1
plt.ylim(0, ymax)
plt.show()

