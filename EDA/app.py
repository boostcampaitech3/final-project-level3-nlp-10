import streamlit as st
from multi_app import MultiApp
from apps import (
question_length1,
answer_length,
nouns,
network,
correlation_plot)

st.set_page_config(layout="wide")


apps = MultiApp()

# Add all your application here

apps.add_app("Question 데이터 분포", question_length1.app)
apps.add_app('Answer 데이터 분포', answer_length.app)
apps.add_app('카테고리별 키워드 분석',nouns.app)
apps.add_app('네트워크 분석', network.app)
apps.add_app('카테고리 상관관계 분석',correlation_plot.app)
# The main app
apps.run()