# -*- coding: utf-8 -*-
"""Copy of StudentCopy_Anti_Refugee_Section1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10JF5AQjKverQ5TJZJyWzRW8YstHchIUY

# Identifying Anti-Refugee Tweets

## Background

**Sentiment Analysis**<br>
It is the process of using the computer to identify and categorize opinions expressed in a piece of text in order to determine whether the writer's attitude towards the given topic is positive or negative (or sometimes even neutral). It can also reveal their emotional state, and the intended effect of their words.

**Why conduct sentiment analysis ?**<br>
The answer depends on where the tool is applied! In business, it can be used to predict the sentiment of the consumers in a market, thereby aiding the growth of the company. In politics, the sentiments of the voters can be used to determine the most appropriate strategy. By listening to and analysing comments on Facebook and Twitter, local government departments can gauge public sentiment and use the results to improve services they provide to the public. Universities can use sentiment analysis to analyze student feedback and improve their curriculum. These are a few of the many uses of sentiment analysis.

**What is Anti-Refugee Tweet Classification**<br>
Anti-refugee tweet classification, the topic that we would be covering in the coming few days, is classifying a given tweet as pro-refugee or anti-refugee. An example to illustrate the definition:

> *anti-refugee tweet*: 'muslim refugee charged with beating a woman'<br>
> *pro-refugee tweet*: 'refugee hotspots in italy and greece not yet adequate'

As you can guess from the above example, an anti-refugee tweet would have negative words, and would convey negative sentiments towards the refugees, sentiments that would potray the refugee in a negative light, while the converse is true for pro-refugee tweets. **Understanding anti-refugee sentiment is the first step in addressing it.** This project will allow us to use AI models to do so.

# Milestone 1: Exploring our data
"""

#@title Run this to import all the necessary packages. This will take a few minutes! { display-mode: "form" }
import json
import tweepy
from sklearn.metrics import accuracy_score
from datetime import datetime, timedelta
import re
import numpy as np
import random
import json
import math
from collections import Counter
import matplotlib.pyplot as plt
import os
import sys
import pandas

import nltk
nltk.download('punkt', quiet=True)
from nltk.tokenize import TweetTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
nltk.download('stopwords' ,quiet=True)
from sklearn.metrics import accuracy_score

import warnings
warnings.filterwarnings('ignore')

# from google.colab import drive
# drive.mount('/content/drive/')

import gdown
import zipfile
import shutil

gdown.download('https://drive.google.com/uc?id=1ifYLZ-19ZyjjRUICe4PDRmZFAkyL73d0','./source_data.zip',True)
my_zip = zipfile.ZipFile('./source_data.zip', mode = 'r')
my_zip.extractall()
basepath = './drive/Team Drives/Inspirit Curriculum/Inspirit AI Program/Working Materials/Tejit\'s Material/Anti-Refugee Sentiment Analysis'
try: 
  shutil.move('./Anti-Refugee Sentiment Analysis/', basepath)
except shutil.Error:
  pass


module_folder = './drive/Team Drives/Inspirit Curriculum/Inspirit AI Program/Working Materials/Tejit\'s Material/Anti-Refugee Sentiment Analysis/'
if module_folder not in sys.path: sys.path.append(module_folder)
import lib
from lib import Tweet
from lib import Tweet_counts

# # If the above doesn't work, then upload the file!
# from google.colab import files
# src = list(files.upload().values())[0]
# open('lib.py','wb').write(src)
# import lib
# from lib import Tweet
# from lib import Tweet_counts

from lib import *

"""### Understanding the structure of a tweet

Tweets are composed of:
* Hashtags: Keywords that start with the '#' symbol
* Mentions: Referencing another user/person with '@'
* Everything else: Anything that isn't a hashtag or mention!

We've made a convenient interface for processing our tweets, which we call the `Tweet` class. Let's try out the `Tweet` class!
"""

my_tweet = Tweet('these are #tags and this is a @mention. hey #wait there\'s another @one here too','true') 
# takes in text and true or false - don't worry about true or false right now!

