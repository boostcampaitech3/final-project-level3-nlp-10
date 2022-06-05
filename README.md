```
git clone https://github.com/boostcampaitech3/final-project-level3-nlp-10.git
pip install -r requirements.txt
cd app
streamlit run {app 파일} --server.port {부여받은 포트번호}
# Ex. streamlit run app.py --server.port 30001
```


- 프로젝트 소개
    - WERODA(위로다)
        - 사용자에게 심리상담을 해주는 Multi-Turn 기반의 챗봇
        - KoGPT2 및 Elastic Search를 이용해 구현
        

- 데이터셋
    - [AI-Hub] 웰니스 대화 스크립트 데이터셋
        - 정신 건강 상담 주제의 359개 대화 의도에 대한 5,232개의 사용자 발화 및 1,023개의 챗봇 발화
        - KoGPT2 모델 학습, Retrieval 데이터셋 구축에 사용
    - [songys/Chatbot_data] Chit-Chat 데이터셋
        - 다음 카페 "사랑보다 아름다운 실연([http://cafe116.daum.net/_c21_/home?grpid=1bld](http://cafe116.daum.net/_c21_/home?grpid=1bld))"에서 자주 나오는 이야기들을 참고하여 제작
        - 챗봇 학습용 문답 페어 11,876개
        - 일상 0, 이별(부정) 1, 사랑(긍정) 2로 라벨링
        - Retrieval 데이터셋 구축에 사용
    - [AI-Hub] 감성 대화 말뭉치
        - 60가지 다양한 감정의 코퍼스 27만 문장
        - 우울증 관련 및 대화 응답 시나리오 포함
        - 감성 대화 엔진 또는 챗봇을 개발하려는 목적에 맞추어 제작
        - 형태소 단위의 세부 태깅을 하지 않고 문장 단위의 정합성만 검수하면 데이터 모델링에 큰 문제가 없으며, 문장에서 의미와 의도를 추출하는 확률이 기존 통계 모델링 기법(CRF+ 등)에 비해 월등히 높은 성능을 보여줌
        - Retrieval 데이터셋 구축에 사용

