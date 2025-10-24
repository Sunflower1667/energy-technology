import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="생각 정리", page_icon="📝", layout="wide")
st.title("2) 발전량 변화에 대한 개인 생각 정리")

st.markdown("""
그래프를 본 뒤, **왜 이런 변화가 나타났는지** 자신의 생각을 적어보세요.  
가능하면 **증거**(정책·기술·사건 등)를 떠올려 논리적으로 정리합니다.
""")

with st.form("reflection"):
    name = st.text_input("이름 또는 별칭", "")
    q1 = st.text_area("① 어떤 발전원이 늘거나 줄었나요? 그 이유는 무엇이라고 생각하나요?", height=120)
    q2 = st.text_area("② 이러한 변화가 환경과 사회에 미치는 영향은 무엇일까요?", height=120)
    q3 = st.text_area("③ 우리 지역/학교에서 실천할 수 있는 것은 무엇이 있을까요?", height=120)
    submitted = st.form_submit_button("저장")

if "responses" not in st.session_state:
    st.session_state["responses"] = []

if submitted:
    st.session_state["responses"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name or "무명",
        "q1": q1, "q2": q2, "q3": q3
    })
    st.success("저장되었습니다. 아래 표에서 확인하고 CSV로 내려받을 수 있습니다.")

if st.session_state["responses"]:
    df = pd.DataFrame(st.session_state["responses"])
    st.dataframe(df, use_container_width=True)
    st.download_button(
        "모아보기 CSV 다운로드",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="학생_생각정리_응답.csv",
        mime="text/csv"
    )
else:
    st.info("아직 저장된 응답이 없습니다. 위 폼을 작성해 주세요.")
