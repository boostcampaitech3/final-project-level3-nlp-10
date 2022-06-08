import pandas as pd
from konlpy.tag import Mecab
import math
from collections import Counter
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx
from matplotlib import font_manager, rc
import matplotlib as mpl
import numpy as np
import warnings
warnings.filterwarnings('ignore')
font_location = '/opt/ml/streamlit/eda/fonts/NanumGothic.ttf'
font_name = font_manager.FontProperties(fname=font_location).get_name()
mpl.rc('font', family=font_name)

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

def relatedWordFinder2(df,col, word_list, before):
    return_basket = []
    related_list = []
    if before > 0:
        for i in range(1, before+1):
            globals()['rt_{}'.format(i)] = [] # 리스트 생성
    
    rows = df[col]
    
    for i in range(len(df)):
        toks = rows[i]
        for k in range(len(word_list)):
            word = word_list[k]
            for t in range(len(toks)):    
                if toks[t] == word:

                    putin_list = [df['category'][i],word]
                    idx = t
                    if before > 0: 
                        for j in range(1,before+1):
                            globals()['related_idx_{}'.format(j)] = idx - j
                            globals()['related_word_{}'.format(j)] = toks[globals()['related_idx_{}'.format(j)]]
                            globals()['rt_{}'.format(j)].append([df['category'][i], globals()['related_word_{}'.format(j)],j])
                            putin_list.append(globals()['related_word_{}'.format(j)])                   

                    related_list.append(putin_list)
                else:
                    pass

    if before > 0:
        for i in range(1, before+1):
            return_basket.append(globals()['rt_{}'.format(i)])


    return_basket.append(related_list)
    return return_basket

def linkingMaker2(basket,before):
    relation = pd.DataFrame(basket[before])
    columns = ['group','word']
    for i in range(1, before+1):
        col = 'b{}'.format(i)
        columns.append(col)
    relation.columns = columns
    for i in range(before):
        globals()['rt{}'.format(i+1)] = pd.DataFrame(basket[i])
        globals()['rt{}'.format(i+1)].columns = ['group','id','distance']
    rt0 = relation[['group','word']]
    rt0['distance'] = np.nan
    rt0.fillna(0,inplace = True)

    for i in range(1,before+1):
        if i == 1:
            globals()['link_{}'.format(i)] = relation[['b{}'.format(i),'word']]
            globals()['link_{}'.format(i)]['from'] = globals()['rt{}'.format(1)]['distance']
            globals()['link_{}'.format(i)]['to'] = rt0['distance']
            globals()['link_{}'.format(i)].columns = ['source','target','from','to']

        else:
            globals()['link_{}'.format(i)] = relation[['b{}'.format(i),'b{}'.format(i-1)]]
            globals()['link_{}'.format(i)]['from'] = globals()['rt{}'.format(i)]['distance']
            globals()['link_{}'.format(i)]['to'] = globals()['rt{}'.format(i-1)]['distance']
            globals()['link_{}'.format(i)].columns = ['source','target','from','to']

    linkinglist = []
    for i in range(1,before+1):
        linkinglist.append(globals()['link_{}'.format(i)])
    linking = pd.concat(linkinglist, ignore_index = True)
    return linking

cmpList = [plt.cm.Blues,plt.cm.Reds,plt.cm.cividis_r]
alphas = [0.88,0.88,0.78]
def network2(linkDF, cmap,alpha):
    plt.figure(figsize = (16,16))
    g_node = nx.from_pandas_edgelist(linkDF, 'source', 'target', create_using = nx.DiGraph()) # 노드 크기 계산을 위함
    g = nx.from_pandas_edgelist(linkDF, 'source', 'target', create_using = nx.cubical_graph())
    degree_dict = g_node.in_degree()
    degree= nx.degree(g)
    layout = nx.kamada_kawai_layout(g,scale = 1.2)
    nx.draw(g, with_labels=True,pos = layout,node_size=[150 + v[1]*250 for v in degree_dict],
        font_family = font_name,
        node_color=[math.sqrt(n[1]*10)*1.7 for n in degree_dict],
        cmap=cmap,vmin = 20,vmax =40 , alpha=alpha)

