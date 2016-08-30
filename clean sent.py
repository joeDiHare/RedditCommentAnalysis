# import csv
#
# results = []
# with open('reddittrain.txt', newline='') as inputfile:
#     for row in csv.reader(inputfile):
#         results.append(row)
import markov
import re
import sys
import random
from local_settings_example import *
order = ORDER
file = "OutputTweet.txt"
print(">>> Generating from {0}".format(file))
string_list = open(file).readlines()
for item in string_list:
  #  print(item)
    source_tweets = item.split(",")
#print(source_tweets)
mine = markov.MarkovChainer(order)
for tweet in source_tweets:
    if re.search('([\.\!\?\"\']$)', tweet):
        pass
    else:
        tweet += "."
    mine.add_text(tweet)

for x in range(0, 10):
    ebook_tweet = mine.generate_sentence()

# randomly drop the last word, as Horse_ebooks appears to do.
if random.randint(0, 4) == 0 and re.search(r'(in|to|from|for|with|by|our|of|your|around|under|beyond)\s\w+$',
                                           ebook_tweet) != None:
    print("Losing last word randomly")
    ebook_tweet = re.sub(r'\s\w+.$', '', ebook_tweet)
    print(ebook_tweet)

# if a tweet is very short, this will randomly add a second sentence to it.
if ebook_tweet != None and len(ebook_tweet) < 40:
    rando = random.randint(0, 10)
    if rando == 0 or rando == 7:
        print("Short tweet: Adding another sentence randomly")
        newer_tweet = mine.generate_sentence()
        if newer_tweet != None:
            ebook_tweet += " " + mine.generate_sentence()
        else:
            ebook_tweet = ebook_tweet
    elif rando == 1:
        # say something crazy/prophetic in all caps
        print("ALL THE THINGS")
        ebook_tweet = ebook_tweet.upper()

# throw out tweets that match anything from the source account.
if ebook_tweet != None and len(ebook_tweet) < 110:
    for tweet in source_tweets:
        if ebook_tweet[:-1] not in tweet:
            continue
        else:
            print("TOO SIMILAR: " + ebook_tweet)
            sys.exit()

print(ebook_tweet)


