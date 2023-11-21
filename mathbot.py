import streamlit as st
import random
from random import randrange
import numpy as np

from gtts import gTTS
import os
from IPython.display import Audio

st.title("Welcome to Dhruv's MathBot")
st.markdown("This application was developed by Dhruv Suresh to help users in practicing their mental math abilities via the visual as well as the auditory medium. The primary purpose of this website is to help aspiring traders and quants to practice their mental math abilities to crack interviews. Existing online platforms tend to cover only the visual medium which I feel is incomplete when it comes to facing mental math questions in actual interviews. This app aims to create a more realistic simulation of an interview environment by combining text as well as speech elements.")
st.markdown("The default settings for addition and subtraction are (2 to 100) +/- (2 to 100). Defaults for multiplication are (2 to 12) x (2 to 100). These settings can be modified as per the difficulty level desired by the user using the sliders below. Addition and Subtraction goes to a maximum of 5 digits and Multiplication a maximum of 4 (if you can do 4x4s mentally you can legally identify yourself as a human calculator)")
st.markdown("The user can also choose to pick and choose only Addition/Subtraction/Multiplication or any conbination of the operations if they wish to do so using the check boxes below. Enjoy!")

add = st.checkbox("Addition", value = True)
sub = st.checkbox("Subtraction", value = True)
mult = st.checkbox("Multiplication", value = True)

# mode = st.radio("Choose Audio/Visual Mode", ['Audio','Visual'], index = 0)

add_sub_range = st.slider('Choose Upper Range for Addition/Subtraction', min_value = 100, max_value = 10000, step = 50, value = 100)
multiply_range1 = st.slider('Choose Upper Range for Multiplication number 1', min_value = 12, max_value = 1000, step = 2, value = 12)
multiply_range2 = st.slider('Choose Upper Range for Multiplication number 2', min_value = 100, max_value = 1000,step = 2, value = 100)

def Visual():
  operations_list = []

  if add:
    operations_list.append("Plus")
  if sub:
    operations_list.append("Minus")
  if mult:
    operations_list.append("Multiplied By")

  rand_idx = random.randrange(len(operations_list))
  random_operation = operations_list[rand_idx]

  if random_operation == "Plus":
    nos_add = np.random.randint(low = 2, size = 2, high = (add_sub_range + 1))
    correct_output = nos_add[1] + nos_add[0]
    number1 = str(nos_add[1])
    number2 = str(nos_add[0])
    text = number1 + " + " + number2
    st.session_state.question = text
    st.session_state.correct_answer = str(correct_output)

  elif random_operation == "Minus":
    sorted_nos_sub = sorted(np.random.randint(low = 2, size = 2, high = (add_sub_range + 1)))
    correct_output = sorted_nos_sub[1] - sorted_nos_sub[0]
    number1 = str(sorted_nos_sub[1])
    number2 = str(sorted_nos_sub[0])
    text = number1 + " - " + number2
    st.session_state.question = text
    st.session_state.correct_answer = str(correct_output)

  elif random_operation == "Multiplied By":
    nos_multiply1 = np.random.randint(low = 2, size = 1, high = (multiply_range + 1))
    nos_multiply2 = np.random.randint(low = 2, size = 1, high = (multiply_range2 + 1))
    correct_output = int(nos_multiply1 * nos_multiply2)
    mylist = [nos_multiply1 , nos_multiply2]
    random.shuffle(mylist)
    number1 = str(mylist[1])
    number2 = str(mylist[0])
    text = number1.strip("[]") + " x " + number2.strip("[]")
    st.session_state.question = text
    st.session_state.correct_answer = str(correct_output)

  return [text,str(correct_output)]

def Audio():
  operations_list = []

  if add:
    operations_list.append("Plus")
  if sub:
    operations_list.append("Minus")
  if mult:
    operations_list.append("Multiplied By")

  rand_idx = random.randrange(len(operations_list))
  random_operation = operations_list[rand_idx]

  if random_operation == "Plus":
    nos_add = np.random.randint(low = 2, size = 2, high = (add_sub_range + 1))
    correct_output = nos_add[1] + nos_add[0]
    number1 = str(nos_add[1])
    number2 = str(nos_add[0])
    text = number1 + " + " + number2
    audio_text = number1 + " Plus " + number2
    st.session_state.question = text
    st.session_state.correct_answer = str(correct_output)

  elif random_operation == "Minus":
    sorted_nos_sub = sorted(np.random.randint(low = 2, size = 2, high = (add_sub_range + 1)))
    correct_output = sorted_nos_sub[1] - sorted_nos_sub[0]
    number1 = str(sorted_nos_sub[1])
    number2 = str(sorted_nos_sub[0])
    text = number1 + " - " + number2
    audio_text = number1 + " Minus " + number2
    st.session_state.question = text
    st.session_state.correct_answer = str(correct_output)

  elif random_operation == "Multiplied By":
    nos_multiply1 = np.random.randint(low = 2, size = 1, high = (multiply_range1 + 1))
    nos_multiply2 = np.random.randint(low = 2, size = 1, high = (multiply_range2 + 1))
    correct_output = int(nos_multiply1 * nos_multiply2)
    mylist = [nos_multiply1 , nos_multiply2]
    random.shuffle(mylist)
    number1 = str(mylist[1])
    number2 = str(mylist[0])
    text = number1.strip("[]") + " x " + number2.strip("[]")
    audio_text = number1 + " Multiplied By " + number2
    st.session_state.question = text
    st.session_state.correct_answer = str(correct_output)

  return [text,str(correct_output),audio_text]

if 'score' not in st.session_state:
  st.session_state.score = 0

st.write("Your score is: ", st.session_state.score)

def Answer_check():
  if st.session_state.correct_answer == st.session_state.input:
    st.session_state.score+=1
  else:
    st.session_state.score-=1

# if mode == "Visual":
#   output_list = Visual()
#   output_text = output_list[0]
#   output_answer = output_list[1]
#   user_input = st.text_input(output_text, key = "input", on_change = Answer_check)

# elif mode == "Audio":
output_list = Audio()
output_text = output_list[0]
output_answer = output_list[1]
output_audio = output_list[2]
language = 'en'
tts = gTTS(text = output_audio, lang = language, slow = False)
tts.save('1.wav')
sound_file = '1.wav'
st.markdown("Please press play to listen to the audio")
st.audio(sound_file)
user_input = st.text_input("Enter your Answer here",key = "input", value = '', on_change = Answer_check)