- 모델
    - KoGPT2 (Multi DownStream Task)
        ![1](https://user-images.githubusercontent.com/62659407/172053006-fab0eb7a-d7b5-4bb6-a2de-9b9deb777261.png)

        - 다양한 DownStream Task를 수행할 수 있는 GPT2의 장점을 이용 → Question으로 심리상담 주제 분류와 Answer 생성을 동시에!
        - 심리상담 데이터는 Wellness DataSet, 일상 대화 데이터는 Chit-Chat DataSet을 이용
            - Wellness DataSet2에서 챗봇의 답변에 대한 응답 데이터는 <긍정답변>과 <부정답변>으로 전환 → Multi-Turn 대화에서 사용
            ![1 (1)](https://user-images.githubusercontent.com/62659407/172053018-2ee6fef2-8dfa-4642-b29f-64685db847dc.png)

        - Auto-Regressive
            ![1 (2)](https://user-images.githubusercontent.com/62659407/172053056-f376ca43-698b-43ac-8c13-ddc92763f8c1.png)

            - GPT2는 이전 토큰들을 이용해 다음 토큰을 예측 → Question 뿐만 아니라, 예측한 심리상담 주제를 이용해 Answer을 생성 → 문맥에 맞는 Answer 생성

        - Multi-Turn
            ![1 (3)](https://user-images.githubusercontent.com/62659407/172053076-f0dfdb4d-75d0-4104-9ee8-7e4a24332c76.png)

            - Question을 긍정 답변 및 부정 답변으로 예측했을 때, 사용자의 이전 Question을 추가해 다시 Task 진행 → 연속한 대화 수행 가능

        - Beam Search
            ![1 (4)](https://user-images.githubusercontent.com/62659407/172053095-70c1887c-00e0-4ed0-92cb-2f67ce024ab5.png)

            - Task를 여러 번 수행하여 최다 예측된 심리상담 주제의 Answer을 최종 답변으로 추출 → Answer의 정확도 향상

        - Retrieve
            ![1 (5)](https://user-images.githubusercontent.com/62659407/172053102-3a642ab0-e99b-4852-9da4-1e9ecb6ed488.png)

            - GPT 계열의 생성 모델의 특성 상 Answer의 완성도가 떨어져 챗봇의 성능 하락을 야기
            
            ![1 (6)](https://user-images.githubusercontent.com/62659407/172053119-249763b3-0eea-4515-a6bc-5ff8662df2f4.png)

            → Answer Dataset을 구축하여 Elastic Search의 BM25 Retrieval을 이용해 생성된 Answer과 가장 유사한 답변을 Answer Dataset에서 추출하여 답변으로 채택

        - Conclusion
            ![1 (7)](https://user-images.githubusercontent.com/62659407/172053132-442b2dc4-c8cc-4e0f-854f-c6abadf036f6.png) 

            - 위의 기능들을 모두 결합하고 발전시켜 다음과 같은 과정으로 최종 답변으로 선택
                1. KoGPT2: Question을 이용해 심리상담 주제와 Answer을 5번 생성
                2. Beam Search: 최다 예측된 심리상담 주제의 답변을 채택 → 답변 후보에 추가
                3. Retrieve: 채택된 답변과 유사한 답변을 Answer Dataset에서 5개 검색 → 유사도 점수가 10점 이상인  유사 답변을 답변 후보에 추가
                4. Count: 답변 후보에서 최다 빈도의 답변을 최종 답변으로 선택

- WorkFlow
    ![1 (8)](https://user-images.githubusercontent.com/62659407/172053145-98ba7b1b-56e5-460c-a388-540f75669fac.png)

    1. 사용자가 Question을 입력
    2. Korean UnSmile Dataset으로 학습한 혐오 표현 필터링 모델을 통해 Question의 혐오 표현 점수 확인 → 0.1점 미만이면, 혐오 표현으로 간주해 사용자에게 ‘순화된 표현을 사용하세요’  경고 및 Question 재입력 요구
    3. Model을 이용해 Question에 대한 적절한 Answer 생성 및 출력
    4. Streamlit을 이용해 위 과정을 Chatting 형태의 Web 구현
        
- Validation
    - 모델 성능 평가 지표 (SSA)
        - 2020년 구글이 챗봇 Meena를 발표하면서 도입한 대화 만족도 평가 지표
        - Sensibleness : 답변의 맥락과 논리성 평가
        - Specificity : 답변의 구체성과 사람과의 유사성 평가
        - e.g. 너 중국 음식 좋아해?
            
            → 오늘 메뉴가 뭔가요? (Sensibleness :0, Specificity: 0)
            
            → 응, 좋아해. (Sensibleness :1, Specificity: 0)
            
            → 응, 난 그 중에 ‘짜장면이’ 제일 좋아. (Sensibleness :1, Specificity: 1)
            
    
    - 작업자 간 일치도 평가
        - 구글 Meena 발표 논문의 작업자 간 일치도 평가 방법을 참조
        - Krippendorff’s alpha : 0~1 사이의 값(0 불일치, 1 일치)을 가짐
        - Agreement는 SSA 계산을 위해 사용.
        ![1 (9)](https://user-images.githubusercontent.com/62659407/172053157-6a90fb70-702f-4c29-94aa-dfdc7f8b25fd.png)

        ⇒ 팀의 작업자 간 일치도 평가 점수가 구글 Meena 발표 논문보다 높음 → 팀의 평가 일치도 ↑
        
    
    - 모델 별 성능 평가
        - 모델 성능
            - Sensibleness: 66.60
            - Specificity: 59.39
            - SSA: 62.99
        
        - 다른 모델과 비교
            ![1 (10)](https://user-images.githubusercontent.com/62659407/172053172-3ae29b04-9242-4e76-b7d0-b2bebb270586.png)
            
    - 시연 영상
       
