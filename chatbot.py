import json 
import numpy as np 
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

with open('intents.json') as file:
    data = json.load(file)
    
training_sentences = []
training_labels = []
labels = []
responses = []


for intent in data['intents']:
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(intent['tag'])
    responses.append(intent['responses'])
    
    if intent['tag'] not in labels:
        labels.append(intent['tag'])
        
num_classes = len(labels)

lbl_encoder = LabelEncoder()
lbl_encoder.fit(training_labels)
training_labels = lbl_encoder.transform(training_labels)

vocab_size = 1000
embedding_dim = 16
max_len = 20
oov_token = "<OOV>"

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(training_sentences)
word_index = tokenizer.word_index
sequences = tokenizer.texts_to_sequences(training_sentences)
padded_sequences = pad_sequences(sequences, truncating='post', maxlen=max_len)

model = Sequential()
model.add(Embedding(vocab_size, embedding_dim, input_length=max_len))
model.add(GlobalAveragePooling1D())
model.add(Dense(16, activation='relu'))
model.add(Dense(16, activation='relu'))
model.add(Dense(num_classes, activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy', 
              optimizer='adam', metrics=['accuracy'])

model.summary()

epochs = 500
history = model.fit(padded_sequences, np.array(training_labels), epochs=epochs)

# to save the trained model
model.save("chat_model")

import pickle

# to save the fitted tokenizer
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
# to save the fitted label encoder
with open('label_encoder.pickle', 'wb') as ecn_file:
    pickle.dump(lbl_encoder, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)

def webscraper(x):
  from urllib.request import Request, urlopen
  from bs4 import BeautifulSoup
  import requests
  from random import randint

  #x = inp

  root = "https://www.google.com"
  link = "https://www.google.com/search?q=top+10+{}+movies&oq=top+&aqs=chrome.0.69i59l3j69i57j69i60l4.651j0j4&sourceid=chrome&ie=UTF-8".format(x)
  results = []

  req = Request(link, headers = {"User-Agent": "Mozilla/5.0"})
  webpage = urlopen(req).read()
  with requests.Session() as c:
    soup = BeautifulSoup(webpage, "html.parser")
    #print(soup)
    for item in soup.find_all('div', attrs = {"class": "RWuggc"}):
      results.append(item)

  titles = []
  for word in results:
    for j in word:
      for i in j:
        for p in i:
          titles.append(p)

  end_of_titles = len(titles)
  movie_index = randint(0, end_of_titles )
  movie_index_end = movie_index + 1
  return(str(*titles[movie_index:movie_index_end]))

import json 
import numpy as nphello
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder
from tkinter import font
from tkinter import ttk
from tkinter import *

import random
import pickle
import time

with open("intents.json") as file:
    data = json.load(file)


def chatbox():

    # load trained model
    model = keras.models.load_model('chat_model')

    # load tokenizer object
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # load label encoder object
    with open('label_encoder.pickle', 'rb') as enc:
        lbl_encoder = pickle.load(enc)

    # parameters
    max_len = 20

    def chatLog():
        text = textBox.get()
        inp = text

        result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([inp]),truncating='post', maxlen=max_len))
        tag = lbl_encoder.inverse_transform([np.argmax(result)])
        textBox.delete(0, 'end')
        chat.configure(state='normal')
        chat.tag_config("darker", background="#d0dce6", foreground='#082e39')
        chat.tag_config("lighter", foreground='#082e39')
        chat.tag_config("username", font='Calibri 14 bold',  background="#d0dce6", foreground='#082e39')
        chat.tag_config("botname", font='Calibri 14 bold', foreground='#082e39')

        chat.insert('end', 'User: ', 'username')
        chat.insert('end', text + '\n', 'darker')
        for i in data['intents']:
            if i['tag'] == tag:
                chat.insert('end', 'Moviebot: ', 'botname')
                chat.insert('end', np.random.choice(i['responses']) + '\n', 'lighter')
        if tag == "genres":
            chat.insert('end', 'Moviebot: ', 'botname')
            chat.insert('end', "Got one for you! How about.. '" + webscraper(inp) + "'?" + '\n', 'lighter')
            genre = inp
        if tag == "another":
            chat.insert('end', 'Moviebot: ', 'botname')
            chat.insert('end', webscraper(genre) + '\n', 'lighter')
        chat.configure(state='disabled')


    root = Tk()
    chatBox = Scrollbar(root)
    chat = Text(root, wrap='word', state='disabled', width=30, height=15,
                yscrollcommand=chatBox.set, background='#e7eff6', font='Calibri 14')
    chatBox.configure(command=chat.yview)


    chat.grid(row=0, columnspan=2, sticky='ewns')
    chatBox.grid(row=0, column=2, sticky='ns')
    Label(root, text="Message: ", font='Calibri 14 bold', foreground='#082e39').grid(row=1, column=0)

    textBox = Entry(root, bd=0, width=30, bg="#8ab9c5", font='Calibri 14', foreground='#082e39')
    textBox.grid(row=1, column=1)

    Button(root, text="Send", command=chatLog, background='#8ab9c5', font='Calibri 13', foreground='#082e39').grid(row=3, columnspan=3)
    root.mainloop()

chatbox()

