from transformers import AutoTokenizer, AutoConfig, AutoModelForSequenceClassification
import torch
import numpy as np
import os
import torch.nn.functional as F
import json
import streamlit as st
from streamlit_chat import message
import gdown

st.set_page_config(
    page_title="HOT6IX - Happy Chatbot",
    page_icon=":robot:"
)

st.header("HOT6IX - Happy Chatbot")

import tokenizers
@st.cache(hash_funcs={tokenizers.Tokenizer: lambda _: None, tokenizers.AddedToken: lambda _: None})
def model_load():
  MODEL_NAME = "klue/roberta-large"
  config = AutoConfig.from_pretrained(MODEL_NAME)
  config.num_labels = 359
  model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, config=config)

  tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
  google_path = 'https://drive.google.com/uc?id='
  file_id = '1AnlHOr8waFOnzgYWVLtFCKpLi4yHQ3GR'
  output_name = 'roberta_model.bin'
  gdown.download(google_path + file_id, output_name, quiet=False)
  model.load_state_dict(torch.load(output_name))  
  return tokenizer, model

@st.cache(hash_funcs={tokenizers.Tokenizer: lambda _: None, tokenizers.AddedToken: lambda _: None})
def json_load():
  with open("../data/idx2label.json", "r", encoding = "utf-8") as file:
    idx2label = json.load(file)

  with open("../data/label2answer.json", "r", encoding = "utf-8") as file:
    label2answer = json.load(file)

  return idx2label, label2answer

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

tokenizer, model = model_load()
model.to(device)

idx2label, label2answer = json_load()

if 'generated' not in st.session_state:
  st.session_state['generated'] = []

if 'past' not in st.session_state:
  st.session_state['past'] = []

user_input = st.text_input("당신: ", key="input")

if user_input:

  tokenized_sentence = tokenizer(
                user_input,
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=512,
                return_token_type_ids = False
                )

  with torch.no_grad():
    outputs = model(
        input_ids=tokenized_sentence['input_ids'].to(device),
        attention_mask=tokenized_sentence['attention_mask'].to(device),
        )
    logits = outputs['logits']
    prob = F.softmax(logits, dim=-1).detach().cpu().numpy()
    logits = logits.detach().cpu().numpy()
    result = np.argmax(logits, axis=-1)

  idx = str(result[0])
  label = idx2label[idx]
  answer = label2answer[label][0]
  
  st.session_state.past.append(user_input)
  st.session_state.generated.append(answer)

if st.session_state['generated']:
  for i in range(len(st.session_state['generated'])-1, -1, -1):
    message(st.session_state['generated'][i], key=str(i))
    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')