def app() :
    st.title('주변 단어 네트워크 분석')
    st.write('📌 전체 데이터에서 가장 많이 출현한 단어들의 주변에는 어떤 단어들이 있는지 최다 빈도 단어들로 네트워크 분석을 진행합니다.')
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

    dict2 = {}
    
    for i in copy_df1.category_under_1.unique() :
        x = nouns_count1(copy_df1,i)
        dict2[i] = x

    dict1 = {}
    for i in copy_df.category_under_1.unique() :
        x = nouns_count1(copy_df,i)
        dict1[i] = x

    reClass = pd.DataFrame(index = dict2.keys(),columns = ['질문','답변'])
    dict1['일반대화'] = 'none'
    reClass['질문'] = dict2.values()
    reClass['답변'] = dict1.values()

    reClass = reClass.reset_index()
    reClass.columns = ['category','질문','답변']

    party = ['질문','답변']
    tokens = []
    for i in range(len(reClass)):
        for k in party:
            tokens += reClass[k][i]
    
    ziff_cnt = Counter(tokens)
    ziff_tags = ziff_cnt.most_common(50)
    ziff_tags = dict(ziff_tags)

    tag_df = pd.DataFrame([ziff_tags])
    tag_df = tag_df.transpose()

    tag_df = tag_df.reset_index()
    tag_df.columns = ['tag_nm','tag_cnt']

    tag_df['log_cnt'] = tag_df['tag_cnt'].apply(lambda x: math.log2(x))
    option = st.selectbox('',
                       ('전체 단어 출현 빈도','전체 단어 출현 빈도의 로그값','네트워크 분석'))
    if option == '전체 단어 출현 빈도' :
        st.write('📌 전체 단어 출현 빈도 : 질문 데이터와 답변 데이터를 합산한 단어 출현 빈도 결과입니다.')
        fig, ax = plt.subplots(figsize = (15,5))
        plt.bar(tag_df['tag_nm'],tag_df['tag_cnt'], color = 'darkseagreen')
        plt.plot(tag_df['tag_nm'],tag_df['tag_cnt'],color = 'mediumseagreen')
        plt.xticks(rotation = 90)
        plt.box()
        plt.show()
        st.pyplot(fig)
    elif option == '전체 단어 출현 빈도의 로그값' :
        st.write('📌 전체 단어 출현 빈도의 로그값 : 합산된 출현 빈도의 로그값을 구한 결과입니다.')
        fig, ax = plt.subplots(figsize = (15,5))
        #plt.scatter(tag_df['tag_nm'],tag_df['log_cnt'],c='greenyellow')
        plt.bar(tag_df['tag_nm'],tag_df['log_cnt'], color = 'mediumseagreen')
        plt.plot(tag_df['tag_nm'],tag_df['log_cnt'])
        plt.xticks(rotation = 90)
        plt.ylim(4.3,6.8)
        plt.box()
        plt.show()
        log_g = tag_df[tag_df['log_cnt'] > 6]
        st.pyplot(fig)
        if st.checkbox('log 값이 6 이상인 단어 확인') :
            st.table(log_g)
    
    else :
        with st.form('form', clear_on_submit=True):
            user_input = st.text_input('💡 여기에 단어를 입력하면 주변 단어를 파악할 수 있습니다.(띄어쓰기로 단어를 구분하며 너무 많이 넣으면 오래 걸립니다.) : ', '')
            submitted = st.form_submit_button('입력')
            if user_input == '' :
                st.write('📌 스트레스,불안, 마음 키워드로 네트워크를 표시한 결과입니다.')
                party = ['질문','답변']
                for i in range(len(party)):
                    globals()['basket_{}'.format(i)] = relatedWordFinder2(reClass,party[i], ['스트레스','불안','마음'], 2)
                    globals()['links_{}'.format(i)] = linkingMaker2(globals()['basket_{}'.format(i)],2)
                    network2(globals()['links_{}'.format(i)], cmpList[i], alphas[i])
                    plt.title("최빈도 단어의 주변 단어 네트워크 - %s" % party[i],fontsize = 20)
                    st.pyplot(plt)
            else :
                user_input = user_input.split()
                st.write(f'📌 {" ".join(user_input)} 키워드로 네트워크를 표시한 결과입니다.')
                party = ['질문','답변']
                for i in range(len(party)):
                    globals()['basket_{}'.format(i)] = relatedWordFinder2(reClass,party[i], user_input, 2)
                    globals()['links_{}'.format(i)] = linkingMaker2(globals()['basket_{}'.format(i)],2)
                    network2(globals()['links_{}'.format(i)], cmpList[i], alphas[i])
                    plt.title("최다빈도 단어의 주변 단어 네트워크 - %s" % party[i],fontsize = 20)
                    st.pyplot(plt)


# with st.form('form', clear_on_submit=True):
#                         user_input = st.text_input('입력할 단어 : ', '')
#                         submitted = st.form_submit_button('전송')
#                     if user_input == '' :
#                         if option == '전체' :
#                             st.write(f'"전체" 문장 총 {len(copy_df)}개, 아직 키워드를 입력하지 않았습니다.')
#                         else :
#                             st.write(f'카테고리가 "{option}"인 문장 총 {len(copy_df[copy_df["category_under_1"] == option])}개, 아직 키워드를 입력하지 않았습니다.')
#                     else :

#                         idx_list = []
#                         for i in copy_df[copy_df['category_under_1'] == option]['context'] :
#                             if user_input in i :
#                                 idx_list.append(copy_df[copy_df['context'] == i].index[0])
                        
#                         if idx_list != [] :
#                             st.write(f'"{user_input}"이(가) 들어간 문장 총 {len(copy_df.iloc[idx_list[:]])}개')
#                             find_df = copy_df.iloc[idx_list[:]][['context','category_under_1']]
#                             st.table(find_df) 