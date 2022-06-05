#!/usr/bin/env python
# coding: utf-8


import streamlit as st
from transformers import GPT2LMHeadModel, PreTrainedTokenizerFast, TextClassificationPipeline, BertForSequenceClassification, AutoTokenizer
import torch
from streamlit_chat import message
import tokenizers
import gdown
from elasticsearch import Elasticsearch
import json
from collections import defaultdict

try:
    es.transport.close()
except:
    pass
es = Elasticsearch('http://localhost:9200')

st.header("당신을 위로해주는 챗봇")

st.sidebar.subheader("Generation Settings")
maxlen=st.sidebar.slider("max length of the sequence", 30, 60,value=50)
topk=st.sidebar.slider("top k sampling", 10, 50, value=50)
topp=st.sidebar.slider("top p sampling", 0.0, 1.0, step=0.01, value=0.85)
sampling=st.sidebar.checkbox("do sampling", value=True)
for _ in range(20): st.sidebar.text(" ")
st.sidebar.subheader("Develop By.")
st.sidebar.text("부스트캠프 AI Tech 3기")
st.sidebar.text("NLP 10조 핫식스")

INDEX_NAME = 'toy_index'

@st.cache(hash_funcs={tokenizers.Tokenizer: lambda _: None, tokenizers.AddedToken: lambda _: None})
def load():
    google_path = 'https://drive.google.com/uc?id='
    file_id = '1pNG24Wpq1g_OMtrMLN27Kl7OxbvPuM8A'
    output_name = '../best_model/pytorch_model.bin'
    gdown.download(google_path + file_id, output_name, quiet=False)
    model = GPT2LMHeadModel.from_pretrained('../best_model')
    tokenizer = PreTrainedTokenizerFast.from_pretrained("skt/kogpt2-base-v2", eos_token='</s>', unk_token='<unk>', pad_token='<pad>', mask_token='<unused0>')
    
    uf_model = BertForSequenceClassification.from_pretrained('smilegate-ai/kor_unsmile')
    uf_tokenizer = AutoTokenizer.from_pretrained('smilegate-ai/kor_unsmile')
    uf = TextClassificationPipeline(
        model=uf_model,
        tokenizer=uf_tokenizer,
        device=0,     # cpu는 -1, gpu일 땐 gpu number라고 함. 처음엔 0.
        return_all_scores=True,
        )

        
    return model, tokenizer, uf

model, tokenizer, uf= load()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

user_id = st.text_input('', placeholder = '이름을 입력하세요.')
utter = st.text_input('당신 : ', key="msg", placeholder = '메세지를 입력하세요.')

