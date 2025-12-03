import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="운동 데이터 분석", layout="wide")

st.title("🏋️ 운동 데이터 분석 웹페이지")
st.write("체지방률과 상관관계가 높은 속성을 찾고, 산점도와 히트맵을 시각화합니다.")

# 파일 업로드
uploaded_file = st.file_uploader("운동 데이터를 업로드하세요 (CSV 또는 Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # 파일 확장자 체크
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📄 데이터 미리보기")
    st.dataframe(df.head())

    # 숫자형 컬럼만 추출
    numeric_cols = df.select_dtypes(include=["float", "int"]).columns

    if "체지방율" not in numeric_cols:
        st.error("⚠️ 데이터에 '체지방율' 컬럼이 존재하지 않습니다.")
    else:
        st.subheader("📊 체지방율과의 상관관계")

        # 상관계수 계산
        corr_series = df[numeric_cols].corr()["체지방율"].sort_values(ascending=False)
        st.write(corr_series)

        # 가장 상관 높은 속성
        top_corr = corr_series.index[1]  # 첫 번째는 자기 자신이므로 두 번째 선택
        st.success(f"📈 체지방율과 가장 상관관계가 높은 속성: **{top_corr}**")

        # 산점도
        st.subheader("산점도 (Scatter Plot)")
        fig, ax = plt.subplots()
        sns.scatterplot(x=df[top_corr], y=df["체지방율"], ax=ax)
        ax.set_xlabel(top_corr)
        ax.set_ylabel("체지방율")
        st.pyplot(fig)

        # 히트맵
        st.subheader("히트맵 (Correlation Heatmap)")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.heatmap(df[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax2)
        st.pyplot(fig2)
