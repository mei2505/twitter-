# -*- coding: utf-8 -*-
"""Twitter API.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MFzB1MkA7JROFQYNJ2ezPmE8GarkM_PI
"""

from google.colab import drive
drive.mount('/content/drive/')

ls drive/My\ Drive

cd drive/My\ Drive/colab

ls

!pip install twitter
!pip install tweepy

from twitter import *

# put your keys
CONSUMER_KEY = '9iRDTaHEyeIPxI3vOydIGZssj'
CONSUMER_SECRET = 'rSbNNMxkKucC6pjGOOOQtGSJbtQ5QKikYaroSjwy7hjhF2fqeZ'
ACCESS_TOKEN = '847810767042650114-AzWiIbiS0TAi2B9RqDL917DUvIVFYyU'
ACCESS_TOKEN_SECRET = '8BmYZyZx8qghFawteVeg8ROq3FuwPs95oDRqBIKDXE9VF'

auth = OAuth(ACCESS_TOKEN,ACCESS_TOKEN_SECRET,CONSUMER_KEY,CONSUMER_SECRET)
twitter = Twitter(auth = auth)

# id23424856 means JPN
results = twitter.trends.place(_id = 23424856)
list_trend = []
for result in results:
  for trend in result['trends']:
    list_trend.append(trend['name'])
print(list_trend)

import tweepy

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

words = list_trend
count = 100

list_text = []
for word in words:
    tweets = api.search(q=word, count=count)
    for tweet in tweets:
        list_text.append(tweet.text)
        print(tweet.text)

import re

list_tmp = []
for text in list_text:
    text_tmp = text
    text_tmp = re.sub('RT .*', '', text_tmp)
    text_tmp = re.sub('@.*', '', text_tmp)
    text_tmp = re.sub('http.*', '', text_tmp)
    text_tmp = re.sub('#.*', '', text_tmp)
    text_tmp = re.sub('\n', '', text_tmp)
    text_tmp = text_tmp.strip()
    if text_tmp != '':
        list_tmp.append(text_tmp)
list_tmp = list(set(list_tmp))
print(list_tmp)

from google.colab import files
import pickle
from datetime import datetime as dt

tdatetime = dt.now()
str_ymd = tdatetime.strftime('%Y%m%d%H%M%S')
filename = str_ymd 
with open(filename,'wb') as f:
  pickle.dump(list_tmp, f)
files.download(filename)

!apt-get -q -y install sudo file mecab libmecab-dev mecab-ipadic-utf8 git curl python-mecab
!git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
!echo yes | mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -n
!sed -e "s!/var/lib/mecab/dic/debian!/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd!g" /etc/mecabrc > /etc/mecabrc.new
!cp /etc/mecabrc /etc/mecabrc.old
!cp /etc/mecabrc.new /etc/mecabrc
!apt-get -q -y install swig
!pip install mecab-python3

# upload 'YYYYMMDDhhmmss_tweetsSearched.pickle'
from google.colab import files

tweets_to_learn = files.upload()

import pickle

list_tweets = []
for key in tweets_to_learn.keys():
  f = open(key, 'rb')
  list_tweets.append(pickle.load(f))
  f.close()

for list_tweet in list_tweets:
  text = ''.join(list_tweet)
print(text)

from __future__ import print_function
from keras.callbacks import LambdaCallback
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys
import io

import MeCab

# commented out making char-dictionary part
# making word-dictinary instead
# original source : 'https://github.com/keras-team/keras/blob/master/examples/lstm_text_generation.py'

#chars = sorted(list(set(text)))
#print('total chars:', len(chars))
#char_indices = dict((c, i) for i, c in enumerate(chars))
#indices_char = dict((i, c) for i, c in enumerate(chars))

#making word dictionary
mecab = MeCab.Tagger("-Owakati")
text = mecab.parse(text)
text = text.split()
chars = sorted(list(set(text)))
count = 0
# initializing dictionary
char_indices = {}
indices_char = {}

# registering words without duplications
for word in chars:
  if not word in char_indices:
    char_indices[word] = count
    count +=1
    print(count,word)
indices_char = dict([(value, key) for (key, value) in char_indices.items()])

# cut the text in semi-redundant sequences of maxlen characters
maxlen = 5
step = 1
sentences = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
  sentences.append(text[i: i + maxlen])
  next_chars.append(text[i + maxlen])
print('nb sequences:', len(sentences))

print('Vectorization...')
x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
  for t, char in enumerate(sentence):
    x[i, t, char_indices[char]] = 1
  y[i, char_indices[next_chars[i]]] = 1

# build the model: a single LSTM
print('Build model...')
model = Sequential()
model.add(LSTM(128, input_shape=(maxlen, len(chars))))
model.add(Dense(len(chars)))
model.add(Activation('softmax'))

optimizer = RMSprop(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=optimizer)

def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

def on_epoch_end(epoch, logs):
  # Function invoked at end of each epoch. Prints generated text.
  print()
  print('----- Generating text after Epoch: %d' % epoch)

  start_index = random.randint(0, len(text) - maxlen - 1)
  for diversity in [0.2, 0.5, 1.0, 1.2]:
    print('----- diversity:', diversity)
    generated = ''
    sentence = text[start_index: start_index + maxlen]
#    generated += sentence
# sentence is was a str, but is a list now
    generated += ''.join(sentence)

    print('----- Generating with seed: "' + ''.join(sentence) + '"')
    sys.stdout.write(generated)

#    for i in range(400):
# 400 words must be too much to tweet
    for i in range(140-maxlen):
      x_pred = np.zeros((1, maxlen, len(chars)))
      for t, char in enumerate(sentence):
        x_pred[0, t, char_indices[char]] = 1.

      preds = model.predict(x_pred, verbose=0)[0]
      next_index = sample(preds, diversity)
      next_char = indices_char[next_index]
      # length should not be more than 140
      if len(generated) + len(next_char) > 140:
        break
      generated += next_char
#      sentence = sentence[1:] + next_char
# sentence is was a str, but is a list now
      sentence = sentence[1:]
      sentence.append(next_char)

      sys.stdout.write(next_char)
      sys.stdout.flush()
    list_generated.append(generated)
    print()

list_generated = []

print_callback = LambdaCallback(on_epoch_end=on_epoch_end)

model.fit(x, y,
          batch_size=128,
          epochs=60,
          callbacks=[print_callback])