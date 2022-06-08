from sklearn.feature_extraction.text import CountVectorizer
import seaborn as sns
import streamlit as st
import pandas as pd
from konlpy.tag import Mecab
import matplotlib.pyplot as plt

def nouns_count1(data,cat,limit = 0) :
    m = Mecab()
    stopwords = ['것','저','수','엔','가','이','은','도','거든요','어','으로',
    '에','이랑','니','도','던','니까','을','거','대체','게','깨','때','나','번','제','데','애','전','내','전','건','뭔가','날',
    '하루','누가','뭐','적','지','걸','때문','그게','이게','정도','후','뭘','중','이것','그거','이거','건가','김','걸까',
    '거기','걔','얼마','그걸','어디','줄','난','걸까요','너','뭔지','뭘까요','땐','가요','쯤','뻔','음','막']
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
        
    # count = Counter(n_nouns)
    # n_best = count.most_common(100) # 빈도 순 추출
    
    # x,y = [], []
    
    # for word, count in n_best :
    #     x.append(word)
    #     y.append(count)

    return n_nouns

def corr_map(data, max_features=500):  # max features = 1000 등 높은값 에러 이슈 rename하지 않은코드는 정상작동
        cv = CountVectorizer(max_features=max_features)
        tdm = cv.fit_transform(data['단어'])
        df = pd.DataFrame(data=tdm.toarray(), columns=cv.get_feature_names_out(), index=list(data.category.unique()))
        df = df.transpose()

        sns.clustermap(df.corr(),
                       annot=True,
                       cmap='RdYlBu_r',
                       vmin=-1, vmax=1,
                       figsize=(12, 10))



def app() :
    st.title('카테고리별 상관관계 분석')
    st.write('📌 각 카테고리 전체에 대해서 count 기반 상위 500 단어에 대한 상관계수와 그에 대한 덴드로그램 입니다.')
    st.write('📌 단어 매핑에 대한 상관관계이기에 값이 클수록 같은 단어의 사용 횟수 차이가 미비합니다. 즉, 같은 단어를 사용한 횟수가 비슷하다고 볼 수 있습니다.')
    url1 = '/opt/ml/streamlit/eda/data/answer.csv'
    url2 = '/opt/ml/streamlit/eda/data/question.csv'
    data = pd.read_csv(url1)
    data1 = pd.read_csv(url2)
    data.drop(['Unnamed: 0'],axis = 1, inplace = True)
    data1.drop(['Unnamed: 0'],axis = 1, inplace = True)
    copy_df = data.copy()
    copy_df1 = data1.copy()
    copy_df['category_under_2']= copy_df['category'].apply(lambda x : '/'.join(x.split('/')[:2]))
    copy_df['category_under_1']= copy_df['category'].apply(lambda x : '/'.join(x.split('/')[:1]))

    copy_df1['category_under_2']= copy_df1['category'].apply(lambda x : '/'.join(x.split('/')[:2]))
    copy_df1['category_under_1']= copy_df1['category'].apply(lambda x : '/'.join(x.split('/')[:1]))

    word_dict = {}
    for i in copy_df1.category_under_1.unique() :
        n_best = nouns_count1(copy_df1,i)
        word_dict[i] = n_best

    df2 = pd.DataFrame(columns = ['단어','category'])
    idx1 = 0
    for i,v in word_dict.items() :
        df2.loc[idx1,'category'] = i
        df2['단어'][idx1] = ' '.join(v)
        idx1 += 1
    
    corr_map(df2)

    st.pyplot(plt)