from konlpy.tag import Mecab
from collections import Counter
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
import matplotlib as mpl
import numpy as np
import altair as alt
from wordcloud import WordCloud

def nouns_count(data,cat,limit = 0) :
    m = Mecab()
    stopwords = ['것','저','수','엔','가','이','은','도','거든요','어','으로',
    '에','이랑','니','도','던','니까','을','거','대체','게','깨','때','나','번','제','데','애','전','내','전','건','뭔가','날',
    '하루','누가','뭐','적','지','걸','때문','그게','이게','정도','후','뭘','중','이것','그거','이거','건가','김','걸까',
    '거기','걔','얼마','그걸','어디','줄','난','걸까요','너','뭔지','뭘까요','땐']
    if cat == '전체' :
        context = data['context'].to_list()
    else :
        context = data[data['category_under_1'] == cat]['context'].to_list()
    n_nouns = []

    for t in context :
        for n in m.nouns(t) : # 명사 추출
            if len(n) > limit :
                if n not in stopwords : 
                    n_nouns.append(n)
        
    count = Counter(n_nouns)
    n_best = count.most_common(100) # 빈도 순 추출
    
    x,y = [], []
    
    for word, count in n_best :
        x.append(word)
        y.append(count)

    return n_best,x,y

def app() :
    st.title('카테고리별 키워드 분석')
    main_option = st.selectbox('데이터를 선택하세요!',
    ('Question','Answer'))
    mpl.rcParams['axes.unicode_minus'] = False
        # 나눔고딕 폰트 적용
    plt.rcParams["font.family"] = 'NanumGothic'
    
    if main_option == 'Question' :
        url1 = '/opt/ml/streamlit/eda/data/question.csv'

        df = pd.read_csv(url1)
        df.drop(['Unnamed: 0'],axis = 1, inplace = True)

        copy_df = df.copy()
        copy_df['category_under_2']= copy_df['category'].apply(lambda x : '/'.join(x.split('/')[:2]))
        copy_df['category_under_1']= copy_df['category'].apply(lambda x : '/'.join(x.split('/')[:1]))
        option = st.selectbox('카테고리를 선택하세요!',
                        ('전체','감정', '내원이유', '모호함', '배경', '부가설명', '상태', '원인', '일반대화', '자가치료',
        '증상', '치료이력', '현재상태'))

        st.write('📌 선택한 카테고리 :', option)
        n_best,x,y= nouns_count(copy_df,option)
        
        nd = pd.DataFrame({'명사' : x,'빈도' : y})

        # columns settings
        with st.container() :
            # col1, col2 = st.columns(2)
            # with col1 :
            # st.subheader('명사 빈도')
            start_rows,end_rows = st.slider(
                '키워드 범위 선택',0, len(nd), (0,min(len(nd),10)))
            # st.write('start row :',start_rows, 'end row :',end_rows )
            #st.bar_chart(count_cat[start_rows:end_rows])
            if start_rows == 0 :
                st.subheader(f'"{option}" 키워드 top {end_rows}')
            else :
                st.subheader(f'"{option}" 키워드 top {start_rows} ~ {end_rows}')

            if start_rows == end_rows :
                if start_rows == 0:
                    end_rows += 1
                else : 
                    start_rows -= 1
            st.write(alt.Chart(nd[start_rows:end_rows]).mark_bar().encode(
            x=alt.X('명사', sort=None),
            y='빈도'))

        with st.container() :
            col1, col2 = st.columns(2)
            
            with col1 :
                checkbox_btn = st.checkbox('테이블 형식으로 보기')
                checkbox_btn2 = st.checkbox('워드클라우드로 보기', value=True)
                if checkbox_btn:
                    st.subheader("Table")
                    st.table(nd.iloc[start_rows:end_rows])
                if checkbox_btn2:
                    dic = {}
                    for i,v in zip(nd['명사'],nd['빈도']) :
                        dic[i] = v

                    font='/opt/ml/streamlit/eda/fonts/NanumGothic.ttf'
                    wc = WordCloud(font_path=font,\
                            background_color="white", \
                            width=1000, \
                            height=1000, \
                            max_font_size = 200)
                    wc = wc.generate_from_frequencies(dic)



                    fig = plt.figure()  # 스트림릿에서 plot그리기
                    plt.title(f'{option} 키워드')
                    plt.imshow(wc, interpolation='bilinear')
                    plt.axis('off')
                    plt.show()
                    st.pyplot(fig)

            with col2 : 
                if st.checkbox('특정 단어가 들어간 문장 확인하기',value = True) :
                    with st.form('form', clear_on_submit=True):
                        user_input = st.text_input('입력할 단어 : ', '')
                        submitted = st.form_submit_button('입력')
                    if user_input == '' :
                        if option == '전체' :
                            st.write(f'"전체" 문장 총 {len(copy_df)}개, 아직 키워드를 입력하지 않았습니다.')
                        else :
                            st.write(f'카테고리가 "{option}"인 문장 총 {len(copy_df[copy_df["category_under_1"] == option])}개, 아직 키워드를 입력하지 않았습니다.')
                    else :
                        idx_list = []
                        for i in copy_df[copy_df['category_under_1'] == option]['context'] :
                            if user_input in i :
                                idx_list.append(copy_df[copy_df['context'] == i].index[0])
                        
                        if idx_list != [] :
                            st.write(f'"{user_input}"이(가) 들어간 문장 총 {len(copy_df.iloc[idx_list[:]])}개')
                            find_df = copy_df.iloc[idx_list[:]][['context','category_under_1']]
                            st.table(find_df) 

    if main_option == 'Answer' :
        url1 = '/opt/ml/streamlit/eda/data/answer.csv'

        df = pd.read_csv(url1)
        df.drop(['Unnamed: 0'],axis = 1, inplace = True)

        copy_df = df.copy()
        copy_df['category_under_2']= copy_df['category'].apply(lambda x : '/'.join(x.split('/')[:2]))
        copy_df['category_under_1']= copy_df['category'].apply(lambda x : '/'.join(x.split('/')[:1]))
        option = st.selectbox('카테고리를 선택하세요!',
                        ('전체','감정', '내원이유', '모호함', '배경', '부가설명', '상태', '원인', '자가치료', '증상',
       '치료이력', '현재상태'))

        st.write('📌 선택한 카테고리 :', option)
        n_best,x,y= nouns_count(copy_df,option)
        
        nd = pd.DataFrame({'명사' : x,'빈도' : y})

        # columns settings
        with st.container() :
            # col1, col2 = st.columns(2)
            # with col1 :
            start_rows,end_rows = st.slider(
                '키워드 범위 선택',0, len(nd), (0, min(len(nd),10)))
            # st.write('start row :',start_rows, 'end row :',end_rows )
            if start_rows == 0 :
                st.subheader(f'"{option}" 키워드 top {end_rows}')
            else :
                st.subheader(f'"{option}" 키워드 top {start_rows} ~ {end_rows}')
            #st.bar_chart(count_cat[start_rows:end_rows])
            if start_rows == end_rows :
                if start_rows == 0:
                    end_rows += 1
                else : 
                    start_rows -= 1
            st.write(alt.Chart(nd[start_rows:end_rows]).mark_bar().encode(
            x=alt.X('명사', sort=None),
            y='빈도'))

        with st.container() :
            col1, col2 = st.columns(2)
            
            with col1 :
                checkbox_btn = st.checkbox('테이블 형식으로 보기')
                checkbox_btn2 = st.checkbox('워드클라우드로 보기', value=True)
                if checkbox_btn:
                    st.subheader("Table")
                    st.table(nd.iloc[start_rows:end_rows])
                if checkbox_btn2:
                    dic = {}
                    for i,v in zip(nd['명사'],nd['빈도']) :
                        dic[i] = v

                    font='/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
                    wc = WordCloud(font_path=font,\
                            background_color="white", \
                            width=1000, \
                            height=1000, \
                            max_font_size = 200)
                    wc = wc.generate_from_frequencies(dic)



                    fig = plt.figure()  # 스트림릿에서 plot그리기
                    plt.title(f'{option} 키워드')
                    plt.imshow(wc, interpolation='bilinear')
                    plt.axis('off')
                    plt.show()
                    st.pyplot(fig)

            with col2 : 
                if st.checkbox('특정 단어가 들어간 문장 확인하기', value = True) :
                    with st.form('form', clear_on_submit=True):
                        user_input = st.text_input('입력할 단어 : ', '')
                        submitted = st.form_submit_button('입력')
                    if user_input == '' :
                        if option == '전체' :
                            st.write(f'"전체" 문장 총 {len(copy_df)}개, 아직 키워드를 입력하지 않았습니다.')
                        else :
                            st.write(f'카테고리가 "{option}"인 문장 총 {len(copy_df[copy_df["category_under_1"] == option])}개, 아직 키워드를 입력하지 않았습니다.')
                    else :

                        idx_list = []
                        for i in copy_df[copy_df['category_under_1'] == option]['context'] :
                            if user_input in i :
                                idx_list.append(copy_df[copy_df['context'] == i].index[0])
                        
                        if idx_list != [] :
                            st.write(f'"{user_input}"이(가) 들어간 문장 총 {len(copy_df.iloc[idx_list[:]])}개')
                            find_df = copy_df.iloc[idx_list[:]][['context','category_under_1']]
                            st.table(find_df) 
    
