import torch
from tokenizers import SentencePieceBPETokenizer
from transformers import GPT2Config, GPT2LMHeadModel
import streamlit as st
from streamlit_chat import message
import tokenizers
import gdown
import os

st.header("kogpt2를 이용한 싱글턴 챗봇")

@st.cache(hash_funcs={tokenizers.Tokenizer: lambda _: None, tokenizers.AddedToken: lambda _: None})
def load():
    tokenizer = SentencePieceBPETokenizer("../kogpt2/vocab.json", "../kogpt2/merges.txt")
    tokenizer.add_special_tokens(['<s>', '</s>'])
    tokenizer.no_padding()
    tokenizer.no_truncation()

    config = GPT2Config(vocab_size=50000)
    model = GPT2LMHeadModel(config)
    google_path = 'https://drive.google.com/uc?id='
    file_id = '1f9_ez8l3Yvmb8faVpa9iHXyMvhhBihGw'
    output_name = '../model/single_turn_model.bin'
    gdown.download(google_path + file_id, output_name, quiet=False)
    model.load_state_dict(torch.load(output_name, map_location=torch.device('cpu')))

    return model, tokenizer

model, tokenizer = load()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

utter = st.text_input("당신: ", key="input")

if utter:
    encoded_utter = torch.tensor(tokenizer.encode('<s>' + utter + '</s><s>').ids).unsqueeze(0)

    sample_output = model.generate(
        encoded_utter,
        num_return_sequences=1,
        do_sample=True,
        max_length=128,
        top_k=50,
        top_p=0.95,
        eos_token_id=tokenizer.token_to_id('</s>'),
        early_stopping=True,
        bad_words_ids=[[tokenizer.token_to_id('<unk>')]]
    )

    decoded_output = tokenizer.decode_batch(sample_output.tolist())[0]

    answer = decoded_output[len(utter)+1:]

    st.session_state.past.append(utter)
    st.session_state.generated.append(answer)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        message(st.session_state['generated'][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
