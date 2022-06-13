#!/usr/bin/env python
# coding: utf-8

# !pip install sentence-transformers

import os
import streamlit as st
from transformers import GPT2LMHeadModel, PreTrainedTokenizerFast, TextClassificationPipeline, BertForSequenceClassification, AutoTokenizer
import torch
from streamlit_chat import message
import tokenizers
import gdown
from elasticsearch import Elasticsearch
import json
import pickle
from collections import defaultdict

from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer, util

# es = Elasticsearch('https://my-deployment-26ce26.es.us-central1.gcp.cloud.es.io:9243', http_auth=('elastic', 'kfBQYEGq1o6fgYMBomEegkLZ'))

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

@st.cache(hash_funcs={tokenizers.Tokenizer: lambda _: None, tokenizers.AddedToken: lambda _: None}, allow_output_mutation=True)
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
        device=-1,     # cpu는 -1, gpu일 땐 gpu number라고 함. 처음엔 0.
        return_all_scores=True,
        )

        
    return model, tokenizer, uf

model, tokenizer, uf= load()

@st.cache(allow_output_mutation=True)
def model_embs():
    sbert_model =  SentenceTransformer('jhgan/ko-sroberta-multitask')
    
    google_path = 'https://drive.google.com/uc?id=1GS6FVw2tKVOO-yCz6mWiWXHIZVHFR25_'
    output_name = '../SBERT/answer_embs.pickle'
    gdown.download(google_path, output_name, quiet=False)
    with open('../SBERT/answer_embs.pickle', 'rb') as f:
        answer_embs = pickle.load(f)

    google_path = 'https://drive.google.com/uc?id=1Gc7Zh-inL8YxKg4HCUsUWKGeBWeOyBWk'
    output_name = '../SBERT/answers.pickle'
    gdown.download(google_path, output_name, quiet=False)
    with open('../SBERT/answers.pickle', 'rb') as f:
        answers = pickle.load(f)
    return sbert_model, answer_embs, answers

sbert_model, answer_embs, answers = model_embs()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


user_id = st.text_input('', placeholder = '이름을 입력하세요.')
with st.form('form', clear_on_submit=True):
    utter = st.text_input('당신 : ', key="msg", placeholder = '메세지를 입력하세요.')
    submitted = st.form_submit_button('전송')

if utter and submitted:
    if user_id == '':
        st.error('이름을 입력해주세요!')
    else:    
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
                    try:
                        sent_idx = int(torch.where(o==tokenizer.encode('<unused1>')[0])[0])
                        sys_idx = int(torch.where(o==tokenizer.encode('<sys>')[0])[0])
                        SENT = tokenizer.decode(o[sent_idx+1:sys_idx])
                        ANS = tokenizer.decode(o[sys_idx+1:], skip_special_tokens=True)
                        SENT_DICT[SENT].append(ANS)
                    except:
                        continue
                
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
                        try:
                            sent_idx = int(torch.where(o==tokenizer.encode('<unused1>')[0])[0])
                            sys_idx = int(torch.where(o==tokenizer.encode('<sys>')[0])[0])
                            SENT = tokenizer.decode(o[sent_idx+1:sys_idx])
                            ANS = tokenizer.decode(o[sys_idx+1:], skip_special_tokens=True)
                            SENT_DICT[SENT].append(ANS)
                        except:
                            continue
                    
                    BEST_OUTPUT = list(sorted(SENT_DICT.items(), key=lambda x:-len(x[1])))[0]
                    BEST_SENT, BEST_ANSWERS = BEST_OUTPUT[0], BEST_OUTPUT[1]

            # elastic search
            if False: 
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

            # SBERT
            if True:
                # 생성 답변들과 유사한 답변 후보들 retrieve
                answer_candidates = []
                for ANSWER in BEST_ANSWERS:
                    answer_emb = sbert_model.encode(ANSWER)

                    top_k = 5
                    cos_scores = util.pytorch_cos_sim(answer_emb, answer_embs)[0]   # 생성 답변 - 답변 후보군 간 코사인 유사도 계산 후,
                    top_results = torch.topk(cos_scores, k=top_k)   # 코사인 유사도 순으로 `top_k` 개 문장 추출

                    # 답변 후보에 추가
                    answer_candidates.extend([answers[i] for i in top_results[1]])

                    # 생성 답변도 완전한 문장이라면, 답변 후보에 추가
                    if ANSWER[-1] in  ['.', '?', '!']:
                        answer_candidates.append(ANSWER)
                # print(answer_candidates)
                answer_can_embs = sbert_model.encode(answer_candidates) # 답변 후보 임베딩

                # 1. 답변 후보들 중 "사용자 발화"와 가장 유사한 것 반환
                user = user[5:-9] # 사용자 발화에서 special token 제외
                user_emb = sbert_model.encode(user)
                
                cos_scores = util.pytorch_cos_sim(user_emb, answer_can_embs)[0] # 사용자 발화 - 추려진 답변 후보군 간 코사인 유사도 계산 후,
                top_results = torch.topk(cos_scores, k=top_k)   # 코사인 유사도 순으로 `top_k` 개 문장 추출

                RESULT = [(answer_candidates[i], score) for score, i in zip(top_results[0], top_results[1])]
                
                # # 2. 답변 후보들을 클러스터링하여 최다 클러스터의 답변 반환
                # num_clusters = 3

                # k_means = KMeans(n_clusters=num_clusters)
                # k_means.fit(answer_can_embs)

                # cluster_assignment = k_means.labels_

                # # 클러스터 개수 만큼 문장을 담을 리스트 초기화
                # clustered_sentences = [[] for _ in range(num_clusters)]
                # # 클러스터링 결과를 돌며 각 클러스터에 맞게 문장 삽입
                # for sentence_id, cluster_id in enumerate(cluster_assignment):
                #     clustered_sentences[cluster_id].append(answer_candidates[sentence_id])
                # print(clustered_sentences)
                # RESULT = sorted(clustered_sentences, key= lambda x: -len(x))


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