# check out the hashtags!
my_tweet.hashtags

# check out the mentions!
my_tweet.mentions

# check out the tweet text!
my_tweet.tokenList

"""## Activity 1. Examining our dataset

Let's a take at our prebuilt database of tweets extracted from twitter! It is in a folder called Data and is stored in a file called data.json.
"""

file = open(basepath+'/Data/data.json','r')
data = json.load(file)

"""Our `data` is a list of tweets that are classified as either TRUE (anti-refugee) or FALSE (pro-refugee). 

How many tweets do we have?
"""

len(data)

"""What does each data point look like?"""

data[50]

"""Each data point is a dictionary (in particular, it is a json object) with two keys:

* classification: which is the category of the tweet 
* tweet: which is the tweet text

We can access the value in each dictionary element by using the individual key associated with each.
"""

# use the 'classification' key to see the sentiment of a tweet
data[0]['classification']

"""We need to find an efficient way to split our data into two different groups. One way to do this would be to write a for loop to go through every tweet in the list. But a better way would be to use a list comprehension.

### Exercise (Coding): List Comprehensions

Python provides a handy tool called *list comprehension*. This can allow us to perform the work of a `for` loop and an `if-else` statment in a single line of code. List comprehensions come in handy when parsing through large amouts of data.

The cell below reminds us what a `for` loop in Python looks like.
"""

# define our original list
original_list = [1,2,9,10,11]

# initialize a new list
new_list = []

# add elements to it!
for i in original_list:
  new_list.append(i+2)
  
print(new_list)

"""A list comprehension can compress this into one line like:"""

new_list = [i+2 for i in original_list]
print(new_list)

"""We can even add conditionals to this! For example..."""

new_list = [i for i in original_list if i > 3]
print(new_list)

"""Here, we found all elements in our original list that were greater than 3.

**Now, you try!** 

Use a list comprehension to get a list of all elements in `original_list` that are less than 10!
"""

### YOUR CODE HERE
new_list = [i for i in original_list if i < 10]
print(new_list)
### END CODE

"""Now that we know how list comprehensions and dictionaries work, we can try using them to split our data into two separate lists. Remember, a list comprehension is essentially a `for` loop and an `if` condition in a single line."""

### YOUR CODE HERE
pro = [d['tweet'] for d in data if d['classification'].lower() == 'false']
anti = [d['tweet'] for d in data if d['classification'].lower() == 'true']

for x in data:
  print(x['classification'].lower())
### END CODE

"""How many tweets do we have of each class?"""

# how many pro refugee tweets? 
len(pro)

# how many anti refugee tweets?
len(anti)

pro[0]

"""# Milestone 2: Handmade classifiers

We'll actually split our data into lists of `Tweet` objects so we can access the hashtags and mentions easily. 

Let's now split our data into a full data set (`tweet_data`).
"""

#@title Formatting our data! {display-mode: 'form'}
tweet_data   = [Tweet(t['tweet'], t['classification']) for t in data]
pro_tweets     = [Tweet(t['tweet'], t['classification']) for t in data if t['classification'].lower()=='false']
anti_tweets    = [Tweet(t['tweet'], t['classification']) for t in data if t['classification'].lower()=='true']

print(pro_tweets[0])
print(pro_tweets[0].mentions)

len(pro_tweets)

"""## Activity 2a. Looking at pro vs. anti tweets

### Exercise (Discussion)

We reformated our data into lists of 'tweets'. Let's now look at a few pro and anti refugee tweets, their original text, hashtags, and mentions.
"""

# display 5 pro refugee tweets!
for i in range(5):
  this_tweet = pro_tweets[i]
  print('---Original tweet text---')
  print(this_tweet.original_tweet_text)

  print('---Hashtags---')
  print(this_tweet.hashtags)

  print('---Mentions---')
  print(this_tweet.mentions)
  
  print('\n')

