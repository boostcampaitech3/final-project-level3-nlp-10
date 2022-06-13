import json
import re
import torch
import pickle

from sentence_transformers import SentenceTransformer, util

# !pip install sentence-transformers

def main():
    answer_list = []
    with open("../data/answer_total.json", "r") as file:
        answers = json.load(file)
        for i, answer in answers.items():
            answer_list.append(answer['text'])

    # answer_total의 답변들에서 \n 제거
    answer_list = [re.sub('\n', '', j) for j in answer_list]

    # SBERT 선택지
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    # model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
    # model = SentenceTransformer('Huffon/sentence-klue-roberta-base')
    

    # answer_list 임베딩!
    answer_embeddings = model.encode(answer_list)

    # 임베딩 저장
    with open('answer_embs.pickle', 'wb') as f:
        pickle.dump(answer_embeddings, f)
    
    with open('answers.pickle', 'wb') as f:
        pickle.dump(answer_list, f)


if __name__ =='__main__':
    main()    