if st.button("전송"):
    
    hate_score = uf(utter)[0][9]['score']
    if hate_score < 0.1:
        st.warning('조금 더 부드럽게 말해주세요.')
        # print(f'-------------------------------')
        # print(f'your name is {user_id}')
        # print(f'your message is {utter}')
        # print(f'max length is {maxlen}')
        # print(f'top k sampling value is {topk}')
        # print(f'top p sampling value is {topp}')
        # print(f'whether to sampling is {sampling}')
        # print(f'!!!!!!! this is hate speech !!!!!!!')
        # print(f'hate score is {hate_score}')
        # print(f'-------------------------------')

    else:
        # print(f'-------------------------------')
        # print(f'your name is {user_id}')
        # print(f'your message is {utter}')
        # print(f'max length is {maxlen}')
        # print(f'top k sampling value is {topk}')
        # print(f'top p sampling value is {topp}')
        # print(f'whether to sampling is {sampling}')
        # print(f'hate score is {hate_score}')
        # print(f'-------------------------------')
        with torch.no_grad():
            user = '<usr>' + utter + '<unused1>'
            encoded = tokenizer.encode(user)
            input_ids = torch.LongTensor(encoded).unsqueeze(dim=0)
            output = model.generate(input_ids,
                                    max_length=maxlen, 
                                    top_k=topk, 
                                    top_p=topp,
                                    do_sample=sampling,
                                    num_return_sequences=5
                                    )

            SENT_DICT = defaultdict(list)
            for o in output:
                sent_idx = int(torch.where(o==tokenizer.encode('<unused1>')[0])[0])
                sys_idx = int(torch.where(o==tokenizer.encode('<sys>')[0])[0])
                SENT = tokenizer.decode(o[sent_idx+1:sys_idx])
                ANS = tokenizer.decode(o[sys_idx+1:], skip_special_tokens=True)
                SENT_DICT[SENT].append(ANS)
            
            BEST_OUTPUT = list(sorted(SENT_DICT.items(), key=lambda x:-len(x[1])))[0]
            BEST_SENT, BEST_ANSWERS = BEST_OUTPUT[0], BEST_OUTPUT[1]
          
            if '답변' in BEST_SENT: # sent : 긍정답변 / 부정답변
                if st.session_state['past']:
                    prev = st.session_state['past'][-1]
                else:
                    prev = ''

                user = '<usr>' + prev + utter + ' <unused1>' # multi-turn
                encoded = tokenizer.encode(user)
                input_ids = torch.LongTensor(encoded).unsqueeze(dim=0)
                output = model.generate(input_ids,
                                    max_length=maxlen, 
                                    top_k=topk, 
                                    top_p=topp,
                                    do_sample=sampling,
                                    num_return_sequences=5
                                    )

                SENT_DICT = defaultdict(list)
                for o in output:
                    sent_idx = int(torch.where(o==tokenizer.encode('<unused1>')[0])[0])
                    sys_idx = int(torch.where(o==tokenizer.encode('<sys>')[0])[0])
                    SENT = tokenizer.decode(o[sent_idx+1:sys_idx])
                    ANS = tokenizer.decode(o[sys_idx+1:], skip_special_tokens=True)
                    SENT_DICT[SENT].append(ANS)
                
                BEST_OUTPUT = list(sorted(SENT_DICT.items(), key=lambda x:-len(x[1])))[0]
                BEST_SENT, BEST_ANSWERS = BEST_OUTPUT[0], BEST_OUTPUT[1]

        for i, ANSWER in enumerate(BEST_ANSWERS):            
            if '00' in ANSWER: 
                BEST_ANSWERS[i] = ANSWER.replace('00', '사용자')        
            if '!' in ANSWER: 
                BEST_ANSWERS[i] = ANSWER.replace('!', '.')
        
        SEARCH_OUTPUT = {}
        for ANSWER in BEST_ANSWERS:
            res = es.search(index=INDEX_NAME, q=ANSWER, size=5)

            if ANSWER[-1] in  ['.', '?', '!']:
                if ANSWER not in SEARCH_OUTPUT.keys(): SEARCH_OUTPUT[ANSWER] = [1, 100]
                else: SEARCH_OUTPUT[ANSWER][0] += 1; SEARCH_OUTPUT[ANSWER][1] += 100

            for hit in res['hits']['hits']:
                score = hit['_score']    
                text = hit['_source']['text'].rstrip('\n')

                if score >= 10.0:
                    if text not in SEARCH_OUTPUT.keys(): SEARCH_OUTPUT[text] = [1, score]
                    else: SEARCH_OUTPUT[text][0] += 1; SEARCH_OUTPUT[text][1] += score
            
        for k in SEARCH_OUTPUT.keys():
            SEARCH_OUTPUT[k][1] /= SEARCH_OUTPUT[k][0]
        
        RESULT = list(sorted(SEARCH_OUTPUT.items(), key= lambda x:(-x[1][0], -x[1][1])))
        if not RESULT[0]: 
            answer = '다시 한번 말씀해주실래요?'
        else:
            print(RESULT)
            answer = RESULT[0][0]

        if '사용자' in answer:
            answer = answer.replace('사용자', user_id)

        st.session_state['past'].append(utter)
        st.session_state['generated'].append(answer)        

if st.session_state['generated']:
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        message(st.session_state['generated'][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
