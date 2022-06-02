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
from tqdm import tqdm

try:
    es.transport.close()
except:
    pass
es = Elasticsearch('http://localhost:9200')

st.header("당신을 위로해주는 챗봇")

st.sidebar.subheader("Generation Settings")
maxlen=st.sidebar.slider("max length of the sequence", 30, 60,value=50)
topk=st.sidebar.slider("top k sampling", 10, 50, value=50)
topp=st.sidebar.slider("top p sampling", 0.0, 1.0, step=0.01, value=0.95)
sampling=st.sidebar.checkbox("do sampling", value=True)
retrieval=st.sidebar.checkbox("do retrieval(BM25)", value=True)
for _ in range(15): st.sidebar.text(" ")
st.sidebar.subheader("Develop By.")
st.sidebar.text("부스트캠프 AI Tech 3기")
st.sidebar.text("NLP 10조 핫식스")

@st.cache(hash_funcs={tokenizers.Tokenizer: lambda _: None, tokenizers.AddedToken: lambda _: None})
def prepare_es(INDEX_NAME):
    INDEX_NAME = INDEX_NAME
    INDEX_SETTINGS = {
        "settings" : {
            "index":{
                "analysis":{
                    "analyzer":{
                        "korean": {
                            "type":"custom",
                            "tokenizer":"nori_tokenizer",
                            "decompound_mode": "mixed",
                            "filter": [ "pos_filter_speech", "nori_readingform",
                            "lowercase", "remove_duplicates"],
                        }
                    },
                    "filter": {
                        "pos_filter_speech": {
                            "type": "nori_part_of_speech",
                            "stoptags": [
                                        "E",
                                        "IC",
                                        "J",
                                        "MAG",
                                        "MM",
                                        "NA",
                                        "NR",
                                        "SC",
                                        "SE",
                                        "SF",
                                        "SH",
                                        "SL",
                                        "SN",
                                        "SP",
                                        "SSC",
                                        "SSO",
                                        "SY",
                                        "UNA",
                                        "UNKNOWN",
                                        "VA",
                                        "VCN",
                                        "VCP",
                                        "VSV",
                                        "VV",
                                        "VX",
                                        "XPN",
                                        "XR",
                                        "XSA",
                                        "XSN",
                                        "XSV"
                                    ]
                        }
                    }
                }
            }
        }
    ,
    "mappings": {
            "properties" : {
                "content" : {
                    "type" : "text",
                    "analyzer": "korean",
                    "search_analyzer": "korean"
                },
                "title" : {
                    "type" : "text",
                    "analyzer": "korean",
                    "search_analyzer": "korean"
                }
            }
        } 
    }

    es.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS)

    with open("../../data/answer_total.json", "r") as file:
        chat_dict = json.load(file) 

    for doc_id, doc in tqdm(chat_dict.items()):
        es.index(index=INDEX_NAME,  id=doc_id, body=doc)
    
    return

INDEX_NAME = 'toy_index'
if not es.indices.exists(index=INDEX_NAME):
    prepare_es(INDEX_NAME)

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

model, tokenizer, uf = load()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

user_id = st.text_input('', placeholder = '이름을 입력하세요.')
utter = st.text_input('당신 : ', key="msg", placeholder = '메세지를 입력하세요.')

if st.button("전송"):
    
    hate_score = uf(utter)[0][9]['score']
    if hate_score < 0.7:
        st.warning('혐오 표현을 사용하지 마세요.')
        print(f'-------------------------------')
        print(f'your name is {user_id}')
        print(f'your message is {utter}')
        print(f'max length is {maxlen}')
        print(f'top k sampling value is {topk}')
        print(f'top p sampling value is {topp}')
        print(f'whether to sampling is {sampling}')
        print(f'whether to retrieval is {retrieval}')
        print(f'!!!!!!! this is hate speech !!!!!!!')
        print(f'hate score is {hate_score}')
        print(f'-------------------------------')

    else:
        print(f'-------------------------------')
        print(f'your name is {user_id}')
        print(f'your message is {utter}')
        print(f'max length is {maxlen}')
        print(f'top k sampling value is {topk}')
        print(f'top p sampling value is {topp}')
        print(f'whether to sampling is {sampling}')
        print(f'whether to retrieval is {retrieval}')
        print(f'hate score is {hate_score}')
        print(f'-------------------------------')
        with torch.no_grad():
            user = '<usr>' + utter + '<unused1>'
            encoded = tokenizer.encode(user)
            input_ids = torch.LongTensor(encoded).unsqueeze(dim=0)
            output = model.generate(input_ids,
                                    max_length=maxlen, 
                                    top_k=topk, 
                                    top_p=topp,
                                    do_sample=sampling,
                                    )
            
            a = tokenizer.decode(output[0]) # <usr> utter <unused1> sent <sys> answer </s>
            idx = torch.where(output[0]==tokenizer.encode('<sys>')[0])
            chatbot = tokenizer.decode(output[0][int(idx[0])+1:], skip_special_tokens=True) # answer

            if '답변' in a: # sent : 긍정답변 / 부정답변
                if st.session_state['past']:
                    prev = st.session_state['past'][-1]
                else:
                    prev = ''

                user = '<usr>' + prev + utter + ' <unused1>' # multi-turn
                encoded = tokenizer.encode(user)
                input_ids = torch.LongTensor(encoded).unsqueeze(dim=0)
                output = model.generate(input_ids,
                                    max_length=maxlen,
                                    do_sample=sampling, 
                                    top_k=topk, 
                                    top_p=topp
                                    )
                a_new = tokenizer.decode(output[0], skip_special_tokens=True)
                idx = torch.where(output[0]==tokenizer.encode('<sys>')[0])
                chatbot = tokenizer.decode(output[0][int(idx[0])+1:], skip_special_tokens=True)
                
                answer = chatbot.strip()
            
            else: 
                answer = chatbot.strip()
        
        if '00' in answer: 
            answer = answer.replace('00', '사용자')

        if retrieval:
            res = es.search(index=INDEX_NAME, q=answer, size=3)
            print(res)
            answer = res['hits']['hits'][0]['_source']['text'].rstrip('\n')
        
        if '사용자' in answer:
            answer = answer.replace('사용자', user_id)

        st.session_state['past'].append(utter)
        st.session_state['generated'].append(answer)
     
if st.session_state['generated']:
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        message(st.session_state['generated'][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')