## Interface Compoment (GUI) - GSN ##

import json 
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder
from tkinter import font
from tkinter import ttk
from tkinter import simpledialog
from tkinter import *
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
from random import randint
import pandas as pd
import numpy as np
import colorama 
from colorama import Fore, Style, Back
import pickle
import googletrans
from googletrans import Translator

# Web scraper function for getting movie recommendations from Google
def webscraper(x):
  root = "https://www.google.com"
  link = "https://www.google.com/search?q=top+10+{}+movies&oq=top+&aqs=chrome.0.69i59l3j69i57j69i60l4.651j0j4&sourceid=chrome&ie=UTF-8".format(x)
  results = []

  req = Request(link, headers = {"User-Agent": "Mozilla/5.0"})
  webpage = urlopen(req).read()
  with requests.Session() as c:
    soup = BeautifulSoup(webpage, "html5lib")
    for item in soup.find_all('div', attrs = {"class": "RWuggc"}):
      results.append(item)

  titles = []
  
  for word in results:
    for j in word:
      for i in j:
        for p in i:
          is_year_of_pub = True                          #filtering out years of publication; filters everything that consists only of numbers, so a movie like 2012 will not make it to the recommendation
          for char in p:
            if ord(char) < 48 or ord(char) > 57:
              is_year_of_pub = False
              break
          if is_year_of_pub == False:                     #Only if p is not a string of numbers, it is put in the titles list
            titles.append(p)

  #print(titles)
  end_of_titles = len(titles)
  movie_index = randint(0, end_of_titles )
  movie_index_end = movie_index + 1
  return str(*(titles[movie_index:movie_index_end]))


def chat():
  translator = Translator()
  colorama.init()

  # load trained model
  model = keras.models.load_model('chat_model.h5')

  # load tokenizer object
  with open('tokenizer.pickle', 'rb') as handle:
      tokenizer = pickle.load(handle)

  # load label encoder object
  with open('label_encoder.pickle', 'rb') as enc:
      lbl_encoder = pickle.load(enc)

  # parameters
  max_len = 20

  language_detect = input("Please state the language you would like to talk in to Moviebot? \n (State the language in English please) ")
  language_detect = language_detect.lower()
  language_lib = googletrans.LANGCODES
  
  while True:
      print(Fore.LIGHTBLUE_EX + "User: " + Style.RESET_ALL, end="")
      inp = input()
      language = language_lib[language_detect]
      inp_translated = (translator.translate(inp)).text
      if inp_translated.lower() == "quit":
          break
      

      result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([inp_translated]),
                                            truncating='post', maxlen=max_len))
      tag = lbl_encoder.inverse_transform([np.argmax(result)])

      data = pd.read_json('intents.json')


      for i in data['intents']:
        if i['tag'] == tag:
          answer = np.random.choice(i['responses'])
          trans_answer = translator.translate(answer, dest = language).text
          print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL , trans_answer)

      if tag == "thanks":
          answer = np.random.choice(i['responses'])
          trans_answer = translator.translate(answer, dest = language).text
          #print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL , trans_answer)
          break
      if tag == "genres":
        answer = np.random.choice(i['responses'])
        trans_answer = translator.translate(answer, dest = language).text
        #print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL , trans_answer)
        print(translator.translate("What about: ", dest = language).text, webscraper(inp_translated))
        genre = inp_translated
      if tag == "another":
        answer = np.random.choice(i['responses'])
        trans_answer = translator.translate(answer, dest = language).text
        #print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL , trans_answer)
        print(webscraper(genre))
        

with open("intents.json") as file:
    data = json.load(file)



def chatbox():

    # load trained model
    model = keras.models.load_model('chat_model.h5')
    
    # load translator
    translator = Translator()

    # load tokenizer object
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # load label encoder object
    with open('label_encoder.pickle', 'rb') as enc:
        lbl_encoder = pickle.load(enc)

    # parameters
    max_len = 20

    # language pop-up

    root = Tk()
    root.withdraw()
    language_detect = simpledialog.askstring(title="Language", prompt="Please enter your preferred language in English.")
    language_detect = language_detect.lower()
    language_lib = googletrans.LANGCODES
    language = language_lib[language_detect]
    
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

        inp_translated = (translator.translate(inp)).text

        chat.insert('end', 'User: ', 'username')
        chat.insert('end', text + '\n', 'darker')

        for i in data['intents']:
            if i['tag'] == tag:
                chat.insert('end', 'Moviebot: ', 'botname')
                answer = np.random.choice(i['responses'])
                trans_answer = translator.translate(answer, dest = language).text
                chat.insert('end', trans_answer + '\n', 'lighter')
        if tag == "genres":
            chat.insert('end', 'Moviebot: ', 'botname')
            answer = "Got one for you! How about.. '" + webscraper(inp_translated) + "'?"
            trans_answer = translator.translate(answer, dest = language).text
            chat.insert('end',  trans_answer + '\n', 'lighter')
            genre = inp_translated
        if tag == "another":
            chat.insert('end', 'Moviebot: ', 'botname')
            answer = webscraper(genre)
            trans_answer = translator.translate(answer, dest = language).text
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
