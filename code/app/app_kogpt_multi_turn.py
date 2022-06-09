import torch
from tokenizers import SentencePieceBPETokenizer
from transformers import GPT2Config, GPT2LMHeadModel
import streamlit as st
from streamlit_chat import message
import tokenizers
import gdown
import os

st.header("kogpt2를 이용한 멀티턴 챗봇")

@st.cache(hash_funcs={tokenizers.Tokenizer: lambda _: None, tokenizers.AddedToken: lambda _: None})
def load():
    tokenizer = SentencePieceBPETokenizer("../kogpt2/vocab.json", "../kogpt2/merges.txt")
    tokenizer.add_special_tokens(['<s>', '</s>'])
    tokenizer.no_padding()
    tokenizer.no_truncation()

    config = GPT2Config(vocab_size=50000)
    model = GPT2LMHeadModel(config)
    google_path = 'https://drive.google.com/uc?id='
    file_id = '1HEQ3enItqS_wY7VA1GilBlDNVfU0OPI0'
<<<<<<< HEAD:code/app/app_kogpt_multi_turn.py
    output_name = '../model/multi_turn_model.bin'
=======
    output_name = 'multi_turn_model.bin'
>>>>>>> ee8d1d69fc284b8925c710663c8473c3b90802fe:chatbot/code/app_kogpt_multi_turn.py
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
    # st.session_state['past'] : user_input
    # st.session_state['generated'] : chatbot
    
    prev = ''
    prev += '<s><pad></s>' * (6 - (2 * min(len(st.session_state['past']), 3)))
    if len(st.session_state['past']) >= 3:
        for i in range(3):
            prev += '<s>' + st.session_state['past'][i-3] + '</s>'
            prev += '<s>' + st.session_state['generated'][i-3] + '</s>'
    else:
        for i in range(len(st.session_state['past'])):
            prev += '<s>' + st.session_state['past'][i] + '</s>'
            prev += '<s>' + st.session_state['generated'][i] + '</s>'

    encoded_utter = torch.tensor(tokenizer.encode(prev + '<s>' + utter + '</s><s>').ids).unsqueeze(0)

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
    x = decoded_output.index(utter)
    answer = decoded_output[x + len(utter) + 1:]

    st.session_state.past.append(utter)
    st.session_state.generated.append(answer)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        message(st.session_state['generated'][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