# display 5 anti-refugee tweets!
for i in range(5):
  this_tweet = anti_tweets[i]
  print('---Original text---')
  print(this_tweet.original_tweet_text)

  print('---Hashtags---')
  print(this_tweet.hashtags)

  print('---Mentions---')
  print(this_tweet.mentions)
  
  print('\n')

"""**In your group, discuss:** 
Does a tweet always have a hashtag or mention?

## Activity 2b. Handmade Rules for Classification

Rule based classification uses certain rules, defined by the user, to classify tweets to the given categories. These rules are generally rigid and hence a rule based classifier cannot assign a probability to a tweet but can only assign a category to it.

An example of a rule based classifier is:

> If the word 'potato' or 'spinach' occurs in a tweet, then classify the tweet as vegetable, otherwise classify it as a fruit!

Oftentimes, due to the rigidity and simplicity of the rule based classifier, the classification is faulty. Hence, do not expect a high accuracy from this classifier.

Before we begin making our rule based classifier, let us visualize the data. Visualization helps us understand properties of the data which will, in turn, help us with the rule based classifier.

### Exercise (Discussion): Figuring out the rules for our tweets

Rule based classification, as the name suggests, is based on a given set of rules. In case of tweets, these rules can be a lot of things. Let us look at the data to figure out the things that we can use for rules.

We know that we have the following unique things in tweets:

1. Hashtags
2. Mentions
3. Other words

**Question:** You think hashtags can be used to classify tweets? Give 5 examples of hashtags that can tell pro or anti refugee tweets apart.
"""

# display the first 10 pro hashtags

pro_hashtags = []

for tweet in pro_tweets:
  if len(tweet.hashtags) > 0: # we use this condition because some tweets might not have hashtags
    pro_hashtags.append(tweet.hashtags)
  if len(pro_hashtags) == 10:
    break


pro_hashtags

# display the first 10 anti hashtags
### YOUR CODE HERE
anti_hashtags = []

for tweet in anti_tweets:
  if len(tweet.hashtags) > 0: # we use this condition because some tweets might not have hashtags
    anti_hashtags.append(tweet.hashtags)
  if len(anti_hashtags) == 10:
    break


anti_hashtags    
  

### END CODE

"""**Question:** Can mentions (tags - '@') be used to classify tweets? Give 5 examples of mentions that can classify pro or anti tweets."""

# display the first 10 pro mentions

pro_mentions = []


for tweet in pro_tweets:
  if len(tweet.mentions) > 0:
    pro_mentions.append(tweet.mentions)
  if len(pro_mentions) == 10:
    break


pro_mentions

# display the first 10 anti mentions
### YOUR CODE HERE

anti_mentions = []


for tweet in anti_tweets:
  if len(tweet.mentions) > 0:
    anti_mentions.append(tweet.mentions)
  if len(anti_mentions) == 10:
    break


anti_mentions


### END CODE

"""**Question:** You think any other words from a tweet can be used to classify pro or anti refugee sentiment? Give 5 examples of words that can classify pro or anti tweets."""

# display words in the first 10 pro tweets
### YOUR CODE HERE
pro_words = []

for tweet in pro_tweets:
  tokens = [t for t in tweet.tokenList if t not in stopwords.words('english')]
  pro_words.append(tokens)
  if len(pro_words) == 10:
      break  
      
pro_words
### END CODE

# display words in the first 10 anti tweets
### YOUR CODE HERE
anti_words = []

for tweet in anti_tweets:
  tokens = [t for t in tweet.tokenList if t not in stopwords.words('english')]
  anti_words.append(tokens)
  if len(anti_words) == 10:
      break  
      
anti_words
### END CODE

### END CODE

"""The more often a hashtag, mention, or rule comes in one category over another, the better we may expect it to work!

**Play around with the interactive form below to see the count of a given property (i.e. hashtag, mention, or just a word), and how often it shows up in the pro or anti refugee tweets. This may give you some indication of what specific ones might work better to categorize tweets.**
"""

#@title Query { run: "auto", vertical-output: true, display-mode: "form" }

examine_tweet = Tweet_counts(tweet_data) 

