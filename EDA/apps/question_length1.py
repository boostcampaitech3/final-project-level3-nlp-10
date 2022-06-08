import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
import matplotlib as mpl
import numpy as np
import altair as alt


def app() :
    st.subheader('👇 관심있는 분포를 선택할 수 있습니다.')
    option = st.selectbox('',
                       ('문장 길이 분포', '어절 길이 분포','카테고리 분포'))
	
    st.write('💡 선택한 분포 :', option)
    file_path = '/opt/ml/streamlit/eda/data/question.csv'
    df = pd.read_csv(file_path)
    df.drop(['Unnamed: 0'], axis = 1, inplace = True)
    
    if option == '문장 길이 분포' :
        mpl.rcParams['axes.unicode_minus'] = False
        # 나눔고딕 폰트 적용
        plt.rcParams["font.family"] = 'NanumGothic'
        
        # 통계량 dataframe
        max_context = max(df['context'].map(lambda x: len(x)))
        min_context = min(df['context'].map(lambda x: len(x)))
        mean_context = round(np.mean(df['context'].map(lambda x: len(x))),2)
        ct = pd.DataFrame([max_context,min_context,mean_context])

        ct.index = ['max', 'min','mean']
        ct.columns = ['length']

        # plot.
        fig,ax = plt.subplots(figsize = (10,6))
        ax.hist(df['context'].map(lambda x: len(x)))
        ax.set_xlabel('문장 길이')
        ax.set_ylabel('빈도')

        # columns settings
        col1, col2 = st.columns(2)
        with col1 :
            st.subheader('Question 문장 길이 분포')
            st.pyplot(fig)
        with col2 :
            st.subheader("Summary")
            st.table(ct)
            if st.checkbox('길이 변환 예시') :
                st.subheader('example')
                dt = pd.DataFrame([[df['context'][1], len(df['context'][1])]])
                dt.columns = ['원본 텍스트', '변환']
                st.table(dt)

    elif option == '어절 길이 분포' :
        mpl.rcParams['axes.unicode_minus'] = False
        # 나눔고딕 폰트 적용
        plt.rcParams["font.family"] = 'NanumGothic'
        st.write('📌 어절 : 문장을 이루는 도막도막의 마디. 문장 성분의 최소 단위로서 띄어쓰기의 단위가 됨')
        st.write('📌 띄어쓰기를 기준으로 토큰별 길이의 평균을 살펴 보고자 했습니다.')
        # file_path = '/opt/ml/excercise/eda/data/question.csv'
        # df = pd.read_csv(file_path)
        # df.drop(['Unnamed: 0'], axis = 1, inplace = True)

        max_context = max(df['context'].str.split().apply(lambda x : [len(i) for i in x]).map(lambda x: np.mean(x)))
        min_context = min(df['context'].str.split().apply(lambda x : [len(i) for i in x]).map(lambda x: np.mean(x)))
        mean_context = round(np.mean(df['context'].str.split().apply(lambda x : [len(i) for i in x]).map(lambda x: np.mean(x))),2)
        ct = pd.DataFrame([max_context,min_context,mean_context])

        ct.index = ['max', 'min','mean']
        ct.columns = ['length']


        # select box dataframe
        col1 = df['context'][1]
        col2 = [len(i) for i in df['context'][1].split()]
        dt1 = pd.DataFrame([[col1, col2]])
        dt1.columns = ['원본 텍스트', '변환']

        answer = ''
        for i in range(len(dt1['변환'])) :
            cnt = 0
            for j in dt1['변환'][i] :
                if cnt == len(dt1['변환'][i])-1 :
                    answer += str(j)
                else :
                    answer += str(j) + ' '
                    cnt += 1
        dt1['변환'] = answer

        # plot
        fig,ax = plt.subplots(figsize = (10,6))
        ax.hist(df['context'].str.split().apply(lambda x : [len(i) for i in x]).map(lambda x: np.mean(x)))
        ax.set_xlabel('어절 길이 평균')
        ax.set_ylabel('빈도')

        # column 1,2 settings
        col1, col2 = st.columns(2)
        with col1 :
            st.subheader('Question 어절 길이 분포')
            st.pyplot(fig)
        with col2 :
            st.subheader("Summary")
            st.table(ct)
            if st.checkbox('어절 변환 예시') :
                 st.subheader('example')
                 st.table(dt1)

    elif option == '카테고리 분포' :
        copy_df = df.copy()
        copy_df['category_under_2']= copy_df['category'].apply(lambda x : '/'.join(x.split('/')[:2]))
        copy_df['category_under_1']= copy_df['category'].apply(lambda x : '/'.join(x.split('/')[:1]))
        cat_option = st.selectbox(
            '카테고리 구분 기준',
            ('원본', '소주제', '대주제'))

        st.write('💡 구분 기준 :', cat_option)
        if cat_option == '원본' :
            idx_list,value_list = [],[]
            for i,v in copy_df['category'].value_counts(ascending = True, sort = True).items() :
                idx_list.append(i)
                value_list.append(v)

            value_list.sort(reverse= True)

            count_cat = pd.DataFrame({'category' : idx_list, 'counts' : value_list})

            # count_cat.index = count_cat['category']
            # count_cat.drop(['category'],axis = 1, inplace = True)

            # column 1,2 settings
            with st.container() :
                st.subheader('Category 분포')
                start_rows,end_rows = st.slider(
                    '카테고리 범위 선택',0, 359, (0, 30))
                st.write('start row :',start_rows, 'end row :',end_rows )
                #st.bar_chart(count_cat[start_rows:end_rows])
                if start_rows == end_rows :
                    if start_rows == 0:
                        end_rows += 1
                    else : 
                        start_rows -= 1
                st.write(alt.Chart(count_cat[start_rows:end_rows]).mark_bar().encode(
                x=alt.X('category', sort=None),
                y='counts'))
            with st.container() :
                st.subheader("Summary")
                cat_mean = np.mean(count_cat[start_rows:end_rows]['counts'])
                cat_max = max(count_cat[start_rows:end_rows]['counts'])
                cat_min = min(count_cat[start_rows:end_rows]['counts'])
                idx = ['max','min','mean']
                col = ['summary']
                cat_dt = pd.DataFrame([cat_max,cat_min,cat_mean], index = idx, columns = col)
                cat_dt = cat_dt.summary.round(1)
                st.table(cat_dt)    
                if st.checkbox('Table 보기') :
                    st.table(copy_df.head(20))

        if cat_option == '소주제' :
            idx_list,value_list = [],[]
            for i,v in copy_df['category_under_2'].value_counts(ascending = True, sort = True).items() :
                idx_list.append(i)
                value_list.append(v)

            value_list.sort(reverse= True)

            count_cat = pd.DataFrame({'category' : idx_list, 'counts' : value_list})

            # count_cat.index = count_cat['category']
            # count_cat.drop(['category'],axis = 1, inplace = True)

            # column 1,2 settings
            with st.container() :
                st.subheader('Category 분포')
                start_rows,end_rows = st.slider(
                    'Select a range of values',0, 177, (0, 30))
                st.write('start row :',start_rows, 'end row :',end_rows )
                #st.bar_chart(count_cat[start_rows:end_rows])
                if start_rows == end_rows :
                    if start_rows == 0:
                        end_rows += 1
                    else : 
                        start_rows -= 1
                st.write(alt.Chart(count_cat[start_rows:end_rows]).mark_bar().encode(
                x=alt.X('category', sort=None),
                y='counts'))
            with st.container() :
                st.subheader("Table")
                cat_mean = np.mean(count_cat[start_rows:end_rows]['counts'])
                cat_max = max(count_cat[start_rows:end_rows]['counts'])
                cat_min = min(count_cat[start_rows:end_rows]['counts'])
                idx = ['max','min','mean']
                col = ['summary']
                cat_dt = pd.DataFrame([cat_max,cat_min,cat_mean], index = idx, columns = col)
                cat_dt = cat_dt.summary.round(1)
                st.table(cat_dt)    
                if st.checkbox('Table 보기') :
                    st.table(copy_df.head(20))

        if cat_option == '대주제' :
            idx_list,value_list = [],[]
            for i,v in copy_df['category_under_1'].value_counts(ascending = True, sort = True).items() :
                idx_list.append(i)
                value_list.append(v)

            value_list.sort(reverse= True)

            count_cat = pd.DataFrame({'category' : idx_list, 'counts' : value_list})

            # count_cat.index = count_cat['category']
            # count_cat.drop(['category'],axis = 1, inplace = True)

            # column 1,2 settings
            with st.container() :
                st.subheader('Category 분포')
                start_rows,end_rows = st.slider(
                    'Select a range of values',0, 12, (0, 12))
                st.write('start row :',start_rows, 'end row :',end_rows )
                #st.bar_chart(count_cat[start_rows:end_rows])
                if start_rows == end_rows :
                    if start_rows == 0:
                        end_rows += 1
                    else : 
                        start_rows -= 1
                st.write(alt.Chart(count_cat[start_rows:end_rows]).mark_bar().encode(
                x=alt.X('category', sort=None),
                y='counts'))
            with st.container() :
                st.subheader("Table")
                cat_mean = np.mean(count_cat[start_rows:end_rows]['counts'])
                cat_max = max(count_cat[start_rows:end_rows]['counts'])
                cat_min = min(count_cat[start_rows:end_rows]['counts'])
                idx = ['max','min','mean']
                col = ['summary']
                cat_dt = pd.DataFrame([cat_max,cat_min,cat_mean], index = idx, columns = col)
                cat_dt = cat_dt.summary.round(1)
                st.table(cat_dt)    
                if st.checkbox('Table 보기') :
                    st.table(copy_df.head(20))