prop = 'Hashtags' #@param ["Hashtags", "Mentions", "Word"]
string = 'buildthewall' #@param {type:"string"}

if prop=='Hashtags':
  if string[0]!= '#': string = '#' + string
  print(examine_tweet.query_hashtag(string.lower()))
elif prop=='Mentions':
  if string[0]!='@': string = '@' + string
  print(examine_tweet.query_mentions(string.lower()))
elif prop=='Word':
  print(examine_tweet.query_words(string.lower()))

#@markdown Metions are tags in twitter - @blah, @realdonaldtrump. 
#@markdown <br><br>**Code result**:

"""**When you're happy with your lists, discuss with your instructor, then write your hashtags, mentions, and words in the lists below. These will be the lists you'll be using today to classify the tweets as anti or pro refugee!**"""

pro_hashtags = ['#buildthewall','#']
anti_hashtags = ['#','#']
pro_mentions = ['@realdonaldtrunp','@']
anti_mentions = ['@','@']
pro_words = ['']
anti_words = ['']

#@title Instructor Solution {display-mode:'form'}

# note to instructor: these won't work very well :( 

pro_hashtags = ['#rohingya','#refugeeswelcome','#syria','#southsudan']
anti_hashtags = ['#maga','#boycottchobani','#buildthewall','#muslim']
pro_mentions = ['@appgrefugees','@refugeesintl','@refugeecouncil','@amnestyuk']
anti_mentions = ['@realdonaldtrump','@potus','@youtube','@infowars']
pro_words = ['syrian','children','crisis','education']
anti_words = ['muslim','boycott','don','deport']

"""# Milestone 3: Coding up our classifiers

### Exercise (Coding)

We have three types of information that we get from tweets: hashtags, mentions, and the actual text. As we saw, we can build lists of words that we think indicate something is a pro or anti tweet. Each list gives us a single classifier. For example, a pro hashtag classifier will see if a tweet has hashtags in our `pro_hashtags` and, if it does, it decides that the tweet is `pro refugee`. In this way, we can also build 5 classifiers other classifiers for each of our lists. Each classifier is a decision on the feature information that we care about (i.e. hashtags, mentions, or text), and which category we care to find (pro or anti). 

Let us build a classifier based on anti-refugee features.
"""

def anti_classifier(tweet):
  for hashtag in tweet.hashtags:
    if hashtag in anti_hashtags:
      return True # for pro
  for mention in tweet.mentions:
    if mention in anti_mentions:
      return True # for pro
  for word in tweet.tokenList:
    if word in anti_words:
      return True # for pro    
  return False # if none of the hastags, mentions, or words are in our anti lists, then the tweet does not express anti-refugee sentiment

"""We need to compare our rule-based classifier's predictions with the real data. Since the `classification` value in the original data was a string, we need a helper function to convert those to Boolean values that we can use to compare to our predictions."""

# helper func to convert string "TRUE" or "FALSE" to boolean values
def make_boolean(s):
  if s.lower() == "false":
    return False
  if s.lower() == "true":
    return True
  
# make the test data  
correct = [make_boolean(i['classification']) for i in data]

"""Once we have made our rule based classifier, we can make predictions! Enter code in the cell below to generate a list of predictions from our classifier."""

### YOUR CODE HERE



### END CODE

"""**Get this classifier's accuracy below!**"""

### YOUR CODE HERE
accuracy_score(_______, ________)
### END CODE

"""**Now try building a pro-classifier to only select for pro-refugee tweets! Then, test its accuracy.**"""

### YOUR CODE HERE


### END CODE

"""### Exercise (Discussion): How did we do?

Discuss these questions in your group, and then with your instructor:
* How well did your rule-based classifiers perform? 
* Was there a difference when you made a classifier to select for anti-refugee sentiment vs one for pro-refugee sentiment?
* What are pros and cons of using hand-built classifiers? 
* Are there any drawbacks to posing this question (of anti vs pro refugee sentiment) as a binary problem?
"""